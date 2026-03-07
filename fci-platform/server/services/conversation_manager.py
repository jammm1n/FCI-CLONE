"""
FCI Platform — Conversation Manager Service

Manages the full lifecycle of investigation conversations:
- Creating conversations (with initial case data injection + AI assessment)
- Sending messages (context assembly → AI call → storage)
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
    "messages": [
        {
            "message_id": "msg_001",
            "role": "system_injected",   # or "user", "assistant", "tool_exchange"
            "content": "...",
            "timestamp": datetime,
            "visible": false,            # hidden from frontend
            ...
        },
    ],
    "created_at": datetime,
    "updated_at": datetime,
}
"""

import logging
import uuid
import os
import base64
from datetime import datetime, timezone
from pathlib import Path

from server.config import settings
from server.database import get_database
from server.services.ai_client import (
    get_ai_response,
    get_ai_response_streaming,
    build_user_message_content,
)
from server.services.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


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
    message, updates case status. AI assessment triggered separately via
    send_message_streaming with is_initial_assessment=True.

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
            "Case data loaded. Provide a brief initial summary: case type classification, "
            "top 3 risk indicators, and suggested investigation approach. "
            "Do NOT use the get_reference_document tool for this initial assessment — "
            "work only with the case data and your core knowledge. Keep it concise."
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
            "mode": "case",
            "title": "",
            "status": "active",
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

        logger.info("Created case conversation %s for case %s", conversation_id, case_id)

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

    Steps:
        1. Retrieve the conversation from MongoDB
        2. Rebuild the API messages array from stored history
        3. Add the new user message (with images if any)
        4. Call the AI
        5. Store the user message, tool exchanges, and AI response
        6. Return the response

    Args:
        conversation_id: The conversation to send the message in.
        content: The user's message text.
        knowledge_base: KnowledgeBase instance.
        images: Optional list of {"base64": "...", "media_type": "..."}.

    Returns:
        dict with message_id, role, content, tools_used, token_usage, timestamp.
    """
    db = get_database()

    # 1. Retrieve conversation
    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    # 2. Rebuild API messages from history
    api_messages = _rebuild_api_messages(conversation["messages"])

    # 3. Build and append the new user message
    # Save images to disk if present
    stored_images = []
    if images:
        stored_images = await _store_images(conversation_id, images)

    user_content = build_user_message_content(content, images)
    api_messages.append({"role": "user", "content": user_content})

    # 4. Call the AI
    system_prompt = knowledge_base.get_system_prompt(mode=conversation.get("mode", "case"))
    ai_result = await get_ai_response(
        system_prompt=system_prompt,
        messages=api_messages,
        knowledge_base=knowledge_base,
    )

    # 5. Store messages
    now = _now()

    # User message (visible)
    user_message = {
        "message_id": _generate_id("msg"),
        "role": "user",
        "content": content,
        "images": stored_images,
        "timestamp": now,
        "visible": True,
    }

    # Tool exchanges (hidden)
    tool_messages = []
    for tc_msg in ai_result.get("tool_call_messages", []):
        tool_messages.append({
            "message_id": _generate_id("msg"),
            "role": "tool_exchange",
            "content": tc_msg["content"],
            "original_role": tc_msg["role"],
            "timestamp": now,
            "visible": False,
        })

    # Assistant response (visible)
    assistant_message = {
        "message_id": _generate_id("msg"),
        "role": "assistant",
        "content": ai_result["content"],
        "tools_used": ai_result["tools_used"],
        "token_usage": ai_result["token_usage"],
        "timestamp": now,
        "visible": True,
    }

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

    Yields the same event dicts as ai_client.get_ai_response_streaming().
    After the stream completes (the "done" event), the caller should call
    store_streamed_response() to persist everything to MongoDB.

    Yields:
        {"type": "content_delta", "text": "..."}
        {"type": "tool_use", "tool": "...", "document_id": "..."}
        {"type": "done", "content": "...", "tools_used": [...], ...}
    """
    db = get_database()

    # Retrieve conversation
    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    # Rebuild API messages from stored history
    api_messages = _rebuild_api_messages(conversation["messages"])

    if not is_initial_assessment:
        # Store images if present
        if images:
            await _store_images(conversation_id, images)

        # Build and append user message
        user_content = build_user_message_content(content, images)
        api_messages.append({"role": "user", "content": user_content})

    # Stream the AI response
    system_prompt = knowledge_base.get_system_prompt(mode=conversation.get("mode", "case"))
    async for event in get_ai_response_streaming(
        system_prompt=system_prompt,
        messages=api_messages,
        knowledge_base=knowledge_base,
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
) -> dict:
    """
    Store a streamed conversation turn in MongoDB.

    When is_initial_assessment=True, skip storing a user message (the
    system_injected message was already stored at creation time). Only
    store tool exchanges + assistant message.

    Called by the router after the streaming generator is fully consumed.
    Returns the assistant message metadata.
    """
    db = get_database()
    now = _now()

    all_new_messages = []

    if not is_initial_assessment:
        # Store images references
        stored_images = []
        if user_images:
            stored_images = await _store_images(conversation_id, user_images)

        # User message
        user_message = {
            "message_id": _generate_id("msg"),
            "role": "user",
            "content": user_content,
            "images": stored_images,
            "timestamp": now,
            "visible": True,
        }
        all_new_messages.append(user_message)

    # Tool exchanges (hidden)
    for tc_msg in tool_call_messages:
        all_new_messages.append({
            "message_id": _generate_id("msg"),
            "role": "tool_exchange",
            "content": tc_msg["content"],
            "original_role": tc_msg["role"],
            "timestamp": now,
            "visible": False,
        })

    # Assistant message
    assistant_msg_id = _generate_id("msg")
    assistant_message = {
        "message_id": assistant_msg_id,
        "role": "assistant",
        "content": ai_content,
        "tools_used": tools_used,
        "token_usage": token_usage,
        "timestamp": now,
        "visible": True,
    }
    all_new_messages.append(assistant_message)

    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$push": {"messages": {"$each": all_new_messages}},
            "$set": {"updated_at": now},
        }
    )

    # Auto-generate title for free_chat conversations on first user message
    if not is_initial_assessment and user_content:
        conversation = await db.conversations.find_one(
            {"_id": conversation_id},
            {"mode": 1, "title": 1},
        )
        if conversation and conversation.get("mode") == "free_chat" and not conversation.get("title"):
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
    # Take first sentence or first 50 chars
    text = content.strip()
    # Try to find first sentence end
    for sep in [". ", "? ", "! ", "\n"]:
        idx = text.find(sep)
        if 0 < idx < 60:
            return text[:idx + 1]
    # Fallback: first 50 chars
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

        visible_messages.append(entry)

    return {
        "conversation_id": conversation_id,
        "case_id": conversation.get("case_id"),
        "mode": conversation.get("mode", "case"),
        "title": conversation.get("title", ""),
        "messages": visible_messages,
    }


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

    This is called on every new turn to reconstruct the full context.
    The stored messages include hidden context (case data, tool exchanges)
    that must be included in the API payload even though they're not
    shown to the user.

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

    Args:
        conversation_id: The conversation these images belong to.
        images: List of {"base64": "...", "media_type": "..."}.

    Returns:
        List of {"image_id": "...", "media_type": "...", "stored_path": "..."}.
    """
    image_dir = Path(settings.IMAGES_DIR) / conversation_id
    image_dir.mkdir(parents=True, exist_ok=True)

    stored = []
    for img in images:
        image_id = _generate_id("img")
        media_type = img["media_type"]

        # Determine file extension from media type
        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/webp": "webp",
        }
        ext = ext_map.get(media_type, "bin")

        filename = f"{image_id}.{ext}"
        filepath = image_dir / filename

        # Decode and write
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