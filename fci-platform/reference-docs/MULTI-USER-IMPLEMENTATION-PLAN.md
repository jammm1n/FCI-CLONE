# Multi-User Case Implementation Plan

## Overview

Multi-user cases involve multiple linked suspects investigated together in a single case. Each subject requires a full data ingestion cycle (C360, KYC, Elliptic, etc.), and the AI investigates all subjects together through a stepped process with a dedicated system prompt.

**Key design decisions:**
- No hard cap on subject count (min 2, no max — practical limits determined by context window)
- Ingestion is sequential: one complete subject at a time, same UI, same sections
- Stepped investigation only — no autopilot/auto-execute for multi-user
- 8 investigation blocks (vs 4 for single-user) with smaller scope per block
- Filtered data injection per block to manage context window
- Dedicated system prompt (`system-prompt-multi-user.md`)
- Sections nested per-subject within the ingestion case document

---

## Phase 1: Data Model & Backend Schema

**Goal:** Establish the multi-user data model in MongoDB without breaking single-user cases.

### 1.1 Ingestion Case Schema Changes

**File:** `server/services/ingestion/ingestion_service.py`

**IMPORTANT — Current section storage structure:** Sections are stored as a nested dict on the ingestion case document, NOT as separate collection documents. Each section is accessed via dot notation (e.g., `sections.c360.status`). The `_empty_sections()` function builds the initial dict with all section keys.

Update `create_ingestion_case` to accept multi-user parameters:

```python
# Single-user case (unchanged):
{
    "_id": case_id,
    "case_mode": "single",
    "subject_uid": "UID_001",
    "sections": {
        "c360": { "status": "empty", "output": None, ... },
        "elliptic": { "status": "empty", ... },
        ...
    }
}

# Multi-user case:
{
    "_id": case_id,
    "case_mode": "multi",
    "total_subjects": 3,
    "current_subject_index": 0,
    "subject_uid": "UID_001",       # primary subject, kept for display
    "subjects": [
        {
            "user_id": "UID_001",
            "label": "Subject 1",
            "status": "in_progress",
            "sections": {           # full _empty_sections() dict per subject
                "c360": { "status": "empty", "output": None, ... },
                "elliptic": { "status": "empty", ... },
                ...
            }
        },
        {
            "user_id": null,
            "label": "Subject 2",
            "status": "pending",
            "sections": null        # populated when subject becomes active
        }
    ],
    "sections": {}                  # empty for multi-user — sections live in subjects[]
}
```

Single-user cases: `case_mode: "single"` (or absent), sections at top level as now. No `subjects` array.

Multi-user cases: Each subject gets its own `sections` dict (identical structure to current top-level sections). `_empty_sections()` is called per subject when that subject becomes active.

### 1.2 Section CRUD Path Changes

**File:** `server/services/ingestion/ingestion_service.py`

All section update operations currently use MongoDB dot notation:
```python
# Current:
f'sections.{section_key}.status'
f'sections.{section_key}.output'

# Multi-user:
f'subjects.{subject_index}.sections.{section_key}.status'
f'subjects.{subject_index}.sections.{section_key}.output'
```

The existing functions to modify (with their current names — not renamed):

- `update_section(case_id, section_key, status, ...)` — add `subject_index` parameter. Build dot path conditionally based on `case_mode`. Default `subject_index=None` for backward compat (uses top-level `sections`).
- `mark_section_none(case_id, section_key)` — pass `subject_index` through to `update_section`.
- `save_notes(case_id, notes_text)` — add `subject_index` parameter, update path.
- `save_text_section(case_id, section_key, text)` — add `subject_index` parameter, update path.
- `save_text_section_with_ai(case_id, section_key, text)` — add `subject_index` parameter, update path.
- `get_case_status(case_id)` — for multi-user, return sections for the current subject only (or specified subject). Must also return `subjects` array with status for progress display.

Helper function to build the dot path:
```python
def _section_path(section_key: str, subject_index: int | None = None) -> str:
    if subject_index is not None:
        return f'subjects.{subject_index}.sections.{section_key}'
    return f'sections.{section_key}'
```

### 1.3 Ready State Detection

**File:** `server/services/ingestion/ingestion_service.py`

`_check_ready_state(case_id)` currently checks if all required sections are terminal and auto-transitions the case to `ready`. For multi-user:

- This function must check only the **current subject's** sections, not the whole case
- When a subject's sections are all terminal, that subject is ready for submission — but the case itself only becomes `ready` when ALL subjects are `complete`
- Add a `_check_subject_ready(case_id, subject_index)` function that checks a single subject's sections
- The case-level `ready` state transitions when `all(s["status"] == "complete" for s in subjects)`

### 1.4 New Service Functions

- `submit_subject(case_id, subject_index)` — mark subject `complete`, advance `current_subject_index`. If next subject exists, populate its `sections` with `_empty_sections()` and set status to `in_progress`. Return next subject info.
- `set_subject_uid(case_id, subject_index, user_id)` — set UID for a pending subject.

### 1.5 Ingestion Router Updates

**File:** `server/routers/ingestion.py`

- `POST /api/ingestion/cases` — accept `case_mode` and `total_subjects` in request body
- All section endpoints — accept `subject_index` query param (default `None` for single-user)
- `POST /api/ingestion/cases/{id}/submit-subject` — new endpoint for subject submission
- `PATCH /api/ingestion/cases/{id}/subjects/{index}/uid` — new endpoint for setting subsequent UIDs

### 1.6 Pydantic Schema Updates

**File:** `server/models/ingestion_schemas.py`

- `CreateIngestionCaseRequest` — add `case_mode: str = "single"`, `total_subjects: int = 1`. Note: existing `coconspirator_uids` field is conceptually related but separate (used for display, not for multi-user ingestion flow).
- `CaseStatusResponse` — add `subjects` list with per-subject status, `current_subject_index`, `case_mode`

### 1.7 Backward Compatibility

All changes must be backward compatible:
- Single-user cases: `case_mode` absent or `"single"`, `subject_index=None` in all calls, sections at top level
- `subject_index=None` defaults to top-level `sections` path — existing code unchanged
- No migration needed for existing data
- All C360 processor, AI processor, Kodex processor functions receive `subject_index` and pass through — their internal logic doesn't change

### Phase 1 Testing
- Create a multi-user ingestion case via API
- Verify per-subject sections are stored at correct path
- Verify section updates use correct dot notation
- Verify `_check_subject_ready` works independently per subject
- Verify single-user cases are completely unaffected (regression test)
- Submit subjects, verify status transitions and `_empty_sections()` population for next subject

---

## Phase 2: Case Assembly — Multi-User

**Goal:** Assemble a multi-user case into a combined case document and promote to investigations.

### 2.1 Assembly Logic

**File:** `server/services/ingestion/ingestion_service.py`

`assemble_case_data` currently:
1. Reads `doc["sections"]` (flat dict)
2. Builds `preprocessed_data` (flat dict)
3. Builds `assembled_case_data` (markdown string)
4. Creates a document in the `cases` collection
5. Marks ingestion case as completed

For multi-user:
1. Gate: all subjects must have status `complete`
2. For each subject, read `subject["sections"]`
3. Build per-subject `preprocessed_data` dicts using existing `C360_AI_TO_PREPROCESSED` and `SECTION_TO_PREPROCESSED` mappings
4. Build assembled markdown with per-subject headers (see 2.3)
5. Store on promoted case with `subjects` array

### 2.2 Promoted Case Schema (cases collection)

```python
# Single-user (unchanged):
{
    "_id": case_id,
    "case_mode": "single",
    "case_type": "investigation",
    "status": "open",
    "assigned_to": "user_001",
    "subject_user_id": "UID_001",
    "summary": "",
    "conversation_id": None,
    "preprocessed_data": { "tx_summary": "...", "user_profile": "...", ... },
    "assembled_case_data": "# Case Data: ...",
    "created_at": ...,
    "updated_at": ...
}

# Multi-user:
{
    "_id": case_id,
    "case_mode": "multi",
    "case_type": "investigation",
    "status": "open",
    "assigned_to": "user_001",
    "subject_user_id": "UID_001",    # primary subject for display
    "total_subjects": 3,
    "subjects": [
        {
            "user_id": "UID_001",
            "label": "Subject 1",
            "preprocessed_data": { "tx_summary": "...", "user_profile": "...", ... }
        },
        {
            "user_id": "UID_002",
            "label": "Subject 2",
            "preprocessed_data": { "tx_summary": "...", ... }
        },
        {
            "user_id": "UID_003",
            "label": "Subject 3",
            "preprocessed_data": { "tx_summary": "...", ... }
        }
    ],
    "preprocessed_data": {},         # empty for multi-user — data lives in subjects
    "assembled_case_data": "# Multi-User Case Data: ...",
    "created_at": ...,
    "updated_at": ...
}
```

### 2.3 Case Data Markdown Builder

**File:** `server/services/conversation_manager.py`

Update `_build_case_data_markdown()` to handle multi-user. Add optional `sections` parameter for filtered injection:

```python
def _build_case_data_markdown(case: dict, sections: list[str] | None = None) -> str:
    subjects = case.get("subjects", [])

    if not subjects:
        # Single-user — existing behavior, unchanged
        # (optionally apply sections filter here too for future use)
        return _build_single_user_markdown(case)

    # Multi-user
    parts = [
        f"# Multi-User Case — Case ID {case.get('_id')}",
        f"**Case Type:** {case.get('case_type', 'Unknown')}",
        f"**Total Subjects:** {len(subjects)}",
        f"**Subject UIDs:** {', '.join(s['user_id'] for s in subjects)}",
        "",
        "---",
        "",
    ]
    for i, subject in enumerate(subjects):
        parts.append(f"# SUBJECT {i+1} — UID {subject['user_id']}")
        parts.append("")
        preprocessed = subject.get("preprocessed_data", {})
        for field, header in section_map.items():
            if sections and field not in sections:
                continue
            content = preprocessed.get(field)
            if content:
                parts.append(f"## {header}")
                parts.append("")
                # Include count annotations (prior_icr_count, rfi_count)
                if field == "prior_icr":
                    total_count = preprocessed.get("prior_icr_count")
                    if total_count:
                        parts.append(
                            f"*Note: {total_count} prior ICRs exist for this subject. "
                            f"The most recent are summarised below.*"
                        )
                        parts.append("")
                elif field == "rfi":
                    total_count = preprocessed.get("rfi_count")
                    if total_count:
                        parts.append(
                            f"*Note: {total_count} RFIs exist for this subject. "
                            f"The most recent are summarised below.*"
                        )
                        parts.append("")
                parts.append(content)
                parts.append("")
                parts.append("---")
                parts.append("")
    return "\n".join(parts)
```

The `sections` parameter enables filtered injection:
- `None` = all sections (Phase 0, full view)
- `["tx_summary", "ctm_alerts"]` = only those sections for all subjects

### 2.4 Pydantic Schema Updates

**File:** `server/models/schemas.py`

- Add `SubjectData` model: `user_id: str`, `label: str`, `preprocessed_data: PreprocessedData`
- Update `CaseDetailResponse` to include `case_mode: str = "single"`, `total_subjects: int = 1`, `subjects: list[SubjectData] = []`

### 2.5 Case Service Updates

**File:** `server/services/case_service.py`

- `get_case(case_id)` — currently builds response dict with `preprocessed_data` at top level. For multi-user, must also return `subjects`, `case_mode`, `total_subjects`.
- `get_cases(user_id)` — return `case_mode` in the summary for each case (used by CaseCard to show "Multi-User" badge and hide Autopilot button).

### Phase 2 Testing
- Assemble a multi-user case with 2-3 subjects
- Verify promoted case has correct structure in `cases` collection
- Verify `_build_case_data_markdown` produces correct output with all sections
- Verify `_build_case_data_markdown` with section filter produces correct filtered output
- Verify count annotations (prior_icr_count, rfi_count) work per subject
- Verify single-user assembly is completely unaffected

---

## Phase 3: Ingestion Frontend

**Goal:** Update the ingestion page to support multi-user creation and sequential ingestion flow.

### 3.1 Case Creation Form

**File:** `client/src/pages/IngestionPage.jsx`

Add to the case creation form:
- Toggle/select: "Single User" (default) / "Multi-User"
- When multi-user: numeric input for total subjects (min 2, no max)
- Subject UID field label changes to "Subject 1 UID"
- Calls updated `createIngestionCase` API with `caseMode` and `totalSubjects`

### 3.2 Subject Progress Header

When viewing a multi-user case, display a progress header above the section grid:

```
Subject 1 of 3 — UID 123456 [complete] → Subject 2 of 3 — UID 789012 [in progress] → Subject 3 of 3 [pending]
```

Clicking a completed subject shows its sections in read-only mode. The current (in-progress) subject's sections are editable.

### 3.3 Section Grid — Subject Filtering

The section grid stays identical in layout. The data source changes:
- All section API calls include `subjectIndex` as a query parameter
- `useIngestionStatus` hook passes `subjectIndex` when polling
- Section content display filters by current subject

### 3.4 Subject Lifecycle Buttons

Replace the single "Assemble Case" button with conditional buttons for multi-user:

- **During subject ingestion:** "Submit Subject & Continue" — calls `submitSubject` endpoint. Only enabled when all required sections for this subject are terminal.
- **After subject submission:** Shows UID entry form for next subject, then reloads empty section grid
- **All subjects complete:** "Assemble Case" button appears (same as current, calls assembly endpoint)

Single-user cases: no change — "Assemble Case" button as now.

### 3.5 Subject Navigation

Allow navigating back to completed subjects:
- Click a completed subject in the progress header to view its sections (read-only)
- Option to re-process a section if needed (marks subject as `in_progress` again)

### 3.6 Ingestion API Updates

**File:** `client/src/services/ingestion_api.js`

- `createIngestionCase()` — accept `caseMode`, `totalSubjects`
- All section functions (upload, process, status) — accept `subjectIndex` parameter, include as query param
- `submitSubject(caseId, subjectIndex)` — new
- `setSubjectUid(caseId, subjectIndex, userId)` — new

### Phase 3 Testing
- Create multi-user case from UI
- Ingest 2 subjects sequentially, verify section isolation per subject
- Navigate between completed and in-progress subjects
- Verify "Submit Subject" button enables only when sections are terminal
- Assemble and verify promotion to cases collection
- Verify single-user ingestion flow is completely unchanged

---

## Phase 4: Multi-User Step Configuration

**Goal:** Define the block structure and data injection mapping for multi-user investigations.

### 4.1 Step Configuration

**File:** `server/config.py`

```python
MULTI_USER_STEP_CONFIG = {
    1: {
        "phase": "setup",
        "label": "Identity & Account Overview",
        "steps_covered": [1, 2, 3],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-setup"],      # same doc, but filtered to Steps 1-3
    },
    2: {
        "phase": "setup",
        "label": "Case History & Context",
        "steps_covered": [4, 5, 6],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-setup"],      # same doc, filtered to Steps 4-6
    },
    3: {
        "phase": "analysis",
        "label": "Transaction & Alert Analysis",
        "steps_covered": [7, 8],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-analysis"],   # filtered to Steps 7-8
    },
    4: {
        "phase": "analysis",
        "label": "On-Chain Analysis",
        "steps_covered": [9, 10, 11],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-analysis"],   # filtered to Steps 9-11
    },
    5: {
        "phase": "analysis",
        "label": "Counterparty & Device Analysis",
        "steps_covered": [12, 13, 14],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-analysis"],   # filtered to Steps 12-14
    },
    6: {
        "phase": "analysis",
        "label": "Communications & OSINT",
        "steps_covered": [15, 16, 17, 18, 19],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-analysis"],   # filtered to Steps 15-16
                                          # + icr-steps-decision for 17-19
    },
    7: {
        "phase": "summary",
        "label": "Summary of Unusual Activity",
        "steps_covered": [20],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-decision"],   # filtered to Step 20
    },
    8: {
        "phase": "decision",
        "label": "Decision & Recommendation",
        "steps_covered": [21],
        "model": "claude-opus-4-6",
        "docs": ["icr-steps-decision", "decision-matrix", "mlro-escalation-matrix"],
    },
}

MULTI_USER_STEP_PHASES = {
    1: "setup", 2: "setup", 3: "analysis", 4: "analysis",
    5: "analysis", 6: "analysis", 7: "summary", 8: "decision",
}
```

**Note:** Block 6 spans two step documents (`icr-steps-analysis` for Steps 15-16 and `icr-steps-decision` for Steps 17-19). The step doc filtering function must handle loading from multiple source docs when needed.

All blocks default to Opus — multi-user cases need the stronger model due to complexity.

### 4.2 Block-to-Data Mapping

**File:** `server/config.py` (alongside the step config)

```python
MULTI_USER_BLOCK_DATA = {
    1: ["user_profile", "kyc", "tx_summary", "account_blocks"],
    2: ["l1_referral", "haoDesk", "prior_icr", "kodex", "l1_victim", "l1_suspect"],
    3: ["tx_summary", "ctm_alerts", "ftm_alerts"],
    4: ["elliptic", "address_xref", "privacy_coin"],
    5: ["counterparty", "failed_fiat", "device_ip"],
    6: ["investigator_notes", "rfi"],
    7: ["tx_summary"],       # light reference data for unusual activity summary
    8: None,                  # decision block — summaries only, no raw data
}
```

Block 8 receives no raw case data — only the rolling step summaries from blocks 1-7.

### 4.3 Step Document Filtering

**File:** `server/services/knowledge_base.py`

Add a function to extract specific steps from a step document:

```python
def get_filtered_step_doc(self, doc_id: str, step_numbers: list[int]) -> str:
    """
    Extract preamble + specific ## STEP N sections from a step document.
    Used for multi-user cases to send only relevant steps per block.

    The preamble is everything before the first ## STEP header (includes
    Phase 0, pacing mode, SLA framework etc. for icr-steps-setup.md).

    Returns the preamble + only the ## STEP sections whose numbers
    are in step_numbers.
    """
    full_doc = self.get_document(doc_id)
    # Split on ## STEP \d+ headers
    # Return preamble + matching sections
```

Step documents use `## STEP N:` as section delimiters (verified in `icr-steps-setup.md`). Regex split on `## STEP \d+` gives individually addressable sections.

Cache the parsed result per doc_id to avoid re-parsing on every call.

### Phase 4 Testing
- Verify `MULTI_USER_STEP_CONFIG` loads correctly
- Verify data mapping returns correct section keys per block
- Verify step doc filtering extracts correct `## STEP` sections from each doc
- Verify preamble (Phase 0, SLA, etc.) is always included
- Verify Block 6 correctly loads from two source documents
- Verify single-user `STEP_CONFIG` is completely unaffected

---

## Phase 5: Conversation Manager — Multi-User Flow

**Goal:** Wire the multi-user step config and data injection into the conversation lifecycle.

### 5.1 Conversation Creation

**File:** `server/services/conversation_manager.py`

`create_conversation` modifications:
- Detect `case.get("case_mode") == "multi"` on the case document
- Use `MULTI_USER_STEP_CONFIG` for investigation state initialization (8 blocks instead of 4)
- Use multi-user initial assessment instruction
- Build full case data markdown (all subjects, all sections) for Phase 0 injection
- System prompt selection happens in `get_step_system_prompt` / `get_system_prompt` — see 5.3

```python
MULTI_USER_INITIAL_ASSESSMENT = (
    "Case data loaded. This is a multi-user case with {n} subjects: {uids}. "
    "Execute Phase 0A from icr-steps-setup.md: case type classification, "
    "data inventory for EACH subject (hard blockers, soft gaps, received), "
    "anomalies, connections between subjects, and clarifying questions. "
    "Do NOT produce a narrative yet — that comes in Phase 0B."
)
```

### 5.2 API Message Rebuilding — Data Injection

**File:** `server/services/conversation_manager.py`

`_rebuild_step_api_messages` modifications:

**CRITICAL:** The current function gates case data injection on `current_step <= 4`:
```python
if current_step <= 4 and case:
    case_data_md = _build_case_data_markdown(case)
```

For multi-user with 8 blocks, this must change to inject filtered data at all blocks except the decision block:

```python
if case and case.get("case_mode") == "multi":
    block_data_keys = MULTI_USER_BLOCK_DATA.get(current_step)
    if block_data_keys is not None:  # None = decision block, no data
        case_data_md = _build_case_data_markdown(case, sections=block_data_keys)
        api_messages.append({"role": "user", "content": f"[CASE DATA]\n\n{case_data_md}"})
        api_messages.append({"role": "assistant", "content": "Case data received..."})
elif current_step <= 4 and case:
    # Single-user — existing behavior
    case_data_md = _build_case_data_markdown(case)
    ...
```

### 5.3 System Prompt & Step Document Injection

**File:** `server/services/knowledge_base.py`

`get_step_system_prompt(step)` currently:
1. Uses `self.case_system_prompt` as the base
2. Looks up `STEP_CONFIG[step]["docs"]` for step-specific documents
3. Includes `general_rules` and `qc_quick_reference`

For multi-user, this function needs to:
1. Accept a `multi_user: bool = False` parameter (or `config_override`)
2. Use `self.multi_user_system_prompt` instead of `self.case_system_prompt`
3. Look up from `MULTI_USER_STEP_CONFIG` instead of `STEP_CONFIG`
4. Call `get_filtered_step_doc()` to extract only the relevant steps from the doc
5. Include `qc_quick_reference` for all blocks (not just steps 1-4) since multi-user blocks cover different step ranges

```python
def get_step_system_prompt(self, step: int, multi_user: bool = False) -> str:
    config = MULTI_USER_STEP_CONFIG if multi_user else STEP_CONFIG
    base_prompt = self.multi_user_system_prompt if multi_user else self.case_system_prompt
    ...
```

The caller in `conversation_manager.py` determines `multi_user` from the case document and passes it through.

### 5.4 Summary Generation

Step summaries work the same mechanically. The `SUMMARY_SYSTEM_PROMPT` should be augmented for multi-user:

```python
MULTI_USER_SUMMARY_PROMPT = SUMMARY_SYSTEM_PROMPT + """
This is a multi-user case. Your summary MUST:
- Use UID labels to distinguish per-subject findings
- Cover all subjects, even if a subject had no relevant data at this step
- This summary will be the primary context for subsequent blocks
"""
```

This ensures Block 8 receives structured per-subject summaries it can synthesize into a combined decision.

### 5.5 Block Transitions

`approve_and_continue` works the same — advances step counter, generates summary. The only differences:
- 8 transitions instead of 4
- At each transition, the next block's data injection is filtered via `MULTI_USER_BLOCK_DATA`
- Must use `MULTI_USER_STEP_CONFIG` for step count and labels

### 5.6 Disable Autopilot/Auto-Execute

For multi-user cases:
- `oneshot_execute` endpoint: check case mode, return 400 with "Autopilot not available for multi-user cases"
- Auto-execute endpoint: same check, return 400
- Reset case endpoint: works as-is (no changes needed)

### Phase 5 Testing
- Open a multi-user case for investigation
- Verify Phase 0 receives full data for all subjects (unfiltered)
- Verify Block 1 receives only `user_profile`, `kyc`, `tx_summary`, `account_blocks` for all subjects
- Verify Block 8 receives only step summaries, no raw data
- Verify step summaries capture per-subject findings with UID labels
- Step through all 8 blocks to completion
- Verify single-user investigation flow is completely unaffected (regression test)
- Verify autopilot/auto-execute return 400 for multi-user

---

## Phase 6: System Prompt — Multi-User

**Goal:** Create a dedicated system prompt for multi-user investigations.

### 6.1 Create `system-prompt-multi-user.md`

**File:** `knowledge_base/system-prompt-multi-user.md`

Structure — shared sections copied from `system-prompt-case.md` (not referenced, copied, so they can be tuned independently):

```markdown
# SYSTEM PROMPT — MULTI-USER INVESTIGATION
---
### IDENTITY & ROLE
You are FCI-GPT, a Senior Compliance Investigator Copilot for Binance L2
Investigations. You are investigating a multi-user case with multiple linked
subjects. You guide investigators through ICR cases step by step, producing
copy-paste-ready ICR text that meets QC standards for multi-user ICRs.

The case data is pre-loaded — work through the steps using the data provided.
---
### MULTI-USER CASE RULES
- This case contains multiple linked subjects. All subjects must be covered
  at every analytical step.
- Always prefix data and analysis with `UID [X]:` labels. Never let the
  reader guess which subject a paragraph refers to.
- Proportionality: full analysis for all subjects, but depth matches
  available data. A subject with no activity at a given step gets a one-line
  confirmation, not a paragraph explaining the absence.
- You will receive data for all subjects at Phase 0, then filtered by
  relevant sections per block for subsequent steps. Each block contains
  data for ALL subjects but only the sections relevant to that block's steps.
- Decision (Block 8): produce a combined recommendation. If subjects have
  divergent risk profiles, state the recommendation per subject with
  rationale for each.
- Same-individual detection: if two UIDs appear to belong to the same person
  (same ID document, matching biometrics), flag this immediately with a
  bridging statement per icr-general-rules.md.
---
### DOCUMENT HIERARCHY (Priority Order)
[Copied from system-prompt-case.md — identical content]
---
### STEP BOUNDARIES
You only have access to one block's step document at a time. The server
controls which document you receive.
- Complete all sections in your current block, then call `signal_step_complete()`.
- Do NOT auto-advance to the next block's ICR sections.
- Do NOT ask the user if they want to continue.
- You MUST still answer investigator questions.

**Multi-User Investigation Blocks:**
- Block 1: Steps 1-3 (Identity & Account Overview)
- Block 2: Steps 4-6 (Case History & Context)
- Block 3: Steps 7-8 (Transaction & Alert Analysis)
- Block 4: Steps 9-11 (On-Chain Analysis)
- Block 5: Steps 12-14 (Counterparty & Device Analysis)
- Block 6: Steps 15-19 (Communications & OSINT)
- Block 7: Step 20 (Summary of Unusual Activity)
- Block 8: Step 21 (Decision & Recommendation)
---
### VOICE & TONE (STRICT)
[Copied from system-prompt-case.md — identical content]
---
### OPERATIONAL OVERRIDE HANDLING
[Copied from system-prompt-case.md — identical content]
---
### FCI / FCMI TERMINOLOGY
[Copied from system-prompt-case.md — identical content]
```

### 6.2 Knowledge Base Loader

**File:** `server/services/knowledge_base.py`

- Add `self.multi_user_system_prompt: str = ""` to `__init__`
- Load `system-prompt-multi-user.md` in `load_on_startup()`
- Add `"multi-user"` case to `get_system_prompt(mode)`:
  ```python
  elif mode == "multi-user":
      return (
          f"{self.multi_user_system_prompt}\n\n---\n\n"
          f"{self.core_content}\n\n---\n\n"
          f"{self.reference_index_text}"
      )
  ```

### 6.3 Phase 0 — Multi-User Specifics

Phase 0A for multi-user must additionally:
- Run the data inventory for EACH subject independently (the hard blockers table applies per subject)
- Flag connections between subjects (shared counterparties, overlapping addresses, same device/IP, same ID document)
- The narrative theory (Phase 0B) should establish how the subjects are linked and what the combined risk picture is

The existing Phase 0A/0B structure in `icr-steps-setup.md` works — the multi-user system prompt adds the per-subject requirement on top. No changes needed to `icr-steps-setup.md` itself.

### Phase 6 Testing
- Verify system prompt loads correctly for multi-user mode
- Verify `get_step_system_prompt(step, multi_user=True)` returns correct prompt with filtered step doc
- Verify Phase 0A produces per-subject inventory with UID labels
- Verify Phase 0B narrative covers all subjects and their connections
- Review AI output quality across all 8 blocks with multi-user prompt

---

## Phase 7: Investigation Frontend — Multi-User

**Goal:** Update the investigation page to handle multi-user display and controls.

### 7.1 Case List Display

**File:** `client/src/components/cases/CaseCard.jsx`

For multi-user cases:
- Show "Multi-User — [N] Subjects" badge alongside case type
- List subject UIDs in the meta row (or truncate if many)
- Hide "Autopilot" button when `case_mode === "multi"`

### 7.2 Case Header

**File:** `client/src/components/investigation/CaseHeader.jsx`

For multi-user cases, display:
- "Multi-User Case — [N] Subjects"
- List of subject UIDs with labels

### 7.3 Step Indicator

**File:** `client/src/components/investigation/StepIndicator.jsx`

Update to show 8 blocks with labels for multi-user. Read block count and labels from the investigation state (which is initialized from the step config). Single-user cases continue showing 4-5 steps.

### 7.4 Case Data Panel / Tabs

**File:** `client/src/components/investigation/CaseDataTabs.jsx`

For multi-user cases, add a top-level subject selector:
- Tab per subject: "Subject 1 — UID 123", "Subject 2 — UID 456"
- Within each subject tab, the existing tab group structure (C360 sub-tabs, Standalone sections)
- Allows investigator to reference any subject's data while reviewing AI output

Single-user cases: no change to tab structure.

### 7.5 Disable Experimental Features

**File:** `client/src/pages/InvestigationPage.jsx`, `client/src/components/ChatInput.jsx`

- Hide experimental popover (auto-execute, express) when multi-user
- Chat input shows standard stepped controls only
- Autopilot execution flow disabled

### 7.6 No Other Frontend Changes

Chat interface, message display, approval flow, step dividers, thinking display, PDF download — all work as-is. The investigator interacts with multi-user cases the same way as single-user, just with more blocks and a subject selector in the data panel.

### Phase 7 Testing
- Open a multi-user case, verify case card shows multi-user badge
- Verify investigation header shows subject list
- Verify step indicator shows 8 blocks with labels
- Verify case data tabs show per-subject data with subject selector
- Verify autopilot/auto-execute/experimental features hidden
- Full walkthrough: 8 blocks to completion, verify approval flow
- Verify single-user investigation UI is completely unchanged

---

## Phase 8: End-to-End Testing & Refinement

**Goal:** Run real multi-user cases through the full pipeline and refine.

### 8.1 Test Cases
- 2-subject case (most common scenario)
- 3-4 subject case (stress test context window)
- Same-individual multi-user case (two UIDs, one person — verify bridging statement)
- Mixed data completeness (Subject 1 has full data, Subject 3 has minimal activity)

### 8.2 Context Window Monitoring
- Measure token usage per block for 2, 3, 4+ subject cases
- Log `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` per block
- Identify if/where context limits are hit
- Adjust block boundaries or data filtering if needed
- Consider whether certain blocks need further splitting for high-subject-count cases

### 8.3 Output Quality Review
- Verify UID labelling consistency across all 8 blocks
- Verify per-subject proportionality (depth matches data availability)
- Verify combined decision correctly handles divergent recommendations per subject
- Verify step summaries capture per-subject findings adequately for downstream blocks
- Verify Phase 0A produces per-subject inventory (not a single combined inventory)
- Compare AI output against manually produced multi-user ICRs for QC compliance

### 8.4 PDF Export
- Verify PDF export works for multi-user case transcripts
- Include subject list in PDF header
- Verify transcript length is manageable (multi-user + 8 blocks = long transcripts)

### 8.5 Refinement
- Adjust block boundaries based on testing
- Tune system prompt based on output quality
- Tune summary prompt to ensure per-subject structure
- Update multi-user rules in `icr-general-rules.md` if platform-specific additions needed
- Document any new gotchas in MEMORY.md

---

## Dependency Chain

```
Phase 1 (Data Model)
    ↓
Phase 2 (Assembly) ──────────────────→ Phase 4 (Step Config)
    ↓                                      ↓
Phase 3 (Ingestion Frontend)          Phase 5 (Conversation Manager)
    ↓                                      ↓
    Ready to ingest                   Phase 6 (System Prompt)
    multi-user cases                       ↓
                                      Phase 7 (Investigation Frontend)
                                           ↓
                                      Phase 8 (Testing)
```

**Critical path:** Phase 1 → Phase 2 → Phase 4 → Phase 5 → Phase 6 → Phase 8

**Parallel work:** Phase 3 (ingestion frontend) can be built in parallel with Phases 4-6 once Phase 2 is complete. Phase 7 (investigation frontend) can be built in parallel with Phase 6 once Phase 5 is complete.

---

## Files Changed Per Phase

| Phase | Files Modified | Files Created |
|-------|---------------|---------------|
| 1 | `ingestion_service.py`, `ingestion.py` (router), `ingestion_schemas.py` | — |
| 2 | `ingestion_service.py`, `conversation_manager.py`, `schemas.py`, `case_service.py` | — |
| 3 | `IngestionPage.jsx`, `ingestion_api.js`, `useIngestionStatus.js` | — |
| 4 | `config.py`, `knowledge_base.py` | — |
| 5 | `conversation_manager.py`, `conversations.py` | — |
| 6 | `knowledge_base.py` | `system-prompt-multi-user.md` |
| 7 | `CaseCard.jsx`, `CaseHeader.jsx`, `StepIndicator.jsx`, `CaseDataTabs.jsx`, `InvestigationPage.jsx`, `ChatInput.jsx` | — |
| 8 | Various (refinement) | — |

---

## Out of Scope (for now)

- Autopilot/auto-execute for multi-user cases
- Dynamic block splitting based on subject count at runtime
- Per-subject investigation state (all subjects progress through blocks together)
- Cross-case subject linking (identifying the same UID across different cases)
- Multi-user specific ingestion prompts (all existing prompts work per-subject as-is)
