"""
FCI Platform — Conversations Router

Endpoints for creating investigation conversations, sending messages
(with streaming support), and retrieving conversation history.

Streaming flow:
    POST /api/conversations/{id}/messages sends an SSE stream.
    The router iterates the async generator from conversation_manager,
    forwards content_delta and tool_use events to the client as SSE,
    then after the "done" event, stores the full turn in MongoDB.
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response
from sse_starlette.sse import EventSourceResponse
from anthropic import RateLimitError

from server.routers.auth import get_current_user
from server.services import conversation_manager
from server.services.knowledge_base import KnowledgeBase
from server.services.pdf_export import generate_conversation_pdf, build_pdf_filename
from server.database import get_database
from server.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _get_knowledge_base(request: Request) -> KnowledgeBase:
    """Get the KnowledgeBase from app state (loaded on startup)."""
    return request.app.state.knowledge_base


# ---------------------------------------------------------------------------
# Create conversation
# ---------------------------------------------------------------------------

@router.post("")
async def create_conversation(
    body: dict,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new conversation — lightweight, no AI call.

    For case mode: pre-stores case data, returns immediately.
    For free_chat mode: creates empty conversation.

    Request body: {"case_id": "CASE-2026-0451", "mode": "case"}
                  or {"mode": "free_chat"}
    """
    mode = body.get("mode", "case")
    case_id = body.get("case_id")

    if mode == "case" and not case_id:
        raise HTTPException(status_code=400, detail="case_id is required for case mode")

    kb = _get_knowledge_base(request)

    try:
        result = await conversation_manager.create_conversation(
            user_id=current_user["user_id"],
            knowledge_base=kb,
            case_id=case_id,
            mode=mode,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


# ---------------------------------------------------------------------------
# Send message (streaming by default, non-streaming fallback)
# ---------------------------------------------------------------------------

@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    body: dict,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a message in an existing conversation.

    By default, returns a streaming SSE response. If the request
    includes "stream": false, returns a regular JSON response.

    Request body:
        {
            "content": "What does the counterparty pattern suggest?",
            "images": [{"base64": "...", "media_type": "image/jpeg"}],  // optional
            "stream": true  // optional, default true
        }

    Streaming response (SSE):
        data: {"type": "content_delta", "text": "The counterparty"}
        data: {"type": "content_delta", "text": " transaction pattern"}
        data: {"type": "tool_use", "tool": "get_reference_document", "document_id": "scam-fraud-sop", "document_title": "Scam & Fraud SOP"}
        data: {"type": "content_delta", "text": " shows..."}
        data: {"type": "done", "message_id": "msg_xyz", "token_usage": {...}}

    Non-streaming response (JSON):
        {"message_id": "...", "role": "assistant", "content": "...", ...}
    """
    content = body.get("content", "")
    images = body.get("images")
    initial_assessment = body.get("initial_assessment", False)
    if not initial_assessment and not content and not images:
        raise HTTPException(status_code=400, detail="content or images required")
    stream = body.get("stream", True)
    kb = _get_knowledge_base(request)

    # --- Non-streaming path ---
    if not stream:
        try:
            result = await conversation_manager.send_message(
                conversation_id=conversation_id,
                content=content,
                knowledge_base=kb,
                images=images,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RateLimitError as e:
            logger.warning("Anthropic rate limit hit during send_message: %s", e)
            raise HTTPException(
                status_code=429,
                detail="AI service is rate-limited. Please wait a moment and try again.",
            )

        return result

    # --- Streaming path ---
    async def event_generator():
        """
        Iterate the streaming generator, yield SSE events,
        then store the completed turn in MongoDB BEFORE yielding
        the done event.

        This ensures that if the client disconnects after receiving
        the done event, the response is already persisted.
        """
        done_event = None
        step_complete_signalled = False
        oneshot_ready_signalled = False

        try:
            async for event in conversation_manager.send_message_streaming(
                conversation_id=conversation_id,
                content=content,
                knowledge_base=kb,
                images=images,
                is_initial_assessment=initial_assessment,
            ):
                if event["type"] == "done":
                    # Capture — do NOT yield yet; store first
                    done_event = event
                elif event["type"] == "tool_use" and event.get("tool") == "signal_step_complete":
                    step_complete_signalled = True
                    yield {"data": json.dumps(event)}
                elif event["type"] == "tool_use" and event.get("tool") == "signal_ready_to_execute":
                    oneshot_ready_signalled = True
                    yield {"data": json.dumps(event)}
                else:
                    # Forward content_delta and tool_use events
                    yield {"data": json.dumps(event)}

        except ValueError as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return
        except RateLimitError as e:
            logger.warning("Anthropic rate limit hit during streaming: %s", e)
            yield {"data": json.dumps({"type": "error", "message": "AI service is rate-limited. Please wait a moment and try again."})}
            return
        except Exception as e:
            logger.exception("Streaming error in conversation %s", conversation_id)
            yield {"data": json.dumps({"type": "error", "message": "Internal server error"})}
            return

        # Store to MongoDB FIRST, then yield done event with message_id
        if done_event:
            try:
                store_result = await conversation_manager.store_streamed_response(
                    conversation_id=conversation_id,
                    user_content=content,
                    user_images=images,
                    ai_content=done_event["content"],
                    tools_used=done_event.get("tools_used", []),
                    token_usage=done_event.get("token_usage", {}),
                    tool_call_messages=done_event.get("tool_call_messages", []),
                    is_initial_assessment=initial_assessment,
                    step_complete_signalled=step_complete_signalled,
                    oneshot_ready_signalled=oneshot_ready_signalled,
                    thinking_content=done_event.get("thinking_content", ""),
                )
                # Now yield done — response is safely persisted
                yield {
                    "data": json.dumps({
                        "type": "done",
                        "message_id": store_result["message_id"],
                        "token_usage": done_event.get("token_usage", {}),
                    })
                }
            except Exception as e:
                logger.exception(
                    "Failed to store streamed response in conversation %s",
                    conversation_id,
                )
                yield {
                    "data": json.dumps({
                        "type": "error",
                        "message": "Response streamed but failed to save.",
                    })
                }

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Get conversation history
# ---------------------------------------------------------------------------

@router.get("/{conversation_id}/history")
async def get_history(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Return the visible conversation history.

    Used when returning to a case in progress. Hidden messages
    (case data injection, tool exchanges) are excluded.
    """
    try:
        history = await conversation_manager.get_history(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return history


# ---------------------------------------------------------------------------
# List conversations
# ---------------------------------------------------------------------------

@router.get("")
async def list_conversations(
    request: Request,
    mode: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    """
    List conversations for the current user.

    Optional query param `mode` to filter (e.g., "free_chat", "case").
    """
    conversations = await conversation_manager.list_conversations(
        user_id=current_user["user_id"],
        mode=mode,
    )
    return {"conversations": conversations}


# ---------------------------------------------------------------------------
# Export conversation as PDF
# ---------------------------------------------------------------------------

@router.get("/{conversation_id}/export/pdf")
async def export_pdf(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Export a conversation transcript as a PDF file."""
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.get("user_id") != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check for visible messages
    visible = [m for m in conversation.get("messages", []) if m.get("visible", True)]
    if not visible:
        raise HTTPException(status_code=400, detail="No messages to export")

    # Fetch case doc if this is a case conversation
    case_doc = None
    case_id = conversation.get("case_id")
    if case_id:
        case_doc = await db.cases.find_one({"case_id": case_id})

    try:
        pdf_bytes = generate_conversation_pdf(
            conversation=conversation,
            case_doc=case_doc,
            images_dir=settings.IMAGES_DIR,
        )
    except Exception as e:
        logger.exception("Failed to generate PDF for conversation %s", conversation_id)
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    filename = build_pdf_filename(conversation, case_doc)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Serve stored image
# ---------------------------------------------------------------------------

@router.get("/{conversation_id}/images/{image_id}")
async def get_image(
    conversation_id: str,
    image_id: str,
):
    """Serve a stored image file by conversation and image ID."""
    image_dir = Path(settings.IMAGES_DIR) / conversation_id
    if not image_dir.is_dir():
        raise HTTPException(status_code=404, detail="Image not found")

    # Find the file matching this image_id (any extension)
    matches = list(image_dir.glob(f"{image_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Image not found")

    filepath = matches[0]
    ext_to_mime = {".jpg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
    media_type = ext_to_mime.get(filepath.suffix, "application/octet-stream")

    return FileResponse(filepath, media_type=media_type)


# ---------------------------------------------------------------------------
# Step transitions
# ---------------------------------------------------------------------------

@router.post("/{conversation_id}/advance-step")
async def advance_step(
    conversation_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Complete the current step and advance to the next one.

    Generates a structured summary of the completed step, stores it,
    and advances investigation_state.current_step.

    Valid for steps 1→2, 2→3, 3→4. Use /qc-check for step 4→5.
    """
    kb = _get_knowledge_base(request)

    try:
        result = await conversation_manager.approve_and_continue(
            conversation_id=conversation_id,
            user_id=current_user["user_id"],
            knowledge_base=kb,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@router.post("/{conversation_id}/qc-check")
async def qc_check(
    conversation_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Transition from step 4 to step 5 (QC Check).

    Generates step 4 summary and advances state. The pasted case text
    should be sent as a regular message via POST /messages afterward.
    """
    kb = _get_knowledge_base(request)

    try:
        result = await conversation_manager.qc_check(
            conversation_id=conversation_id,
            user_id=current_user["user_id"],
            knowledge_base=kb,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@router.get("/{conversation_id}/state")
async def get_state(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Return the current investigation state for a conversation."""
    try:
        state = await conversation_manager.get_investigation_state(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return state


# ---------------------------------------------------------------------------
# Auto-execute (run remaining steps without human approval)
# ---------------------------------------------------------------------------

@router.post("/{conversation_id}/auto-execute")
async def auto_execute(
    conversation_id: str,
    body: dict,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Auto-execute remaining investigation steps through a single SSE stream.

    Runs each step sequentially: stream AI → store → advance → repeat.
    Stops after step 4 (step 5 QC requires manual input).

    Request body: {"skip_summaries": false}

    SSE events:
        {"type": "auto_step_start", "step": 2, "phase": "analysis", "user_content": "Begin Step 2: ..."}
        {"type": "content_delta", "text": "..."}
        {"type": "tool_use", "tool": "...", ...}
        {"type": "auto_step_done", "step": 2, "message_id": "msg_xxx", "token_usage": {...}}
        {"type": "auto_step_divider", "content": "Step 2 complete. Moving to Step 3: Decision."}
        ... (repeat for each step)
        {"type": "auto_complete"}
    """
    skip_summaries = body.get("skip_summaries", False)
    kb = _get_knowledge_base(request)

    PHASE_LABELS = {
        "setup": "Setup", "analysis": "Analysis", "decision": "Decision",
        "post": "Post-Decision", "qc_check": "QC Check",
    }
    STEP_PHASE_MAP = {1: "setup", 2: "analysis", 3: "decision", 4: "post", 5: "qc_check"}

    async def event_generator():
        try:
            db = get_database()
            conv = await db.conversations.find_one({"_id": conversation_id})

            if not conv:
                yield {"data": json.dumps({"type": "error", "message": "Conversation not found"})}
                return

            state = conv.get("investigation_state")
            if not state:
                yield {"data": json.dumps({"type": "error", "message": "No investigation state"})}
                return

            current_step = state["current_step"]

            # If current step is already complete, advance first
            if state.get("step_complete_signalled", False) and current_step < 4:
                if skip_summaries:
                    result = await conversation_manager.lightweight_step_advance(
                        conversation_id=conversation_id,
                        user_id=current_user["user_id"],
                    )
                else:
                    result = await conversation_manager.approve_and_continue(
                        conversation_id=conversation_id,
                        user_id=current_user["user_id"],
                        knowledge_base=kb,
                    )

                phase_label = PHASE_LABELS.get(STEP_PHASE_MAP.get(current_step), "")
                next_label = PHASE_LABELS.get(result["phase"], result["phase"])
                yield {"data": json.dumps({
                    "type": "auto_step_divider",
                    "content": f"Step {current_step} ({phase_label}) complete. Moving to Step {result['step']}: {next_label}.",
                })}

                current_step = result["step"]

            # Run steps from current_step through 4
            for step_num in range(current_step, 5):
                phase = STEP_PHASE_MAP.get(step_num, "unknown")
                phase_label = PHASE_LABELS.get(phase, phase)

                # Check if this step already has output
                conv_fresh = await db.conversations.find_one({"_id": conversation_id})
                has_output = any(
                    m.get("step") == step_num
                    and m["role"] == "assistant"
                    and m.get("visible", True)
                    for m in conv_fresh.get("messages", [])
                )

                if has_output:
                    # Step already done — advance
                    if step_num < 4:
                        if skip_summaries:
                            result = await conversation_manager.lightweight_step_advance(
                                conversation_id=conversation_id,
                                user_id=current_user["user_id"],
                            )
                        else:
                            result = await conversation_manager.approve_and_continue(
                                conversation_id=conversation_id,
                                user_id=current_user["user_id"],
                                knowledge_base=kb,
                            )
                        next_label = PHASE_LABELS.get(result["phase"], result["phase"])
                        yield {"data": json.dumps({
                            "type": "auto_step_divider",
                            "content": f"Step {step_num} ({phase_label}) complete. Moving to Step {result['step']}: {next_label}.",
                        })}
                    continue

                # Determine message content
                is_initial = False
                content = f"Begin Step {step_num}: {phase_label}. Your step document is loaded. Proceed in express mode."

                if step_num == 1:
                    has_any_visible = any(
                        m.get("step") == 1 and m.get("visible", True)
                        for m in conv_fresh.get("messages", [])
                    )
                    if not has_any_visible:
                        content = ""
                        is_initial = True

                # Emit step start
                yield {"data": json.dumps({
                    "type": "auto_step_start",
                    "step": step_num,
                    "phase": phase,
                    "user_content": content if not is_initial else None,
                })}

                # Stream AI response
                done_event = None

                async for event in conversation_manager.send_message_streaming(
                    conversation_id=conversation_id,
                    content=content,
                    knowledge_base=kb,
                    is_initial_assessment=is_initial,
                ):
                    if event["type"] == "done":
                        done_event = event
                    elif event["type"] == "tool_use" and event.get("tool") == "signal_step_complete":
                        pass  # Silently consume in auto mode
                    else:
                        yield {"data": json.dumps(event)}

                # Store response
                if done_event:
                    store_result = await conversation_manager.store_streamed_response(
                        conversation_id=conversation_id,
                        user_content=content,
                        user_images=None,
                        ai_content=done_event["content"],
                        tools_used=done_event.get("tools_used", []),
                        token_usage=done_event.get("token_usage", {}),
                        tool_call_messages=done_event.get("tool_call_messages", []),
                        is_initial_assessment=is_initial,
                        step_complete_signalled=False,
                    )

                    yield {"data": json.dumps({
                        "type": "auto_step_done",
                        "step": step_num,
                        "message_id": store_result["message_id"],
                        "token_usage": done_event.get("token_usage", {}),
                    })}

                # Advance to next step
                if step_num < 4:
                    if skip_summaries:
                        result = await conversation_manager.lightweight_step_advance(
                            conversation_id=conversation_id,
                            user_id=current_user["user_id"],
                        )
                    else:
                        result = await conversation_manager.approve_and_continue(
                            conversation_id=conversation_id,
                            user_id=current_user["user_id"],
                            knowledge_base=kb,
                        )

                    next_label = PHASE_LABELS.get(result["phase"], result["phase"])
                    yield {"data": json.dumps({
                        "type": "auto_step_divider",
                        "content": f"Step {step_num} ({phase_label}) complete. Moving to Step {result['step']}: {next_label}.",
                    })}

            yield {"data": json.dumps({"type": "auto_complete"})}

        except RateLimitError as e:
            logger.warning("Rate limit during auto-execute: %s", e)
            yield {"data": json.dumps({"type": "error", "message": "AI service rate-limited. Try again shortly."})}
        except Exception as e:
            logger.exception("Auto-execute error in conversation %s", conversation_id)
            yield {"data": json.dumps({"type": "error", "message": str(e)})}

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Delete conversation
# ---------------------------------------------------------------------------

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a conversation owned by the current user."""
    try:
        await conversation_manager.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "deleted"}


# ---------------------------------------------------------------------------
# One-shot execution
# ---------------------------------------------------------------------------

@router.post("/{conversation_id}/oneshot-execute")
async def oneshot_execute(
    conversation_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Execute the full ICR in one-shot mode via a single streaming AI call.

    Uses Opus + extended thinking (configurable). All step documents are
    loaded into a single system prompt. The setup transcript is included
    as context.

    SSE events:
        {"type": "content_delta", "text": "..."}
        {"type": "tool_use", "tool": "...", ...}
        {"type": "done", "message_id": "msg_xxx", "token_usage": {...}}
    """
    kb = _get_knowledge_base(request)

    async def event_generator():
        done_event = None

        try:
            async for event in conversation_manager.oneshot_execute(
                conversation_id=conversation_id,
                knowledge_base=kb,
            ):
                if event["type"] == "done":
                    done_event = event
                else:
                    yield {"data": json.dumps(event)}

        except ValueError as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            return
        except RateLimitError as e:
            logger.warning("Rate limit during oneshot execution: %s", e)
            yield {"data": json.dumps({"type": "error", "message": "AI service rate-limited. Try again shortly."})}
            return
        except Exception as e:
            logger.exception("Oneshot execution error in conversation %s", conversation_id)
            yield {"data": json.dumps({"type": "error", "message": "Internal server error"})}
            return

        # Store to MongoDB FIRST, then yield done event
        if done_event:
            try:
                store_result = await conversation_manager.store_oneshot_execution(
                    conversation_id=conversation_id,
                    user_id=current_user["user_id"],
                    ai_content=done_event["content"],
                    tools_used=done_event.get("tools_used", []),
                    token_usage=done_event.get("token_usage", {}),
                    tool_call_messages=done_event.get("tool_call_messages", []),
                    thinking_content=done_event.get("thinking_content", ""),
                )
                yield {
                    "data": json.dumps({
                        "type": "done",
                        "message_id": store_result["message_id"],
                        "token_usage": done_event.get("token_usage", {}),
                    })
                }
            except Exception as e:
                logger.exception(
                    "Failed to store oneshot execution in conversation %s",
                    conversation_id,
                )
                yield {
                    "data": json.dumps({
                        "type": "error",
                        "message": "Response streamed but failed to save.",
                    })
                }

    return EventSourceResponse(event_generator())


@router.post("/{conversation_id}/reset")
async def reset_case(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Reset a case investigation — deletes the conversation and clears
    the case's conversation_id so it can be re-opened fresh.
    """
    try:
        result = await conversation_manager.reset_case_conversation(
            conversation_id=conversation_id,
            user_id=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result