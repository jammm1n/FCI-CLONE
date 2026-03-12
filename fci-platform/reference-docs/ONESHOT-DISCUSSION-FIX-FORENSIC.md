# Oneshot (Autopilot) Discussion Flow — Forensic Fix Record

**Date:** 2026-03-12
**Status:** Fixed and tested on small case. Large-case testing pending.

---

## 1. Background: How Oneshot Mode Works

Oneshot (internally "autopilot") is a two-phase investigation mode:

1. **Setup phase** — AI reviews case data, asks clarifying questions, then calls the `signal_ready_to_execute` tool to indicate readiness. The frontend shows "Execute Full ICR" and "Continue Discussion" buttons.
2. **Execution phase** — Investigator clicks "Execute Full ICR". A separate endpoint (`/oneshot-execute`) streams the complete ICR using extended thinking and a 64K token budget.

The setup phase uses `TOOLS_ONESHOT_SETUP` (only `signal_ready_to_execute` + `get_reference_document`) and the system prompt from `knowledge_base/system-prompt-oneshot.md`. The execution phase uses `TOOLS_ONESHOT_EXECUTE` (only `get_reference_document`) and the full execution prompt.

### Key State Variables

| Variable | Location | Purpose |
|---|---|---|
| `oneshotReady` | Frontend (useStreamingChat hook) | True when AI has signalled readiness. Controls button visibility. |
| `oneshotSignalled` | Frontend (InvestigationPage) | Permanent latch — once true, the `wasSending` useEffect re-asserts `oneshotReady` after every AI response ends. |
| `oneshotExecuted` | Frontend (InvestigationPage) | True after successful execution. Prevents re-execution. |
| `oneshot_ready` | MongoDB (conversation doc) | Persisted readiness flag. Restored on page reload via history endpoint. |
| `oneshot_executed` | MongoDB (conversation doc) | Persisted execution completion flag. |
| `oneshot_in_discussion` | MongoDB (conversation doc) | **NEW.** Persisted discussion mode flag. Set when investigator clicks "Continue Discussion", cleared when AI re-signals readiness. |

### The `wasSending` / `oneshotSignalled` Latch Mechanism

```
InvestigationPage.jsx lines 184-203
```

This is a critical piece of UI logic that was the root cause of Bug 1:

- `oneshotSignalled` is a permanent latch: once `oneshotReady` becomes true, `oneshotSignalled` is set to true and never resets (line 184-186).
- When `sending` transitions from true to false (AI finishes responding), the `wasSending` useEffect fires (line 191-203).
- If `oneshotSignalled` is true and `oneshotReady` is false, it re-asserts `oneshotReady = true` (line 199-200).
- **Design intent:** If the investigator sends a follow-up question after the AI signalled readiness, the Execute button temporarily hides during streaming, then reappears when the response completes.
- **Problem:** This latch made it impossible to permanently dismiss the Execute button via "Continue Discussion" — it would always come back.

---

## 2. Bugs Found

### Bug 1: Execute Button Reappears After Every Message

**Trigger:** Click "Continue Discussion" -> send a message -> AI responds -> Execute button reappears.

**Root cause:** `onContinueOneshotDiscussion` only reset `oneshotReady` to false, but not `oneshotSignalled`. The `wasSending` useEffect (line 199) immediately re-asserted `oneshotReady = true` when the next AI response finished streaming, because `oneshotSignalled` was still true.

**Impact:** Genuine discussion was impossible — the Execute button dominated the UI after every exchange.

### Bug 2: Page Reload Restored Execute Button During Discussion

**Trigger:** Click "Continue Discussion" -> reload the page -> Execute button appears.

**Root cause:** `oneshot_ready` in MongoDB was only ever set to `true` (in `store_streamed_response` when the tool was called) and never reset to `false`. The history endpoint returned `oneshot_state.ready = true`, and the frontend init code (line 104-107) restored `oneshotReady` and `oneshotSignalled`.

**Impact:** Reloading the page during a discussion put the user back into the "ready to execute" state, contradicting their intent.

### Bug 3: AI Launched Into Full Case Assessment During Discussion

**Trigger:** Click "Continue Discussion" -> ask questions -> say "ready to go" -> AI produces comprehensive case assessment instead of conversing.

**Root cause:** No instruction was injected into the API messages to tell the AI it was in discussion mode. The AI saw its prior conversation (where it had already signalled readiness) plus the user's new message, and interpreted this as permission to begin analysis. The system prompt's "WHAT NOT TO DO" section only governed the initial setup phase, not post-signal discussion.

**Impact:** The AI consumed the 8K setup token budget producing a truncated case assessment instead of answering questions or re-signalling readiness.

### Bug 4: Discussion Instruction Only Fired Once (First Fix Failure)

**Trigger:** First fix injected the discussion instruction only when `oneshot_ready == True` in MongoDB. After the first message (which reset `oneshot_ready` to false), subsequent messages had no instruction.

**Root cause:** The detection condition `conversation.get("oneshot_ready") and not conversation.get("oneshot_executed")` was only true for the first message after "Continue Discussion". The second message onward saw `oneshot_ready = false` and skipped the injection entirely.

**Impact:** User's second or third message (e.g. "I'm ready now") caused the AI to launch into assessment — same as Bug 3 but delayed by one exchange.

### Bug 5: AI Re-Signals Without Tool Call (Anticipated)

**Trigger:** After discussion, the AI writes "I'm ready to proceed" but forgets to call the `signal_ready_to_execute` tool. The Execute button never reappears.

**Root cause:** The AI is more reliable at producing natural language than remembering to call tools. The system prompt and discussion instruction mentioned the tool but didn't provide a redundancy mechanism.

**Impact:** User gets permanently stuck in discussion mode with no way to trigger execution.

### Bug 6: Truncation During Execution Marked As Complete

**Trigger:** Large case execution hits the 64K token limit -> `done` event has `truncated: true` -> `oneshotExecuted` set to true -> case permanently marked as complete with incomplete output.

**Root cause:** The `done` event handler in `handleOneshotExecute` didn't distinguish between truncated and non-truncated completion. Both paths set `oneshotExecuted = true`.

**Impact:** Incomplete ICR output with no way to continue execution. The "Continue Execution" infrastructure existed but was never reached because the truncated response took the success path.

---

## 3. Fixes Applied

### Fix 1: Reset `oneshotSignalled` Latch on "Continue Discussion"

**File:** `client/src/pages/InvestigationPage.jsx` line 989-992

```javascript
onContinueOneshotDiscussion={() => {
  setOneshotReady(false);
  setOneshotSignalled(false);  // <-- NEW: break the latch
}}
```

**Mechanism:** By resetting the latch, the `wasSending` useEffect (line 199) no longer re-asserts `oneshotReady` after subsequent AI responses. The Execute button stays hidden until the AI explicitly calls `signal_ready_to_execute` again, which sets `oneshotReady` via the tool event in `useStreamingChat.js`, which then re-sets `oneshotSignalled` via the latch useEffect (line 184-186).

**Resolves:** Bug 1

### Fix 2: Persistent `oneshot_in_discussion` Flag in MongoDB

**File:** `server/services/conversation_manager.py` lines 574-589

On the first message after "Continue Discussion" (detected by `oneshot_ready == True` in MongoDB):
- Sets `oneshot_ready = false` (fixes page reload — Bug 2)
- Sets `oneshot_in_discussion = true` (persistent flag for subsequent messages — fixes Bug 4)

On subsequent discussion messages:
- Detects `oneshot_in_discussion == true` and injects instruction (every message, not just the first)

When AI calls `signal_ready_to_execute` again:
- `store_streamed_response` sets `oneshot_ready = true` and `oneshot_in_discussion = false` (line 784-785)

**Resolves:** Bug 2, Bug 4

### Fix 3: Discussion Mode Instruction Injection

**File:** `server/services/conversation_manager.py` lines 591-618

Injects a user/assistant message pair into `api_messages` (ephemeral — not stored in MongoDB) before the user's actual message. This is injected on EVERY discussion message while `oneshot_in_discussion` is true.

Key prompt design decisions:
- **"You physically cannot execute from here"** — frames the prohibition as a technical limitation, not a preference. The AI is less likely to attempt something it believes is mechanically impossible.
- **Explicit trigger phrases** — lists "go ahead", "ready", "let's do it", "I'm done", "that's all", "carry on", "come on then" as examples that mean "re-signal readiness" not "start producing output".
- **Ambiguity rule** — "If unsure whether the user wants to continue discussing or proceed, ask them directly rather than guessing." Prevents the AI from interpreting casual language as execution permission.
- **User/assistant pair format** — the injected assistant acknowledgment ("Understood...") ensures proper message alternation and primes the AI into the correct mode.

**Resolves:** Bug 3

### Fix 4: `[READY TO EXECUTE]` Phrase-Based Redundancy

**Files:** Three layers of detection for the trigger phrase.

**a) System prompt** (`knowledge_base/system-prompt-oneshot.md`):
- Point 4 now requires BOTH the tool call AND the phrase `[READY TO EXECUTE]`
- New "DISCUSSION MODE" section explains re-signaling flow, phrase requirement, and that "this is the ONLY way to restore the execution button"

**b) Backend router** (`server/routers/conversations.py` lines 192-204):
- After streaming completes, checks `done_event["content"]` for `[READY TO EXECUTE]`
- If found and no tool call was detected, sets `oneshot_ready_signalled = True` and emits a synthetic `signal_ready_to_execute` tool event to the frontend
- This ensures MongoDB gets `oneshot_ready = true` + `oneshot_in_discussion = false` via `store_streamed_response`, and the frontend gets the tool event to show the button

**c) Frontend hook** (`client/src/hooks/useStreamingChat.js` lines 64-69):
- Accumulates streamed content in `contentAccum`
- Checks for `[READY TO EXECUTE]` on every `content_delta` event
- Sets `oneshotReady = true` immediately when detected — button appears as soon as the phrase streams in, before the response completes

**Detection priority:** The tool call is the primary signal (detected during streaming). The phrase is a fallback (detected in content). If both fire, the second detection is a harmless no-op. If only the phrase fires, the backend synthesizes the equivalent tool event.

**Resolves:** Bug 5

### Fix 5: Truncation Routes Through Partial Save

**File:** `client/src/pages/InvestigationPage.jsx` lines 550-573

When the `done` event has `truncated: true` in `handleOneshotExecute`:
- Sets `executionInterrupted: true` on the message (enables "Continue Execution" button)
- Calls `savePartialOnFailure()` to persist content via API (which sets `oneshotPartial = true`)
- Does NOT set `oneshotExecuted = true`

When `truncated` is false (true completion):
- Existing behavior: sets `oneshotExecuted = true`

**Resolves:** Bug 6

---

## 4. System Prompt Changes

**File:** `knowledge_base/system-prompt-oneshot.md`

### Changed: Point 4 (Signal Readiness)

Before:
```
Call `signal_ready_to_execute` when you assess >= 95% confidence...
```

After:
```
Call `signal_ready_to_execute` AND include the exact phrase `[READY TO EXECUTE]`
in your response text when you assess >= 95% confidence... Both the tool call
and the phrase are required — this triggers a UI button that lets the investigator
launch execution. You cannot launch execution yourself; only the investigator can.
```

### Added: Discussion Mode Section (after "WHAT NOT TO DO")

```markdown
### DISCUSSION MODE
If the investigator chooses to discuss further after you signal readiness,
you enter **discussion mode**. In discussion mode:
- You will receive a [SYSTEM] instruction confirming this — follow it precisely
- Respond conversationally to whatever the investigator asks
- You CANNOT start execution yourself — only the investigator can, via a UI button
- When the investigator indicates they are satisfied (e.g. "go ahead", "ready",
  "let's do it"), you MUST re-signal readiness by calling `signal_ready_to_execute`
  and writing `[READY TO EXECUTE]`. This is the ONLY way to restore the execution
  button. Do NOT attempt to produce ICR output — it will not work in this phase.
```

---

## 5. Files Modified (Summary)

| File | Changes |
|---|---|
| `client/src/pages/InvestigationPage.jsx` | Fix 1: reset `oneshotSignalled` on Continue Discussion. Fix 5: truncation routes through partial save. |
| `client/src/hooks/useStreamingChat.js` | Fix 4c: phrase detection in streamed content deltas. |
| `server/services/conversation_manager.py` | Fix 2: `oneshot_in_discussion` persistent flag + `oneshot_ready` reset. Fix 3: discussion instruction injection. Fix 4a (store side): `oneshot_in_discussion = false` when AI re-signals. |
| `server/routers/conversations.py` | Fix 4b: phrase detection in `done_event` content + synthetic tool event emission. |
| `knowledge_base/system-prompt-oneshot.md` | Fix 4a (prompt side): phrase requirement in point 4 + new Discussion Mode section. |

---

## 6. Architecture: Message Flow During Discussion Mode

### First message after "Continue Discussion"

```
1. User clicks "Continue Discussion"
   Frontend: oneshotReady=false, oneshotSignalled=false

2. User types a message and sends
   Frontend: sendMessage() -> POST /api/conversations/{id}/messages

3. Backend: send_message_streaming()
   - Reads conversation from MongoDB: oneshot_ready=true, oneshot_in_discussion=false
   - Detects entering_discussion (oneshot_ready=true, not executed, not initial)
   - MongoDB update: oneshot_ready=false, oneshot_in_discussion=true
   - Loads TOOLS_ONESHOT_SETUP (signal_ready_to_execute available)
   - Rebuilds api_messages from stored history
   - INJECTS discussion instruction pair (ephemeral):
     [user: DISCUSSION MODE rules] + [assistant: Understood...]
   - Appends real user message
   - Streams AI response

4. Router: event_generator()
   - Streams content_delta events to frontend
   - If AI calls signal_ready_to_execute: oneshot_ready_signalled=true
   - On done: checks content for [READY TO EXECUTE] phrase (fallback)
   - Calls store_streamed_response (persists user msg + AI msg to MongoDB)
   - Yields done event to frontend

5. Frontend: useStreamingChat readStream()
   - Accumulates content, checks for [READY TO EXECUTE] phrase
   - If tool event signal_ready_to_execute received: oneshotReady=true
```

### Subsequent discussion messages (N=2, 3, ...)

```
1. Backend reads conversation: oneshot_ready=false, oneshot_in_discussion=true
   - Does NOT enter entering_discussion branch (oneshot_ready is false)
   - But in_discussion=true, so instruction is still injected
   - Same flow as above from step 3 onward
```

### AI re-signals readiness

```
1. AI calls signal_ready_to_execute tool during response
   OR writes [READY TO EXECUTE] in content (or both)

2. Router detects tool call -> oneshot_ready_signalled=true
   (or detects phrase in done_event -> oneshot_ready_signalled=true + synthetic event)

3. store_streamed_response: sets oneshot_ready=true, oneshot_in_discussion=false

4. Frontend: oneshotReady=true -> oneshotSignalled=true (latch)
   Execute button reappears
```

### Page reload during discussion

```
1. MongoDB state: oneshot_ready=false, oneshot_in_discussion=true
2. History endpoint returns: oneshot_state.ready=false
3. Frontend: oneshotReady=false, oneshotSignalled=false
4. No Execute button shown — normal chat input visible
5. Next message: backend detects oneshot_in_discussion=true, injects instruction
```

---

## 7. Remaining Risks and Known Limitations

### Risk 1: AI Ignores Both Tool and Phrase (LOW after fixes)

If the AI produces neither the tool call nor the `[READY TO EXECUTE]` phrase when the user says "go ahead", the user remains stuck in discussion mode. Mitigations in place:
- System prompt teaches the phrase from the start
- Injected instruction repeats it on every message with explicit trigger examples
- "Physically cannot execute" framing discourages workarounds
- Ambiguity rule tells AI to ask rather than guess

**Escape hatch if this happens:** User can ask "Signal that you're ready" or "Call signal_ready_to_execute" — the AI should comply with a direct instruction to use a specific tool.

### Risk 2: False Positive Phrase Detection (VERY LOW)

`[READY TO EXECUTE]` in square brackets is distinctive enough to avoid false positives in normal conversation. The AI would have to spontaneously produce this exact bracketed phrase during discussion for a false trigger. Even if it did, the worst case is the Execute button appearing prematurely — the investigator can just click "Continue Discussion" again.

### Risk 3: Injected Instruction Grows API Context (LOW)

The user/assistant instruction pair adds ~250 tokens per discussion message. This is small relative to the system prompt (~1200 tokens) and case data injection. Even after 10 discussion exchanges, the overhead is ~2500 tokens — well within the setup phase budget.

### Risk 4: Discussion State Persists Across Sessions (BY DESIGN)

`oneshot_in_discussion` in MongoDB persists indefinitely until the AI re-signals readiness. If the investigator abandons a discussion mid-conversation and returns days later, the next message will still get the discussion instruction injected. This is correct — the conversation is still in discussion mode until explicitly resolved.

---

## 8. Relevance to Step-by-Step Investigation Mode

The step-by-step mode has a parallel mechanism for step transitions:

| Oneshot Concept | Step-by-Step Equivalent |
|---|---|
| `signal_ready_to_execute` tool | `signal_step_complete` tool |
| `oneshotReady` / `oneshotSignalled` | `stepComplete` / `stepSignalled` |
| `wasSending` latch re-asserts ready | `wasSending` latch re-asserts stepComplete |
| "Continue Discussion" button | "Continue Discussion" button (per-step) |
| Discussion mode instruction injection | **DOES NOT EXIST YET** |
| `[READY TO EXECUTE]` phrase fallback | **DOES NOT EXIST YET** |
| `oneshot_in_discussion` MongoDB flag | **DOES NOT EXIST YET** |

**Known step-by-step bugs (reported but not yet investigated):**
- AI launches into ICR analysis during step 1 (setup) instead of doing data review
- AI advances to step 2 content while still in step 1
- General: AI ignores step boundaries and produces output for later steps

**Likely root causes (by analogy to oneshot bugs):**
- The `wasSending` latch (line 196-197) has the same re-assertion pattern for `stepComplete` — same Bug 1 risk
- No discussion mode instruction injection exists for step-by-step "Continue Discussion"
- No phrase-based fallback exists for `signal_step_complete`
- Step boundary prompting may be too weak to prevent the AI from producing content for future steps
- The step system prompt may not clearly enough communicate that the AI cannot advance steps itself — the investigator controls transitions via the UI

**These should be investigated and fixed using the same pattern established here.**
