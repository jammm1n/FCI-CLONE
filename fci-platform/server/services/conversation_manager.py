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
    case_id: str,
    user_id: str,
    knowledge_base: KnowledgeBase,
) -> dict:
    """
    Create a new investigation conversation for a case.

    Steps:
        1. Load the case from MongoDB (including preprocessed_data)
        2. Build the case data markdown from preprocessed_data fields
        3. Create a conversation document in MongoDB
        4. Assemble the initial API payload (system prompt + case data)
        5. Call the AI for the initial assessment
        6. Store the hidden context message and AI response
        7. Update the case status and conversation_id

    Returns:
        dict with conversation_id, case_id, and initial_response.
    """
    db = get_database()

    # 1. Load the case
    case = await db.cases.find_one({"_id": case_id})
    if case is None:
        raise ValueError(f"Case not found: {case_id}")

    if case.get("conversation_id"):
        raise ValueError(
            f"Case {case_id} already has a conversation: {case['conversation_id']}"
        )

    # 2. Build case data markdown
    case_data_markdown = _build_case_data_markdown(case)

    # 3. Create the conversation document
    conversation_id = _generate_id("conv")
    conversation_doc = {
        "_id": conversation_id,
        "case_id": case_id,
        "user_id": user_id,
        "status": "active",
        "messages": [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    await db.conversations.insert_one(conversation_doc)

    # 4. Assemble the initial API payload
    # The case data is injected as the first user message, with an instruction
    # for the AI to begin its initial assessment.
    initial_user_content = (
        f"[CASE DATA]\n\n{case_data_markdown}\n\n"
        "Case data loaded. Provide a brief initial summary: case type classification, "
        "top 3 risk indicators, and suggested investigation approach. "
        "Do NOT use the get_reference_document tool for this initial assessment — "
        "work only with the case data and your core knowledge. Keep it concise."
    )

    system_prompt = knowledge_base.get_system_prompt()
    messages_for_api = [
        {"role": "user", "content": initial_user_content}
    ]

    # 5. Call the AI
    logger.info("Creating conversation %s for case %s", conversation_id, case_id)
    ai_result = await get_ai_response(
        system_prompt=system_prompt,
        messages=messages_for_api,
        knowledge_base=knowledge_base,
    )

    # 6. Store messages in MongoDB
    now = _now()

    # Hidden case data injection
    case_data_message = {
        "message_id": _generate_id("msg"),
        "role": "system_injected",
        "content": initial_user_content,
        "timestamp": now,
        "visible": False,
    }

    # Store any tool call intermediate messages (hidden)
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

    # AI's initial assessment (visible)
    assistant_message = {
        "message_id": _generate_id("msg"),
        "role": "assistant",
        "content": ai_result["content"],
        "tools_used": ai_result["tools_used"],
        "token_usage": ai_result["token_usage"],
        "timestamp": now,
        "visible": True,
    }

    # Append all messages to the conversation
    all_new_messages = [case_data_message] + tool_messages + [assistant_message]
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$push": {"messages": {"$each": all_new_messages}},
            "$set": {"updated_at": now},
        }
    )

    # 7. Update the case
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

    logger.info(
        "Conversation %s created. Initial assessment: %d chars, tools: %s",
        conversation_id,
        len(ai_result["content"]),
        [t["document_id"] for t in ai_result["tools_used"]],
    )

    return {
        "conversation_id": conversation_id,
        "case_id": case_id,
        "initial_response": {
            "message_id": assistant_message["message_id"],
            "role": "assistant",
            "content": ai_result["content"],
            "tools_used": ai_result["tools_used"],
            "token_usage": ai_result["token_usage"],
            "timestamp": now.isoformat(),
        },
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
    system_prompt = knowledge_base.get_system_prompt()
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
):
    """
    Send a message and stream the response.

    Yields the same event dicts as ai_client.get_ai_response_streaming().
    After the stream completes (the "done" event), the caller should call
    store_streamed_response() to persist everything to MongoDB.

    This two-step pattern (stream → store) keeps the streaming generator
    clean and avoids DB writes during iteration.

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

    # Rebuild API messages
    api_messages = _rebuild_api_messages(conversation["messages"])

    # Store images if present
    if images:
        await _store_images(conversation_id, images)

    # Build and append user message
    user_content = build_user_message_content(content, images)
    api_messages.append({"role": "user", "content": user_content})

    # Stream the AI response
    system_prompt = knowledge_base.get_system_prompt()
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
) -> dict:
    """
    Store a streamed conversation turn in MongoDB.

    Called by the router after the streaming generator is fully consumed.
    Returns the assistant message metadata.
    """
    db = get_database()
    now = _now()

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

    # Tool exchanges (hidden)
    tool_messages = []
    for tc_msg in tool_call_messages:
        tool_messages.append({
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

    all_new_messages = [user_message] + tool_messages + [assistant_message]
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$push": {"messages": {"$each": all_new_messages}},
            "$set": {"updated_at": now},
        }
    )

    return {
        "message_id": assistant_msg_id,
        "timestamp": now.isoformat(),
    }


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
        "case_id": conversation["case_id"],
        "messages": visible_messages,
    }


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
                content_blocks.append({"type": "text", "text": msg["content"]})
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

    # Map field names to display headers
    section_map = {
        "c360_analysis": "C360 Analysis",
        "elliptic_analysis": "Elliptic Wallet Screening",
        "previous_cases": "Previous Investigations",
        "chat_history_summary": "L1 Customer Service Interactions",
        "kyc_summary": "KYC Information",
        "law_enforcement": "Law Enforcement Cases",
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