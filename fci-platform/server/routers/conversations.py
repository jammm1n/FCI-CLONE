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

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from anthropic import RateLimitError

from server.routers.auth import get_current_user
from server.services import conversation_manager
from server.services.knowledge_base import KnowledgeBase

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
        then store the completed turn in MongoDB.
        """
        done_event = None

        try:
            async for event in conversation_manager.send_message_streaming(
                conversation_id=conversation_id,
                content=content,
                knowledge_base=kb,
                images=images,
                is_initial_assessment=initial_assessment,
            ):
                if event["type"] == "done":
                    # Capture the done event for storage, then yield it
                    done_event = event
                    # Yield a slim done event to the frontend
                    yield {
                        "data": json.dumps({
                            "type": "done",
                            "message_id": None,  # Will be set after storage
                            "token_usage": event.get("token_usage", {}),
                        })
                    }
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

        # After streaming is complete, store the turn in MongoDB
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
                )
                # Yield a final storage confirmation event
                yield {
                    "data": json.dumps({
                        "type": "stored",
                        "message_id": store_result["message_id"],
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