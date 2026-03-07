# Knowledge Base Cleanup — Implementation Plan

## Scope
Case Investigation chat only. Free Chat is parked for later.

## Goal
Make the Case Investigation AI lean, non-repetitive, and self-contained in the step docs. Every piece of guidance has ONE authoritative location. The AI can work through an entire case using only the loaded documents without scattered cross-references.

## Current State (loaded every turn, ~90K tokens)
| File | Lines | ~Tokens |
|------|-------|---------|
| SYSTEM-PROMPT.md | 442 | 6,000 |
| icr-general-rules.md | 573 | 5,000 |
| icr-steps-setup.md | 629 | 9,000 |
| icr-steps-analysis.md | 1,584 | 22,000 |
| icr-steps-decision.md | 739 | 10,000 |
| icr-steps-post.md | 411 | 6,000 |
| prompt-library.md | 1,375 | 19,000 |
| decision-matrix.md | 135 | 6,000 |
| mlro-escalation-matrix.md | 98 | 1,400 |
| qc-submission-checklist.md | 512 | 5,000 |
| **TOTAL** | **~6,498** | **~89,400** |

## Target State
| File | Estimated Tokens | Change |
|------|-----------------|--------|
| SYSTEM-PROMPT.md | ~1,500 | Radical trim — identity, voice, hierarchy only |
| icr-general-rules.md | ~4,000 | De-duplicate, remove what moved to step docs |
| icr-steps-setup.md | ~11,000 | Gains Phase 0, corporate/HPI/KOL detection, express mode |
| icr-steps-analysis.md | ~23,000 | Gains Elliptic output spec (14E), inline output specs |
| icr-steps-decision.md | ~11,000 | Gains Summary prompt (#11), pre-decision check, pre-submission |
| icr-steps-post.md | ~6,500 | Gains offboarding rules currently in general-rules |
| prompt-library.md | 0 | DELETED |
| decision-matrix.md | ~5,500 | Remove rules that duplicate other docs |
| mlro-escalation-matrix.md | ~1,400 | Unchanged |
| qc-submission-checklist.md | ~5,000 | Unchanged (externally maintained) |
| **TOTAL** | **~68,900** | **~20K reduction** |

---

## PHASE 1: DELETE prompt-library.md

### Pre-condition
Verify every prompt is accounted for before deletion.

### Prompt Disposition Table

| # | Name | Lines in library | Disposition | Detail |
|---|------|-----------------|-------------|--------|
| Global Rules | Formatting rules | 8-23 | DELETE | Already in `icr-general-rules.md` |
| 1 | Transaction Analysis | 27-102 | DELETE | Exact duplicate of `prompts/prompt-01-transaction-analysis.md`. Step 7 already has output spec. |
| 2 | CTM Enhanced | 103-157 | EXTRACT to reference tier | Create `knowledge_base/reference/prompt-02-ctm-enhanced.md`. Rarely used. Step 8 already says "if snapshot of suspicious transactions, use Prompt #2" — update that reference to point to fetchable doc. |
| 3 | Account Blocks | 158-199 | DELETE | Exact duplicate of `prompts/prompt-03-account-blocks.md`. Step 3 already has output spec. |
| 4 | Prior ICR | 200-228 | DELETE | Exact duplicate of `prompts/prompt-04-prior-icr.md`. Step 5 already has output spec. |
| 5 | Scam/P2P | 229-249 | DELETE | Scam identification logic to be absorbed into `prompts/prompt-23-l1-communications.md` (future task — not part of this cleanup). |
| 6 | CTM Standard | 250-295 | DELETE | Exact duplicate of `prompts/prompt-06-ctm-alerts.md`. Step 8 already has output spec. |
| 7 | Privacy Coin | 296-335 | DELETE | Exact duplicate of `prompts/prompt-07-privacy-coin.md`. Step 11 already has output spec. |
| 8 | Failed Fiat | 336-377 | DELETE | Exact duplicate of `prompts/prompt-08-failed-fiat.md`. Step 13 already has output spec. |
| 9 | Device & IP (narrative) | 378-425 | DELETE | Step 14 already has full output spec for device narrative. |
| 10 | RFI Summary | 426-453 | DELETE | Exact duplicate of `prompts/prompt-10-rfi-summary.md`. Step 15 already has output spec. |
| 11 | Summary of Investigation | 454-521 | EMBED | Move output spec into Step 20 Part B of `icr-steps-decision.md`. See Phase 3 for detail. |
| 12 | Counterparty Analysis | 522-630 | DELETE | Step 12 already has output spec. Ingestion uses `prompts/prompt-19-counterparty-ingestion.md`. |
| 13 | KYB Summary | 631-671 | EMBED | Move corporate KYB output spec into Step 2 corporate handling in `icr-steps-setup.md`. See Phase 3 for detail. |
| — | Mode 2 intro | 672-679 | DELETE | Obsolete — ingestion handles Mode 2. |
| 9E | Device Extraction | 680-783 | DELETE | Ingestion uses `prompts/prompt-17-device-ip-ingestion.md`. Not needed in investigation chat. |
| 14E | Elliptic Top Addresses | 784-1018 | EMBED | Move output spec into Steps 9-10 of `icr-steps-analysis.md`. See Phase 3 for detail. |
| 15E | LE/Kodex Extraction | 1019-1170 | DELETE | Ingestion uses `prompts/prompt-15e-kodex-per-case.md` + `prompt-15e-kodex-summary.md`. Not needed in investigation chat. |
| 16E | Case Intake | 1171-1375 | EXTRACT to reference tier | Create `knowledge_base/reference/prompt-16e-case-intake.md`. Niche utility. Not needed in standard investigation flow. |

### Execution Steps
1. Read `prompt-library.md` lines 454-521 (Prompt #11). Extract the output spec content.
2. Read `prompt-library.md` lines 631-671 (Prompt #13 KYB). Extract the output spec content.
3. Read `prompt-library.md` lines 784-1018 (Prompt #14E Elliptic). Extract the output spec content.
4. Read `prompt-library.md` lines 103-157 (Prompt #2 CTM Enhanced). Save as `knowledge_base/reference/prompt-02-ctm-enhanced.md`.
5. Read `prompt-library.md` lines 1171-1375 (Prompt #16E Case Intake). Save as `knowledge_base/reference/prompt-16e-case-intake.md`.
6. Embed extracted content per Phase 3 instructions.
7. Delete `knowledge_base/core/prompt-library.md`.

### Verification
After deletion, confirm:
- [ ] Every prompt # from 1-16E is accounted for (individual file, embedded in step doc, or reference tier)
- [ ] No step doc still says "Execute Prompt #X" without the spec being inline or the prompt being fetchable
- [ ] Individual prompt files in `knowledge_base/prompts/` are untouched (ingestion uses them)

---

## PHASE 2: TRIM SYSTEM-PROMPT.md

### What STAYS (target ~60-80 lines, ~1,500 tokens)

**Section 1: Identity & Role (~5 lines)**
- "You are FCI-GPT, a Senior Compliance Investigator copilot..."
- Remove Mode 1/Mode 2 distinction. Just state: assists investigators with case investigations.

**Section 2: Document Hierarchy (~15 lines)**
- Priority order (System Prompt > Decision Matrix > Step Docs > General Rules > SOPs)
- List of available documents (names only, not full descriptions)
- Reference tier access via tool call

**Section 3: Voice & Tone (~25 lines)**
- Passive/objective voice rules (no "I", "We", "investigator")
- "Elliptic" capitalisation
- Currency Display Rule (one line: "All non-USD amounts must include USD equivalent in square brackets")
- Plain Language Rule
- "Pending" prohibition (one line — not a paragraph)
- Formatting Consistency Rule (short paragraph format, no headings/bullets within ICR boxes)
- Narrative Balance Rule (risk indicators paired with mitigating context)
- Brevity Principle (write only what's necessary)

**Section 4: FCI/FCMI Terminology (~2 lines)**

### What MOVES to `icr-steps-setup.md`

These sections move to a new "PRE-INVESTIGATION" or "PHASE 0" section at the top of `icr-steps-setup.md`, before Step 1:

| Section | Current Lines | Destination |
|---------|--------------|-------------|
| Phase 0: Narrative First | 177-211 | `icr-steps-setup.md` — new "Phase 0" section |
| Corporate Account Detection | 129-162 | `icr-steps-setup.md` — within Phase 0 (detection triggers) |
| HPI Detection | 164-168 | `icr-steps-setup.md` — within Phase 0 (detection triggers) |
| KOL Detection | 170-175 | `icr-steps-setup.md` — within Phase 0 (detection triggers) |
| Express Mode definition + block groupings | 230-322 (within Pacing Rules) | `icr-steps-setup.md` — new "EXPRESS MODE" section after Phase 0 |
| Standard Mode pacing (Rules 1-3) | 213-229 | `icr-steps-setup.md` — alongside express mode as "STANDARD MODE" |

### What MOVES to `icr-steps-decision.md`

| Section | Current Lines | Destination |
|---------|--------------|-------------|
| Pre-Decision Check (Step 21 Gate) | 399-414 | `icr-steps-decision.md` — prepend to Step 21 |
| Pre-Submission Verification (Phase 2) | 416-432 | `icr-steps-decision.md` — new section after Step 21 |

### What is DELETED (redundant or obsolete)

| Section | Current Lines | Reason |
|---------|--------------|--------|
| Mode Detection Gate + trigger phrase mapping | 57-105 | Obsolete — ingestion handles Mode 2. Case Investigation is always Mode 1. |
| Parallel Chat Data Integration | 324-342 | Obsolete — ingestion handles all data processing. No more parallel chats. |
| Knowledge Extraction Mode | 344-367 | Utility feature — not part of case investigation. Can be resurrected for Free Chat later if needed. |
| Operational Lessons OL-1 to OL-11 | 369-397 | Each one cross-checked and either already exists in decision matrix/step docs or moved there. See OL disposition below. |
| Data Handling: Hexa Protocol | 107-127 | Already in `icr-general-rules.md`. Delete from system prompt. |
| Source of Truth Hierarchy | 49-55 | Already in `icr-general-rules.md`. Delete from system prompt. |

### Operational Lessons Disposition

Each OL is checked against existing documents. If it already exists elsewhere, delete from system prompt. If unique, move to the correct home.

| OL | Content | Already Exists In | Action |
|----|---------|-------------------|--------|
| OL-1 | Unusual Transaction Totals — only current L1 referral | Step 20 Part A already has this as "CRITICAL RULE" | DELETE from system prompt |
| OL-2 | Focus on New Activity (prior ICR scoping) | Step 5 (Prior ICR) covers this | DELETE — verify Step 5 has equivalent, add if not |
| OL-3 | RFI Response Check Before Closure | `icr-general-rules.md` already has this | DELETE from system prompt |
| OL-4 | Proportional Detail | Brevity Principle in Voice & Tone (staying in system prompt) covers this | DELETE — it's the same concept |
| OL-5 | No Reporting References (SAR/STR) | Step 21 already has this in language rules | DELETE from system prompt |
| OL-6 | Offboarding Threshold (hard evidence) | Decision Matrix Rule #58 + Step 21 | DELETE from system prompt |
| OL-7 | SLA Awareness | `icr-general-rules.md` SLA Framework section | DELETE from system prompt |
| OL-8 | Prior RFIs From Other Departments | Step 18/19 RFI handling | VERIFY exists in step docs — add to Step 19 if not |
| OL-9 | Existing RFI Covers Current Case | Decision Matrix Rule #47 area | VERIFY exists — add to Step 18 if not |
| OL-10 | Case Rejection Restrictions | `icr-general-rules.md` already has this | DELETE from system prompt |
| OL-11 | Risk Appetite Calibration | Decision Matrix Rule #58 | DELETE from system prompt |

### Execution Steps
1. Read current SYSTEM-PROMPT.md in full.
2. Write new lean SYSTEM-PROMPT.md (~60-80 lines) with Sections 1-4 above.
3. Read `icr-steps-setup.md` to understand current structure.
4. Edit `icr-steps-setup.md`: insert Phase 0, detection triggers, and express/standard mode sections before Step 1.
5. Read `icr-steps-decision.md` to understand current structure.
6. Edit `icr-steps-decision.md`: prepend Pre-Decision Check to Step 21, add Pre-Submission Verification after Step 21.
7. For each OL marked "VERIFY": check the target document. If the rule is missing, add it. If present, confirm and delete OL.

### Verification
- [ ] New system prompt is under 80 lines
- [ ] No procedural workflow instructions remain in system prompt
- [ ] Phase 0 + detection triggers are in `icr-steps-setup.md`
- [ ] Express mode block definitions are in `icr-steps-setup.md`
- [ ] Pre-Decision Check is in `icr-steps-decision.md` Step 21
- [ ] Pre-Submission Verification is in `icr-steps-decision.md`
- [ ] Every OL either confirmed in its target doc or moved there
- [ ] No content lost — everything accounted for

---

## PHASE 3: EMBED OUTPUT SPECS IN STEP DOCS

Three prompts have output specs that need embedding in step docs.

### 3A: Prompt #11 (Summary of Investigation) -> Step 20 Part B

**Source:** `prompt-library.md` lines 454-521
**Target:** `icr-steps-decision.md` Step 20 Part B

Step 20 Part B already has substantial spec (two paragraphs, 150-200 words, mandatory risk position). Compare the existing Step 20 Part B spec against Prompt #11 content:
- If Step 20 Part B already covers everything in Prompt #11: no changes needed, just delete the prompt.
- If Prompt #11 has additional detail (e.g., specific section-by-section summary instructions): merge that detail into the Step 20 Part B spec.

**Execution:**
1. Read Prompt #11 from prompt-library.md (lines 454-521).
2. Read Step 20 Part B from icr-steps-decision.md.
3. Compare. Identify any unique content in Prompt #11 not already in Step 20 Part B.
4. If unique content exists, edit `icr-steps-decision.md` to incorporate it into Step 20 Part B.

### 3B: Prompt #13 KYB (Corporate KYB Summary) -> Step 2

**Source:** `prompt-library.md` lines 631-671
**Target:** `icr-steps-setup.md` Step 2 (corporate handling section)

Step 2 already has corporate KYB handling (modify Hexa in-place, append UBO paragraph). Compare against Prompt #13 KYB:
- Prompt #13 KYB specifies: company name, incorporation date, registry number, addresses, UBOs (names/nationalities), 2-3 sentence business summary, passive compliance voice, 60-80 words.
- Check if Step 2 already has this level of detail.

**Execution:**
1. Read Prompt #13 KYB from prompt-library.md (lines 631-671).
2. Read Step 2 corporate section from icr-steps-setup.md.
3. Compare. Merge any additional output spec from Prompt #13 into Step 2.

### 3C: Prompt #14E (Elliptic Top Addresses) -> Steps 9-10

**Source:** `prompt-library.md` lines 784-1018
**Target:** `icr-steps-analysis.md` Steps 9 and 10

This is the largest embed (~235 lines, ~3,800 tokens). Steps 9-10 already have detailed specs (Robert's Rule, risk score thresholds, high-risk wallet documentation). However, Prompt 14E has structured extraction output format (wallet screening table, 12 fields per wallet, summary statistics, UOL cross-reference, flags list).

Key question: The investigation AI receives preprocessed Elliptic data, but until the API is wired up, the AI may still need to process screenshots. The output spec for what the AI should WRITE in the ICR (narrative, not extraction tables) is already in Steps 9-10. The extraction format in 14E is for preprocessing.

**Decision:** Only embed the parts of 14E that define what the final ICR narrative should look like. Skip the extraction table format (that's ingestion's job, or temporary screenshot processing).

**Execution:**
1. Read Prompt #14E from prompt-library.md (lines 784-1018).
2. Read Steps 9-10 from icr-steps-analysis.md.
3. Identify any OUTPUT NARRATIVE specs in 14E not already in Steps 9-10.
4. Embed only narrative-relevant specs. Skip extraction table formats.

---

## PHASE 4: DE-DUPLICATE icr-general-rules.md AND decision-matrix.md

### QC Checklist
**Leave unchanged.** Externally maintained by QC department. Accept duplication with this file.

### Rules to de-duplicate

For each rule below: keep it in ONE authoritative location, delete from others. Where the rule is deleted, optionally add a one-line reference like "See [document] for [rule name]" ONLY if the context makes it necessary. Do not add references everywhere — the AI reads all docs anyway.

| Rule | KEEP in (authoritative) | DELETE from |
|------|------------------------|-------------|
| Currency Display | `icr-general-rules.md` | system prompt (moved to Voice & Tone as one-liner — this is the exception, keep the one-liner in system prompt AND the full spec in general-rules since Voice & Tone is about formatting) |
| Risk Position Requirement | `icr-general-rules.md` | decision-matrix Rule #24 (replace with: "See icr-general-rules.md Risk Position Requirement") |
| Three-way Offboarding Match | `icr-steps-post.md` Step 22 | `icr-general-rules.md` (delete), decision-matrix Rule #49 (replace with reference) |
| Uncooperative vs Unresponsive | `icr-steps-decision.md` Steps 18-19 | `icr-general-rules.md` (delete), decision-matrix Rule #48 (replace with reference) |
| WOM / Withdrawals Enabled | `icr-steps-post.md` Step 22 | `icr-general-rules.md` (delete), decision-matrix Rule #46 (replace with reference) |
| 2FA Reset Block Rule | `icr-general-rules.md` | `icr-steps-setup.md` Step 3 (delete), `icr-steps-analysis.md` Step 14 (delete) |
| Hexa Protocol | `icr-general-rules.md` | system prompt (already being deleted in Phase 2) |
| Source of Truth Hierarchy | `icr-general-rules.md` | system prompt (already being deleted in Phase 2) |
| Multi-User Proportionality | `icr-general-rules.md` | decision-matrix Rule #6 (replace with reference) |
| Case Rejection Rules | `icr-general-rules.md` | system prompt OL-10 (already being deleted in Phase 2) |
| SLA Framework | `icr-general-rules.md` | system prompt OL-7 (already being deleted in Phase 2) |

### Execution Steps
1. Read `icr-general-rules.md` in full. Identify exact line locations of each rule above.
2. Read `decision-matrix.md` in full. Identify Rules #6, #24, #46, #48, #49.
3. For each rule pair: confirm the authoritative version has complete content, then delete/replace the duplicate.
4. Read `icr-steps-setup.md` Step 3 and `icr-steps-analysis.md` Step 14 — remove 2FA reset block rule (leave one in general-rules).
5. After de-duplication, verify `icr-general-rules.md` still reads coherently.

### Verification
- [ ] No rule appears in full in more than one document (except QC checklist, which is exempt)
- [ ] Decision matrix rules that were de-duplicated now have a short reference to the authoritative source
- [ ] `icr-general-rules.md` is coherent and self-contained for the rules it owns

---

## PHASE 5: UPDATE STEP DOC PROMPT REFERENCES

After Phases 1-4, step docs still reference "Execute Prompt #X" in various places. These need updating.

### References to update

| Step Doc | Step | Current Reference | New Instruction |
|----------|------|-------------------|-----------------|
| setup.md | Step 3 | "Prompt #3 (Account Blocks)" | Replace with inline: "Write block summary paragraph in chronological order..." (spec already exists in step) |
| setup.md | Step 4 | "Prompt #5 (Scam Analysis P2P)" | Remove reference. Step 4 already has the output template inline. |
| setup.md | Step 5 | "Prompt #4 (Prior ICR Analysis)" | Replace with inline: "Write single paragraph, 60-75 words..." (spec already exists in step) |
| setup.md | Step 6 | "Prompt #15E (LE data extraction)" | Remove — ingestion handles this. Step 6 has narrative spec. |
| analysis.md | Step 7 | "Prompt #1 (Transaction Analysis)" | Replace with inline spec (already exists in step — 150 word max, etc.) |
| analysis.md | Step 8 | "Prompt #2 (CTM Enhanced)" | Update to: "For cases with specific flagged transaction spreadsheets, fetch CTM Enhanced Analysis prompt from reference tier via tool call." |
| analysis.md | Step 8 | "Prompt #6 (CTM Standard)" | Replace with inline spec (already exists in step) |
| analysis.md | Step 11 | "Prompt #7 (Privacy Coin)" | Replace with inline spec (already exists in step — 50-70 words) |
| analysis.md | Step 12 | "Prompt #12 (Counterparty)" | Remove — ingestion handles extraction. Step 12 has narrative spec. |
| analysis.md | Step 13 | "Prompt #8 (Failed Fiat)" | Replace with inline spec (already exists — 3 sentences max) |
| analysis.md | Step 14 | "Prompt #9 (Device & IP)" | Replace with inline spec (already exists in step) |
| analysis.md | Step 14 | "Prompt #9E (extraction)" | Remove — ingestion handles this. |
| analysis.md | Step 15 | "Prompt #10 (RFI Summary)" | Replace with inline spec (already exists — 50-60 words) |
| analysis.md | Steps 9-10 | "Prompt #14E (Elliptic)" | Replaced by embedded spec (Phase 3C) |
| decision.md | Step 20B | "Prompt #11 (Summary)" | Replaced by embedded spec (Phase 3A) |

### Execution
1. After Phases 1-4 complete, search all step docs for "Prompt #" or "prompt-library" references.
2. For each: either confirm the inline spec is already sufficient (just delete the prompt reference) or add the missing spec inline.
3. Verify no step doc references prompt-library.md or any prompt by number without the spec being self-contained.

---

## EXECUTION ORDER

Phases must be executed in this order due to dependencies:

1. **Phase 3 first** — Embed output specs (11, 13-KYB, 14E) into step docs BEFORE deleting prompt-library.md
2. **Phase 1** — Delete prompt-library.md (now safe because all content is accounted for)
3. **Phase 2** — Trim system prompt, move procedural content to step docs
4. **Phase 4** — De-duplicate across general-rules and decision-matrix
5. **Phase 5** — Update all prompt references in step docs

### Between each phase: verify no content was lost.

---

## FILES MODIFIED (summary)

| File | Phases | Nature of Change |
|------|--------|-----------------|
| `knowledge_base/core/SYSTEM-PROMPT.md` | 2 | Rewrite — ~442 lines to ~60-80 lines |
| `knowledge_base/core/prompt-library.md` | 1 | DELETE |
| `knowledge_base/core/icr-steps-setup.md` | 2, 3B, 4, 5 | Add Phase 0, detection triggers, express mode, KYB spec; de-dup 2FA; update prompt refs |
| `knowledge_base/core/icr-steps-analysis.md` | 3C, 4, 5 | Add Elliptic output spec; de-dup 2FA; update prompt refs |
| `knowledge_base/core/icr-steps-decision.md` | 2, 3A, 4, 5 | Add pre-decision check, pre-submission, Summary spec; de-dup uncooperative/unresponsive; update prompt refs |
| `knowledge_base/core/icr-steps-post.md` | 4 | Receives three-way match and WOM as authoritative home (verify already there) |
| `knowledge_base/core/icr-general-rules.md` | 4 | Remove rules moved to step docs (three-way match, uncooperative/unresponsive, WOM) |
| `knowledge_base/core/decision-matrix.md` | 4 | Replace duplicate rules #6, #24, #46, #48, #49 with references |
| `knowledge_base/core/mlro-escalation-matrix.md` | — | Unchanged |
| `knowledge_base/core/qc-submission-checklist.md` | — | Unchanged |

### New files created
| File | Source |
|------|--------|
| `knowledge_base/reference/prompt-02-ctm-enhanced.md` | Extracted from prompt-library.md lines 103-157 |
| `knowledge_base/reference/prompt-16e-case-intake.md` | Extracted from prompt-library.md lines 1171-1375 |

---

## FUTURE TASKS (not part of this cleanup)

- Absorb Prompt #5 (Scam/P2P) logic into `prompts/prompt-23-l1-communications.md`
- Architect Free Chat mode (separate system prompt, YAML prompt index, tool-fetched prompts)
- Wire up Elliptic API and update Steps 9-10 spec accordingly
- Prompt quality review (all ingestion prompts against real data)
- Elliptic AI processing (Prompt 14E ingestion equivalent)
- Block-aware context architecture (step-based document loading — see `reference-docs/CONTEXT-MANAGEMENT-PLAN.md`)

---

## DECISION LOG

Decisions made during planning session (2026-03-07):

1. **Case Investigation scope only.** Free Chat parked for later.
2. **No separate prompts for Case Investigation.** Everything in step docs.
3. **Prompt library deleted entirely.** Individual prompt files in `knowledge_base/prompts/` remain for ingestion.
4. **QC checklist untouched.** Externally maintained — accept duplication.
5. **Express mode becomes default.** Standard (step-by-step) is the alternative. Express mode definition moves to step-setup.
6. **Output format specs embedded in step docs** where the step doc doesn't already have them.
7. **Single source of truth** for every rule. One authoritative location, references (not restations) elsewhere.
8. **Elliptic analysis is core** — every case, not filed away. Output spec embedded in Steps 9-10.
9. **Prompt #2 (CTM Enhanced)** and **Prompt #16E (Case Intake)** go to reference tier (tool-fetchable).
10. **Prompt #5 (Scam/P2P)** to be absorbed into prompt-23 (future task, not this cleanup).
