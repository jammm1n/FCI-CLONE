# Prompt & Knowledge Base Cleanup Plan

## Context
Ingestion→Investigation pipeline complete (March 2026). All preprocessing now handled by ingestion. The core KB loads ~90K tokens into every conversation. Priority: reduce token overhead before implementing block-aware context (see `reference-docs/CONTEXT-MANAGEMENT-PLAN.md`).

## Current Core KB (loaded every turn, ~90K tokens)
| Document | Lines | ~Tokens |
|----------|-------|---------|
| SYSTEM-PROMPT.md | 441 | 6K |
| icr-general-rules.md | 572 | 8K |
| icr-steps-setup.md | 629 | 9K |
| icr-steps-analysis.md | 1,584 | 22K |
| icr-steps-decision.md | 739 | 10K |
| icr-steps-post.md | 411 | 6K |
| prompt-library.md | 1,375 | 19K |
| decision-matrix.md | 134 | 2K |
| mlro-escalation-matrix.md | 97 | 1.5K |
| qc-submission-checklist.md | 511 | 7K |

## Work Order

### Phase 1: Prompt Library (~19K tokens — biggest win)

**Action:** Read every prompt in `knowledge_base/core/prompt-library.md` and cross-reference against ingestion prompts in `knowledge_base/prompts/`. Produce disposition per prompt:

Ingestion prompts that REPLACE prompt-library entries:
- Prompt #1 (Transaction Analysis) → `prompt-01-transaction-analysis.md`
- Prompt #3 (Account Blocks) → `prompt-03-account-blocks.md`
- Prompt #4 (Prior ICR) → `prompt-04-prior-icr.md`
- Prompt #5 (Scam/L1) → `prompt-20-l1-referral.md`
- Prompt #6 (CTM Standard) → `prompt-06-ctm-alerts.md`
- Prompt #7 (Privacy Coin) → `prompt-07-privacy-coin.md`
- Prompt #8 (Failed Fiat) → `prompt-08-failed-fiat.md`
- Prompt #9E (Device Extraction) → `prompt-17-device-ip-ingestion.md`
- Prompt #10 (RFI Summary) → `prompt-10-rfi-summary.md`
- Prompt #12 (Counterparty) → `prompt-19-counterparty-ingestion.md`
- Prompt #14E (Elliptic Extraction) → handled by elliptic_processor
- Prompt #15E (LE/Kodex Extraction) → `prompt-15e-kodex-per-case.md` + `prompt-15e-kodex-summary.md`
- Prompt #16E (Case Intake) → handled by ingestion case creation
- Prompt #13 (KYC) → `prompt-13-kyc-document.md`

Prompts that MAY still be needed during investigation chat:
- **Prompt #11 (Summary of Investigation)** — No ingestion equivalent. Used at Step 20 to generate executive summary from all prior outputs. KEEP or embed in icr-steps-decision.md.
- **Prompt #2 (CTM Enhanced)** — Specific flagged transaction analysis. May be needed if investigator asks AI to re-analyze specific CTM alerts during chat. EVALUATE.
- **Prompt #9 (Device narrative, not extraction)** — Narrative version vs extraction. Ingestion does extraction; investigation chat may need narrative guidance. EVALUATE.

**Disposition options per prompt:**
1. **REMOVE** — ingestion handles preprocessing entirely
2. **EXTRACT OUTPUT SPEC** — keep only the output format/structure description (what good ICR narrative looks like for this section), embed in relevant step document
3. **KEEP** — no ingestion equivalent, needed during investigation

**Expected outcome:** Replace 1,375-line prompt-library.md with either nothing (if all output specs embedded in step docs) or a ~100-line "ICR output format reference" document.

### Phase 2: System Prompt Cleanup

`SYSTEM-PROMPT.md` (441 lines) has overlap with other docs:

**Overlaps to resolve:**
- Currency display rule → also in general-rules + prompt-library global rules
- Risk position requirement → also in general-rules + step docs + QC
- "No pending language" → also in general-rules + decision steps
- Operational Lessons OL-1 through OL-11 → many restate Decision Matrix rules
- Mode detection (Full Walkthrough vs Standalone) → may be obsolete now that ingestion handles data processing
- Phase 0 (Narrative First) → could move to step-setup
- Pacing rules → could move to step docs

**Target:** Strip to ~150-200 lines covering ONLY:
- AI identity and persona
- Behavioral rules (voice, tone, formatting)
- Document hierarchy (5-tier priority)
- Compact routing/index reference (what docs exist, when to fetch them)

Everything procedural moves to step docs or general rules.

### Phase 3: De-duplicate Steps vs Rules

Cross-cutting repetition to resolve:
- Currency display: lives in ONE place (general-rules), referenced elsewhere
- Risk position: lives in ONE place (general-rules), referenced elsewhere
- RFI rules: primary home in decision steps, cross-ref from general-rules
- Offboarding rules: primary home in post steps, cross-ref from decision
- Template cleanup: primary home in QC, not restated in steps
- Language rules: primary home in system prompt or general-rules

**Principle:** Each piece of guidance has ONE authoritative location. Other documents reference it, don't restate it.

### Phase 4: Block-Aware Context Architecture

Only after Phases 1-3 complete. Full plan in `reference-docs/CONTEXT-MANAGEMENT-PLAN.md`. Key elements:
- Step-based document loading (4 investigation phases)
- Tier 1 always-loaded: SYSTEM-PROMPT + general-rules + escalation-matrix + routing-table + index (~30-35K)
- Step docs fetched on-demand via tool calls
- QC checklist split into 4 step-aligned files
- Step boundary compression (Opus summary, context reset)
- Sonnet for within-step, Opus for summaries
- Target: <80K tokens per API call (down from 140-160K)

## Key Files
- Core KB: `knowledge_base/core/` (10 files)
- Ingestion prompts: `knowledge_base/prompts/` (16 files)
- Context plan: `reference-docs/CONTEXT-MANAGEMENT-PLAN.md`
- KB loader: `server/services/knowledge_base.py`
- System prompt assembly: `knowledge_base.py` → `get_system_prompt()` concatenates all core files
