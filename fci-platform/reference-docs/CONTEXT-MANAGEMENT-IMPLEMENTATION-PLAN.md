# Context Management — Implementation Plan

**Date:** 7 March 2026
**Status:** Approved for implementation
**Supersedes:** `CONTEXT-MANAGEMENT-PLAN.md` (6 March 2026 — retained as historical reference)

---

## 1. Problem Statement

The current architecture loads all core knowledge base documents (~290K chars / ~58K tokens) into every API call regardless of investigation phase. Case data adds ~15-25K tokens. Conversation history grows unbounded. Complex cases reach 140-160K tokens.

**Observed baselines (7 March 2026):**
- Case investigation: ~85K tokens before first message
- Free chat: ~75K tokens before first message

---

## 2. Architecture Decisions

All decisions below were made during the 7 March 2026 planning session.

### 2.1 Server-Driven Step Loading (Not AI-Driven)

The server tracks which step the investigation is on (`investigation_state.current_step` in MongoDB) and deterministically injects the correct documents into the system prompt. The AI does not fetch its own step documents via tool calls.

**Rationale:** Step document selection is deterministic — Step 2 always needs `icr-steps-analysis.md`. Making the AI fetch its own instructions introduces an unnecessary failure mode. The server handles deterministic loading; the AI handles dynamic loading (reference SOPs via tool calls based on case content).

**Consequence:** No routing table document needed. No tool call overhead at step start.

### 2.2 Five Investigation Steps

| Step | Phase | Step Document | Additional Docs |
|------|-------|---------------|-----------------|
| 1 | Setup | icr-steps-setup.md | — |
| 2 | Analysis | icr-steps-analysis.md | — |
| 3 | Decision | icr-steps-decision.md | decision-matrix.md, mlro-escalation-matrix.md |
| 4 | Post-Decision | icr-steps-post.md | mlro-escalation-matrix.md |
| 5 | QC Check | — | qc-full-checklist.md, pasted case text |

Step 5 has no step instruction doc — the full QC checklist IS the instruction.

### 2.3 Investigator Controls Step Transitions

The AI never decides when to advance steps. The investigator clicks:
- **"Approve and Continue"** (Steps 1→2, 2→3, 3→4) — advances with summary generation
- **"QC Check"** (Step 4→5) — opens a paste modal where the investigator pastes their case text from HaoDesk, then submits

### 2.4 Per-Step Model Configuration

Model is configurable per step, not global. Allows testing Sonnet vs Opus at different steps.

```python
STEP_CONFIG = {
    1: {"model": "claude-sonnet-4-6"},
    2: {"model": "claude-opus-4-6"},   # heaviest step
    3: {"model": "claude-sonnet-4-6"},
    4: {"model": "claude-sonnet-4-6"},
    5: {"model": "claude-opus-4-6"},   # QC needs strong reasoning
    "summary": {"model": "claude-opus-4-6"},  # step boundary summaries
}
```

This is a starting point — adjust per step based on testing.

### 2.5 Step Summaries — Invisible Infrastructure

When the investigator clicks "Approve and Continue":
1. Server generates a structured summary of the completed step (separate API call)
2. Summary is stored in the conversation document
3. Summary is injected as context for subsequent steps
4. Summary is NOT shown to the investigator (for now)

Visibility can be added later as a read-only display. No edit/approve flow for summaries.

### 2.6 QC Checklist Split

The current `qc-submission-checklist.md` (511 lines, ~27K chars) is split into:
- **`qc-quick-reference.md`** (~lines 1-165, ~10K chars) — process instructions, auto-fail checks, AI verification process, all 48 checks in compact table format. Loaded during Steps 1-4 for inline QC tick boxes.
- **`qc-full-checklist.md`** (full original file, kept as-is) — loaded only at Step 5.

One source file to maintain. Quick reference is the compact subset.

### 2.7 General Rules Restructuring

`icr-general-rules.md` is trimmed from ~22K chars to ~12K chars by relocating step-specific content:

**Keep in general-rules (cross-cutting):**
- Source of Truth Hierarchy
- Hexa Protocol (general rule + correction sequence)
- Corporate Account Rules (canonical version)
- Brevity Principle
- Risk Position Requirement
- Currency Display Rule
- Output Hygiene
- Parallel Chat Data Products
- Terminology Rules

**Move to Setup (icr-steps-setup.md):**
- Scam/Fraud Case Intake Extraction → Phase 0 context
- SLA Framework → Phase 0 context setting

**Move to Post (icr-steps-post.md):**
- Pre-Submission Requirements (operation log, Save All and Generate, template cleanup)
- Always Editable Fields validation
- Older Format ICR save warning
- Fraud/Scam Template Cleanup + FRC/C2C Freeze Handling

**Remove (duplicates):**
- Case Rejection Rules from general-rules (already exists in post, lines 40-48)
- Corporate KYB detail from setup Step 2 (general-rules has the canonical version; setup should reference it)

### 2.8 Free Chat — Deferred

Rolling summarization with configurable token threshold (~160-170K max). Separate design and implementation effort. Not part of this plan.

### 2.9 No Fixed Token Targets

The 200K context window is available. Use it effectively. Manage context when quality degrades, not to hit arbitrary numbers. The step architecture naturally reduces per-step context by loading only relevant documents.

---

## 3. Per-Step Document Injection Map

| Component | Step 1 | Step 2 | Step 3 | Step 4 | Step 5 |
|-----------|--------|--------|--------|--------|--------|
| system-prompt-case.md | Y | Y | Y | Y | Y |
| general-rules (trimmed, ~12K) | Y | Y | Y | Y | Y |
| qc-quick-reference.md (~10K) | Y | Y | Y | Y | - |
| reference-index.yaml (formatted) | Y | Y | Y | Y | Y |
| icr-steps-setup.md (~40K) | Y | - | - | - | - |
| icr-steps-analysis.md (~82K) | - | Y | - | - | - |
| icr-steps-decision.md (~33K) | - | - | Y | - | - |
| decision-matrix.md (~35K) | - | - | Y | - | - |
| mlro-escalation-matrix.md (~5K) | - | - | Y | Y | - |
| icr-steps-post.md (~33K) | - | - | - | Y | - |
| qc-full-checklist.md (~27K) | - | - | - | - | Y |
| Case data (variable) | Y | Y | Y | Y | - |
| Previous step summaries (~2K each) | - | Y | Y | Y | Y |
| Pasted case text (investigator) | - | - | - | - | Y |

Reference SOPs available via `get_reference_document` tool call at any step.
Processing prompts available via `get_prompt` tool call at any step.

---

## 4. Step Lifecycle

### 4.1 Step Start (Steps 1-4)

1. Server reads `investigation_state.current_step` from conversation document
2. Server assembles system prompt: always-loaded docs + step-specific docs (from Section 3 map)
3. Case data is injected fresh (reinjected every step, not carried)
4. Previous step summaries are injected (0 for Step 1, growing by ~2K per completed step)
5. Only messages from the current step are included in conversation history
6. API call is made with the assembled payload

### 4.2 Within a Step

- Normal chat: investigator messages, AI responses, tool calls for reference SOPs as needed
- All messages tagged with their step number in MongoDB
- Reference SOPs fetched on-demand persist in conversation history for the remainder of the step

### 4.3 Step Completion (Steps 1-4)

1. Investigator clicks **"Approve and Continue"**
2. `POST /api/conversations/{id}/advance-step`
3. Server extracts all messages from the current step
4. Server generates structured summary via separate API call (configurable model, non-streaming)
5. Summary stored in `investigation_state.steps[N-1].summary`
6. `current_step` incremented
7. Step divider message inserted (for UI display, never sent to API)
8. Response returned to frontend

### 4.4 QC Check Transition (Step 4 → Step 5)

1. Investigator clicks **"QC Check"** button
2. Frontend shows paste modal: "Paste your case file from HaoDesk"
3. Investigator pastes case text and submits
4. `POST /api/conversations/{id}/qc-check` with `{ "case_text": "..." }`
5. Server advances to Step 5
6. Server assembles system prompt with full QC checklist
7. Pasted case text becomes the first user message in Step 5
8. AI immediately runs QC checks — no preamble needed

### 4.5 Investigation Complete

After Step 5, the investigation is complete. No further step transitions. The conversation remains open for follow-up questions about QC findings.

---

## 5. MongoDB Schema

### 5.1 Conversation Document (Updated)

```json
{
  "_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "user_id": "user_001",
  "mode": "case",
  "investigation_state": {
    "current_step": 2,
    "steps": [
      {
        "step_number": 1,
        "phase": "setup",
        "status": "completed",
        "summary": "## Step 1 Summary: Setup\n...",
        "summary_model": "claude-opus-4-6",
        "summary_token_usage": { "input_tokens": 65000, "output_tokens": 1200 },
        "completed_at": "2026-03-07T10:15:00Z",
        "approved_by": "user_001"
      },
      {
        "step_number": 2,
        "phase": "analysis",
        "status": "active",
        "summary": null,
        "completed_at": null,
        "approved_by": null
      }
    ]
  },
  "messages": [
    {
      "message_id": "msg_001",
      "role": "system_injected",
      "step": 1,
      "content": "[CASE DATA]\n...",
      "visible": false
    },
    {
      "message_id": "msg_010",
      "role": "step_divider",
      "step": 1,
      "content": "Step 1 (Setup) complete. Moving to Step 2: Analysis.",
      "visible": true
    },
    {
      "message_id": "msg_011",
      "role": "user",
      "step": 2,
      "content": "...",
      "visible": true
    }
  ]
}
```

### 5.2 Message Rules

- Every message gets a `step` field
- `step_divider` role: frontend display only, never sent to Anthropic API
- `system_injected` (case data): re-created per step, only current step's version sent to API
- When building API payload: filter `messages` to `step == current_step` only
- Old step messages stay in MongoDB for UI scrollback and PDF export

---

## 6. Step Summary Generation

### 6.1 Summary Template

```markdown
## Step [N] Summary: [Phase Name]

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
[Which sections of the case template were drafted and approved]
```

### 6.2 Summary System Prompt

```
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

FORMAT: Use the structured template provided. Target 1,000-2,500 tokens.
Up to 3,000 for complex steps with many findings.
```

### 6.3 Summary Generation Call

- Non-streaming, separate API call
- Input: all messages from the completed step (including tool exchanges)
- Model: configurable (default Opus)
- Max tokens: 3,000

---

## 7. API Payload Assembly

```python
def _build_step_system_prompt(self, step: int) -> str:
    """Assemble system prompt for a specific investigation step."""
    parts = [
        self.kb.case_system_prompt,
        self.kb.general_rules,          # trimmed version
        self.kb.qc_quick_reference if step <= 4 else "",
        self.kb.reference_index_text,
    ]

    # Step-specific documents
    step_docs = STEP_CONFIG[step].get("docs", [])
    for doc_id in step_docs:
        parts.append(self.kb.get_document(doc_id))

    return "\n\n---\n\n".join(p for p in parts if p)


def _rebuild_api_messages(self, conversation: dict) -> list[dict]:
    """Build API messages for current step only."""
    state = conversation["investigation_state"]
    current_step = state["current_step"]
    api_messages = []

    # Inject summaries from completed steps
    completed_summaries = [
        s["summary"] for s in state["steps"]
        if s["status"] == "completed" and s["summary"]
    ]
    if completed_summaries:
        summary_text = "\n\n---\n\n".join(completed_summaries)
        api_messages.append({
            "role": "user",
            "content": (
                "[PREVIOUS STEP SUMMARIES]\n\n" + summary_text
            ),
        })
        api_messages.append({
            "role": "assistant",
            "content": "Understood. I have the context from previous steps.",
        })

    # Case data (Steps 1-4 only, not Step 5)
    if current_step <= 4:
        # Inject fresh case data as first message
        ...

    # Only messages from current step
    step_messages = [
        m for m in conversation["messages"]
        if m.get("step") == current_step and m["role"] != "step_divider"
    ]
    # Rebuild as API messages (existing logic)
    ...

    return api_messages
```

---

## 8. New API Endpoints

### 8.1 Advance Step

```
POST /api/conversations/{conversation_id}/advance-step
Authorization: Bearer {token}

Response: {
  "step": 2,
  "phase": "analysis",
  "summary": "## Step 1 Summary: Setup\n..."
}
```

### 8.2 QC Check

```
POST /api/conversations/{conversation_id}/qc-check
Authorization: Bearer {token}
Body: { "case_text": "..." }

Response: {
  "step": 5,
  "phase": "qc_check"
}
```

### 8.3 Get Investigation State

```
GET /api/conversations/{conversation_id}/state
Authorization: Bearer {token}

Response: {
  "current_step": 2,
  "phase": "analysis",
  "steps": [...]
}
```

---

## 9. Frontend Changes

### 9.1 Step Indicator
Header shows: "Step 2 of 5: Analysis"

### 9.2 Approve and Continue Button
Shown at bottom of chat area when investigator is ready to advance. Triggers `advance-step` endpoint. Shows loading state during summary generation.

### 9.3 QC Check Button + Paste Modal
Replaces "Approve and Continue" at Step 4. Opens modal with large textarea: "Paste your case file from HaoDesk." Submit triggers `qc-check` endpoint.

### 9.4 Step Dividers
Visual divider in chat: "Step 1 (Setup) complete. Moving to Step 2: Analysis." Not interactive. Scrollable — investigator can see all previous steps' chat.

### 9.5 Context Warning
If step conversation exceeds configurable token threshold, show advisory: "This step has a long conversation. Consider completing it to preserve context quality." Non-blocking.

---

## 10. Implementation Phases

### Phase A: Content Work (No Code Changes)

**Session 2. Estimated effort: 1 session.**

1. Create `knowledge_base/qc-quick-reference.md` from lines 1-165 of `qc-submission-checklist.md`
2. Rename `qc-submission-checklist.md` → `qc-full-checklist.md` (or keep name, reference by new role)
3. Restructure `icr-general-rules.md`:
   a. Remove: Scam/Fraud Case Intake Extraction (lines 382-411) → move to setup
   b. Remove: SLA Framework (lines 326-354) → move to setup
   c. Remove: Pre-Submission Requirements (lines 238-286) → move to post
   d. Remove: Always Editable Fields (lines 358-379) → move to post
   e. Remove: Older Format ICR save warning (lines 279-286) → move to post
   f. Remove: Fraud/Scam Template Cleanup + FRC/C2C (lines 515-548) → move to post
   g. Remove: Case Rejection Rules (lines 303-323) → already in post
   h. Keep everything else (cross-cutting rules)
4. Add relocated content to `icr-steps-setup.md` (items a, b)
5. Add relocated content to `icr-steps-post.md` (items c, d, e, f)
6. Remove duplicate Corporate KYB from `icr-steps-setup.md` (lines 233-335) — add reference to general-rules canonical version
7. Validate: no content lost, no contradictions

### Phase B: Backend — Knowledge Base & Config

**Session 3. Estimated effort: 1 session.**

8. Add `STEP_CONFIG` to `server/config.py` — per-step model + document list
9. Add `get_step_system_prompt(step: int)` to `knowledge_base.py`
10. Add `get_document(doc_id: str)` — unified document retrieval for step docs, QC, decision matrix, escalation matrix
11. Keep existing `get_system_prompt("case")` and `get_system_prompt("free_chat")` working
12. Verify free chat is unaffected

### Phase C: Backend — Step Architecture

**Session 4. Estimated effort: 1-2 sessions.**

13. Add `investigation_state` initialization to conversation creation
14. Add `step` field to all message storage
15. Modify `_rebuild_api_messages()` — filter by current step, inject summaries, inject case data fresh
16. Add `_generate_step_summary()` — separate API call with summary prompt
17. Add `approve_and_continue()` to conversation manager
18. Add `qc_check()` to conversation manager
19. Add endpoints: `advance-step`, `qc-check`, `state`
20. Wire per-step model routing in `ai_client.py`

### Phase D: Frontend

**Session 5. Estimated effort: 1 session.**

21. Step indicator component in investigation header
22. "Approve and Continue" button in chat area
23. "QC Check" button + paste modal
24. Step divider rendering in ChatMessageList
25. Context warning (advisory)

### Phase E: Testing & Polish

**Session 6.**

26. Run through a real case end-to-end
27. Validate token usage at each step
28. Test step summary quality
29. Test per-step model switching
30. Fix issues

### Phase F: Deferred

31. Auto-execute mode (all 4 steps run automatically)
32. Free chat rolling summarization
33. Step summary visibility in case data panel

---

## 11. Files Changed (Complete List)

### Phase A (Content)
| File | Action |
|------|--------|
| `knowledge_base/qc-quick-reference.md` | NEW — compact QC reference |
| `knowledge_base/core/qc-submission-checklist.md` | Renamed or kept as full checklist |
| `knowledge_base/core/icr-general-rules.md` | MODIFY — remove step-specific content |
| `knowledge_base/core/icr-steps-setup.md` | MODIFY — add relocated content, remove KYB duplicate |
| `knowledge_base/core/icr-steps-post.md` | MODIFY — add relocated content |

### Phase B (Backend KB)
| File | Action |
|------|--------|
| `server/config.py` | MODIFY — add STEP_CONFIG |
| `server/services/knowledge_base.py` | MODIFY — add step-aware methods |

### Phase C (Backend Step Architecture)
| File | Action |
|------|--------|
| `server/services/conversation_manager.py` | MODIFY — step state, filtered messages, summaries |
| `server/services/ai_client.py` | MODIFY — per-step model routing |
| `server/routers/conversations.py` | MODIFY — new endpoints |
| `server/models/schemas.py` | MODIFY — investigation state schema |

### Phase D (Frontend)
| File | Action |
|------|--------|
| `client/src/pages/InvestigationPage.jsx` | MODIFY — step indicator, approve button |
| `client/src/components/investigation/ChatMessageList.jsx` | MODIFY — step dividers |
| `client/src/components/investigation/ChatInput.jsx` | MODIFY — approve/QC buttons |
| `client/src/components/shared/QCPasteModal.jsx` | NEW — paste modal |
| `client/src/components/shared/StepIndicator.jsx` | NEW — step display |
| `client/src/services/api.js` | MODIFY — new API calls |

### Files NOT Changed
- All reference documents in `knowledge_base/reference/`
- All processing prompts in `knowledge_base/prompts/`
- `knowledge_base/prompt-index.yaml`
- `knowledge_base/system-prompt-free-chat.md`
- All ingestion code
- `server/services/icr/` (toolkit — never modified)

---

## 12. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Summary loses critical information between steps | Configurable summary model (default Opus). Structured template forces coverage. Can add investigator visibility later. |
| Step runs too long, context degrades within step | Advisory context warning. Step structure naturally limits conversation length. |
| Sonnet struggles with heavy steps (Analysis at ~82K step doc) | Per-step model config. Switch individual steps to Opus as needed. |
| Content restructuring introduces gaps | Phase A validation step: read every file, confirm no content lost. |
| Backward compatibility during development | Existing `get_system_prompt()` kept working until Phase C fully wired. |
| QC quick reference drifts from full checklist | Single maintenance point: update full checklist, sync quick reference tables. |

---

## 13. Phase D Handoff Notes (from Phases B–C implementation)

These details were decided during Phase B–C implementation and are needed for Phase D.

### Backend API details

- **`POST /api/conversations/{id}/advance-step`** — generates step summary (Opus, can take 5-10s), returns `{step, phase, summary}`. Frontend needs a loading state during this call.
- **`POST /api/conversations/{id}/qc-check`** — state-only. Generates step 4 summary and advances to step 5. Does NOT accept or store pasted case text. Returns `{step, phase}`. After this returns, the frontend sends the pasted text as a regular message via `POST /api/conversations/{id}/messages`.
- **`GET /api/conversations/{id}/state`** — returns `{current_step, phase, steps: [...]}`.

### History response changes

`GET /api/conversations/{id}/history` now includes:
- `investigation_state: {current_step, phase, steps: [...]}` at the top level (only for case conversations)
- Each message includes `step: int` (the step it belongs to)
- Messages with `role: "step_divider"` appear in visible history — render as visual separators, not chat bubbles

### Button logic

| Current step | Show |
|---|---|
| 1, 2, 3 | "Approve and Continue" button |
| 4 | "QC Check" button (opens paste modal) |
| 5 | Neither (investigation complete after QC) |

### QC paste flow

1. Investigator clicks "QC Check" button
2. Modal opens with large textarea: "Paste your case file from HaoDesk"
3. Investigator pastes and clicks Submit
4. Frontend calls `POST /qc-check` (loading state while summary generates)
5. On success, frontend calls `POST /messages` with `{content: pastedText, stream: true}` to trigger QC analysis
6. AI streams its QC check response

### ai_client.py was NOT changed

Per-step model routing was already supported via the `model` parameter. `conversation_manager.py` passes `model=STEP_CONFIG[step]["model"]` to `ai_client`. No changes to `ai_client.py` were needed (contrary to what Section 11 Phase C predicted).

---

*This document captures the implementation plan as of 7 March 2026. It supersedes `CONTEXT-MANAGEMENT-PLAN.md` which is retained as historical reference.*
