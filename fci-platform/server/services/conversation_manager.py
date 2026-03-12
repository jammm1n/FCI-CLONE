"""
FCI Platform — Conversation Manager Service

Manages the full lifecycle of investigation conversations:
- Creating conversations (with initial case data injection + AI assessment)
- Sending messages (context assembly → AI call → storage)
- Step-based investigation flow (step transitions, summaries)
- Retrieving conversation history (visible messages only)
- Assembling the API payload for each Anthropic API call

This is the orchestration layer between the routers, the AI client,
and MongoDB. It owns the conversation state.

MongoDB document structure (conversations collection):
{
    "_id": "conv_abc123",
    "case_id": "CASE-2026-0451",
    "user_id": "user_001",
    "status": "active",
    "investigation_state": {
        "current_step": 1,
        "steps": [
            {
                "step_number": 1,
                "phase": "setup",
                "status": "active",
                "summary": null,
                ...
            }
        ]
    },
    "messages": [
        {
            "message_id": "msg_001",
            "role": "system_injected",
            "content": "...",
            "step": 1,
            "timestamp": datetime,
            "visible": false,
            ...
        },
    ],
    "created_at": datetime,
    "updated_at": datetime,
}
"""

import asyncio
import logging
import uuid
import base64
from datetime import datetime, timezone
from pathlib import Path

from server.config import (
    settings, STEP_CONFIG, STEP_PHASES,
    MULTI_USER_STEP_CONFIG, MULTI_USER_STEP_PHASES,
    MULTI_USER_BLOCK_DATA, ALL_SECTIONS, NO_INJECTION,
)
from server.database import get_database
from server.services.ai_client import (
    get_ai_response,
    get_ai_response_streaming,
    build_user_message_content,
    TOOLS_ONESHOT_SETUP,
    TOOLS_ONESHOT_EXECUTE,
)
from server.services.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INITIAL_ASSESSMENT_INSTRUCTION = (
    "Case data loaded. Execute Phase 0A from icr-steps-setup.md: "
    "case type classification, data inventory (hard blockers, soft gaps, received), "
    "anomalies in received data, and clarifying questions. "
    "Do NOT produce a narrative or risk assessment yet — that comes in Phase 0B "
    "after the investigator responds. Do NOT use the get_reference_document tool "
    "for this initial assessment — work with the case data, your core knowledge, "
    "and the Standard Hard Blockers Reference in the step document."
)

SUMMARY_SYSTEM_PROMPT = """\
You are summarizing one step of a financial crime investigation. Your summary will
be provided to a fresh AI instance that continues the investigation in the next step.
The fresh instance will NOT have access to this step's conversation — only this summary.

MUST PRESERVE:
- All factual findings: transaction amounts, dates, addresses, counterparties, risk
  indicators, patterns identified
- All decisions and their rationale
- Key conclusions from reference documents consulted
- What investigation steps have been completed and what remains
- Open questions, flags, or items deferred for later steps
- Investigator instructions or preferences stated during this step
- KYC verification results and identity discrepancies
- Specific numerical thresholds or values that informed decisions

MUST NOT PRESERVE:
- Full text of retrieved SOPs — only the relevant findings and rules applied
- Conversational filler, acknowledgments
- Redundant restatement of case data (the AI always has fresh case data)
- Step-by-step reasoning process if the conclusion is clear

FORMAT: Use the structured template below. Target 1,000-2,500 tokens.
Up to 3,000 for complex steps with many findings.

## Step {step_number} Summary: {phase_name}

### Case Classification
[Current case type, any changes or refinements from this step]

### Key Findings
[Bullet points: most important facts, risk indicators, and conclusions]

### Decisions Made
[What was decided or confirmed: KYC status, classification, risk level, etc.]

### Evidence Reviewed
[Which data sources were examined, what was found, what was ruled out]

### Documents Consulted
[Which SOPs/guidelines were retrieved and the specific guidance applied]

### Open Questions
[Anything flagged for investigation in subsequent steps]

### Case Form Sections Completed
[Which sections of the case template were drafted and approved]"""

MULTI_USER_SUMMARY_ADDENDUM = """
This is a multi-user case. Your summary MUST:
- Use UID labels to distinguish per-subject findings
- Cover all subjects, even if a subject had no relevant data at this step
- This summary will be the primary context for subsequent blocks"""

MULTI_USER_INITIAL_ASSESSMENT = (
    "Case data loaded. This is a multi-user case with {n} subjects: {uids}. "
    "Execute Phase 0A from icr-steps-setup.md: case type classification, "
    "data inventory for EACH subject (hard blockers, soft gaps, received), "
    "anomalies, connections between subjects, and clarifying questions. "
    "Do NOT produce a narrative yet — that comes in Phase 0B."
)


def _generate_id(prefix: str = "msg") -> str:
    """Generate a short unique ID with a prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _now() -> datetime:
    """Current UTC timestamp."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Conversation creation
# ---------------------------------------------------------------------------

async def create_conversation(
    user_id: str,
    knowledge_base: KnowledgeBase,
    case_id: str | None = None,
    mode: str = "case",
) -> dict:
    """
    Create a new conversation — lightweight, no AI call.

    For mode="case": loads case, builds case data, pre-stores system_injected
    message, initializes investigation_state, updates case status.
    AI assessment triggered separately via send_message_streaming
    with is_initial_assessment=True.

    For mode="free_chat": creates empty conversation doc, no case data.

    Returns:
        dict with conversation_id, case_id (or None), mode.
    """
    db = get_database()
    conversation_id = _generate_id("conv")
    now = _now()

    if mode == "case":
        if not case_id:
            raise ValueError("case_id is required for case mode")

        # Load the case
        case = await db.cases.find_one({"_id": case_id})
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        if case.get("conversation_id"):
            # Already has a conversation — return it instead of erroring
            existing_id = case["conversation_id"]
            logger.info("Case %s already has conversation %s — returning existing", case_id, existing_id)
            return {
                "conversation_id": existing_id,
                "case_id": case_id,
                "mode": "case",
            }

        # Detect multi-user case
        is_multi = case.get("case_mode") == "multi"
        logger.info("create_conversation: case_id=%s, case_mode=%s, is_multi=%s", case_id, case.get("case_mode"), is_multi)
        step_config = MULTI_USER_STEP_CONFIG if is_multi else STEP_CONFIG
        step_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES
        total_steps = 9 if is_multi else 5

        # Build case data markdown and pre-store the system_injected message
        case_data_markdown = _build_case_data_markdown(case)

        if is_multi:
            subjects = case.get("subjects", [])
            uids = ", ".join(
                s.get("user_id") or f"Subject {i+1}"
                for i, s in enumerate(subjects)
            )
            instruction = MULTI_USER_INITIAL_ASSESSMENT.format(
                n=len(subjects), uids=uids,
            )
        else:
            instruction = INITIAL_ASSESSMENT_INSTRUCTION

        initial_user_content = (
            f"[CASE DATA]\n\n{case_data_markdown}\n\n{instruction}"
        )

        case_data_message = {
            "message_id": _generate_id("msg"),
            "role": "system_injected",
            "content": initial_user_content,
            "step": 1,
            "timestamp": now,
            "visible": False,
        }

        # Build step labels for frontend StepIndicator
        step_labels = {}
        for block_num, block_config in step_config.items():
            if block_num == "summary":
                continue
            step_labels[str(block_num)] = block_config.get("label", "")

        conversation_doc = {
            "_id": conversation_id,
            "case_id": case_id,
            "user_id": user_id,
            "mode": "case",
            "case_mode": "multi" if is_multi else "single",
            "title": "",
            "status": "active",
            "investigation_state": {
                "current_step": 1,
                "total_steps": total_steps,
                "step_labels": step_labels,
                "steps": [
                    {
                        "step_number": 1,
                        "phase": step_phases[1],
                        "label": step_labels.get("1", ""),
                        "status": "active",
                        "summary": None,
                        "summary_model": None,
                        "summary_token_usage": None,
                        "completed_at": None,
                        "approved_by": None,
                    }
                ],
            },
            "messages": [case_data_message],
            "created_at": now,
            "updated_at": now,
        }
        await db.conversations.insert_one(conversation_doc)

        # Update the case
        await db.cases.update_one(
            {"_id": case_id},
            {
                "$set": {
                    "conversation_id": conversation_id,
                    "status": "in_progress",
                    "updated_at": now,
                }
            }
        )

        logger.info("Created case conversation %s for case %s (step 1)", conversation_id, case_id)

    elif mode == "oneshot":
        # One-shot mode: like case mode but no investigation_state (no steps)
        if not case_id:
            raise ValueError("case_id is required for oneshot mode")

        case = await db.cases.find_one({"_id": case_id})
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        if case.get("conversation_id"):
            existing_id = case["conversation_id"]
            logger.info("Case %s already has conversation %s — returning existing", case_id, existing_id)
            return {
                "conversation_id": existing_id,
                "case_id": case_id,
                "mode": "oneshot",
            }

        # Build case data and store as system_injected
        case_data_markdown = _build_case_data_markdown(case)
        initial_user_content = (
            f"[CASE DATA]\n\n{case_data_markdown}\n\n"
            "Review this case data thoroughly. Identify any gaps, ambiguities, "
            "or missing information. Ask clarifying questions if needed, then "
            "signal when you are ready for full ICR execution."
        )

        case_data_message = {
            "message_id": _generate_id("msg"),
            "role": "system_injected",
            "content": initial_user_content,
            "timestamp": now,
            "visible": False,
        }

        conversation_doc = {
            "_id": conversation_id,
            "case_id": case_id,
            "user_id": user_id,
            "mode": "oneshot",
            "title": "",
            "status": "active",
            "oneshot_ready": False,
            "oneshot_executed": False,
            "messages": [case_data_message],
            "created_at": now,
            "updated_at": now,
        }
        await db.conversations.insert_one(conversation_doc)

        await db.cases.update_one(
            {"_id": case_id},
            {
                "$set": {
                    "conversation_id": conversation_id,
                    "status": "in_progress",
                    "updated_at": now,
                }
            }
        )

        logger.info("Created oneshot conversation %s for case %s", conversation_id, case_id)

    else:  # free_chat
        conversation_doc = {
            "_id": conversation_id,
            "case_id": None,
            "user_id": user_id,
            "mode": "free_chat",
            "title": "",
            "status": "active",
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
        await db.conversations.insert_one(conversation_doc)
        logger.info("Created free_chat conversation %s", conversation_id)

    return {
        "conversation_id": conversation_id,
        "case_id": case_id,
        "mode": mode,
    }


# ---------------------------------------------------------------------------
# Send message (non-streaming)
# ---------------------------------------------------------------------------

async def send_message(
    conversation_id: str,
    content: str,
    knowledge_base: KnowledgeBase,
    images: list[dict] | None = None,
) -> dict:
    """
    Send a new message in an existing conversation.

    Branches on investigation_state: step-based conversations use per-step
    system prompts, models, and filtered message history.
    """
    db = get_database()

    # 1. Retrieve conversation
    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    # 2. Build system prompt and API messages based on mode
    if conversation.get("investigation_state"):
        step = conversation["investigation_state"]["current_step"]
        is_multi_sr = conversation.get("case_mode") == "multi"
        sr_config = MULTI_USER_STEP_CONFIG if is_multi_sr else STEP_CONFIG
        system_prompt = knowledge_base.get_step_system_prompt(step, multi_user=is_multi_sr)
        model = sr_config[step]["model"]
        case = None
        if conversation.get("case_id"):
            if is_multi_sr:
                block_data = MULTI_USER_BLOCK_DATA.get(step)
                needs_case = block_data is not NO_INJECTION
            else:
                needs_case = step <= 4
            if needs_case:
                case = await db.cases.find_one({"_id": conversation["case_id"]})
        api_messages = _rebuild_step_api_messages(conversation, case)
    else:
        system_prompt = knowledge_base.get_system_prompt(mode=conversation.get("mode", "case"))
        model = None
        api_messages = _rebuild_api_messages(conversation["messages"])

    # 3. Build and append the new user message
    stored_images = []
    if images:
        stored_images = await _store_images(conversation_id, images)

    user_content = build_user_message_content(content, images)
    api_messages.append({"role": "user", "content": user_content})

    # 4. Call the AI
    ai_result = await get_ai_response(
        system_prompt=system_prompt,
        messages=api_messages,
        knowledge_base=knowledge_base,
        model=model,
    )

    # 5. Store messages
    now = _now()
    current_step = conversation.get("investigation_state", {}).get("current_step")

    user_message = {
        "message_id": _generate_id("msg"),
        "role": "user",
        "content": content,
        "images": stored_images,
        "timestamp": now,
        "visible": True,
    }
    if current_step:
        user_message["step"] = current_step

    tool_messages = []
    for tc_msg in ai_result.get("tool_call_messages", []):
        msg = {
            "message_id": _generate_id("msg"),
            "role": "tool_exchange",
            "content": tc_msg["content"],
            "original_role": tc_msg["role"],
            "timestamp": now,
            "visible": False,
        }
        if current_step:
            msg["step"] = current_step
        tool_messages.append(msg)

    assistant_message = {
        "message_id": _generate_id("msg"),
        "role": "assistant",
        "content": ai_result["content"],
        "tools_used": ai_result["tools_used"],
        "token_usage": ai_result["token_usage"],
        "timestamp": now,
        "visible": True,
    }
    if current_step:
        assistant_message["step"] = current_step

    all_new_messages = [user_message] + tool_messages + [assistant_message]
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$push": {"messages": {"$each": all_new_messages}},
            "$set": {"updated_at": now},
        }
    )

    logger.info(
        "Message sent in %s. Response: %d chars, tools: %s",
        conversation_id,
        len(ai_result["content"]),
        [t["document_id"] for t in ai_result["tools_used"]],
    )

    return {
        "message_id": assistant_message["message_id"],
        "role": "assistant",
        "content": ai_result["content"],
        "tools_used": ai_result["tools_used"],
        "token_usage": ai_result["token_usage"],
        "timestamp": now.isoformat(),
    }


# ---------------------------------------------------------------------------
# Send message (streaming)
# ---------------------------------------------------------------------------

async def send_message_streaming(
    conversation_id: str,
    content: str,
    knowledge_base: KnowledgeBase,
    images: list[dict] | None = None,
    is_initial_assessment: bool = False,
):
    """
    Send a message and stream the response.

    When is_initial_assessment=True, the system_injected message is already
    stored — just rebuild API messages from history and stream (no new user
    message appended).

    Branches on investigation_state: step-based conversations use per-step
    system prompts, models, and filtered message history with fresh case
    data injection.

    Yields the same event dicts as ai_client.get_ai_response_streaming().
    After the stream completes (the "done" event), the caller should call
    store_streamed_response() to persist everything to MongoDB.
    """
    db = get_database()

    # Retrieve conversation
    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    # Build system prompt and API messages based on mode
    has_step_state = bool(conversation.get("investigation_state"))
    conv_mode = conversation.get("mode", "case")
    tools_override = None  # None = use default TOOLS

    if has_step_state:
        step = conversation["investigation_state"]["current_step"]
        is_multi = conversation.get("case_mode") == "multi"
        config = MULTI_USER_STEP_CONFIG if is_multi else STEP_CONFIG
        system_prompt = knowledge_base.get_step_system_prompt(step, multi_user=is_multi)
        model = config[step]["model"]

        # Determine whether to load case data for injection
        case = None
        if conversation.get("case_id"):
            if is_multi:
                block_data = MULTI_USER_BLOCK_DATA.get(step)
                needs_case = block_data is not NO_INJECTION
            else:
                needs_case = step <= 4
            if needs_case:
                case = await db.cases.find_one({"_id": conversation["case_id"]})

        api_messages = _rebuild_step_api_messages(conversation, case)
    elif conv_mode == "oneshot":
        system_prompt = knowledge_base.get_system_prompt(mode="oneshot")
        if conversation.get("oneshot_executed"):
            model = settings.ONESHOT_MODEL
            tools_override = None  # standard tools for post-execution follow-up
        else:
            model = None
            tools_override = TOOLS_ONESHOT_SETUP
        api_messages = _rebuild_api_messages(conversation["messages"])

        # Detect "Continue Discussion" — user sending a message after the AI
        # signalled ready (first message) OR ongoing discussion mode (subsequent).
        in_discussion = conversation.get("oneshot_in_discussion", False)
        entering_discussion = (
            not is_initial_assessment
            and not in_discussion
            and conversation.get("oneshot_ready")
            and not conversation.get("oneshot_executed")
        )
        if entering_discussion:
            # First message after "Continue Discussion" — set persistent flag
            await db.conversations.update_one(
                {"_id": conversation_id},
                {"$set": {"oneshot_ready": False, "oneshot_in_discussion": True}},
            )
            in_discussion = True

        if in_discussion and not is_initial_assessment:
            # Inject discussion-mode instruction on EVERY discussion message
            # so the AI knows to converse, not produce ICR output.
            api_messages.append({
                "role": "user",
                "content": (
                    "[SYSTEM] The investigator has chosen to continue discussing before "
                    "execution. You are now in DISCUSSION MODE. Rules:\n\n"
                    "1. Respond conversationally to their message.\n"
                    "2. Do NOT produce any ICR text, case assessments, block-by-block "
                    "analysis, or investigation output — even if the user asks you to "
                    "proceed, go ahead, or start. You physically cannot execute from here; "
                    "execution is triggered by a separate UI button that only appears when "
                    "you signal readiness.\n"
                    "3. When the investigator indicates they are satisfied and want to "
                    'proceed (e.g. "go ahead", "ready", "let\'s do it", "I\'m done", '
                    '"that\'s all", "carry on", "come on then"), you MUST do BOTH:\n'
                    "   a) Call the signal_ready_to_execute tool\n"
                    "   b) Include the exact phrase [READY TO EXECUTE] in your response\n"
                    "This is the ONLY way to restore the Execute button for the investigator.\n"
                    "4. If you are unsure whether the user wants to continue discussing or "
                    "proceed, ask them directly rather than guessing."
                ),
            })
            api_messages.append({
                "role": "assistant",
                "content": "Understood. I'll respond to your questions conversationally and signal readiness again when appropriate.",
            })
    else:
        system_prompt = knowledge_base.get_system_prompt(mode=conv_mode)
        model = None
        api_messages = _rebuild_api_messages(conversation["messages"])

    if not is_initial_assessment:
        # Normal message
        if images:
            await _store_images(conversation_id, images)
        user_content = build_user_message_content(content, images)
        api_messages.append({"role": "user", "content": user_content})
    elif has_step_state:
        # Step-based initial assessment: case data is already injected by
        # _rebuild_step_api_messages (with ack). Add the instruction as
        # the last user message so the API payload ends with a user turn.
        api_messages.append({
            "role": "user",
            "content": INITIAL_ASSESSMENT_INSTRUCTION,
        })
    # else: non-step/oneshot initial assessment — system_injected already has instruction

    # Stream the AI response
    streaming_kwargs = {
        "system_prompt": system_prompt,
        "messages": api_messages,
        "knowledge_base": knowledge_base,
        "model": model,
    }
    if tools_override is not None:
        streaming_kwargs["tools"] = tools_override

    # Enable thinking for oneshot follow-up chat (post-execution)
    if conv_mode == "oneshot" and conversation.get("oneshot_executed"):
        streaming_kwargs["thinking"] = {
            "type": "enabled",
            "budget_tokens": settings.ONESHOT_FOLLOWUP_THINKING_BUDGET,
        }

    async for event in get_ai_response_streaming(**streaming_kwargs):
        yield event


async def store_streamed_response(
    conversation_id: str,
    user_content: str,
    user_images: list[dict] | None,
    ai_content: str,
    tools_used: list[dict],
    token_usage: dict,
    tool_call_messages: list[dict],
    is_initial_assessment: bool = False,
    step_complete_signalled: bool = False,
    oneshot_ready_signalled: bool = False,
    thinking_content: str = "",
) -> dict:
    """
    Store a streamed conversation turn in MongoDB.

    When is_initial_assessment=True on the step path, stores a hidden
    instruction message so that subsequent rebuilds maintain proper
    user/assistant alternation.

    Called by the router after the streaming generator is fully consumed.
    Returns the assistant message metadata.
    """
    db = get_database()
    now = _now()

    # Read conversation for step and mode info
    conv = await db.conversations.find_one(
        {"_id": conversation_id},
        {"investigation_state.current_step": 1, "mode": 1, "title": 1, "case_mode": 1},
    )
    current_step = conv.get("investigation_state", {}).get("current_step") if conv else None

    all_new_messages = []

    if is_initial_assessment and current_step:
        # Step-based initial assessment: store the instruction as a hidden
        # user message so _rebuild_step_api_messages can replay it
        # Use the correct instruction based on case mode
        if conv and conv.get("case_mode") == "multi":
            stored_instruction = MULTI_USER_INITIAL_ASSESSMENT
        else:
            stored_instruction = INITIAL_ASSESSMENT_INSTRUCTION
        instruction_msg = {
            "message_id": _generate_id("msg"),
            "role": "user",
            "content": stored_instruction,
            "step": current_step,
            "timestamp": now,
            "visible": False,
        }
        all_new_messages.append(instruction_msg)
    elif not is_initial_assessment:
        # Regular message — store user message
        stored_images = []
        if user_images:
            stored_images = await _store_images(conversation_id, user_images)

        user_message = {
            "message_id": _generate_id("msg"),
            "role": "user",
            "content": user_content,
            "images": stored_images,
            "timestamp": now,
            "visible": True,
        }
        if current_step:
            user_message["step"] = current_step
        all_new_messages.append(user_message)

    # Tool exchanges (hidden)
    for tc_msg in tool_call_messages:
        msg = {
            "message_id": _generate_id("msg"),
            "role": "tool_exchange",
            "content": tc_msg["content"],
            "original_role": tc_msg["role"],
            "timestamp": now,
            "visible": False,
        }
        if current_step:
            msg["step"] = current_step
        all_new_messages.append(msg)

    # Build full tools_used: injected step docs + AI-fetched references
    all_tools_used = list(tools_used)
    if current_step:
        step_doc_titles = {
            "icr-steps-setup": "ICR Steps: Setup & Context",
            "icr-steps-analysis": "ICR Steps: Analysis",
            "icr-steps-decision": "ICR Steps: Decision",
            "icr-steps-post": "ICR Steps: Post-Decision",
            "decision-matrix": "Decision Matrix",
            "mlro-escalation-matrix": "MLRO Escalation Matrix",
            "qc-quick-reference": "QC Quick Reference",
            "qc-full-checklist": "QC Submission Checklist",
            "icr-general-rules": "ICR General Rules",
        }
        # Always-included docs for this step (mode-aware)
        is_multi_tu = conv.get("case_mode") == "multi"
        tu_config = MULTI_USER_STEP_CONFIG if is_multi_tu else STEP_CONFIG
        sp_doc_id = "system-prompt-multi-user" if is_multi_tu else "system-prompt-case"
        injected = []
        injected.append({"tool": "system_injected", "document_id": sp_doc_id, "document_title": "System Prompt"})
        injected.append({"tool": "system_injected", "document_id": "icr-general-rules", "document_title": "ICR General Rules"})
        if is_multi_tu or current_step <= 4:
            injected.append({"tool": "system_injected", "document_id": "qc-quick-reference", "document_title": "QC Quick Reference"})
        # Step-specific docs
        for doc_id in tu_config.get(current_step, {}).get("docs", []):
            title = step_doc_titles.get(doc_id, doc_id)
            injected.append({"tool": "system_injected", "document_id": doc_id, "document_title": title})
        all_tools_used = injected + all_tools_used

    # Assistant message
    assistant_msg_id = _generate_id("msg")
    assistant_message = {
        "message_id": assistant_msg_id,
        "role": "assistant",
        "content": ai_content,
        "tools_used": all_tools_used,
        "token_usage": token_usage,
        "timestamp": now,
        "visible": True,
    }
    if thinking_content:
        assistant_message["thinking_content"] = thinking_content
    if current_step:
        assistant_message["step"] = current_step
    all_new_messages.append(assistant_message)

    set_fields = {"updated_at": now}
    if current_step and step_complete_signalled:
        set_fields["investigation_state.step_complete_signalled"] = True
    if oneshot_ready_signalled:
        set_fields["oneshot_ready"] = True
        set_fields["oneshot_in_discussion"] = False

    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$push": {"messages": {"$each": all_new_messages}},
            "$set": set_fields,
        }
    )

    # Auto-generate title for free_chat conversations on first user message
    if not is_initial_assessment and user_content and conv:
        if conv.get("mode") == "free_chat" and not conv.get("title"):
            title = _generate_title(user_content)
            await db.conversations.update_one(
                {"_id": conversation_id},
                {"$set": {"title": title}},
            )

    return {
        "message_id": assistant_msg_id,
        "timestamp": now.isoformat(),
    }


def _generate_title(content: str) -> str:
    """Generate a conversation title from the first user message (heuristic)."""
    text = content.strip()
    for sep in [". ", "? ", "! ", "\n"]:
        idx = text.find(sep)
        if 0 < idx < 60:
            return text[:idx + 1]
    if len(text) > 50:
        return text[:50].rstrip() + "..."
    return text


# ---------------------------------------------------------------------------
# Get conversation history
# ---------------------------------------------------------------------------

async def get_history(conversation_id: str) -> dict:
    """
    Return the visible conversation history for frontend display.

    Filters out hidden messages (case data injection, tool exchanges).
    Returns messages in chronological order.
    Includes investigation_state if present.
    """
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    visible_messages = []
    for msg in conversation.get("messages", []):
        if not msg.get("visible", True):
            continue

        entry = {
            "message_id": msg["message_id"],
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg["timestamp"].isoformat() if isinstance(msg["timestamp"], datetime) else msg["timestamp"],
        }

        # Include optional fields if present
        if msg.get("tools_used"):
            entry["tools_used"] = msg["tools_used"]
        if msg.get("images"):
            entry["images"] = msg["images"]
        if msg.get("step") is not None:
            entry["step"] = msg["step"]
        if msg.get("thinking_content"):
            entry["thinking_content"] = msg["thinking_content"]
        if msg.get("oneshot_partial"):
            entry["executionInterrupted"] = True

        visible_messages.append(entry)

    result = {
        "conversation_id": conversation_id,
        "case_id": conversation.get("case_id"),
        "mode": conversation.get("mode", "case"),
        "title": conversation.get("title", ""),
        "messages": visible_messages,
    }

    # Include investigation state if present
    state = conversation.get("investigation_state")
    if state:
        is_multi_hist = conversation.get("case_mode") == "multi"
        hist_phases = MULTI_USER_STEP_PHASES if is_multi_hist else STEP_PHASES
        result["investigation_state"] = {
            "current_step": state["current_step"],
            "total_steps": state.get("total_steps", 5),
            "step_labels": state.get("step_labels", {}),
            "phase": hist_phases.get(state["current_step"], "unknown"),
            "steps": state["steps"],
            "step_complete_signalled": state.get("step_complete_signalled", False),
            "case_mode": conversation.get("case_mode", "single"),
        }

    # Include oneshot state if present
    if conversation.get("mode") == "oneshot":
        result["oneshot_state"] = {
            "ready": conversation.get("oneshot_ready", False),
            "executed": conversation.get("oneshot_executed", False),
            "has_partial": bool(conversation.get("oneshot_partial_msg_id")),
        }

    return result


# ---------------------------------------------------------------------------
# List & delete conversations
# ---------------------------------------------------------------------------

async def list_conversations(
    user_id: str,
    mode: str | None = None,
) -> list[dict]:
    """
    List conversations for a user, optionally filtered by mode.
    Returns summaries sorted by updated_at descending.
    """
    db = get_database()

    query = {"user_id": user_id}
    if mode:
        query["mode"] = mode

    cursor = db.conversations.find(
        query,
        {"_id": 1, "case_id": 1, "mode": 1, "title": 1, "updated_at": 1, "messages": 1},
    ).sort("updated_at", -1)

    results = []
    async for doc in cursor:
        # Count only visible messages
        visible_count = sum(
            1 for m in doc.get("messages", []) if m.get("visible", True)
        )
        results.append({
            "conversation_id": doc["_id"],
            "title": doc.get("title", ""),
            "mode": doc.get("mode", "case"),
            "case_id": doc.get("case_id"),
            "updated_at": doc["updated_at"].isoformat() if isinstance(doc["updated_at"], datetime) else doc["updated_at"],
            "message_count": visible_count,
        })

    return results


async def delete_conversation(
    conversation_id: str,
    user_id: str,
) -> None:
    """Delete a conversation, verifying ownership."""
    db = get_database()

    result = await db.conversations.delete_one({
        "_id": conversation_id,
        "user_id": user_id,
    })

    if result.deleted_count == 0:
        raise ValueError(f"Conversation not found or not owned by user: {conversation_id}")

    logger.info("Deleted conversation %s for user %s", conversation_id, user_id)


async def reset_case_conversation(
    conversation_id: str,
    user_id: str,
) -> dict:
    """
    Reset a case investigation by deleting the conversation and clearing
    the case's conversation_id. The case returns to its pre-investigation state.
    """
    db = get_database()

    conversation = await db.conversations.find_one(
        {"_id": conversation_id, "user_id": user_id},
        {"case_id": 1},
    )
    if conversation is None:
        raise ValueError(f"Conversation not found or not owned by user: {conversation_id}")

    case_id = conversation.get("case_id")

    # Delete the conversation
    await db.conversations.delete_one({"_id": conversation_id})

    # Clear the case's conversation_id so it can be re-opened fresh
    if case_id:
        await db.cases.update_one(
            {"_id": case_id},
            {"$unset": {"conversation_id": ""}, "$set": {"status": "open"}},
        )

    logger.info(
        "Reset case conversation %s (case %s) for user %s",
        conversation_id, case_id, user_id,
    )

    return {"status": "reset", "case_id": case_id}


# ---------------------------------------------------------------------------
# One-shot execution
# ---------------------------------------------------------------------------

async def oneshot_execute(
    conversation_id: str,
    knowledge_base: KnowledgeBase,
):
    """
    Execute the full ICR in one-shot mode.

    Builds the execution system prompt with ALL step docs, includes
    the setup transcript as context, and streams a single massive
    AI response.

    Uses configurable model (Opus), thinking, and max_tokens from settings.

    Yields SSE-compatible event dicts:
        {"type": "content_delta", "text": "..."}
        {"type": "tool_use", ...}
        {"type": "done", "content": "...", "tools_used": [...], "token_usage": {...},
         "tool_call_messages": [...]}
    """
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    if conversation.get("mode") != "oneshot":
        raise ValueError("One-shot execution requires a oneshot conversation")

    if conversation.get("oneshot_executed"):
        raise ValueError("One-shot execution has already been performed")

    # Build the execution system prompt (all step docs + rules)
    system_prompt = knowledge_base.get_oneshot_execution_prompt()

    execution_instruction = (
        "Execute the full ICR now. Work through all four blocks in order "
        "(Setup, Analysis, Decision, Post-Decision). Produce copy-paste-ready "
        "ICR text for every section. Validate against QC checks after each block. "
        "End with a QC summary."
    )

    # Check for continuation mode (partial exists from a prior failed attempt)
    partial_msg_id = conversation.get("oneshot_partial_msg_id")

    if partial_msg_id:
        # Continuation mode: filter out trigger + partial from stored messages,
        # then append the full execution instruction + partial as assistant + continue prompt
        partial_msg = None
        filtered_messages = []
        for msg in conversation.get("messages", []):
            if msg["message_id"] == partial_msg_id:
                partial_msg = msg
                continue
            # Also skip the trigger "Execute Full ICR" user message that precedes the partial
            if msg.get("role") == "user" and msg.get("content") == "Execute Full ICR" and msg.get("visible", True):
                # Only skip the last one (the trigger for this execution)
                # Check if this is the trigger immediately before the partial
                continue
            filtered_messages.append(msg)

        api_messages = _rebuild_api_messages(filtered_messages)
        api_messages.append({"role": "user", "content": execution_instruction})

        if partial_msg and partial_msg.get("content"):
            api_messages.append({"role": "assistant", "content": partial_msg["content"]})
            api_messages.append({
                "role": "user",
                "content": (
                    "Your previous response was interrupted by a connection failure. "
                    "Continue exactly where you left off. Do not repeat any content "
                    "already produced. Pick up mid-sentence if needed."
                ),
            })

        logger.info(
            "One-shot continuation for %s from partial %s (%d chars)",
            conversation_id, partial_msg_id,
            len(partial_msg["content"]) if partial_msg else 0,
        )
    else:
        # First execution — standard flow
        api_messages = _rebuild_api_messages(conversation["messages"])
        api_messages.append({"role": "user", "content": execution_instruction})

    # Configure model and thinking
    model = settings.ONESHOT_MODEL
    max_tokens = settings.ONESHOT_MAX_TOKENS
    thinking = None
    if settings.ONESHOT_THINKING_ENABLED:
        thinking = {
            "type": "enabled",
            "budget_tokens": settings.ONESHOT_THINKING_BUDGET,
        }

    async for event in get_ai_response_streaming(
        system_prompt=system_prompt,
        messages=api_messages,
        knowledge_base=knowledge_base,
        model=model,
        tools=TOOLS_ONESHOT_EXECUTE,
        max_tokens=max_tokens,
        thinking=thinking,
    ):
        yield event


def _oneshot_injected_docs() -> list[dict]:
    """Return the list of system-injected execution documents for oneshot tools_used."""
    return [
        {"tool": "system_injected", "document_id": "system-prompt-oneshot-execution", "document_title": "One-Shot Execution Prompt"},
        {"tool": "system_injected", "document_id": "icr-general-rules", "document_title": "ICR General Rules"},
        {"tool": "system_injected", "document_id": "qc-quick-reference", "document_title": "QC Quick Reference"},
        {"tool": "system_injected", "document_id": "icr-steps-setup", "document_title": "ICR Steps: Setup"},
        {"tool": "system_injected", "document_id": "icr-steps-analysis", "document_title": "ICR Steps: Analysis"},
        {"tool": "system_injected", "document_id": "icr-steps-decision", "document_title": "ICR Steps: Decision"},
        {"tool": "system_injected", "document_id": "icr-steps-post", "document_title": "ICR Steps: Post-Decision"},
        {"tool": "system_injected", "document_id": "decision-matrix", "document_title": "Decision Matrix"},
        {"tool": "system_injected", "document_id": "mlro-escalation-matrix", "document_title": "MLRO Escalation Matrix"},
        {"tool": "system_injected", "document_id": "qc-full-checklist", "document_title": "QC Submission Checklist"},
    ]


async def store_oneshot_partial(
    conversation_id: str,
    partial_content: str,
    tools_used: list[dict],
    thinking_content: str = "",
) -> dict:
    """
    Save partial oneshot output after a stream failure.

    On first call: creates the trigger user message + partial assistant message.
    On subsequent calls: updates the existing partial message in-place.
    """
    db = get_database()
    now = _now()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")
    if conversation.get("mode") != "oneshot":
        raise ValueError("store_oneshot_partial requires a oneshot conversation")
    if conversation.get("oneshot_executed"):
        raise ValueError("One-shot execution already completed")

    all_tools_used = _oneshot_injected_docs() + list(tools_used)
    existing_partial_id = conversation.get("oneshot_partial_msg_id")

    if existing_partial_id:
        # Subsequent save — update existing partial in-place
        update_fields = {
            "messages.$.content": partial_content,
            "messages.$.tools_used": all_tools_used,
            "messages.$.thinking_content": thinking_content,
            "updated_at": now,
        }
        await db.conversations.update_one(
            {"_id": conversation_id, "messages.message_id": existing_partial_id},
            {"$set": update_fields},
        )
        logger.info(
            "One-shot partial updated for %s (msg %s). Content: %d chars",
            conversation_id, existing_partial_id, len(partial_content),
        )
        return {"message_id": existing_partial_id, "status": "partial_saved"}
    else:
        # First save — create trigger + partial messages
        trigger_msg_id = _generate_id("msg")
        partial_msg_id = _generate_id("msg")

        trigger_msg = {
            "message_id": trigger_msg_id,
            "role": "user",
            "content": "Execute Full ICR",
            "timestamp": now,
            "visible": True,
        }

        partial_msg = {
            "message_id": partial_msg_id,
            "role": "assistant",
            "content": partial_content,
            "tools_used": all_tools_used,
            "token_usage": {},
            "timestamp": now,
            "visible": True,
            "oneshot_partial": True,
            "oneshot_execution": True,
        }
        if thinking_content:
            partial_msg["thinking_content"] = thinking_content

        await db.conversations.update_one(
            {"_id": conversation_id},
            {
                "$push": {"messages": {"$each": [trigger_msg, partial_msg]}},
                "$set": {
                    "oneshot_partial_msg_id": partial_msg_id,
                    "updated_at": now,
                },
            },
        )
        logger.info(
            "One-shot partial saved for %s (msg %s). Content: %d chars",
            conversation_id, partial_msg_id, len(partial_content),
        )
        return {"message_id": partial_msg_id, "status": "partial_saved"}


async def store_oneshot_execution(
    conversation_id: str,
    user_id: str,
    ai_content: str,
    tools_used: list[dict],
    token_usage: dict,
    tool_call_messages: list[dict],
    thinking_content: str = "",
) -> dict:
    """Store the one-shot execution result and mark the conversation as executed."""
    db = get_database()
    now = _now()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    existing_partial_msg_id = conversation.get("oneshot_partial_msg_id") if conversation else None
    all_tools_used = _oneshot_injected_docs() + list(tools_used)

    if existing_partial_msg_id:
        # Merge mode: continuation completed successfully
        # Find the partial message to merge content
        partial_msg = None
        for msg in conversation.get("messages", []):
            if msg["message_id"] == existing_partial_msg_id:
                partial_msg = msg
                break

        merged_content = (partial_msg["content"] if partial_msg else "") + ai_content

        # Merge thinking
        prior_thinking = partial_msg.get("thinking_content", "") if partial_msg else ""
        if prior_thinking and thinking_content:
            merged_thinking = prior_thinking + "\n---\n" + thinking_content
        elif thinking_content:
            merged_thinking = thinking_content
        else:
            merged_thinking = prior_thinking

        # Update the partial message in-place → final message
        update_fields = {
            "messages.$.content": merged_content,
            "messages.$.tools_used": all_tools_used,
            "messages.$.token_usage": token_usage,
            "messages.$.oneshot_partial": False,
            "messages.$.oneshot_execution": True,
        }
        if merged_thinking:
            update_fields["messages.$.thinking_content"] = merged_thinking

        await db.conversations.update_one(
            {"_id": conversation_id, "messages.message_id": existing_partial_msg_id},
            {"$set": update_fields},
        )

        # Push any tool_exchange messages from continuation
        tool_exchange_msgs = []
        for tc_msg in tool_call_messages:
            tool_exchange_msgs.append({
                "message_id": _generate_id("msg"),
                "role": "tool_exchange",
                "content": tc_msg["content"],
                "original_role": tc_msg["role"],
                "timestamp": now,
                "visible": False,
            })

        update_ops = {
            "$set": {
                "oneshot_executed": True,
                "updated_at": now,
            },
            "$unset": {"oneshot_partial_msg_id": ""},
        }
        if tool_exchange_msgs:
            update_ops["$push"] = {"messages": {"$each": tool_exchange_msgs}}

        await db.conversations.update_one({"_id": conversation_id}, update_ops)

        logger.info(
            "One-shot execution merged for %s (msg %s). Total: %d chars",
            conversation_id, existing_partial_msg_id, len(merged_content),
        )

        return {
            "message_id": existing_partial_msg_id,
            "timestamp": now.isoformat(),
        }
    else:
        # First success — no prior partial
        all_new_messages = []

        trigger_msg = {
            "message_id": _generate_id("msg"),
            "role": "user",
            "content": "Execute Full ICR",
            "timestamp": now,
            "visible": True,
        }
        all_new_messages.append(trigger_msg)

        for tc_msg in tool_call_messages:
            msg = {
                "message_id": _generate_id("msg"),
                "role": "tool_exchange",
                "content": tc_msg["content"],
                "original_role": tc_msg["role"],
                "timestamp": now,
                "visible": False,
            }
            all_new_messages.append(msg)

        assistant_msg_id = _generate_id("msg")
        assistant_message = {
            "message_id": assistant_msg_id,
            "role": "assistant",
            "content": ai_content,
            "tools_used": all_tools_used,
            "token_usage": token_usage,
            "timestamp": now,
            "visible": True,
            "oneshot_execution": True,
        }
        if thinking_content:
            assistant_message["thinking_content"] = thinking_content
        all_new_messages.append(assistant_message)

        await db.conversations.update_one(
            {"_id": conversation_id},
            {
                "$push": {"messages": {"$each": all_new_messages}},
                "$set": {
                    "oneshot_executed": True,
                    "updated_at": now,
                },
            }
        )

        logger.info(
            "One-shot execution stored for %s. Output: %d chars, tools: %s",
            conversation_id,
            len(ai_content),
            [t.get("document_id") for t in tools_used],
        )

        return {
            "message_id": assistant_msg_id,
            "timestamp": now.isoformat(),
        }


# ---------------------------------------------------------------------------
# API message reconstruction
# ---------------------------------------------------------------------------

def _rebuild_api_messages(stored_messages: list[dict]) -> list[dict]:
    """
    Rebuild the Anthropic API messages array from stored conversation history.

    Used for free_chat mode and legacy case conversations without
    investigation_state. Includes ALL messages regardless of step.

    Mapping from stored roles to API roles:
        system_injected  → role: "user" (the initial case data injection)
        user             → role: "user"
        assistant        → role: "assistant"
        tool_exchange    → role depends on original_role field
    """
    api_messages = []

    for msg in stored_messages:
        role = msg["role"]

        if role == "system_injected":
            # Case data injection — sent as a user message
            api_messages.append({
                "role": "user",
                "content": msg["content"],
            })

        elif role == "user":
            # Regular user message — reconstruct with images if present
            if msg.get("images"):
                # Reload images from disk and build proper content blocks
                content_blocks = []
                for img_ref in msg["images"]:
                    try:
                        img_bytes = Path(img_ref["stored_path"]).read_bytes()
                        img_b64 = base64.b64encode(img_bytes).decode("ascii")
                        content_blocks.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": img_ref["media_type"],
                                "data": img_b64,
                            }
                        })
                    except Exception as e:
                        logger.warning("Could not reload image %s: %s", img_ref.get("stored_path"), e)
                content_blocks.append({"type": "text", "text": msg["content"] or "Describe this image."})
                api_messages.append({
                    "role": "user",
                    "content": content_blocks,
                })
            else:
                api_messages.append({
                    "role": "user",
                    "content": msg["content"],
                })

        elif role == "assistant":
            # Assistant response — just the text content
            api_messages.append({
                "role": "assistant",
                "content": msg["content"],
            })

        elif role == "tool_exchange":
            # Tool call intermediate messages — need to be included
            # exactly as sent/received to keep the API happy
            original_role = msg.get("original_role", "user")
            api_messages.append({
                "role": original_role,
                "content": msg["content"],
            })

    return api_messages


def _rebuild_step_api_messages(
    conversation: dict,
    case: dict | None,
) -> list[dict]:
    """
    Build API messages for the current investigation step.

    Unlike _rebuild_api_messages (which includes all messages), this:
    1. Injects completed step summaries as a synthetic user/assistant pair
    2. Injects fresh case data from the case document (steps 1-4 only)
    3. Filters stored messages to current step only
    4. Excludes system_injected (case data is injected fresh above)
    5. Excludes step_divider (never sent to API)
    """
    state = conversation["investigation_state"]
    current_step = state["current_step"]
    api_messages = []

    # 1. Inject summaries from completed steps
    completed_summaries = [
        s["summary"] for s in state["steps"]
        if s["status"] == "completed" and s.get("summary")
    ]
    if completed_summaries:
        summary_text = "\n\n---\n\n".join(completed_summaries)
        api_messages.append({
            "role": "user",
            "content": f"[PREVIOUS STEP SUMMARIES]\n\n{summary_text}",
        })
        api_messages.append({
            "role": "assistant",
            "content": "Understood. I have the context from previous steps.",
        })

    # 2. Inject fresh case data — mode-aware
    is_multi = conversation.get("case_mode") == "multi"

    if is_multi and case:
        block_data_keys = MULTI_USER_BLOCK_DATA.get(current_step)
        if block_data_keys is ALL_SECTIONS:
            case_data_md = _build_case_data_markdown(case, sections=None)
        elif block_data_keys is NO_INJECTION:
            case_data_md = None
        else:
            case_data_md = _build_case_data_markdown(case, sections=block_data_keys)

        if case_data_md:
            api_messages.append({
                "role": "user",
                "content": f"[CASE DATA]\n\n{case_data_md}",
            })
            api_messages.append({
                "role": "assistant",
                "content": "Case data received. Ready to proceed with this step.",
            })
    elif not is_multi and current_step <= 4 and case:
        case_data_md = _build_case_data_markdown(case)
        api_messages.append({
            "role": "user",
            "content": f"[CASE DATA]\n\n{case_data_md}",
        })
        api_messages.append({
            "role": "assistant",
            "content": "Case data received. Ready to proceed with this step.",
        })

    # 3. Filter messages to current step, excluding system_injected and step_divider
    for msg in conversation.get("messages", []):
        if msg.get("step") != current_step:
            continue

        role = msg["role"]

        if role in ("system_injected", "step_divider"):
            continue

        if role == "user":
            if msg.get("images"):
                content_blocks = []
                for img_ref in msg["images"]:
                    try:
                        img_bytes = Path(img_ref["stored_path"]).read_bytes()
                        img_b64 = base64.b64encode(img_bytes).decode("ascii")
                        content_blocks.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": img_ref["media_type"],
                                "data": img_b64,
                            }
                        })
                    except Exception as e:
                        logger.warning("Could not reload image %s: %s", img_ref.get("stored_path"), e)
                content_blocks.append({"type": "text", "text": msg["content"] or "Describe this image."})
                api_messages.append({"role": "user", "content": content_blocks})
            else:
                api_messages.append({"role": "user", "content": msg["content"]})

        elif role == "assistant":
            api_messages.append({"role": "assistant", "content": msg["content"]})

        elif role == "tool_exchange":
            original_role = msg.get("original_role", "user")
            api_messages.append({"role": original_role, "content": msg["content"]})

    return api_messages


# ---------------------------------------------------------------------------
# Case data assembly
# ---------------------------------------------------------------------------

_CASE_DATA_SECTION_MAP = {
    # C360 sub-processors
    "tx_summary": "Transaction Summary",
    "user_profile": "User Profile",
    "privacy_coin": "Privacy Coin Breakdown",
    "counterparty": "Counterparty Analysis",
    "device_ip": "Device & IP Analysis",
    "failed_fiat": "Failed Fiat Withdrawals",
    "ctm_alerts": "CTM Alerts",
    "ftm_alerts": "FTM Alerts",
    "account_blocks": "Account Blocks",
    "address_xref": "Address Cross-Reference",
    "uid_search": "UID Search Results",
    # Standalone sections
    "elliptic_addresses": "Elliptic Screening Addresses",
    "elliptic": "Elliptic Wallet Screening",
    "l1_referral": "L1 Referral Narrative",
    "haoDesk": "HaoDesk Case Data",
    "kyc": "KYC Document Summary",
    "prior_icr": "Prior ICR Summary",
    "rfi": "RFI Summary",
    "kodex": "Law Enforcement / Kodex",
    "l1_victim": "L1 Victim Communications",
    "l1_suspect": "L1 Suspect Communications",
    "investigator_notes": "Investigator Notes & OSINT",
}


def _render_preprocessed_sections(
    preprocessed: dict,
    sections_filter: list[str] | None = None,
) -> list[str]:
    """Render preprocessed_data fields as markdown parts.

    If sections_filter is provided, only include fields in that list.
    """
    parts = []
    for field, header in _CASE_DATA_SECTION_MAP.items():
        if sections_filter and field not in sections_filter:
            continue
        content = preprocessed.get(field)
        if content:
            parts.append(f"## {header}")
            parts.append("")
            if field == "prior_icr":
                total_count = preprocessed.get("prior_icr_count")
                if total_count:
                    parts.append(
                        f"*Note: {total_count} prior ICRs exist for this subject. "
                        f"The most recent are summarised below.*"
                    )
                    parts.append("")
            elif field == "rfi":
                total_count = preprocessed.get("rfi_count")
                if total_count:
                    parts.append(
                        f"*Note: {total_count} RFIs exist for this subject. "
                        f"The most recent are summarised below.*"
                    )
                    parts.append("")
            parts.append(content)
            parts.append("")
            parts.append("---")
            parts.append("")
    return parts


def _build_case_data_markdown(
    case: dict,
    sections: list[str] | None = None,
) -> str:
    """
    Build a markdown document from a case's preprocessed_data fields.

    For single-user: concatenates top-level preprocessed_data with headers.
    For multi-user: iterates over subjects, rendering per-subject data.

    Args:
        case: The case document (from cases collection).
        sections: Optional list of section keys to include. None = all sections.
    """
    subjects = case.get("subjects", [])

    if subjects:
        # ── Multi-user ──
        parts = [
            f"# Multi-User Case — Case ID {case.get('_id', 'Unknown')}",
            f"**Case Type:** {case.get('case_type', 'Unknown')}",
            f"**Total Subjects:** {len(subjects)}",
            f"**Subject UIDs:** {', '.join(s.get('user_id', 'Unknown') for s in subjects)}",
            "",
            "---",
            "",
        ]
        for i, subject in enumerate(subjects):
            preprocessed = subject.get("preprocessed_data", {})
            parts.append(f"# SUBJECT {i+1} — UID {subject.get('user_id', 'Unknown')}")
            parts.append("")
            subject_parts = _render_preprocessed_sections(preprocessed, sections)
            if subject_parts:
                parts.extend(subject_parts)
            else:
                parts.append("(No data available for this subject.)")
                parts.append("")
        return "\n".join(parts)

    # ── Single-user (unchanged behavior) ──
    preprocessed = case.get("preprocessed_data", {})
    if not preprocessed:
        return "(No preprocessed data available for this case.)"

    parts = [
        f"**Case ID:** {case.get('_id', 'Unknown')}",
        f"**Case Type:** {case.get('case_type', 'Unknown')}",
        f"**Subject User:** {case.get('subject_user_id', 'Unknown')}",
        f"**Summary:** {case.get('summary', 'No summary available')}",
        "",
        "---",
        "",
    ]
    parts.extend(_render_preprocessed_sections(preprocessed, sections))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Image storage
# ---------------------------------------------------------------------------

async def _store_images(
    conversation_id: str,
    images: list[dict],
) -> list[dict]:
    """
    Store uploaded images to disk and return reference metadata.

    Images are saved to: {IMAGES_DIR}/{conversation_id}/{image_id}.{ext}
    """
    image_dir = Path(settings.IMAGES_DIR) / conversation_id
    image_dir.mkdir(parents=True, exist_ok=True)

    stored = []
    for img in images:
        image_id = _generate_id("img")
        media_type = img["media_type"]

        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/webp": "webp",
        }
        ext = ext_map.get(media_type, "bin")

        filename = f"{image_id}.{ext}"
        filepath = image_dir / filename

        try:
            image_bytes = base64.b64decode(img["base64"])
            filepath.write_bytes(image_bytes)
            logger.info("Stored image: %s (%d bytes)", filepath, len(image_bytes))
        except Exception as e:
            logger.error("Failed to store image %s: %s", image_id, e)
            continue

        stored.append({
            "image_id": image_id,
            "media_type": media_type,
            "stored_path": str(filepath),
        })

    return stored


# ---------------------------------------------------------------------------
# Step summary generation
# ---------------------------------------------------------------------------

async def _generate_step_summary(
    conversation: dict,
    step: int,
    knowledge_base: KnowledgeBase,
) -> dict:
    """
    Generate a structured summary of a completed investigation step.

    Makes a separate non-streaming API call with the summary system prompt
    and all messages from the step as context.

    Returns:
        dict with summary (str), model (str), token_usage (dict).
    """
    # Extract step messages and rebuild as API-format messages.
    # Retry once after a short delay if no messages found — handles the
    # race condition where advance-step is called before the streaming
    # response has been fully persisted to MongoDB.
    step_api_messages = []
    for attempt in range(2):
        step_api_messages = []
        for msg in conversation.get("messages", []):
            if msg.get("step") != step:
                continue
            role = msg["role"]
            if role == "step_divider":
                continue
            if role == "system_injected":
                step_api_messages.append({"role": "user", "content": msg["content"]})
            elif role == "user":
                step_api_messages.append({"role": "user", "content": msg["content"]})
            elif role == "assistant":
                step_api_messages.append({"role": "assistant", "content": msg["content"]})
            elif role == "tool_exchange":
                step_api_messages.append({
                    "role": msg.get("original_role", "user"),
                    "content": msg["content"],
                })

        if step_api_messages:
            break

        if attempt == 0:
            logger.warning(
                "No messages found for step %d on first read — "
                "retrying after 1s (possible write race)",
                step,
            )
            await asyncio.sleep(1)
            db = get_database()
            conversation = await db.conversations.find_one(
                {"_id": conversation["_id"]}
            )

    if not step_api_messages:
        raise ValueError(f"No messages found for step {step}")

    # Mode-aware config
    is_multi = conversation.get("case_mode") == "multi"
    step_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES
    config = MULTI_USER_STEP_CONFIG if is_multi else STEP_CONFIG

    # Ensure the messages end with a user message (API requirement)
    if step_api_messages[-1]["role"] != "user":
        block_label = "Block" if is_multi else "Step"
        step_api_messages.append({
            "role": "user",
            "content": (
                f"Generate a structured summary of {block_label} {step} "
                f"({step_phases[step].replace('_', ' ').title()}) "
                "using the template provided in your instructions."
            ),
        })

    # Build summary system prompt with step info
    phase_name = step_phases[step].replace("_", " ").title()
    system_prompt = SUMMARY_SYSTEM_PROMPT.format(
        step_number=step,
        phase_name=phase_name,
    )
    if is_multi:
        system_prompt += MULTI_USER_SUMMARY_ADDENDUM

    summary_model = config["summary"]["model"]

    result = await get_ai_response(
        system_prompt=system_prompt,
        messages=step_api_messages,
        knowledge_base=knowledge_base,
        model=summary_model,
    )

    return {
        "summary": result["content"],
        "model": summary_model,
        "token_usage": result["token_usage"],
    }


# ---------------------------------------------------------------------------
# Step transitions
# ---------------------------------------------------------------------------

async def approve_and_continue(
    conversation_id: str,
    user_id: str,
    knowledge_base: KnowledgeBase,
) -> dict:
    """
    Complete the current step and advance to the next one.

    1. Generate a structured summary of the current step
    2. Mark the step as completed with summary
    3. Create the next step entry
    4. Insert a step_divider message
    5. Return the new step info and summary

    Valid for steps 1→2, 2→3, 3→4. Use qc_check() for 4→5.
    """
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    state = conversation.get("investigation_state")
    if not state:
        raise ValueError("Conversation has no investigation state")

    current_step = state["current_step"]
    is_multi = conversation.get("case_mode") == "multi"
    max_approve_step = 8 if is_multi else 3
    if current_step > max_approve_step:
        raise ValueError(
            f"Cannot advance from step {current_step}. "
            "Use QC check for the final transition."
        )

    step_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES
    step_labels = state.get("step_labels", {})

    # Generate summary
    summary_result = await _generate_step_summary(
        conversation, current_step, knowledge_base
    )

    now = _now()
    next_step = current_step + 1
    next_phase = step_phases[next_step]
    next_label = step_labels.get(str(next_step), next_phase.replace("_", " ").title())

    # Build updated steps array
    steps = [dict(s) for s in state["steps"]]
    steps[current_step - 1].update({
        "status": "completed",
        "summary": summary_result["summary"],
        "summary_model": summary_result["model"],
        "summary_token_usage": summary_result["token_usage"],
        "completed_at": now,
        "approved_by": user_id,
    })
    steps.append({
        "step_number": next_step,
        "phase": next_phase,
        "label": next_label,
        "status": "active",
        "summary": None,
        "summary_model": None,
        "summary_token_usage": None,
        "completed_at": None,
        "approved_by": None,
    })

    # Step divider message
    block_label = "Block" if is_multi else "Step"
    divider_msg = {
        "message_id": _generate_id("msg"),
        "role": "step_divider",
        "content": (
            f"{block_label} {current_step} ({step_phases[current_step].replace('_', ' ').title()}) "
            f"complete. Moving to {block_label} {next_step}: {next_label}."
        ),
        "step": current_step,
        "timestamp": now,
        "visible": True,
    }

    # Update conversation
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$set": {
                "investigation_state.steps": steps,
                "investigation_state.current_step": next_step,
                "investigation_state.step_complete_signalled": False,
                "updated_at": now,
            },
            "$push": {"messages": divider_msg},
        }
    )

    logger.info(
        "Advanced conversation %s from step %d to step %d. Summary: %d chars",
        conversation_id, current_step, next_step, len(summary_result["summary"]),
    )

    return {
        "step": next_step,
        "phase": next_phase,
        "summary": summary_result["summary"],
    }


async def qc_check(
    conversation_id: str,
    user_id: str,
    knowledge_base: KnowledgeBase,
) -> dict:
    """
    Transition from step 4 (Post-Decision) to step 5 (QC Check).

    Generates a summary for step 4, advances state to step 5.
    Does NOT store the pasted case text — the frontend sends it
    as a regular message via the messages endpoint afterward.
    """
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    state = conversation.get("investigation_state")
    if not state:
        raise ValueError("Conversation has no investigation state")

    current_step = state["current_step"]
    is_multi = conversation.get("case_mode") == "multi"
    expected_step = 8 if is_multi else 4
    qc_step = 9 if is_multi else 5

    if current_step != expected_step:
        raise ValueError(
            f"QC check can only be initiated from step {expected_step}, "
            f"currently on step {current_step}"
        )

    # Generate summary for the pre-QC step
    summary_result = await _generate_step_summary(
        conversation, current_step, knowledge_base
    )

    now = _now()
    step_labels = state.get("step_labels", {})
    qc_label = step_labels.get(str(qc_step), "QC Check")

    # Build updated steps array
    steps = [dict(s) for s in state["steps"]]
    steps[current_step - 1].update({
        "status": "completed",
        "summary": summary_result["summary"],
        "summary_model": summary_result["model"],
        "summary_token_usage": summary_result["token_usage"],
        "completed_at": now,
        "approved_by": user_id,
    })
    steps.append({
        "step_number": qc_step,
        "phase": "qc_check",
        "label": qc_label,
        "status": "active",
        "summary": None,
        "summary_model": None,
        "summary_token_usage": None,
        "completed_at": None,
        "approved_by": None,
    })

    # Step divider message
    block_label = "Block" if is_multi else "Step"
    prev_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES
    divider_msg = {
        "message_id": _generate_id("msg"),
        "role": "step_divider",
        "content": (
            f"{block_label} {current_step} "
            f"({prev_phases[current_step].replace('_', ' ').title()}) "
            f"complete. Moving to {block_label} {qc_step}: {qc_label}."
        ),
        "step": current_step,
        "timestamp": now,
        "visible": True,
    }

    # Update conversation
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$set": {
                "investigation_state.steps": steps,
                "investigation_state.current_step": qc_step,
                "investigation_state.step_complete_signalled": False,
                "updated_at": now,
            },
            "$push": {"messages": divider_msg},
        }
    )

    logger.info(
        "QC check initiated for conversation %s. Step %d summary: %d chars",
        conversation_id, current_step, len(summary_result["summary"]),
    )

    return {
        "step": qc_step,
        "phase": "qc_check",
    }


async def lightweight_step_advance(
    conversation_id: str,
    user_id: str,
) -> dict:
    """
    Advance to the next step without generating a summary.

    Used by auto-execute mode when skip_summaries=True.
    Same as approve_and_continue but skips the AI summary call.
    """
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    state = conversation.get("investigation_state")
    if not state:
        raise ValueError("Conversation has no investigation state")

    current_step = state["current_step"]
    is_multi = conversation.get("case_mode") == "multi"
    max_step = 8 if is_multi else 3
    if current_step > max_step:
        raise ValueError(f"Cannot advance from step {current_step}")

    step_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES
    step_labels = state.get("step_labels", {})

    now = _now()
    next_step = current_step + 1
    next_phase = step_phases[next_step]
    next_label = step_labels.get(str(next_step), next_phase.replace("_", " ").title())

    steps = [dict(s) for s in state["steps"]]
    steps[current_step - 1].update({
        "status": "completed",
        "summary": None,
        "summary_model": None,
        "summary_token_usage": None,
        "completed_at": now,
        "approved_by": user_id,
    })
    steps.append({
        "step_number": next_step,
        "phase": next_phase,
        "label": next_label,
        "status": "active",
        "summary": None,
        "summary_model": None,
        "summary_token_usage": None,
        "completed_at": None,
        "approved_by": None,
    })

    block_label = "Block" if is_multi else "Step"
    divider_msg = {
        "message_id": _generate_id("msg"),
        "role": "step_divider",
        "content": (
            f"{block_label} {current_step} ({step_phases[current_step].replace('_', ' ').title()}) "
            f"complete. Moving to {block_label} {next_step}: {next_label}."
        ),
        "step": current_step,
        "timestamp": now,
        "visible": True,
    }

    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$set": {
                "investigation_state.steps": steps,
                "investigation_state.current_step": next_step,
                "investigation_state.step_complete_signalled": False,
                "updated_at": now,
            },
            "$push": {"messages": divider_msg},
        }
    )

    logger.info(
        "Lightweight advance: conversation %s from step %d to step %d (no summary)",
        conversation_id, current_step, next_step,
    )

    return {
        "step": next_step,
        "phase": next_phase,
    }


# ---------------------------------------------------------------------------
# Investigation state
# ---------------------------------------------------------------------------

async def get_investigation_state(conversation_id: str) -> dict:
    """Return the current investigation state for a conversation."""
    db = get_database()

    conversation = await db.conversations.find_one(
        {"_id": conversation_id},
        {"investigation_state": 1, "case_mode": 1},
    )
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    state = conversation.get("investigation_state")
    if not state:
        raise ValueError("Conversation has no investigation state")

    is_multi = conversation.get("case_mode") == "multi"
    step_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES

    return {
        "current_step": state["current_step"],
        "total_steps": state.get("total_steps", 5),
        "step_labels": state.get("step_labels", {}),
        "phase": step_phases.get(state["current_step"], "unknown"),
        "steps": state["steps"],
        "case_mode": conversation.get("case_mode", "single"),
    }
