# FCI Investigation Platform — Blocked Investigation Architecture

**Date:** 5 March 2026
**Status:** Planning / Pre-Development
**Purpose:** Capture architectural decisions and design for the blocked investigation mode with context chunking and dual model routing. This document records the discussion and rationale so development can proceed from a clear foundation.

---

## 1. The Problem Being Solved

The current architecture sends the entire system prompt, all step documents, all case data, and the full conversation history with every API call. The context payload only ever grows throughout an investigation.

By the end of a complex case (30+ turns, reference documents retrieved, images uploaded), the total context can reach 140-160K tokens. This has three consequences:

- It pushes towards the 200K token context window limit, risking degradation on long cases.
- It requires Opus to reliably extract the right information from a large, noisy payload. Sonnet may struggle with 150K of mixed instructions, data, and conversation.
- It costs more because every token in the context is billed on every call.

## 2. The Solution: Blocked Investigation Mode

Split the investigation into four natural blocks that map to the existing case form structure:

| Block | Phase | Step Document | Focus |
|-------|-------|---------------|-------|
| 1 | Setup | icr-steps-setup.md (629 lines) | Case classification, KYC review, subject profile, initial risk assessment |
| 2 | Analysis | icr-steps-analysis.md (1,584 lines) | Transaction analysis, counterparty evaluation, wallet screening, evidence review |
| 3 | Decision | icr-steps-decision.md (739 lines) | Case outcome, classification rationale, escalation routing |
| 4 | Post | icr-steps-post.md (411 lines) | Post-decision actions, submission preparation, QC self-check |

These are not artificial boundaries. They map directly to how the investigation methodology is already structured in the SOPs and the case form.

### 2.1 How It Works

1. The investigator opens a case. Block 1 starts automatically.
2. The AI loads only the context relevant to Block 1 (see Section 4 for details).
3. The investigator works through Block 1 with the AI. Normal chat, images, tool calls for reference documents.
4. When the block is complete, the investigator reviews the output and clicks an "Approve and Continue" button.
5. Opus generates a structured summary of Block 1 (see Section 5 for the summary template).
6. A fresh conversation starts for Block 2. The context is: core documents + Block 2 step documents and prompts + full case data + Block 1 summary. No conversation history from Block 1. No images from Block 1. No reference documents retrieved during Block 1.
7. This pattern repeats for Blocks 3 and 4.

### 2.2 What Gets Dropped at Each Boundary

- All conversation history from the completed block.
- All images that were uploaded during the completed block (e.g. KYC screenshots reviewed in Block 1 are not carried into Block 2).
- All reference documents retrieved via tool calls during the completed block. If the AI needs a document again in the next block, it makes a fresh tool call.
- The step document and prompt library section for the completed block (Block 2 doesn't need the setup instructions).

### 2.3 What Gets Carried Forward

- The structured summary from each completed block (1-2K tokens per summary).
- The full original case data (reinjected fresh, not from the conversation).
- Core documents that are always needed (see Section 4).

## 3. Dual Model Architecture

Two models, used for different purposes:

| Context | Model | Rationale |
|---------|-------|-----------|
| Investigation mode: within a block | Sonnet 4.6 | Lean, focused context. Sonnet is reliable when the payload is well-structured and not too large. Cost-effective for the bulk of daily volume. |
| Investigation mode: block summary generation | Opus 4.6 | One call per block transition (4 per case). The summary quality is critical because subsequent blocks depend on it. Worth paying for the stronger model. |
| Free chat mode | Opus 4.6 | Full payload, unpredictable queries. The user might ask about anything. Needs the more capable model to handle the larger, unstructured context. |

### 3.1 Cost Implications

**Investigation mode (per case, estimated):**
- Sonnet calls: 20-25 API calls across 4 blocks, at lean context sizes (55-70K tokens). Relatively cheap.
- Opus calls: 4 summary calls (one per block boundary), small input, structured output. Modest cost per call.
- Estimated total per case: approximately $0.50-1.50 depending on case complexity.

**Free chat mode:**
- Opus with full ~96K+ token payload. More expensive per call, but discretionary use rather than core workflow.

**Monthly budget at $1,000:**
- At $1 per case, 10 cases/day, 20 working days = $200/month per investigator. Leaves room for 3-5 investigators plus free chat usage within the $1,000 budget.

### 3.2 Backend Implementation

The existing `ai_client.py` already accepts a `model` parameter on every call. The routing logic is:

```
if mode == "investigation":
    if generating_block_summary:
        model = "claude-opus-4-6"    # Or whatever the SafuAPI deployment name is
    else:
        model = "claude-sonnet-4-6"
elif mode == "free_chat":
    model = "claude-opus-4-6"
```

The conversation manager needs to know the current mode and block state. This is stored in the conversation document in MongoDB alongside the existing fields.

## 4. Context Payload Per Block

### 4.1 Core Documents (Always Loaded, Every Block)

These are needed regardless of which block the investigation is in:

| Document | Lines | Reason |
|----------|-------|--------|
| SYSTEM-PROMPT.md | ~441 | AI persona and behaviour |
| icr-general-rules.md | 572 | Investigation standards, always applicable |
| decision-matrix.md | 134 | Case classification reference, needed throughout |
| qc-submission-checklist.md | 511 | QC standards, used for self-checking at every stage |
| mlro-escalation-matrix.md | 97 | Escalation criteria, could be triggered at any point |
| reference-index.yaml (formatted) | ~87 | AI needs to know what reference docs are available |

**Estimated core total:** ~45-50K tokens (the full set of always-needed documents without block-specific steps or prompts)

### 4.2 Block-Specific Documents

Each block loads only its own step document and the relevant section of the prompt library:

| Block | Step Document | Prompt Library Section | Estimated Additional Tokens |
|-------|--------------|----------------------|---------------------------|
| Block 1 (Setup) | icr-steps-setup.md | Setup prompts | ~8-10K |
| Block 2 (Analysis) | icr-steps-analysis.md | Analysis prompts | ~18-22K |
| Block 3 (Decision) | icr-steps-decision.md | Decision prompts | ~10-12K |
| Block 4 (Post) | icr-steps-post.md | Post prompts | ~6-8K |

### 4.3 Prompt Library Split

The current prompt-library.md (1,375 lines) is split into separate files:

- **prompt-library-setup.md** — prompts for Block 1 (KYC review, case classification, initial assessment)
- **prompt-library-analysis.md** — prompts for Block 2 (transaction analysis, counterparty evaluation, wallet screening)
- **prompt-library-decision.md** — prompts for Block 3 (case outcome, classification rationale, escalation)
- **prompt-library-post.md** — prompts for Block 4 (post-decision actions, submission)
- **prompt-library-preprocessing.md** — mode 2 preprocessing prompts (data extraction, chat summarisation). Retained for free chat where investigators may still want to do quick preprocessing tasks.

All files remain in the same directory. There is only one copy of each document on disk. The loader decides what gets assembled for each mode. Free chat loads all five prompt library files. Investigation mode loads only the file for the current block.

Action required: review prompt-library.md, map each prompt to its block, and split the file. This is a content task, not a code task.

### 4.4 Total Context Estimate Per Block

| Component | Tokens (estimated) |
|-----------|-------------------|
| Core documents | 45-50K |
| Block-specific steps + prompts | 8-22K (varies by block; analysis is the heaviest) |
| Case data (reinjected each block) | 10-15K |
| Previous block summaries | 0-6K (0 for Block 1, up to ~6K by Block 4) |
| Conversation history (current block only) | 5-15K (grows during the block, resets at boundary) |
| Retrieved reference documents (current block only) | 0-15K (depends on tool calls) |
| **Typical total at busiest point** | **60-75K** |

Compare this to the current approach, which can reach 140-160K by the end of a case. The chunked approach stays well under half the context window at all times.

## 5. Block Summary Template

When the investigator approves a block and clicks "Continue," Opus generates a structured summary. This summary becomes part of the context for all subsequent blocks, so its quality matters.

The summary prompt should force a consistent output format. Draft structure:

```
## Block [N] Summary: [Phase Name]

### Case Classification
[Current case type, any changes or refinements from this block]

### Key Findings
[Bullet points: the most important facts, risk indicators, and conclusions from this block]

### Decisions Made
[What was decided or confirmed: KYC status, account classification, risk level, etc.]

### Evidence Reviewed
[Which data sources were examined, what was found, what was ruled out]

### Documents Consulted
[Which reference SOPs or guidelines were retrieved and applied]

### Open Questions
[Anything flagged for investigation in subsequent blocks]

### Case Form Sections Completed
[Which sections of the case template were drafted and approved by the investigator]
```

This format gives the AI in the next block a reliable, structured starting point. It knows the classification, the findings so far, what's been decided, and what still needs to be done.

The summary should be generated by Opus with a specific prompt that instructs it to be thorough but concise, and to include anything that a fresh AI instance would need to continue the investigation without access to the original conversation.

## 6. Free Chat Mode (No Changes)

Free chat mode continues to work exactly as it does now:

- Full system prompt with all step documents, all prompts, decision matrix, everything.
- Opus model for all calls.
- No block boundaries, no summaries, no context chunking.
- Full conversation history maintained throughout.

The investigator might use free chat to explore a question about a case, discuss policy, ask about a specific SOP, or examine data in an unstructured way. The full context is needed because the query is unpredictable.

Free chat is not the primary workflow. The main daily volume is investigation mode. Free chat is a supplementary tool that investigators use when they need to think through something outside the structured case flow.

## 7. UI Changes Required

### 7.1 Investigation View — Continuous Chat with Block Dividers

The investigator should see one continuous conversation for the entire case. The block transitions happen in the backend, but the UI does not clear or separate the chat into different views. The full message history stays visible and scrollable throughout.

When the investigator clicks "Approve and Continue" at the end of a block:

1. Opus generates the structured summary (see Section 5).
2. A visual divider message is inserted into the chat stream. Something like: "Block 1 (Setup) complete. Context summarised for Block 2: Analysis." This is a system-level message, distinct from user and assistant messages.
3. The AI's next response comes from a fresh context (new block's step documents, clean history, block summaries), but the investigator sees it as a continuation of the same conversation thread.
4. Block indicator in the header or above the chat updates (e.g. "Block 2 of 4: Analysis").
5. The "Approve and Continue" button should require a deliberate action and not be triggered accidentally.

The investigator can scroll up at any time to see everything from earlier blocks. The divider messages make it clear where each block boundary is. The AI cannot see anything above the current block's divider (it's working from fresh context), but the human can.

### 7.2 Block Summaries in the Case Data Panel

When a block is completed, its summary should appear as a new tab in the case data panel on the left side (e.g. "Block 1 Summary"). This gives the investigator quick access to the structured summary without scrolling through the full chat history.

### 7.3 PDF Export

The PDF export is straightforward: it renders the full continuous chat history with block dividers included as section markers. The output reads as a complete investigation from start to finish. Block summaries can be included as appendices or inline at each divider.

## 8. MongoDB Schema Changes

Since the chat appears as one continuous conversation to the investigator, all messages live in a single conversation document. Each message is tagged with its block number so the backend knows which messages belong to the current block's context and which are from previous blocks.

```json
{
  "_id": "conv_abc123",
  "case_id": "CASE-2026-0451",
  "user_id": "user_001",
  "mode": "case",
  "investigation_state": {
    "current_block": 2,
    "blocks": [
      {
        "block_number": 1,
        "phase": "setup",
        "status": "completed",
        "summary": "## Block 1 Summary: Setup\n\n### Case Classification\n...",
        "summary_model": "claude-opus-4-6",
        "summary_token_usage": { "input_tokens": 65000, "output_tokens": 800 },
        "completed_at": "2026-03-05T10:15:00Z",
        "approved_by": "user_001"
      },
      {
        "block_number": 2,
        "phase": "analysis",
        "status": "active",
        "summary": null,
        "conversation_id": null,
        "completed_at": null,
        "approved_by": null
      }
    ]
  },
  "messages": [
    {
      "message_id": "msg_001",
      "role": "system_injected",
      "block": 1,
      "content": "[CASE DATA]\n...",
      "visible": false
    },
    {
      "message_id": "msg_002",
      "role": "assistant",
      "block": 1,
      "content": "## Initial Assessment\n...",
      "visible": true
    },
    {
      "message_id": "msg_003",
      "role": "user",
      "block": 1,
      "content": "Confirmed, KYC looks correct.",
      "visible": true
    },
    {
      "message_id": "msg_004",
      "role": "block_divider",
      "block": 1,
      "content": "Block 1 (Setup) complete. Context summarised for Block 2: Analysis.",
      "visible": true
    },
    {
      "message_id": "msg_005",
      "role": "assistant",
      "block": 2,
      "content": "Continuing with the analysis phase...",
      "visible": true
    }
  ],
  "status": "active",
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T10:30:00Z"
}
```

When building the API payload for a call during Block 2, the conversation manager:

1. Loads core documents + Block 2 step document + Block 2 prompts (cached system prompt).
2. Injects the full case data fresh (same as Block 1, reinjected not carried).
3. Injects Block 1's summary as context.
4. Includes only messages where `block == 2` in the conversation history.
5. Ignores all messages from Block 1 (they're still in the database for the UI and PDF export, but they're not sent to the API).

The `block_divider` role is a frontend-only message type. It's never sent to the Anthropic API. It exists purely for the UI to render the divider and for the PDF export to mark section boundaries.

## 9. Implementation Priority and Build Order

The block architecture should be built before the data ingestion portal, not after. The conversation manager is the core of the entire backend. Building data ingestion on top of the current unbounded architecture and then retrofitting blocks means rewriting the conversation manager and rewiring the ingestion. Building blocks first means data ingestion gets built on the final architecture.

The block architecture can be fully tested using the existing pre-staged demo cases. No real data ingestion is needed to validate the approach.

### Build Order

**Step 1: Split the prompt library file.**

The current prompt-library.md (1,375 lines) becomes multiple files:
- prompt-library-setup.md (prompts for Block 1)
- prompt-library-analysis.md (prompts for Block 2)
- prompt-library-decision.md (prompts for Block 3)
- prompt-library-post.md (prompts for Block 4)
- prompt-library-preprocessing.md (mode 2 prompts, retained for free chat use)

The four step documents (icr-steps-setup.md, icr-steps-analysis.md, icr-steps-decision.md, icr-steps-post.md) are already separate files. No change needed.

All files remain in the same directory. One copy of each document on disk. Only the loader decides what gets assembled for each mode.

**Step 2: Update the loader and verify both modes still work.**

Update `get_system_prompt()` so it reassembles all the split files into the same payload as before. Both free chat and the existing case investigation chat should work identically to today, loading from split files instead of monolithic ones.

Test thoroughly. If anything breaks at this point, it's the split that caused it, not the block architecture. This gives a clean, stable baseline before any architectural changes.

**Step 3: Add `get_block_system_prompt(block_number)` method.**

This method selects only the relevant files for a given block:
- Core documents (always loaded): system prompt, general rules, decision matrix, QC checklist, escalation matrix, reference index.
- Block-specific: the step document and prompt library section for that block number only.

Free chat continues using `get_system_prompt()` which loads everything. No change to free chat.

**Step 4: Build the block architecture in the conversation manager.**

- Block state tracking in the conversation document.
- `block` field on every message.
- Context assembly filtered by current block number.
- Case data reinjected fresh at each block boundary.
- Previous block summaries injected as context.
- Block divider messages in the UI.
- Model routing: Sonnet within blocks, Opus for summary generation.
- "Approve and Continue" button in the frontend.

Test on existing demo cases. Validate Sonnet reliability with lean context. Validate summary quality. Refine the summary template.

**Step 5: Build the data ingestion portal.**

With the block architecture stable and tested, build the ingestion UI and backend pipelines on top of the final architecture. Case data flows into a system that already knows how to chunk context, route models, and manage block state.

**Step 6: Deploy and pilot.**

Deploy to shared infrastructure. Run the controlled pilot with real investigators on real cases.

## 10. Open Questions

- **Does SafuAPI support prompt caching?** If yes, the core documents (~40-45K tokens) are cached once and reused across all blocks and all cases. If no, every call pays full price for the core documents, which increases costs.
- **What is the exact SafuAPI model deployment name for Opus?** The PRD lists `claude-opus-4-20250514-v1` as a candidate but this hasn't been confirmed.
- **Does SafuAPI support tool use?** If not, the block architecture still works but reference documents would need to be loaded statically per block based on case type rather than dynamically via tool calls.
- **Does SafuAPI support streaming?** If not, the user experience is degraded (responses appear all at once) but the block architecture is unaffected.
- **Should the investigator be able to re-open a previous block's AI context?** The continuous chat means the investigator can always scroll up and read everything from earlier blocks. But the AI in the current block can't see that history. If an investigator needs the AI to reconsider something from Block 1 while in Block 3, they would need to paste the relevant detail into the chat as a new message. This may be sufficient for the pilot. If it becomes a friction point, we can revisit.

---

*This document captures the planning discussion as of 5 March 2026. It should be reviewed and refined before implementation begins.*
