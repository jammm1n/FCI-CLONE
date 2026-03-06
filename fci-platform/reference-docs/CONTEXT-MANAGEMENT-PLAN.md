# Context Management Architecture — Unified Plan

**Date:** 6 March 2026
**Status:** Planning — supersedes `FCI-Blocked-Investigation-Architecture.md` and `ROLLING-SUMMARIZATION-IMPL.md`
**Author:** Ben + Claude (discussion-driven design)

---

## 1. Problem Statement

The current architecture sends the full system prompt (~96K tokens across 10 core documents), the full case data (~10-15K tokens), and the entire conversation history with every API call. The context payload only grows throughout an investigation.

By the end of a complex case (30+ turns, reference documents retrieved, images uploaded), the total context can reach 140-160K tokens. This causes:

1. **Latency degradation** — response times worsen as context grows.
2. **Context window pressure** — approaching 200K risks quality degradation, especially with Sonnet.
3. **Unnecessary cost** — every token in the conversation history is billed at full price on every call.
4. **Model constraint** — the current payload size requires Opus for reliability. Sonnet would be cheaper and faster but struggles with 150K of mixed instructions, data, and conversation.

The worst offenders are:
- **Step documents loaded all at once** — 3,363 lines across 4 step files, but only one is relevant at any time.
- **Prompt library** — 1,375 lines, most of which relate to preprocessing (moving to ingestion layer) and won't be needed in the investigation chat.
- **QC checklist** — 511 lines loaded for every turn, but only a subset is relevant to the current investigation phase.
- **Tool exchange messages** — retrieved SOPs (4,000-15,000 tokens each) persist in every subsequent API call forever.

---

## 2. Solution Overview

A three-part architecture that reinforces itself:

1. **Step-based document loading via AI tool calls** — instead of loading all documents into the system prompt, the AI fetches step-specific documents on demand using the existing tool call mechanism.
2. **Step-based context compression** — at each step boundary, the conversation is summarized and the context resets. The AI gets a fresh start with only the summary, the next step's documents, and fresh case data.
3. **Lean always-loaded system prompt** — a minimal set of documents that the AI needs unpredictably across all steps, plus a routing table telling it which documents to fetch at each step.

Combined, these keep the total context well under 80K tokens at all times, making Sonnet viable as the primary investigation model.

---

## 3. The Four Investigation Steps

The investigation is split into four steps that map to the existing case form structure and step documents:

| Step | Phase | Step Document | Focus |
|------|-------|---------------|-------|
| 1 | Setup | `icr-steps-setup.md` (629 lines) | Case classification, KYC review, subject profile, initial risk assessment |
| 2 | Analysis | `icr-steps-analysis.md` (1,584 lines) | Transaction analysis, counterparty evaluation, wallet screening, evidence review |
| 3 | Decision | `icr-steps-decision.md` (739 lines) | Case outcome, classification rationale, escalation routing |
| 4 | Post | `icr-steps-post.md` (411 lines) | Post-decision actions, submission preparation, QC self-check |

These are not artificial boundaries. They map directly to how the investigation methodology is already structured in the SOPs and the case form.

---

## 4. Document Tiering — What's Always Loaded vs On-Demand

### 4.1 Tier 1: Always Loaded (Every Step, Every Turn)

These documents must be available regardless of which step the investigation is in, because they can be needed unpredictably:

| Document | Lines | Reason |
|----------|-------|--------|
| `SYSTEM-PROMPT.md` | 441 | AI persona, behaviour rules, output format |
| `icr-general-rules.md` | 572 | Investigation standards, always applicable |
| `mlro-escalation-matrix.md` | 97 | Escalation criteria — could be triggered at any point |
| **Step routing table** (new) | ~40 | Tells the AI which documents to fetch at each step (see Section 4.3) |
| **Investigation document index** (new) | ~60 | Expanded index covering step docs, QC sections, and reference docs |

**Estimated Tier 1 total: ~30-35K tokens** (down from ~96K currently).

### 4.2 Removed from Always-Loaded

These documents move from core (always loaded) to on-demand (fetched via tool call):

| Document | Lines | New Tier | Rationale |
|----------|-------|----------|-----------|
| `prompt-library.md` | 1,375 | **Removed entirely** | Preprocessing prompts move to ingestion layer. Investigation chat prompts embedded in step documents or not needed. |
| `icr-steps-setup.md` | 629 | On-demand | Only needed during Step 1. AI fetches it when Step 1 begins. |
| `icr-steps-analysis.md` | 1,584 | On-demand | Only needed during Step 2. |
| `icr-steps-decision.md` | 739 | On-demand | Only needed during Step 3. |
| `icr-steps-post.md` | 411 | On-demand | Only needed during Step 4. |
| `decision-matrix.md` | 134 | On-demand | Only needed during Step 3 (decision phase). AI fetches it then. |
| `qc-submission-checklist.md` | 511 | **Split into 4 parts** (on-demand) | Each step gets its relevant QC section. Full QC available via tool call for end-of-case review. See Section 5. |

### 4.3 The Routing Table (New Document)

A compact document (~40 lines) included in the always-loaded Tier 1 that tells the AI exactly what to do at each step boundary. This replaces loading all step documents upfront.

```markdown
# Investigation Step Routing

## How Steps Work
This investigation proceeds through 4 steps. At the start of each step, use the
get_investigation_document tool to fetch the documents listed below. Each step's
documents replace the previous step's — you do not carry forward old step documents.

A conversation summary from previous steps is provided separately. Work from the
summary, not from memory of previous step conversations.

## Step 1: Setup
**Trigger:** Investigation begins (first message).
**Fetch these documents:**
- `step-setup` — Setup phase instructions and procedures
- `qc-setup` — QC checks relevant to Setup (KYC, case classification)

## Step 2: Analysis
**Trigger:** Step 1 complete, summary provided.
**Fetch these documents:**
- `step-analysis` — Analysis phase instructions and procedures
- `qc-analysis` — QC checks relevant to Analysis (main body, counterparties, devices)

## Step 3: Decision
**Trigger:** Step 2 complete, summary provided.
**Fetch these documents:**
- `step-decision` — Decision phase instructions and procedures
- `qc-decision` — QC checks relevant to Decision (escalations, RFI, off-boarding)
- `decision-matrix` — Case classification and outcome decision matrix

## Step 4: Post-Decision
**Trigger:** Step 3 complete, summary provided.
**Fetch these documents:**
- `step-post` — Post-decision instructions and procedures
- `qc-post` — QC checks relevant to Post (attachments, formatting, final validation)

## Full QC Review
**Trigger:** Investigator requests "run QC checks" or "check before I submit".
**Fetch:** `qc-full` — Complete QC submission checklist (all 48 checks)

## Reference Documents
The reference document index lists SOPs and guidelines available on demand.
Fetch these as needed during any step when the investigation requires them.
```

### 4.4 Expanded Document Index

The existing `reference-index.yaml` is expanded to include step documents and QC sections alongside the existing reference SOPs. The AI uses the same `get_investigation_document` tool (renamed from `get_reference_document`) to fetch any on-demand document.

New entries added to the index:

```yaml
# Step documents
- id: step-setup
  title: "Investigation Step 1: Setup"
  filename: "core/icr-steps-setup.md"
  covers:
    - Case classification and intake
    - KYC verification procedures
    - Subject profile analysis
    - Initial risk assessment
  token_estimate: 9000

- id: step-analysis
  title: "Investigation Step 2: Analysis"
  filename: "core/icr-steps-analysis.md"
  covers:
    - Transaction summary analysis
    - Counterparty evaluation
    - Wallet screening and on-chain analysis
    - CTM/FTM alert review
    - Device and IP analysis
    - Privacy coin assessment
  token_estimate: 22000

- id: step-decision
  title: "Investigation Step 3: Decision"
  filename: "core/icr-steps-decision.md"
  covers:
    - Case outcome determination
    - Classification rationale
    - Escalation routing (MLRO, sanctions, LE)
    - RFI decision and drafting
  token_estimate: 10000

- id: step-post
  title: "Investigation Step 4: Post-Decision"
  filename: "core/icr-steps-post.md"
  covers:
    - Off-boarding procedures
    - Submission preparation
    - Attachment checklist
    - Final QC self-check
  token_estimate: 6000

- id: decision-matrix
  title: "Case Decision Matrix"
  filename: "core/decision-matrix.md"
  covers:
    - Case classification criteria
    - Outcome determination rules
    - Retain/offboard/RFI decision logic
  token_estimate: 2000

# QC split sections (see Section 5)
- id: qc-setup
  title: "QC Checks: Setup Phase"
  filename: "qc/qc-setup.md"
  covers: [KYC checks, case phase selection]
  token_estimate: 1500

- id: qc-analysis
  title: "QC Checks: Analysis Phase"
  filename: "qc/qc-analysis.md"
  covers: [Main body checks, counterparties, devices, transactions]
  token_estimate: 3000

- id: qc-decision
  title: "QC Checks: Decision Phase"
  filename: "qc/qc-decision.md"
  covers: [Escalation checks, RFI checks, off-boarding checks]
  token_estimate: 4000

- id: qc-post
  title: "QC Checks: Post-Decision Phase"
  filename: "qc/qc-post.md"
  covers: [Attachment checks, formatting, mandatory field validation]
  token_estimate: 3000

- id: qc-full
  title: "Full QC Submission Checklist"
  filename: "core/qc-submission-checklist.md"
  covers: [All 48 QC checks, auto-fail items, scoring]
  token_estimate: 7000
```

---

## 5. QC Document Split

The QC checklist (511 lines, 48 checks) is split into four step-aligned sections. Each step loads only its relevant QC checks, reducing per-step QC overhead from ~7K tokens to ~1.5-4K.

### Proposed Split

| QC Section | File | Contents | Checks |
|------------|------|----------|--------|
| `qc-setup.md` | `knowledge_base/qc/` | Section 1 (KYC, 5 checks) + Section 2 (Suspicious Activity, 1 check) + auto-fail items relevant to setup | ~6 checks |
| `qc-analysis.md` | `knowledge_base/qc/` | Section 3 (Main Body, 12 checks) — transactions, counterparties, devices, privacy coins, LE enquiries | ~12 checks |
| `qc-decision.md` | `knowledge_base/qc/` | Section 4 (RFI, 6 checks) + Section 5 (Escalations, 5 checks) + Section 6 (Off-boarding, 7 checks) + auto-fail items relevant to decision | ~18 checks |
| `qc-post.md` | `knowledge_base/qc/` | Section 7 (Attachments, 6 checks) + Section 8 (Others, 5 checks) + Phase 4 mandatory field validation + RFI response handling (5 checks) | ~16 checks |

Each split file includes:
- The auto-fail checks relevant to that phase (so they're always visible when they matter)
- The scoring context ("100 points, pass mark 76") at the top of each file
- The AI verification process steps relevant to that phase

The full `qc-submission-checklist.md` remains untouched in `core/` for the full QC review tool call.

### Full QC Review via Tool Call

When the investigator says "run QC checks" or "check before I submit" (typically at the end of Step 4), the AI fetches `qc-full` which returns the complete 511-line checklist. This is a single tool call — the same mechanism as fetching any other document.

---

## 6. Step Lifecycle — How a Step Runs

### 6.1 Step Start

1. **System loads the always-loaded Tier 1 documents** (persona, general rules, escalation matrix, routing table, document index).
2. **Case data is injected** fresh (same as today — reinjected, not carried from previous step).
3. **Previous step summaries are injected** as context (0K for Step 1, growing by ~2K per completed step).
4. **The AI reads the routing table** and immediately fetches the current step's documents via tool call (`step-{phase}` + `qc-{phase}`).
5. **The conversation begins** with the AI working from its step documents.

### 6.2 Within a Step

- Normal chat: user messages, AI responses, tool calls for reference documents as needed.
- The step document and QC section remain in context (they were fetched as tool results).
- Reference SOPs fetched on demand persist in the conversation history for the remainder of the step.
- **No rolling summarization within a step** (see Section 7 for why).

### 6.3 Step Completion

1. The investigator reviews the step output and clicks **"Approve and Continue"**.
2. **Opus generates a structured summary** of the step (see Section 8 for the summary template).
3. The summary is stored in the conversation document.
4. **Context resets:** All conversation history from the completed step is dropped from the API payload. All tool exchange messages (including fetched SOPs) are dropped. The step document is dropped.
5. **Step N+1 begins** with: Tier 1 docs + fresh case data + all previous step summaries + clean conversation history.
6. The AI reads the routing table and fetches the next step's documents.

### 6.4 Context Budget Per Step

| Component | Tokens (estimated) |
|-----------|-------------------|
| Tier 1 always-loaded (persona, general rules, escalation, routing table, index) | 30-35K |
| Step document (fetched via tool call) | 6-22K (varies — Analysis is heaviest) |
| Step QC section (fetched via tool call) | 1.5-4K |
| Case data (reinjected) | 10-15K |
| Previous step summaries | 0-6K (0 for Step 1, ~2K per completed step) |
| Conversation history (current step only) | 5-15K (resets at boundary) |
| Reference SOPs fetched during this step | 0-15K |
| **Typical total at busiest point** | **55-75K** |

Compare: current architecture reaches 140-160K. This stays under half the context window at all times, comfortably within Sonnet's reliable operating range.

---

## 7. Why Not Rolling Summarization Within Steps?

The previous `ROLLING-SUMMARIZATION-IMPL.md` planned token-budget rolling summarization that could trigger mid-conversation. With step-based compression, this creates a problem:

**The collision:** If rolling summarization triggers mid-step, it compresses the tool exchange messages that delivered the step document. The AI loses the detailed instructions it's currently working from.

**Solutions considered:**
- **Summary-aware document re-injection** — after compressing, reload the active step document. Complex: the summary function needs to know which documents are active, and the re-injection adds tokens.
- **Token threshold with re-injection** — compress at a token cap, then re-fetch. Adds complexity for an edge case.

**Decision:** Avoid the problem entirely. Steps are short enough (typically 5-10 exchanges) that context won't hit dangerous levels within a single step. The step boundary is the natural compression point.

**Safety valve:** If a step somehow runs extremely long (20+ exchanges, unusual case), the system can warn the investigator that context is growing and suggest completing the step. This is a UI warning, not automatic compression. In practice, this should be rare — the step structure naturally keeps conversations focused.

---

## 8. Step Summary — Template and Generation

When the investigator approves a step, Opus generates a structured summary. This summary becomes context for all subsequent steps. Quality is critical — if the summary misses an important finding, subsequent steps lose access to it.

### 8.1 Summary Template

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
[Which SOPs/guidelines were retrieved and the specific guidance applied from each]

### Open Questions
[Anything flagged for investigation in subsequent steps]

### Case Form Sections Completed
[Which sections of the case template were drafted and approved]
```

### 8.2 Summary Generation

- **Model:** Opus. One call per step boundary (4 per case maximum). The summary quality justifies the stronger model.
- **Non-streaming.** This is a single structured output, not interactive.
- **Max tokens:** 3,000. A well-structured step summary should be 1,000-2,500 tokens.
- **Input:** The full conversation history from the completed step (all messages, including tool exchanges).
- **The summary prompt** instructs Opus to preserve all factual findings, decisions, rationale, and open items. It must not redundantly restate case data (the AI always gets fresh case data). It must capture the essence of any SOPs that were consulted — the specific rules applied and outcomes, not the full SOP text.

### 8.3 Summarization System Prompt

```
You are summarizing one step of a financial crime investigation. Your summary will
be provided to a fresh AI instance that continues the investigation in the next step.
The fresh instance will NOT have access to this step's conversation — only this summary
and the most recent step's conversation.

MUST PRESERVE:
- All factual findings: transaction amounts, dates, addresses, counterparties, risk
  indicators, patterns identified
- All decisions and their rationale (classification, risk level, escalation decisions)
- Key conclusions from reference documents consulted — the specific rules/criteria
  applied and their outcomes
- What investigation steps have been completed and what remains
- Any open questions, flags, or items deferred for later steps
- Investigator instructions or preferences stated during this step
- KYC verification results and identity discrepancies
- Specific numerical thresholds or values that informed decisions

MUST NOT PRESERVE:
- Full text of retrieved SOPs — only the relevant findings and rules applied
- Conversational filler, acknowledgments
- Redundant restatement of case data (the AI always has fresh case data)
- Step-by-step reasoning process if the conclusion is clear

FORMAT:
Use the structured template provided. Be thorough but concise. Target 1,000-2,500
tokens. Up to 3,000 for complex steps with many findings.
```

---

## 9. Dual Model Routing

| Context | Model | Rationale |
|---------|-------|-----------|
| Investigation: within a step | Sonnet | Lean, focused context. Reliable when payload is well-structured and under 80K. Cost-effective for daily volume. |
| Investigation: step summary generation | Opus | One call per step (4 per case). Summary quality is critical — subsequent steps depend on it. |
| Free chat mode | Opus | Full payload, unpredictable queries. Needs the more capable model. |

### 9.1 Cost Estimate

**Investigation mode (per case):**
- Sonnet calls: ~20-25 calls across 4 steps, at 55-75K context. Relatively cheap.
- Opus calls: 4 summary calls (one per step boundary). Small input, structured output. Modest.
- Estimated total per case: ~$0.50-1.50 depending on complexity.

**Monthly budget at $1,000:**
- At $1/case, 10 cases/day, 20 working days = $200/month per investigator.
- Leaves room for 3-5 investigators plus free chat.

### 9.2 Backend Implementation

The existing `ai_client.py` already accepts a `model` parameter. Routing logic:

```python
if mode == "investigation":
    if generating_step_summary:
        model = "claude-opus-4-6"
    else:
        model = "claude-sonnet-4-6"
elif mode == "free_chat":
    model = "claude-opus-4-6"
```

---

## 10. Auto-Execute Mode ("Full Case Review")

A mode where the AI runs through all four steps automatically without investigator input between steps.

### 10.1 How It Works

1. Investigator opens a case and selects "Full Case Review".
2. **Step 1:** AI loads Step 1 documents, runs through Setup, produces output.
3. **Automatic transition:** System generates Opus summary of Step 1.
4. **Step 2:** Fresh context, AI loads Step 2 documents, runs Analysis.
5. Repeat through Steps 3 and 4.
6. AI loads `qc-full`, runs a complete QC check.
7. Complete case output is presented to the investigator for review.

### 10.2 Architecture

Same step-based architecture as interactive mode. The only difference is the step transitions are automatic — the "Approve and Continue" action fires programmatically after each step completes, rather than waiting for the investigator to click.

No new infrastructure needed. The auto-execute mode is a frontend orchestration layer on top of the existing step system.

### 10.3 Error Handling

In interactive mode, the investigator can correct mistakes mid-step. In auto-execute mode, mistakes propagate. Mitigation:

- After auto-execute completes, present a **per-step review** interface where the investigator can read each step's output and the AI's QC findings.
- The investigator can accept, edit, or flag sections for re-investigation.
- If a step's output is unacceptable, the investigator can re-run that single step interactively.

This is a v2 feature. Build the interactive step system first, validate it works, then add auto-execute as an orchestration layer.

---

## 11. UI Design

### 11.1 Investigation View — Continuous Chat with Step Dividers

The investigator sees one continuous conversation for the entire case. Step transitions happen in the backend, but the UI does not clear or separate the chat.

When the investigator clicks "Approve and Continue":
1. Opus generates the structured summary.
2. A visual divider is inserted: "Step 1 (Setup) complete. Context summarised for Step 2: Analysis."
3. The AI's next response comes from fresh context, but the investigator sees it as a continuation.
4. Step indicator updates in the header (e.g., "Step 2 of 4: Analysis").

The investigator can scroll up to see everything from earlier steps. The AI cannot see messages from previous steps — it works from the summary.

### 11.2 Step Summaries in Case Data Panel

Completed step summaries appear as tabs in the case data panel (e.g., "Step 1 Summary"). Quick access without scrolling through chat history.

### 11.3 PDF Export

Renders the full continuous chat with step dividers as section markers. Step summaries included inline at each divider. Reads as a complete investigation from start to finish.

### 11.4 Context Warning

If a step's conversation grows unusually long (approaching a configurable token threshold), show a subtle warning: "This step has a long conversation. Consider completing it to preserve context quality." This is advisory only — no automatic action.

---

## 12. MongoDB Schema

All messages live in a single conversation document. Each message is tagged with its step number.

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
        "summary": "## Step 1 Summary: Setup\n\n### Case Classification\n...",
        "summary_model": "claude-opus-4-6",
        "summary_token_usage": { "input_tokens": 65000, "output_tokens": 1200 },
        "completed_at": "2026-03-05T10:15:00Z",
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
      "message_id": "msg_002",
      "role": "assistant",
      "step": 1,
      "content": "## Initial Assessment\n...",
      "visible": true
    },
    {
      "message_id": "msg_010",
      "role": "step_divider",
      "step": 1,
      "content": "Step 1 (Setup) complete. Context summarised for Step 2: Analysis.",
      "visible": true
    },
    {
      "message_id": "msg_011",
      "role": "assistant",
      "step": 2,
      "content": "Continuing with the analysis phase...",
      "visible": true
    }
  ],
  "status": "active",
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T10:30:00Z"
}
```

### 12.1 API Payload Assembly for Step N

When building the API payload:
1. Load Tier 1 documents (persona, general rules, escalation matrix, routing table, document index).
2. Inject fresh case data.
3. Inject summaries from all completed steps (steps 1 through N-1).
4. Include only messages where `step == N` in the conversation history.
5. Ignore all messages from previous steps (they exist in MongoDB for UI/PDF, not for the API).

The `step_divider` role is frontend-only. Never sent to the Anthropic API.

---

## 13. Knowledge Base Loader Changes

### 13.1 Current: `knowledge_base.py`

Currently loads all `core/*.md` files and formats the reference index. `get_system_prompt()` returns everything concatenated.

### 13.2 New: Investigation Mode System Prompt

A new method that returns only Tier 1 documents:

```python
def get_investigation_system_prompt(self) -> str:
    """Return the lean system prompt for investigation mode.

    Includes only always-needed documents + routing table + document index.
    Step-specific documents are fetched by the AI via tool calls.
    """
    return f"{self.persona}\n\n---\n\n{self.general_rules}\n\n---\n\n{self.escalation_matrix}\n\n---\n\n{self.routing_table}\n\n---\n\n{self.document_index_text}"
```

### 13.3 Free Chat: Unchanged

`get_system_prompt()` continues to return the full payload (all core documents, all prompt content). Free chat uses Opus and needs the full context.

### 13.4 Document Retrieval: Expanded

`get_reference_document()` is renamed to `get_investigation_document()` and its lookup expanded to include step documents, QC sections, and the decision matrix — not just reference SOPs.

The tool definition sent to the API is updated accordingly:

```python
{
    "name": "get_investigation_document",
    "description": "Retrieve an investigation document by ID. Use this to fetch step instructions, QC checklists, the decision matrix, and reference SOPs. Check the document index in your system prompt for available documents and their IDs.",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The document ID from the index (e.g., 'step-setup', 'qc-analysis', 'scam-fraud-sop')"
            }
        },
        "required": ["document_id"]
    }
}
```

---

## 14. Conversation Manager Changes

### 14.1 Step State Tracking

The conversation manager tracks which step is active. This determines:
- Which model to use (Sonnet for within-step, Opus for summaries).
- Which messages to include in the API payload (current step only).
- When to inject step summaries.

### 14.2 Step Transition Flow

```python
async def approve_and_continue(conversation_id: str, user_id: str):
    """Handle step completion: generate summary, advance to next step."""
    conversation = await db.conversations.find_one({"_id": conversation_id})
    current_step = conversation["investigation_state"]["current_step"]

    # 1. Get all messages from the current step
    step_messages = [m for m in conversation["messages"] if m["step"] == current_step]

    # 2. Generate summary with Opus
    summary = await _generate_step_summary(step_messages, current_step)

    # 3. Store summary and advance step
    await db.conversations.update_one(
        {"_id": conversation_id},
        {
            "$set": {
                f"investigation_state.steps.{current_step - 1}.status": "completed",
                f"investigation_state.steps.{current_step - 1}.summary": summary,
                f"investigation_state.steps.{current_step - 1}.completed_at": _now(),
                f"investigation_state.steps.{current_step - 1}.approved_by": user_id,
                "investigation_state.current_step": current_step + 1,
            }
        }
    )

    # 4. Insert step divider message
    divider = {
        "message_id": _generate_id(),
        "role": "step_divider",
        "step": current_step,
        "content": f"Step {current_step} ({STEP_PHASES[current_step]}) complete. "
                   f"Context summarised for Step {current_step + 1}: {STEP_PHASES[current_step + 1]}.",
        "visible": True,
    }
    await db.conversations.update_one(
        {"_id": conversation_id},
        {"$push": {"messages": divider}}
    )
```

### 14.3 API Message Assembly

```python
def _rebuild_api_messages(
    conversation: dict,
) -> list[dict]:
    """Rebuild API messages for the current step only."""
    state = conversation["investigation_state"]
    current_step = state["current_step"]
    api_messages = []

    # Inject summaries from all completed steps
    completed_summaries = []
    for step_info in state["steps"]:
        if step_info["status"] == "completed" and step_info["summary"]:
            completed_summaries.append(step_info["summary"])

    if completed_summaries:
        summary_text = "\n\n---\n\n".join(completed_summaries)
        api_messages.append({
            "role": "user",
            "content": (
                "[PREVIOUS STEP SUMMARIES — These summarise the investigation "
                "progress from earlier steps. The original case data is provided "
                "separately.]\n\n" + summary_text
            ),
        })
        api_messages.append({
            "role": "assistant",
            "content": "Understood. I have the context from previous steps and will continue from here.",
        })

    # Include only messages from the current step
    current_step_messages = [
        m for m in conversation["messages"] if m.get("step") == current_step
    ]

    for msg in current_step_messages:
        # ... existing message rebuild logic (unchanged) ...
        pass

    return api_messages
```

---

## 15. Implementation Order

### Phase A: Knowledge Base Restructuring (no code changes)

1. **Split QC checklist** into 4 step-aligned files in `knowledge_base/qc/`.
2. **Write the routing table** document.
3. **Expand the document index** YAML to include step docs, QC sections, decision matrix.
4. **Remove prompt-library.md** from core (or strip it to investigation-only prompts if any remain).

Content tasks. No backend or frontend changes. Can be validated by reading.

### Phase B: Loader and Tool Changes

5. **Add `get_investigation_system_prompt()`** to `knowledge_base.py`.
6. **Expand `get_investigation_document()`** to serve step docs, QC sections, and decision matrix.
7. **Update the tool definition** in `ai_client.py` (rename, update description).
8. **Verify free chat still works** (uses `get_system_prompt()`, unchanged).

### Phase C: Step Architecture (Backend)

9. **Add `investigation_state` to conversation schema** in MongoDB.
10. **Add step tracking** to conversation creation (investigation mode starts at Step 1).
11. **Modify `_rebuild_api_messages()`** to filter by current step and inject summaries.
12. **Add `approve_and_continue()`** endpoint/method.
13. **Add Opus summary generation** (`_generate_step_summary()`).
14. **Add model routing** (Sonnet within step, Opus for summaries).

### Phase D: Frontend

15. **Step indicator** in investigation header.
16. **"Approve and Continue" button** at step completion.
17. **Step divider messages** in chat stream.
18. **Step summaries** as tabs in case data panel.
19. **Context length warning** (advisory, non-blocking).

### Phase E: Auto-Execute Mode (v2)

20. **Frontend orchestration** — automatic step transitions.
21. **Per-step review interface** after auto-execution.
22. **Re-run single step** capability.

### Phase F: Verification

23. **Test with demo cases** — validate Sonnet reliability with lean context.
24. **Validate summary quality** — Opus summaries must preserve all critical information.
25. **Compare outputs** — run the same case in old (full context) and new (step-based) modes.
26. **Measure token usage** — confirm the expected reductions.

---

## 16. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI fails to fetch step documents via tool call | Investigation starts without instructions | Routing table is explicit. If the AI doesn't fetch on first turn, the system prompt contains a fallback instruction: "You MUST fetch your step documents before proceeding." Can also auto-inject a first user message that triggers the fetch. |
| Summary loses critical information | Next step AI makes decisions without key context | Opus for summaries. Structured template forces coverage. Investigator reviews summary at step boundary. |
| A single step runs too long for context | Quality degradation within step | Advisory context warning. Step structure naturally limits conversation length. Worst case: investigator manually splits work. |
| Sonnet struggles with complex analysis even at 70K context | Lower quality outputs than Opus | Fallback: configurable model override per step. Step 2 (Analysis, heaviest) could use Opus if needed. |
| Document fetching adds latency (extra API round-trip for tool call) | Slower first response per step | One tool call at step start. Latency is ~2-3s. Acceptable for a step transition that happens 4 times per case. |

---

## 17. Files Changed (Summary)

| File | Change |
|------|--------|
| `knowledge_base/qc/qc-setup.md` | **NEW** — QC checks for Step 1 |
| `knowledge_base/qc/qc-analysis.md` | **NEW** — QC checks for Step 2 |
| `knowledge_base/qc/qc-decision.md` | **NEW** — QC checks for Step 3 |
| `knowledge_base/qc/qc-post.md` | **NEW** — QC checks for Step 4 |
| `knowledge_base/core/routing-table.md` | **NEW** — Step routing instructions |
| `knowledge_base/reference-index.yaml` | **MODIFY** — Add step docs, QC sections, decision matrix |
| `server/services/knowledge_base.py` | **MODIFY** — Add `get_investigation_system_prompt()`, expand document retrieval |
| `server/services/ai_client.py` | **MODIFY** — Update tool definition, add model routing |
| `server/services/conversation_manager.py` | **MODIFY** — Step state tracking, filtered message assembly, summary generation, step transitions |
| `server/routers/conversations.py` | **MODIFY** — Add `approve_and_continue` endpoint |
| `client/src/pages/InvestigationPage.jsx` | **MODIFY** — Step indicator, approve button, dividers |
| `client/src/components/investigation/*` | **MODIFY** — Step summary tabs, context warning |

### Files NOT Changed
- `knowledge_base/core/qc-submission-checklist.md` — stays as-is for full QC tool call.
- `knowledge_base/core/SYSTEM-PROMPT.md` — stays (Tier 1).
- `knowledge_base/core/icr-general-rules.md` — stays (Tier 1).
- `knowledge_base/core/mlro-escalation-matrix.md` — stays (Tier 1).
- All step documents — stay where they are, just served on-demand instead of always-loaded.
- All reference documents — unchanged.
- All ingestion code — unaffected.

---

## 18. Open Questions

1. **Prompt library disposition** — Which (if any) prompts from `prompt-library.md` are still needed in the investigation chat after preprocessing moves to ingestion? If none, the file can be removed from core entirely. If some remain, they should be embedded in the relevant step document or served on-demand.

2. **Model override per step** — Should Step 2 (Analysis, 1,584-line step doc, heaviest workload) default to Opus instead of Sonnet? Or start with Sonnet and see how it performs?

3. **Summary review** — Should the investigator see and approve the step summary before continuing? The blocked architecture plan had "Approve and Continue" which implies review. But if the summary is just infrastructure (not shown to the investigator), the UX is simpler. Recommendation: show it in a collapsible panel but don't require explicit approval of the summary text — the investigator approves the step's *work*, not the summary.

4. **General rules document** — At 572 lines, `icr-general-rules.md` is the largest Tier 1 document. Should any of its content move to on-demand? Or is it genuinely needed at every step? Needs a content review.

5. **Auto-execute scope** — Should auto-execute mode run all 4 steps, or should it stop after Step 3 (Decision) and require the investigator to handle Step 4 (Post-Decision) manually? Post-decision involves external actions (filing off-boarding, attaching screenshots) that the AI can't do.

---

*This document captures the unified architecture as of 6 March 2026. It supersedes both `FCI-Blocked-Investigation-Architecture.md` and `ROLLING-SUMMARIZATION-IMPL.md`. Those documents remain as historical reference but should not be used for implementation.*
