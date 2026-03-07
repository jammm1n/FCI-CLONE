"""
FCI Platform — AI Client Service

Wraps the Anthropic API with:
- Async message creation (non-streaming and streaming)
- Tool call loop for reference document retrieval
- Image content block assembly
- Token usage tracking

This is the core API integration layer. The conversation_manager calls
this service with an assembled payload; this service handles the API
interaction, tool processing, and response extraction.
"""

import logging
from typing import AsyncGenerator

from anthropic import AsyncAnthropic, RateLimitError, APIStatusError

from server.config import settings
from server.services.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions — sent with every API call
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_reference_document",
        "description": (
            "Retrieve a reference document from the knowledge base. "
            "Use this tool when you need detailed procedural guidance, "
            "SOP requirements, or historical decision precedents that are "
            "not covered by your core knowledge. Consult the reference "
            "document index in your system prompt to identify the correct "
            "document_id. Only request documents that are directly relevant "
            "to the current investigation question or case form section."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": (
                        "The unique identifier of the reference document "
                        "to retrieve, as listed in the reference document index."
                    )
                }
            },
            "required": ["document_id"]
        }
    },
    {
        "name": "get_prompt",
        "description": (
            "Retrieve a data processing prompt from the prompt library. "
            "Use this tool when you need to process raw data pasted by "
            "the investigator (e.g., C360 transaction data, device/IP "
            "output, Elliptic screenshots, communications). The prompt "
            "will include formatting rules automatically. Consult the "
            "processing prompt index in your system prompt to identify "
            "the correct prompt_id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt_id": {
                    "type": "string",
                    "description": (
                        "The unique identifier of the processing prompt "
                        "to retrieve, as listed in the processing prompt index."
                    )
                }
            },
            "required": ["prompt_id"]
        }
    },
]


# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    """Get or create the async Anthropic client singleton."""
    global _client
    if _client is None:
        _client = AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            max_retries=3,  # Auto-retries 429s with exponential backoff
        )
    return _client


# ---------------------------------------------------------------------------
# Tool call processing
# ---------------------------------------------------------------------------

def _process_tool_calls(
    response_content: list,
    knowledge_base: KnowledgeBase,
) -> tuple[list[dict], list[dict]]:
    """
    Extract tool calls from a response and generate tool results.

    Args:
        response_content: The content blocks from the API response.
        knowledge_base: The KnowledgeBase instance for document retrieval.

    Returns:
        Tuple of (tool_results, tools_used_metadata).
        - tool_results: list of tool_result dicts to send back to the API
        - tools_used_metadata: list of {tool, document_id, document_title}
          for the frontend audit trail
    """
    tool_results = []
    tools_used = []

    for block in response_content:
        if block.type == "tool_use":
            if block.name == "get_reference_document":
                doc_id = block.input.get("document_id", "")
                doc_content = knowledge_base.get_reference_document(doc_id)

                # Find document metadata for the audit trail
                doc_meta = next(
                    (d for d in knowledge_base.reference_index if d["id"] == doc_id),
                    None
                )
                tools_used.append({
                    "tool": "get_reference_document",
                    "document_id": doc_id,
                    "document_title": doc_meta["title"] if doc_meta else doc_id,
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": doc_content,
                })

                logger.info(
                    "Tool call: get_reference_document(%s) — %s",
                    doc_id,
                    doc_meta["title"] if doc_meta else "unknown document"
                )
            elif block.name == "get_prompt":
                prompt_id = block.input.get("prompt_id", "")
                prompt_content = knowledge_base.get_prompt(prompt_id)

                prompt_meta = next(
                    (p for p in knowledge_base.prompt_index if p["id"] == prompt_id),
                    None
                )
                tools_used.append({
                    "tool": "get_prompt",
                    "document_id": prompt_id,
                    "document_title": prompt_meta["title"] if prompt_meta else prompt_id,
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": prompt_content,
                })

                logger.info(
                    "Tool call: get_prompt(%s) — %s",
                    prompt_id,
                    prompt_meta["title"] if prompt_meta else "unknown prompt"
                )
            else:
                # Unknown tool — return an error so the model can recover
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Error: Unknown tool '{block.name}'.",
                    "is_error": True,
                })
                logger.warning("Unknown tool called: %s", block.name)

    return tool_results, tools_used


def _extract_text(response_content: list) -> str:
    """Extract all text content from a response's content blocks."""
    parts = []
    for block in response_content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Non-streaming response
# ---------------------------------------------------------------------------

async def get_ai_response(
    system_prompt: str,
    messages: list[dict],
    knowledge_base: KnowledgeBase,
    model: str | None = None,
) -> dict:
    """
    Send messages to the Anthropic API and handle tool calls.

    Runs a loop: call API → if tool_use, process tools, append results,
    call again → repeat until end_turn or safety limit reached.

    Args:
        system_prompt: The full system prompt (core KB + reference index).
        messages: The complete messages array (case data + history + new message).
        knowledge_base: KnowledgeBase instance for tool call handling.
        model: Model override (defaults to settings.ANTHROPIC_MODEL).

    Returns:
        dict with keys:
            - content (str): The final text response
            - tools_used (list[dict]): Documents retrieved during this turn
            - token_usage (dict): {input_tokens, output_tokens} from final call
            - tool_call_messages (list[dict]): The intermediate tool call messages
              to store in conversation history (assistant tool_use + user tool_result)
    """
    client = get_client()
    model = model or settings.ANTHROPIC_MODEL
    all_tools_used = []
    tool_call_messages = []
    tool_call_count = 0

    # Copy messages so we don't mutate the caller's list
    working_messages = list(messages)

    while True:
        response = await client.messages.create(
            model=model,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=working_messages,
            tools=TOOLS,
        )

        cache_created = getattr(response.usage, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(response.usage, "cache_read_input_tokens", 0) or 0
        logger.info(
            "API call: model=%s, input=%d, output=%d, cache_created=%d, cache_read=%d, stop=%s",
            response.model,
            response.usage.input_tokens,
            response.usage.output_tokens,
            cache_created,
            cache_read,
            response.stop_reason,
        )

        # --- Final text response ---
        if response.stop_reason == "end_turn":
            return {
                "content": _extract_text(response.content),
                "tools_used": all_tools_used,
                "token_usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_creation_input_tokens": cache_created,
                    "cache_read_input_tokens": cache_read,
                },
                "tool_call_messages": tool_call_messages,
            }

        # --- Tool use ---
        if response.stop_reason == "tool_use":
            tool_call_count += 1

            if tool_call_count > settings.MAX_TOOL_CALLS_PER_TURN:
                # Safety limit — force the model to respond with what it has
                logger.warning(
                    "Tool call limit reached (%d). Forcing text response.",
                    settings.MAX_TOOL_CALLS_PER_TURN,
                )
                # Append assistant's response and a nudge to wrap up
                working_messages.append({
                    "role": "assistant",
                    "content": _serialize_content(response.content),
                })
                working_messages.append({
                    "role": "user",
                    "content": (
                        "Maximum reference documents reached for this turn. "
                        "Please provide your response with the information available."
                    ),
                })
                continue

            # Process tool calls
            tool_results, tools_used = _process_tool_calls(
                response.content, knowledge_base
            )
            all_tools_used.extend(tools_used)

            # Append assistant's tool_use message
            serialized_assistant = _serialize_content(response.content)
            working_messages.append({
                "role": "assistant",
                "content": serialized_assistant,
            })

            # Append tool results as a user message
            working_messages.append({
                "role": "user",
                "content": tool_results,
            })

            # Track these intermediate messages for conversation storage
            tool_call_messages.append({
                "role": "assistant",
                "content": serialized_assistant,
            })
            tool_call_messages.append({
                "role": "user",
                "content": tool_results,
            })

            continue

        # --- Unexpected stop reason ---
        logger.warning("Unexpected stop_reason: %s", response.stop_reason)
        return {
            "content": _extract_text(response.content) or "[No response generated]",
            "tools_used": all_tools_used,
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_creation_input_tokens": cache_created,
                "cache_read_input_tokens": cache_read,
            },
            "tool_call_messages": tool_call_messages,
        }


# ---------------------------------------------------------------------------
# Streaming response
# ---------------------------------------------------------------------------

async def get_ai_response_streaming(
    system_prompt: str,
    messages: list[dict],
    knowledge_base: KnowledgeBase,
    model: str | None = None,
) -> AsyncGenerator[dict, None]:
    """
    Stream a response from the Anthropic API, handling tool calls.

    Yields event dicts that the conversation router converts to SSE:
        {"type": "content_delta", "text": "..."}
        {"type": "tool_use", "tool": "...", "document_id": "..."}
        {"type": "done", "content": "...", "tools_used": [...], "token_usage": {...},
         "tool_call_messages": [...]}

    Strategy for tool calls during streaming:
        1. Stream the API call, yielding text chunks as they arrive
        2. After the stream completes, check the final message's stop_reason
        3. If tool_use: process tools silently, then stream the next API call
        4. Repeat until end_turn
        5. Yield a final "done" event with metadata

    This means the user sees text flowing, a brief pause during tool
    processing, then more text. Good UX for the investigation workflow.
    """
    client = get_client()
    model = model or settings.ANTHROPIC_MODEL
    all_tools_used = []
    tool_call_messages = []
    tool_call_count = 0
    full_text = ""

    # Copy messages so we don't mutate the caller's list
    working_messages = list(messages)

    while True:
        # Stream the API call
        async with client.messages.stream(
            model=model,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=working_messages,
            tools=TOOLS,
        ) as stream:
            # Yield text chunks as they arrive
            async for text in stream.text_stream:
                full_text += text
                yield {"type": "content_delta", "text": text}

            # Get the accumulated final message
            final_message = await stream.get_final_message()

        cache_created = getattr(final_message.usage, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(final_message.usage, "cache_read_input_tokens", 0) or 0
        logger.info(
            "Streaming API call: model=%s, input=%d, output=%d, cache_created=%d, cache_read=%d, stop=%s",
            final_message.model,
            final_message.usage.input_tokens,
            final_message.usage.output_tokens,
            cache_created,
            cache_read,
            final_message.stop_reason,
        )

        # --- Final response (no more tool calls) ---
        if final_message.stop_reason == "end_turn":
            yield {
                "type": "done",
                "content": full_text,
                "tools_used": all_tools_used,
                "token_usage": {
                    "input_tokens": final_message.usage.input_tokens,
                    "output_tokens": final_message.usage.output_tokens,
                    "cache_creation_input_tokens": cache_created,
                    "cache_read_input_tokens": cache_read,
                },
                "tool_call_messages": tool_call_messages,
            }
            return

        # --- Tool use: process tools and loop ---
        if final_message.stop_reason == "tool_use":
            tool_call_count += 1

            if tool_call_count > settings.MAX_TOOL_CALLS_PER_TURN:
                logger.warning(
                    "Tool call limit reached (%d) during streaming.",
                    settings.MAX_TOOL_CALLS_PER_TURN,
                )
                working_messages.append({
                    "role": "assistant",
                    "content": _serialize_content(final_message.content),
                })
                working_messages.append({
                    "role": "user",
                    "content": (
                        "Maximum reference documents reached for this turn. "
                        "Please provide your response with the information available."
                    ),
                })
                # Reset full_text for the final forced response
                full_text = ""
                continue

            # Process tool calls
            tool_results, tools_used = _process_tool_calls(
                final_message.content, knowledge_base
            )
            all_tools_used.extend(tools_used)

            # Notify the frontend about tool usage
            for tool_info in tools_used:
                yield {
                    "type": "tool_use",
                    "tool": tool_info["tool"],
                    "document_id": tool_info["document_id"],
                    "document_title": tool_info["document_title"],
                }

            # Append to working messages for the next API call
            serialized_assistant = _serialize_content(final_message.content)
            working_messages.append({
                "role": "assistant",
                "content": serialized_assistant,
            })
            working_messages.append({
                "role": "user",
                "content": tool_results,
            })

            # Track for conversation storage
            tool_call_messages.append({
                "role": "assistant",
                "content": serialized_assistant,
            })
            tool_call_messages.append({
                "role": "user",
                "content": tool_results,
            })

            # Reset full_text — the next streamed response is the continuation
            # We keep accumulated text from earlier in the turn since the model
            # may have produced text before the tool call
            full_text = ""

            continue

        # --- Unexpected stop reason ---
        logger.warning(
            "Unexpected stop_reason during streaming: %s",
            final_message.stop_reason,
        )
        yield {
            "type": "done",
            "content": full_text or "[No response generated]",
            "tools_used": all_tools_used,
            "token_usage": {
                "input_tokens": final_message.usage.input_tokens,
                "output_tokens": final_message.usage.output_tokens,
            },
            "tool_call_messages": tool_call_messages,
        }
        return


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize_content(content_blocks: list) -> list[dict]:
    """
    Serialize Anthropic SDK content blocks to plain dicts for
    inclusion in the messages array on subsequent API calls.

    The SDK returns typed objects (TextBlock, ToolUseBlock, etc.)
    but the API expects plain dicts when you send them back.
    """
    serialized = []
    for block in content_blocks:
        if block.type == "text":
            serialized.append({
                "type": "text",
                "text": block.text,
            })
        elif block.type == "tool_use":
            serialized.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
        else:
            # Pass through any other block types as-is
            logger.warning("Unknown content block type: %s", block.type)
            if hasattr(block, "model_dump"):
                serialized.append(block.model_dump())
    return serialized


def build_image_content_block(base64_data: str, media_type: str) -> dict:
    """
    Build an Anthropic API image content block from base64 data.

    Args:
        base64_data: The base64-encoded image data.
        media_type: MIME type (e.g., "image/jpeg", "image/png").

    Returns:
        Dict suitable for inclusion in a message's content array.
    """
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64_data,
        }
    }


def build_user_message_content(
    text: str,
    images: list[dict] | None = None,
) -> list[dict] | str:
    """
    Build the content for a user message, handling text-only and
    text-with-images cases.

    Args:
        text: The user's message text.
        images: Optional list of {"base64": "...", "media_type": "..."} dicts.

    Returns:
        Either a plain string (text only) or a list of content blocks
        (text + images). The Anthropic API accepts both formats.
    """
    if not images:
        return text

    content = []
    # Images first, then text (Anthropic recommends images before text)
    for img in images:
        content.append(build_image_content_block(
            base64_data=img["base64"],
            media_type=img["media_type"],
        ))
    content.append({"type": "text", "text": text or "Describe this image."})

    return content