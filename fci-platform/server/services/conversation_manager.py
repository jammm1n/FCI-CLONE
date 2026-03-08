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

import logging
import uuid
import base64
from datetime import datetime, timezone
from pathlib import Path

from server.config import settings, STEP_CONFIG, STEP_PHASES
from server.database import get_database
from server.services.ai_client import (
    get_ai_response,
    get_ai_response_streaming,
    build_user_message_content,
)
from server.services.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INITIAL_ASSESSMENT_INSTRUCTION = (
    "Case data loaded. Provide a brief initial summary: case type classification, "
    "top 3 risk indicators, and suggested investigation approach. "
    "Do NOT use the get_reference_document tool for this initial assessment — "
    "work only with the case data and your core knowledge. Keep it concise."
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

        # Build case data markdown and pre-store the system_injected message
        case_data_markdown = _build_case_data_markdown(case)
        initial_user_content = (
            f"[CASE DATA]\n\n{case_data_markdown}\n\n"
            f"{INITIAL_ASSESSMENT_INSTRUCTION}"
        )

        case_data_message = {
            "message_id": _generate_id("msg"),
            "role": "system_injected",
            "content": initial_user_content,
            "step": 1,
            "timestamp": now,
            "visible": False,
        }

        conversation_doc = {
            "_id": conversation_id,
            "case_id": case_id,
            "user_id": user_id,
            "mode": "case",
            "title": "",
            "status": "active",
            "investigation_state": {
                "current_step": 1,
                "steps": [
                    {
                        "step_number": 1,
                        "phase": "setup",
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
        system_prompt = knowledge_base.get_step_system_prompt(step)
        model = STEP_CONFIG[step]["model"]
        case = None
        if step <= 4 and conversation.get("case_id"):
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

    if has_step_state:
        step = conversation["investigation_state"]["current_step"]
        system_prompt = knowledge_base.get_step_system_prompt(step)
        model = STEP_CONFIG[step]["model"]
        case = None
        if step <= 4 and conversation.get("case_id"):
            case = await db.cases.find_one({"_id": conversation["case_id"]})
        api_messages = _rebuild_step_api_messages(conversation, case)
    else:
        system_prompt = knowledge_base.get_system_prompt(mode=conversation.get("mode", "case"))
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
    # else: non-step initial assessment — system_injected already has instruction

    # Stream the AI response
    async for event in get_ai_response_streaming(
        system_prompt=system_prompt,
        messages=api_messages,
        knowledge_base=knowledge_base,
        model=model,
    ):
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
        {"investigation_state.current_step": 1, "mode": 1, "title": 1},
    )
    current_step = conv.get("investigation_state", {}).get("current_step") if conv else None

    all_new_messages = []

    if is_initial_assessment and current_step:
        # Step-based initial assessment: store the instruction as a hidden
        # user message so _rebuild_step_api_messages can replay it
        instruction_msg = {
            "message_id": _generate_id("msg"),
            "role": "user",
            "content": INITIAL_ASSESSMENT_INSTRUCTION,
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
        # Always-included docs for this step
        injected = []
        injected.append({"tool": "system_injected", "document_id": "system-prompt-case", "document_title": "System Prompt"})
        injected.append({"tool": "system_injected", "document_id": "icr-general-rules", "document_title": "ICR General Rules"})
        if current_step <= 4:
            injected.append({"tool": "system_injected", "document_id": "qc-quick-reference", "document_title": "QC Quick Reference"})
        # Step-specific docs
        for doc_id in STEP_CONFIG.get(current_step, {}).get("docs", []):
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
    if current_step:
        assistant_message["step"] = current_step
    all_new_messages.append(assistant_message)

    set_fields = {"updated_at": now}
    if current_step and step_complete_signalled:
        set_fields["investigation_state.step_complete_signalled"] = True

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
        result["investigation_state"] = {
            "current_step": state["current_step"],
            "phase": STEP_PHASES.get(state["current_step"], "unknown"),
            "steps": state["steps"],
            "step_complete_signalled": state.get("step_complete_signalled", False),
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

    # 2. Inject fresh case data (steps 1-4 only, not step 5)
    if current_step <= 4 and case:
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

def _build_case_data_markdown(case: dict) -> str:
    """
    Build a markdown document from a case's preprocessed_data fields.

    Concatenates all available data sections with headers.
    Only includes sections that have data.
    """
    preprocessed = case.get("preprocessed_data", {})
    if not preprocessed:
        return "(No preprocessed data available for this case.)"

    # Map field names to display headers (matches ingestion assembly output)
    section_map = {
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
        "elliptic": "Elliptic Wallet Screening",
        "l1_referral": "L1 Referral Narrative",
        "haoDesk": "HaoDesk Case Data",
        "kyc": "KYC Document Summary",
        "prior_icr": "Prior ICR Summary",
        "rfi": "RFI Summary",
        "kodex": "Law Enforcement / Kodex",
        "l1_victim": "L1 Victim Communications",
        "l1_suspect": "L1 Suspect Communications",
        "investigator_notes": "Investigator Notes",
    }

    parts = [
        f"**Case ID:** {case.get('_id', 'Unknown')}",
        f"**Case Type:** {case.get('case_type', 'Unknown')}",
        f"**Subject User:** {case.get('subject_user_id', 'Unknown')}",
        f"**Summary:** {case.get('summary', 'No summary available')}",
        "",
        "---",
        "",
    ]

    for field, header in section_map.items():
        content = preprocessed.get(field)
        if content:
            parts.append(f"## {header}")
            parts.append("")
            parts.append(content)
            parts.append("")
            parts.append("---")
            parts.append("")

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
    # Extract step messages and rebuild as API-format messages
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

    if not step_api_messages:
        raise ValueError(f"No messages found for step {step}")

    # Ensure the messages end with a user message (API requirement)
    if step_api_messages[-1]["role"] != "user":
        step_api_messages.append({
            "role": "user",
            "content": (
                f"Generate a structured summary of Step {step} "
                f"({STEP_PHASES[step].replace('_', ' ').title()}) "
                "using the template provided in your instructions."
            ),
        })

    # Build summary system prompt with step info
    phase_name = STEP_PHASES[step].replace("_", " ").title()
    system_prompt = SUMMARY_SYSTEM_PROMPT.format(
        step_number=step,
        phase_name=phase_name,
    )

    summary_model = STEP_CONFIG["summary"]["model"]

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
    if current_step > 3:
        raise ValueError(
            f"Cannot advance from step {current_step}. "
            "Use QC check for step 4→5."
        )

    # Generate summary
    summary_result = await _generate_step_summary(
        conversation, current_step, knowledge_base
    )

    now = _now()
    next_step = current_step + 1
    next_phase = STEP_PHASES[next_step]

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
        "status": "active",
        "summary": None,
        "summary_model": None,
        "summary_token_usage": None,
        "completed_at": None,
        "approved_by": None,
    })

    # Step divider message
    divider_msg = {
        "message_id": _generate_id("msg"),
        "role": "step_divider",
        "content": (
            f"Step {current_step} ({STEP_PHASES[current_step].replace('_', ' ').title()}) "
            f"complete. Moving to Step {next_step}: {next_phase.replace('_', ' ').title()}."
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
    if current_step != 4:
        raise ValueError(
            f"QC check can only be initiated from step 4, "
            f"currently on step {current_step}"
        )

    # Generate summary for step 4
    summary_result = await _generate_step_summary(
        conversation, current_step, knowledge_base
    )

    now = _now()

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
        "step_number": 5,
        "phase": "qc_check",
        "status": "active",
        "summary": None,
        "summary_model": None,
        "summary_token_usage": None,
        "completed_at": None,
        "approved_by": None,
    })

    # Step divider message
    divider_msg = {
        "message_id": _generate_id("msg"),
        "role": "step_divider",
        "content": "Step 4 (Post) complete. Moving to Step 5: QC Check.",
        "step": 4,
        "timestamp": now,
        "visible": True,
    }

    # Update conversation
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$set": {
                "investigation_state.steps": steps,
                "investigation_state.current_step": 5,
                "investigation_state.step_complete_signalled": False,
                "updated_at": now,
            },
            "$push": {"messages": divider_msg},
        }
    )

    logger.info(
        "QC check initiated for conversation %s. Step 4 summary: %d chars",
        conversation_id, len(summary_result["summary"]),
    )

    return {
        "step": 5,
        "phase": "qc_check",
    }


# ---------------------------------------------------------------------------
# Investigation state
# ---------------------------------------------------------------------------

async def get_investigation_state(conversation_id: str) -> dict:
    """Return the current investigation state for a conversation."""
    db = get_database()

    conversation = await db.conversations.find_one(
        {"_id": conversation_id},
        {"investigation_state": 1},
    )
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    state = conversation.get("investigation_state")
    if not state:
        raise ValueError("Conversation has no investigation state")

    return {
        "current_step": state["current_step"],
        "phase": STEP_PHASES.get(state["current_step"], "unknown"),
        "steps": state["steps"],
    }
