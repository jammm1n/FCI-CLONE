# Rolling Conversation Summarization — Implementation Specification

**Date:** 5 March 2026
**Status:** Ready for implementation
**Purpose:** Reduce context window usage and API latency by summarizing older conversation history before each API call, using token-based triggers rather than message counts.

---

## 1. Problem Statement

The current architecture sends the full system prompt (~45-50K tokens), case data (~10-15K tokens), and the **entire conversation history** with every API call. The conversation history grows unboundedly and includes:

- Large AI responses (2,000-4,000+ tokens each — intentionally verbose with rationale, QC checks, and structured analysis)
- Tool exchange messages containing **full reference documents** (4,000-15,000 tokens each) that persist in every subsequent API call
- User messages (often short — "ok", "continue", "confirmed")

A typical case investigation may have only 5-10 user messages, but the AI responses and retrieved SOPs can push the total payload to 140-160K tokens. This causes:

1. **Severe latency** — response times degrade noticeably as context grows
2. **Context window pressure** — approaching the 200K limit risks quality degradation
3. **Unnecessary cost** — cached system prompt is cheap, but conversation history tokens are billed at full price on every call

The worst offender is tool exchange messages: when the AI retrieves an 8,000-token SOP in turn 3, that document is re-sent in turns 4, 5, 6, ... N for the rest of the conversation, even though its content has already been applied.

---

## 2. Solution: Token-Budget Rolling Summarization

Before each API call, estimate the total payload size. If it exceeds a configurable budget, use Opus to summarize older messages into a structured recap. Keep recent messages verbatim. The summary replaces old messages in the API payload only — all original messages remain in MongoDB for UI display and PDF export.

### 2.1 Key Principles

- **Token-based triggers, not message-based.** A 5-message conversation with massive AI responses and two SOP retrievals can easily exceed 60K of history. A 20-message free chat with short answers might only be 15K. The trigger must measure actual content size.
- **Nothing is deleted.** The summary is metadata that controls API payload assembly. All original messages stay in the database. The UI and PDF export are unaffected.
- **Incremental summarization.** Each summary builds on the previous one rather than reprocessing the entire conversation from scratch.
- **Invisible to the user.** No UI changes. No buttons. No notifications. The investigator sees the same continuous chat. Only the AI's working memory changes.
- **Backward compatible.** Existing conversations without a `rolling_summary` field work exactly as they do today — all messages sent to the API.

---

## 3. Configuration

Add to `server/config.py` (Settings class):

```python
# Rolling summarization
CONTEXT_TOKEN_BUDGET: int = 100_000       # Trigger summarization when total payload estimate exceeds this
RECENT_CONTEXT_BUDGET: int = 15_000       # Token budget reserved for recent verbatim messages
SUMMARIZATION_MODEL: str = "claude-opus-4-6"  # Model used for generating summaries
SUMMARIZATION_MAX_TOKENS: int = 3000      # Max output tokens for the summary response
```

### 3.1 Tuning Rationale

| Setting | Value | Rationale |
|---------|-------|-----------|
| `CONTEXT_TOKEN_BUDGET` | 100,000 | The context window is 200K. Triggering at 100K leaves ample room for the AI's response and any tool calls. Conservative but safe. |
| `RECENT_CONTEXT_BUDGET` | 15,000 | Preserves roughly 3-5 recent exchanges verbatim (given large AI responses). The AI needs enough recent context to maintain conversational coherence. |
| `SUMMARIZATION_MODEL` | `claude-opus-4-6` | Summary quality is critical — if the summary misses an important finding, the AI loses access to it. Opus is the right choice for this. |
| `SUMMARIZATION_MAX_TOKENS` | 3,000 | A well-structured summary of a partial investigation should fit in 2,000-3,000 tokens. This caps the summary's own contribution to context. |

---

## 4. MongoDB Schema Change

Add `rolling_summary` field to the conversation document. This is optional — existing documents without it continue to work unchanged.

```json
{
  "_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "user_id": "user_001",
  "mode": "case",
  "title": "",
  "status": "active",
  "rolling_summary": {
    "content": "## Conversation Summary\n\n### Case Classification\nFraud / scam case...\n\n### Key Findings\n- Transaction analysis revealed...\n...",
    "summarized_through_index": 8,
    "model": "claude-opus-4-6",
    "token_estimate": 2400,
    "created_at": "2026-03-05T10:30:00Z"
  },
  "messages": [
    /* ALL messages remain — nothing deleted */
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

### 4.1 Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `rolling_summary.content` | string | The structured summary text, injected into the API payload as a user message |
| `rolling_summary.summarized_through_index` | int | The index (0-based) into the `messages` array of the last message included in this summary. Messages after this index are sent verbatim. |
| `rolling_summary.model` | string | Model that generated the summary (for audit) |
| `rolling_summary.token_estimate` | int | Estimated token count of the summary content (for budget calculations) |
| `rolling_summary.created_at` | datetime | When the summary was generated |

### 4.2 Why `summarized_through_index` Instead of `message_id`

Using the array index is simpler and faster — no need to search through messages to find the boundary. Messages are append-only (never reordered or deleted mid-array), so the index is stable. When rebuilding API messages, the code splits the array: `messages[0:boundary]` are summarized, `messages[boundary+1:]` are sent verbatim.

---

## 5. Implementation: conversation_manager.py

### 5.1 New Helper: `_estimate_tokens()`

```python
def _estimate_tokens(text: str) -> int:
    """
    Rough token estimate. 1 token ≈ 4 characters for English text.
    Intentionally conservative (slightly overestimates) to avoid
    triggering summarization too late.
    """
    if isinstance(text, str):
        return len(text) // 3  # Slightly aggressive to catch large payloads early
    if isinstance(text, list):
        # Content blocks (tool results, image messages)
        total = 0
        for block in text:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    total += len(block.get("text", "")) // 3
                elif block.get("type") == "tool_result":
                    content = block.get("content", "")
                    total += len(content) // 3 if isinstance(content, str) else 500
                elif block.get("type") == "image":
                    total += 1000  # Images have a rough fixed token cost
                else:
                    total += len(str(block)) // 3
            elif isinstance(block, str):
                total += len(block) // 3
        return total
    return 0
```

**Note on `// 3` vs `// 4`:** Using `// 3` (≈3 chars per token) is intentionally conservative. It's better to trigger summarization slightly early than slightly late. The cost of a premature summary is one extra Opus call (~$0.10); the cost of a late summary is a degraded or failed API call.

### 5.2 New Helper: `_estimate_messages_tokens()`

```python
def _estimate_messages_tokens(stored_messages: list[dict]) -> int:
    """Estimate total token count for a list of stored messages."""
    total = 0
    for msg in stored_messages:
        total += _estimate_tokens(msg.get("content", ""))
        # Tool exchanges can have list content (tool results with full SOP text)
        if msg.get("role") == "tool_exchange" and isinstance(msg.get("content"), list):
            total += _estimate_tokens(msg["content"])
    return total
```

### 5.3 New Method: `_maybe_summarize()`

This is the core logic. Called before `_rebuild_api_messages()` in both `send_message()` and `send_message_streaming()`.

```python
async def _maybe_summarize(
    conversation_id: str,
    conversation: dict,
    system_prompt: str,
) -> dict:
    """
    Check if the conversation needs summarization. If so, generate a
    summary of older messages and store it in the conversation document.

    Returns the (potentially updated) conversation document.

    The decision flow:
    1. Estimate total payload: system_prompt + case_data + all messages
    2. If total < CONTEXT_TOKEN_BUDGET: return unchanged (no summarization needed)
    3. Walk backward from newest message, accumulating tokens
    4. When accumulated tokens exceed RECENT_CONTEXT_BUDGET, mark the boundary
    5. Everything before the boundary gets summarized
    6. Call Opus to generate the summary
    7. Store the summary in the conversation document
    8. Return the updated conversation

    If the conversation already has a rolling_summary, the new summary
    is incremental: Opus receives the previous summary + messages since
    that summary, and produces an updated summary.
    """
    messages = conversation.get("messages", [])
    if not messages:
        return conversation

    # Step 1: Estimate total payload size
    system_tokens = _estimate_tokens(system_prompt)
    messages_tokens = _estimate_messages_tokens(messages)
    existing_summary = conversation.get("rolling_summary")
    summary_tokens = existing_summary["token_estimate"] if existing_summary else 0

    # If we already have a summary, the effective message tokens are:
    # summary + messages after the summary boundary
    if existing_summary:
        boundary = existing_summary["summarized_through_index"] + 1
        recent_messages = messages[boundary:]
        effective_messages_tokens = summary_tokens + _estimate_messages_tokens(recent_messages)
    else:
        effective_messages_tokens = messages_tokens

    total_estimate = system_tokens + effective_messages_tokens

    if total_estimate < settings.CONTEXT_TOKEN_BUDGET:
        return conversation  # No summarization needed

    logger.info(
        "Conversation %s estimated at %d tokens (budget: %d). Triggering summarization.",
        conversation_id, total_estimate, settings.CONTEXT_TOKEN_BUDGET,
    )

    # Step 2: Find the boundary — walk backward, keeping recent messages
    # that fit within RECENT_CONTEXT_BUDGET
    recent_tokens = 0
    boundary_index = len(messages) - 1  # Start from the end

    for i in range(len(messages) - 1, -1, -1):
        msg_tokens = _estimate_tokens(messages[i].get("content", ""))
        if messages[i].get("role") == "tool_exchange":
            msg_tokens += _estimate_tokens(messages[i].get("content", ""))

        if recent_tokens + msg_tokens > settings.RECENT_CONTEXT_BUDGET:
            boundary_index = i
            break
        recent_tokens += msg_tokens
    else:
        # All messages fit within recent budget — shouldn't normally happen
        # if we triggered summarization, but handle gracefully
        return conversation

    # Ensure we don't re-summarize already-summarized messages
    if existing_summary:
        old_boundary = existing_summary["summarized_through_index"]
        if boundary_index <= old_boundary:
            # Nothing new to summarize — the growth is in recent messages
            # This can happen if a single recent exchange is very large
            logger.info("No new messages to summarize beyond existing summary.")
            return conversation
        # Only summarize messages between old boundary and new boundary
        messages_to_summarize = messages[old_boundary + 1:boundary_index + 1]
        previous_summary_content = existing_summary["content"]
    else:
        messages_to_summarize = messages[:boundary_index + 1]
        previous_summary_content = None

    if not messages_to_summarize:
        return conversation

    # Step 3: Build the summarization prompt
    summary_input = _build_summarization_input(
        messages_to_summarize,
        previous_summary_content,
    )

    # Step 4: Call Opus for summarization (non-streaming, dedicated call)
    from server.services.ai_client import get_client
    client = get_client()

    summary_response = await client.messages.create(
        model=settings.SUMMARIZATION_MODEL,
        max_tokens=settings.SUMMARIZATION_MAX_TOKENS,
        system=[{
            "type": "text",
            "text": SUMMARIZATION_SYSTEM_PROMPT,
        }],
        messages=[{
            "role": "user",
            "content": summary_input,
        }],
    )

    summary_content = ""
    for block in summary_response.content:
        if hasattr(block, "text"):
            summary_content += block.text

    summary_token_estimate = _estimate_tokens(summary_content)

    logger.info(
        "Generated summary for conversation %s: %d tokens (summarized through index %d, "
        "covering %d messages). Model: %s, input: %d, output: %d",
        conversation_id,
        summary_token_estimate,
        boundary_index,
        len(messages_to_summarize),
        settings.SUMMARIZATION_MODEL,
        summary_response.usage.input_tokens,
        summary_response.usage.output_tokens,
    )

    # Step 5: Store the summary
    db = get_database()
    rolling_summary = {
        "content": summary_content,
        "summarized_through_index": boundary_index,
        "model": settings.SUMMARIZATION_MODEL,
        "token_estimate": summary_token_estimate,
        "created_at": _now(),
    }

    await db.conversations.update_one(
        {"_id": conversation_id},
        {"$set": {"rolling_summary": rolling_summary}},
    )

    # Update the in-memory conversation object
    conversation["rolling_summary"] = rolling_summary
    return conversation
```

### 5.4 Summarization Prompt

This is a module-level constant in `conversation_manager.py`:

```python
SUMMARIZATION_SYSTEM_PROMPT = """You are summarizing an ongoing financial crime investigation conversation. Your summary will replace the older messages in the AI assistant's context window. The assistant will NOT have access to the original messages — only this summary and the most recent messages.

Your summary must preserve all information that the assistant would need to continue the investigation seamlessly:

MUST PRESERVE:
- All factual findings: transaction amounts, dates, addresses, counterparties, risk indicators, patterns identified
- All decisions made and their rationale (case classification, risk level, escalation decisions)
- Key conclusions drawn from any reference documents (SOPs, decision matrix rules) that were consulted — the specific rules or criteria that were applied and the outcome
- The current investigation phase and what steps have been completed
- Any open questions, flags, or items deferred for later investigation steps
- Any instructions or preferences the investigator has stated
- KYC verification results and any identity discrepancies
- Specific numerical thresholds or values that informed decisions

MUST NOT PRESERVE:
- The full text of retrieved reference documents or SOPs — only the relevant findings and rules that were applied
- Conversational filler, pleasantries, or acknowledgments
- Redundant restatements of the original case data (the assistant always has the full case data separately)
- The step-by-step reasoning process if the conclusion is clear — preserve the conclusion and key supporting evidence

FORMAT:
Use markdown with clear sections. Be thorough but concise. A typical summary should be 800-2,000 tokens. If the investigation is complex with many findings, up to 3,000 tokens is acceptable.

Structure your summary as:
## Investigation Progress Summary

### Current Phase
[Where the investigation stands — which steps completed, what's next]

### Case Classification & Risk Assessment
[Current classification, risk level, any changes from initial assessment]

### Key Findings
[Bullet points: the most important facts discovered, organized by topic]

### Decisions & Rationale
[What has been decided and why — including any SOP rules or decision matrix entries applied]

### Reference Documents Consulted
[Which documents were retrieved, and the specific guidance that was applied from each]

### Open Items
[Anything flagged for later, unresolved questions, pending actions]

### Investigator Directives
[Any specific instructions or preferences the investigator has communicated]"""
```

### 5.5 New Helper: `_build_summarization_input()`

```python
def _build_summarization_input(
    messages_to_summarize: list[dict],
    previous_summary: str | None,
) -> str:
    """
    Build the user message content for the summarization API call.

    If there's a previous summary, include it so Opus can build
    incrementally rather than from scratch.
    """
    parts = []

    if previous_summary:
        parts.append("## EXISTING SUMMARY (from earlier in this conversation)")
        parts.append("")
        parts.append(previous_summary)
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append("## NEW MESSAGES TO INCORPORATE INTO THE SUMMARY")
        parts.append("Update the existing summary to incorporate the following new messages. "
                      "Merge new findings into the appropriate sections. Remove any items from "
                      "'Open Items' that have been resolved.")
    else:
        parts.append("## MESSAGES TO SUMMARIZE")
        parts.append("Create a structured summary of the following conversation messages.")

    parts.append("")

    for msg in messages_to_summarize:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")

        # Map internal roles to readable labels
        role_label = {
            "system_injected": "SYSTEM (case data injection)",
            "user": "INVESTIGATOR",
            "assistant": "AI ASSISTANT",
            "tool_exchange": "TOOL EXCHANGE",
        }.get(role, role.upper())

        # For tool exchanges, flag what they contain
        if role == "tool_exchange":
            original_role = msg.get("original_role", "unknown")
            if original_role == "assistant":
                role_label = "AI ASSISTANT (tool call request)"
            else:
                role_label = "TOOL RESULT (reference document content)"

        # Serialize content
        if isinstance(content, list):
            # Tool results or image blocks
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "tool_result":
                        text_parts.append(f"[Tool result for {block.get('tool_use_id', 'unknown')}]: {block.get('content', '')[:2000]}...")
                    elif block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        text_parts.append(f"[Tool call: {block.get('name', 'unknown')}({block.get('input', {})})]")
                    elif block.get("type") == "image":
                        text_parts.append("[Image uploaded by investigator]")
                    else:
                        text_parts.append(str(block))
            content_str = "\n".join(text_parts)
        else:
            content_str = str(content)

        parts.append(f"**[{role_label}]**")
        parts.append(content_str)
        parts.append("")

    return "\n".join(parts)
```

### 5.6 Modified: `_rebuild_api_messages()`

The existing function signature changes to accept the optional rolling summary:

```python
def _rebuild_api_messages(
    stored_messages: list[dict],
    rolling_summary: dict | None = None,
) -> list[dict]:
    """
    Rebuild the Anthropic API messages array from stored conversation history.

    If a rolling_summary is provided, messages up to and including
    summarized_through_index are replaced with the summary text.
    Messages after that index are included verbatim as today.

    The summary is injected as a user message at the start of the
    conversation (after any system_injected case data message that
    might exist in the recent messages).
    """
    api_messages = []

    if rolling_summary:
        boundary = rolling_summary["summarized_through_index"]

        # Inject the summary as the first message (role: user)
        # This comes after the system prompt (which is separate)
        # but before any recent messages
        api_messages.append({
            "role": "user",
            "content": (
                "[CONVERSATION SUMMARY — Earlier messages in this investigation "
                "have been summarized. The original case data is provided separately. "
                "This summary covers the investigation progress so far.]\n\n"
                + rolling_summary["content"]
            ),
        })
        # Need a brief assistant acknowledgment to maintain valid
        # user/assistant alternation
        api_messages.append({
            "role": "assistant",
            "content": "Understood. I have the investigation context from the summary and will continue from here.",
        })

        # Only process messages after the boundary
        messages_to_process = stored_messages[boundary + 1:]
    else:
        messages_to_process = stored_messages

    # Original _rebuild_api_messages logic applied to messages_to_process
    for msg in messages_to_process:
        role = msg["role"]

        if role == "system_injected":
            api_messages.append({
                "role": "user",
                "content": msg["content"],
            })

        elif role == "user":
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
```

### 5.7 Modified: `send_message()` (non-streaming)

Changes at lines 205-230 of the current file. Add the summarization check between retrieving the conversation and rebuilding messages:

```python
async def send_message(
    conversation_id: str,
    content: str,
    knowledge_base: KnowledgeBase,
    images: list[dict] | None = None,
) -> dict:
    db = get_database()

    # 1. Retrieve conversation
    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    # 2. Check if summarization is needed (NEW)
    system_prompt = knowledge_base.get_system_prompt()
    conversation = await _maybe_summarize(conversation_id, conversation, system_prompt)

    # 3. Rebuild API messages from history (MODIFIED — pass rolling_summary)
    api_messages = _rebuild_api_messages(
        conversation["messages"],
        rolling_summary=conversation.get("rolling_summary"),
    )

    # ... rest of function unchanged ...
```

### 5.8 Modified: `send_message_streaming()`

Same pattern — add the summarization check at lines 321-329 of the current file:

```python
async def send_message_streaming(
    conversation_id: str,
    content: str,
    knowledge_base: KnowledgeBase,
    images: list[dict] | None = None,
    is_initial_assessment: bool = False,
):
    db = get_database()

    conversation = await db.conversations.find_one({"_id": conversation_id})
    if conversation is None:
        raise ValueError(f"Conversation not found: {conversation_id}")

    # Check if summarization is needed (NEW)
    system_prompt = knowledge_base.get_system_prompt()
    conversation = await _maybe_summarize(conversation_id, conversation, system_prompt)

    # Rebuild API messages (MODIFIED — pass rolling_summary)
    api_messages = _rebuild_api_messages(
        conversation["messages"],
        rolling_summary=conversation.get("rolling_summary"),
    )

    # ... rest of function unchanged ...
```

---

## 6. Files Changed

| File | Change | Lines Affected |
|------|--------|----------------|
| `server/config.py` | Add 4 new settings | 4 new lines (after line 27) |
| `server/services/conversation_manager.py` | Add `_estimate_tokens()`, `_estimate_messages_tokens()`, `_maybe_summarize()`, `_build_summarization_input()`, `SUMMARIZATION_SYSTEM_PROMPT` constant. Modify `_rebuild_api_messages()` signature and logic. Modify `send_message()` and `send_message_streaming()` to call `_maybe_summarize()`. | ~200 new lines, ~15 modified lines |
| **No other files changed** | Router, AI client, schemas, frontend — all unchanged | — |

### 6.1 Files NOT Changed (and Why)

| File | Why No Change |
|------|---------------|
| `server/services/ai_client.py` | Already accepts `model` parameter. The summarization call uses the Anthropic client directly (simple one-shot call, no tool loop needed). |
| `server/routers/conversations.py` | The router calls `conversation_manager.send_message_streaming()` — summarization happens inside the manager, invisible to the router. |
| `server/models/schemas.py` | The `rolling_summary` field is stored directly in MongoDB as a dict. No Pydantic model needed — it's internal state, never exposed via API. |
| `client/src/**` | No frontend changes whatsoever. The UI still shows all messages. Summarization only affects what gets sent to the Anthropic API. |

---

## 7. API Payload Assembly — Before and After

### 7.1 Before (Current — No Summarization)

```
[System prompt: 45-50K tokens — cached]
[Message 1: system_injected case data — 12K tokens]
[Message 2: assistant initial assessment — 3K tokens]
[Message 3: user "process the CTM alerts" — 20 tokens]
[Message 4: tool_exchange assistant tool_use — 200 tokens]
[Message 5: tool_exchange tool_result (CTM SOP: 7K tokens)]
[Message 6: assistant CTM analysis — 4K tokens]
[Message 7: user "ok, now check elliptic" — 15 tokens]
[Message 8: tool_exchange assistant tool_use — 200 tokens]
[Message 9: tool_exchange tool_result (scam-fraud SOP: 8K tokens)]
[Message 10: assistant elliptic analysis — 3.5K tokens]
[Message 11: user "continue to transaction summary" — 20 tokens]
[Message 12: assistant transaction summary — 4K tokens]
... (continues growing) ...

Total by turn 12: ~82K message tokens + 50K system = ~132K total
```

### 7.2 After (With Rolling Summarization)

If summarization triggers before turn 11:

```
[System prompt: 45-50K tokens — cached]
[Summary message: 2.5K tokens — covers turns 1-10]
[Assistant ack: 20 tokens]
[Message 11: user "continue to transaction summary" — 20 tokens]
[Message 12: assistant transaction summary — 4K tokens]

Total: ~57K total
```

The 7K CTM SOP and 8K scam-fraud SOP are compressed into ~200 tokens of findings within the summary. The full case data is still in the system_injected message if it falls within the recent window, or its key content is captured in the summary if it doesn't.

---

## 8. Edge Cases and Handling

### 8.1 Initial Assessment (First Turn)

The `is_initial_assessment` flow creates a conversation with one `system_injected` message and immediately streams. This is always well within budget (~65K total). Summarization will never trigger on the first turn.

### 8.2 Free Chat Mode

Free chat conversations typically have lighter context (no case data injection, shorter exchanges). Summarization works identically — if a free chat conversation somehow grows large, it gets summarized. In practice, free chat rarely triggers summarization.

### 8.3 Very Large Single Exchange

If a single recent user+assistant exchange exceeds `RECENT_CONTEXT_BUDGET` (e.g., user uploads multiple images and the AI writes a 10K-token response), the boundary logic will keep that exchange verbatim and summarize everything before it. In the extreme case where a single exchange exceeds the total budget, summarization can't help — but this would require a ~100K single response, which is implausible.

### 8.4 Existing Conversations (Migration)

No migration needed. Conversations without `rolling_summary` field are handled by the `if rolling_summary:` check — they fall through to the original behavior. Summarization activates naturally when the conversation grows large enough.

### 8.5 system_injected Message in Summarized Range

When the `system_injected` case data message falls within the summarized range (i.e., it's been summarized along with other early messages), the summary captures its key content. However, the case data is also part of the system prompt context. The summarization prompt explicitly tells Opus not to redundantly restate case data that the assistant already has.

In practice: the `system_injected` message is always the first message (index 0). Once there are enough subsequent messages to trigger summarization, the case data is in the summary's scope. The summary captures any findings derived from the case data, but doesn't repeat the raw data.

### 8.6 Summarization Failure

If the Opus summarization call fails (rate limit, API error, timeout):
- Log the error
- Return the conversation unchanged (no summary stored)
- The current turn proceeds with the full unsummarized context
- Summarization will be retried on the next turn

This is safe because summarization is an optimization, not a requirement. The worst case is the conversation continues with full context for one more turn.

### 8.7 Anthropic API Role Alternation

The Anthropic API requires strict user/assistant role alternation. Injecting the summary as a `user` message followed by an `assistant` acknowledgment maintains this invariant. The subsequent recent messages then continue the alternation naturally.

If the first recent message after the boundary is an `assistant` message, this works because the summary acknowledgment is also `assistant` — but we'd have two consecutive `assistant` messages. To handle this: if the first message after the boundary is `assistant`, omit the acknowledgment message (the summary user message is followed directly by the assistant's actual content).

---

## 9. Observability and Logging

### 9.1 Log Messages

Every summarization event logs:
- Conversation ID
- Total estimated tokens before summarization
- Number of messages summarized
- Boundary index
- Summary token count
- Opus API usage (input/output tokens)
- Whether this was incremental (built on existing summary) or fresh

### 9.2 Token Usage Tracking

The summarization Opus call's token usage is NOT added to the conversation's token_usage tracking (which tracks the investigation AI calls). It's a separate infrastructure cost. Log it for cost monitoring but don't conflate it with the investigation's API usage.

### 9.3 Future: Admin Visibility

Not in this build, but a future admin endpoint could expose:
- Which conversations have rolling summaries
- How many times each conversation has been summarized
- Token savings per conversation (estimated full payload vs actual payload sent)

---

## 10. Testing Plan

### 10.1 Unit Tests

| Test | Validates |
|------|-----------|
| `test_estimate_tokens_string` | Token estimation for plain text (verify ≈ len/3) |
| `test_estimate_tokens_content_blocks` | Token estimation for tool results, image blocks |
| `test_rebuild_with_no_summary` | Existing behavior unchanged when no summary present |
| `test_rebuild_with_summary` | Messages before boundary replaced with summary; messages after boundary verbatim |
| `test_rebuild_role_alternation` | Summary injection maintains valid user/assistant alternation |
| `test_boundary_calculation` | Walking backward from end correctly identifies boundary at RECENT_CONTEXT_BUDGET |
| `test_incremental_summary_input` | Previous summary included in summarization input |
| `test_no_summarize_under_budget` | _maybe_summarize returns unchanged when under CONTEXT_TOKEN_BUDGET |

### 10.2 Integration Tests

| Test | Validates |
|------|-----------|
| `test_full_conversation_with_summarization` | Create conversation, send enough messages to trigger summarization, verify next message uses summary |
| `test_summary_stored_in_mongodb` | After summarization, verify `rolling_summary` field exists with correct structure |
| `test_backward_compatible` | Old conversations without `rolling_summary` field work unchanged |
| `test_summarization_failure_graceful` | Mock Opus failure, verify conversation continues without summary |

### 10.3 Manual Testing

1. Open a demo case, send 3-4 messages including ones that trigger SOP retrieval
2. Check MongoDB — verify `rolling_summary` appears when budget is exceeded
3. Continue the conversation — verify the AI still has context from earlier turns (it references findings from the summary)
4. Check the UI — all messages still visible, scrollable, no visual difference
5. Export PDF — all messages present in the transcript
6. Reduce `CONTEXT_TOKEN_BUDGET` to a low value (e.g., 20,000) to force early summarization for testing

---

## 11. Build Order

This is a single-file-primary change. Suggested implementation sequence:

1. **Add config settings** to `server/config.py` (5 minutes)
2. **Add `_estimate_tokens()` and `_estimate_messages_tokens()`** — pure functions, easy to test (15 minutes)
3. **Add `SUMMARIZATION_SYSTEM_PROMPT` constant and `_build_summarization_input()`** — the prompt engineering (30 minutes, iterate on prompt quality)
4. **Modify `_rebuild_api_messages()`** — add `rolling_summary` parameter and summary injection logic (20 minutes)
5. **Add `_maybe_summarize()`** — the core orchestration (45 minutes)
6. **Modify `send_message()` and `send_message_streaming()`** — add the two-line summarization check (5 minutes)
7. **Test with reduced budget** — set `CONTEXT_TOKEN_BUDGET=20000` and run a case to verify summarization triggers and the AI maintains coherence (30 minutes)
8. **Tune the budget** — set to production values and verify with realistic case conversations (15 minutes)

Total estimated effort: ~3 hours including testing and prompt tuning.

---

## 12. Future Enhancements (Not In This Build)

- **Selective step document loading:** Track the current investigation phase and load only the relevant step document + prompt library section. This reduces the system prompt from ~50K to ~35K. Complements summarization but is independent.
- **Blocked investigation architecture:** The rolling summary lays groundwork for this. A "block summary" is conceptually a forced summarization at a phase boundary with investigator approval. The summary infrastructure built here can be reused.
- **Token counting API:** Replace the `len/3` heuristic with Anthropic's actual token counting endpoint for precise budget management. Not needed for MVP — the heuristic is conservative enough.
- **Summary quality monitoring:** Periodically compare the AI's behavior with and without summarization on the same conversation to detect information loss. Important for production but not for initial rollout.
