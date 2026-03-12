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

TOOL_SIGNAL_STEP_COMPLETE = {
    "name": "signal_step_complete",
    "description": (
        "Signal that you have completed all sections and blocks in the "
        "current investigation step. Call this tool ONLY when you have "
        "finished producing all ICR-ready text for every section covered "
        "by your current step document. After calling this tool, stop — "
        "do not proceed to the next block or step. The investigator will "
        "review your work and advance when ready."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": (
                    "Brief summary of what was completed in this step "
                    "(e.g., 'Block 1 complete: Phase 0 + Steps 1-6')"
                )
            }
        },
        "required": ["summary"]
    }
}

TOOL_GET_REFERENCE_DOCUMENT = {
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
}

TOOL_GET_PROMPT = {
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
}

TOOL_SIGNAL_READY_TO_EXECUTE = {
    "name": "signal_ready_to_execute",
    "description": (
        "Signal that you have reviewed all case data, asked any necessary "
        "clarifying questions, and are confident you have sufficient "
        "information to produce the complete ICR in autopilot mode. Call "
        "this ONLY when you assess >= 95% confidence that all required "
        "data is available and unambiguous. The investigator will then "
        "trigger the full ICR execution."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "assessment": {
                "type": "string",
                "description": (
                    "Brief assessment of data completeness and any "
                    "remaining minor gaps that will not block the ICR"
                )
            }
        },
        "required": ["assessment"]
    }
}

# Tool sets for different modes
TOOLS = [TOOL_SIGNAL_STEP_COMPLETE, TOOL_GET_REFERENCE_DOCUMENT, TOOL_GET_PROMPT]
TOOLS_ONESHOT_SETUP = [TOOL_SIGNAL_READY_TO_EXECUTE, TOOL_GET_REFERENCE_DOCUMENT]
TOOLS_ONESHOT_EXECUTE = [TOOL_GET_REFERENCE_DOCUMENT]


# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    """Get or create the async Anthropic client singleton."""
    global _client
    if _client is None:
        kwargs = {
            "api_key": settings.ANTHROPIC_API_KEY,
            "max_retries": 3,  # Auto-retries 429s with exponential backoff
        }
        if settings.ANTHROPIC_BASE_URL:
            kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
        _client = AsyncAnthropic(**kwargs)
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
            if block.name == "signal_step_complete":
                summary = block.input.get("summary", "")
                # Not added to tools_used — it's not a document reference
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": (
                        "Step completion acknowledged. The investigator has been notified. "
                        "Do not proceed to the next block or step. Wait for the investigator "
                        "to advance."
                    ),
                })
                logger.info("Tool call: signal_step_complete — %s", summary)
            elif block.name == "signal_ready_to_execute":
                assessment = block.input.get("assessment", "")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": (
                        "Readiness acknowledged. The investigator has been notified and "
                        "can now trigger the full ICR execution. Wait for the investigator "
                        "to proceed. Do not begin producing ICR text."
                    ),
                })
                logger.info("Tool call: signal_ready_to_execute — %s", assessment)
            elif block.name == "get_reference_document":
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
    tools: list[dict] | None = None,
    max_tokens: int | None = None,
    thinking: dict | None = None,
    auto_continue: bool = False,
    continuation_thinking_budget: int | None = None,
    max_continuations: int | None = None,
) -> AsyncGenerator[dict, None]:
    """
    Stream a response from the Anthropic API, handling tool calls.

    Yields event dicts that the conversation router converts to SSE:
        {"type": "content_delta", "text": "..."}
        {"type": "tool_use", "tool": "...", "document_id": "..."}
        {"type": "done", "content": "...", "tools_used": [...], "token_usage": {...},
         "tool_call_messages": [...]}

    Optional overrides:
        tools: Custom tool set (defaults to TOOLS).
        max_tokens: Override max tokens (defaults to settings.ANTHROPIC_MAX_TOKENS).
        thinking: Extended thinking config, e.g. {"type": "enabled", "budget_tokens": 10000}.
    """
    client = get_client()
    model = model or settings.ANTHROPIC_MODEL
    active_tools = tools if tools is not None else TOOLS
    active_max_tokens = max_tokens or settings.ANTHROPIC_MAX_TOKENS
    all_tools_used = []
    tool_call_messages = []
    tool_call_count = 0
    full_text = ""
    full_thinking = ""

    # Auto-continuation state
    continuation_count = 0
    max_cont = max_continuations or settings.ONESHOT_MAX_CONTINUATIONS
    cont_thinking_budget = continuation_thinking_budget or settings.ONESHOT_CONTINUATION_THINKING_BUDGET

    # Token usage accumulated across all API calls (tool loops + continuations)
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_created = 0
    total_cache_read = 0

    # Text accumulated across continuations (separate from full_text which resets)
    total_text = ""

    # Copy messages so we don't mutate the caller's list
    working_messages = list(messages)

    while True:
        # Build API call params
        api_params = {
            "model": model,
            "max_tokens": active_max_tokens,
            "system": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            "messages": working_messages,
            "tools": active_tools,
        }
        if thinking:
            api_params["thinking"] = thinking

        # Stream the API call
        async with client.messages.stream(**api_params) as stream:
            # Yield text and thinking chunks as they arrive
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    if chunk.delta.type == "text_delta":
                        full_text += chunk.delta.text
                        yield {"type": "content_delta", "text": chunk.delta.text}
                    elif chunk.delta.type == "thinking_delta":
                        full_thinking += chunk.delta.thinking
                        yield {"type": "thinking_delta", "text": chunk.delta.thinking}

            # Get the accumulated final message
            final_message = await stream.get_final_message()

        cache_created = getattr(final_message.usage, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(final_message.usage, "cache_read_input_tokens", 0) or 0
        total_input_tokens += final_message.usage.input_tokens
        total_output_tokens += final_message.usage.output_tokens
        total_cache_created += cache_created
        total_cache_read += cache_read

        logger.info(
            "Streaming API call: model=%s, input=%d, output=%d, cache_created=%d, cache_read=%d, stop=%s, continuation=%d",
            final_message.model,
            final_message.usage.input_tokens,
            final_message.usage.output_tokens,
            cache_created,
            cache_read,
            final_message.stop_reason,
            continuation_count,
        )

        # --- Final response (no more tool calls) ---
        if final_message.stop_reason == "end_turn":
            done_event = {
                "type": "done",
                "content": total_text + full_text,
                "tools_used": all_tools_used,
                "token_usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "cache_creation_input_tokens": total_cache_created,
                    "cache_read_input_tokens": total_cache_read,
                },
                "tool_call_messages": tool_call_messages,
            }
            if full_thinking:
                done_event["thinking_content"] = full_thinking
            yield done_event
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

            # Check for signal tools (emitted separately, not stored as tools_used)
            for block in final_message.content:
                if block.type == "tool_use" and block.name == "signal_step_complete":
                    yield {
                        "type": "tool_use",
                        "tool": "signal_step_complete",
                        "document_id": None,
                        "document_title": block.input.get("summary", ""),
                    }
                elif block.type == "tool_use" and block.name == "signal_ready_to_execute":
                    yield {
                        "type": "tool_use",
                        "tool": "signal_ready_to_execute",
                        "document_id": None,
                        "document_title": block.input.get("assessment", ""),
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

        # --- Truncation: any stop reason that isn't end_turn or tool_use ---
        stop_reason = final_message.stop_reason or "none"

        # Auto-continue if enabled, under the retry cap, and we have content
        if auto_continue and continuation_count < max_cont and full_text:
            continuation_count += 1
            logger.info(
                "Auto-continuation %d/%d (stop_reason=%s, output_so_far=%d chars)",
                continuation_count, max_cont, stop_reason,
                len(total_text) + len(full_text),
            )

            # Emit continuation marker for frontend visibility
            yield {
                "type": "continuation",
                "attempt": continuation_count,
                "max_attempts": max_cont,
                "reason": str(stop_reason),
            }

            # Serialize partial response and append to working_messages
            serialized_assistant = _serialize_content(final_message.content)
            working_messages.append({
                "role": "assistant",
                "content": serialized_assistant,
            })

            # Continuation instruction with tail context
            last_chars = full_text[-200:] if len(full_text) > 200 else full_text
            working_messages.append({
                "role": "user",
                "content": (
                    "Your previous response was cut off. Continue exactly where you "
                    "left off. Do not repeat any content already produced. Pick up "
                    f"mid-sentence if needed.\n\nYour last output ended with:\n{last_chars}"
                ),
            })

            # Reduce thinking budget for continuation calls
            if thinking:
                thinking = {
                    "type": "enabled",
                    "budget_tokens": cont_thinking_budget,
                }

            # Carry text to total, reset for next segment
            total_text += full_text
            full_text = ""
            # full_thinking is NOT reset — accumulates across everything

            continue  # Back to while True

        # Auto-continue exhausted or disabled — emit truncated done
        logger.warning(
            "Response truncated: stop_reason=%s, continuations=%d/%d, total_output=%d chars",
            stop_reason, continuation_count, max_cont,
            len(total_text) + len(full_text),
        )
        done_event = {
            "type": "done",
            "content": (total_text + full_text) or "[No response generated]",
            "tools_used": all_tools_used,
            "token_usage": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cache_creation_input_tokens": total_cache_created,
                "cache_read_input_tokens": total_cache_read,
            },
            "tool_call_messages": tool_call_messages,
            "truncated": True,  # ALWAYS mark non-end_turn as truncated
        }
        if full_thinking:
            done_event["thinking_content"] = full_thinking
        yield done_event
        return


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize_content(content_blocks: list) -> list[dict]:
    """
    Serialize Anthropic SDK content blocks to plain dicts for
    inclusion in the messages array on subsequent API calls.

    The SDK returns typed objects (TextBlock, ToolUseBlock, ThinkingBlock, etc.)
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
        elif block.type == "thinking":
            serialized.append({
                "type": "thinking",
                "thinking": block.thinking,
                "signature": block.signature,
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