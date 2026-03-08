# Multi-User Case Implementation Plan

## Overview

Multi-user cases involve multiple linked suspects investigated together in a single case. Each subject requires a full data ingestion cycle (C360, KYC, Elliptic, etc.), and the AI investigates all subjects together through a stepped process with a dedicated system prompt.

**Key design decisions:**
- No hard cap on subject count (min 2, no max — practical limits determined by context window)
- Ingestion is sequential: one complete subject at a time, same UI, same sections
- Stepped investigation only — no autopilot/auto-execute for multi-user
- 9 investigation blocks: 8 ICR blocks (vs 4 for single-user) + 1 QC block — smaller scope per block
- Block 1 injects ALL case data (unfiltered) for Phase 0 inventory; blocks 2-8 inject filtered data per block to manage context window
- Dedicated system prompt (`system-prompt-multi-user.md`)
- Sections nested per-subject within the ingestion case document
- For multi-user cases, `coconspirator_uids` is NOT used — the `subjects` array replaces it entirely. `coconspirator_uids` remains for single-user cases only (display in assembled markdown header).

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
- `get_case_status(case_id)` — for multi-user, return sections for the **current subject only** (keyed by `current_subject_index`). This preserves the existing polling hook's terminal-state detection logic (it checks `sections[*].status !== 'processing'`). Also return `subjects` array with per-subject summary status, `current_subject_index`, and `case_mode` for the progress header display.

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

- `CreateIngestionCaseRequest` — add `case_mode: str = "single"`, `total_subjects: int = 1`. For multi-user cases, `coconspirator_uids` should NOT be populated — the `subjects` array replaces it.
- Add `SubjectStatusSummary` model: `user_id: str | None`, `label: str`, `status: str` (pending / in_progress / complete), `sections_complete: int = 0`, `sections_total: int = 0`
- `CaseStatusResponse` — add `case_mode: str = "single"`, `current_subject_index: int = 0`, `subjects: list[SubjectStatusSummary] = []`. The `sections` field continues to hold the current subject's sections (see 1.2).

### 1.7 Backward Compatibility

All changes must be backward compatible:
- Single-user cases: `case_mode` absent or `"single"`, `subject_index=None` in all calls, sections at top level
- `subject_index=None` defaults to top-level `sections` path — existing code unchanged
- No migration needed for existing data
- All C360 processor, AI processor, Kodex processor functions receive `subject_index` and pass through — their internal logic doesn't change
- `coconspirator_uids` field is untouched for single-user cases. For multi-user cases, it is left as an empty list — subject tracking is handled entirely by the `subjects` array

**IMPORTANT — Key mapping indirection to be aware of:** Ingestion section keys (`previous_icrs`, `rfis`, `hexa_dump`, `raw_hex_dump`) differ from preprocessed_data keys (`prior_icr`, `rfi`, `l1_referral`, `haoDesk`). The mapping happens during assembly via `C360_AI_TO_PREPROCESSED` and `SECTION_TO_PREPROCESSED` in `ingestion_service.py`. This indirection is unchanged for multi-user — the same mappings apply per subject.

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
- Update `CaseSummary` to include `case_mode: str = "single"`, `total_subjects: int = 1` — needed by CaseCard to show multi-user badge and hide Autopilot button

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
        "docs": ["icr-steps-analysis", "icr-steps-decision"],  # Steps 15-16 from analysis, 17-19 from decision
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
    9: {
        "phase": "qc_check",
        "label": "QC Check",
        "steps_covered": [],              # No ICR steps — QC is a review-only block
        "model": "claude-opus-4-6",
        "docs": ["qc-full-checklist"],    # Same as single-user step 5
    },
    "summary": {
        "model": "claude-opus-4-6",       # Model for inter-block summary generation
    },
}

MULTI_USER_STEP_PHASES = {
    1: "setup", 2: "setup", 3: "analysis", 4: "analysis",
    5: "analysis", 6: "analysis", 7: "summary", 8: "decision", 9: "qc_check",
}
```

**Notes:**
- Block 6 spans two step documents (`icr-steps-analysis` for Steps 15-16 and `icr-steps-decision` for Steps 17-19). Both docs are listed in the `docs` array — `get_filtered_step_doc()` extracts only the `steps_covered` from each.
- Block 9 (QC Check) mirrors single-user step 5: the investigator pastes their completed multi-user ICR text, and the AI reviews it against the QC checklist. The QC paste modal (`QCPasteModal`) is reused. The transition from block 8→9 uses the same `qc_check()` function as single-user (see Phase 5.5).
- All blocks default to Opus — multi-user cases need the stronger model due to complexity.

### 4.2 Block-to-Data Mapping

**File:** `server/config.py` (alongside the step config)

```python
MULTI_USER_BLOCK_DATA = {
    1: None,                  # ALL data — unfiltered. Phase 0 (initial assessment) runs
                              # within block 1 and needs a full data inventory for every
                              # subject. The AI then uses the step doc to scope its
                              # narrative to Steps 1-3 only. This matches single-user
                              # behavior where all data is injected at every step.
    2: ["l1_referral", "haoDesk", "prior_icr", "kodex", "l1_victim", "l1_suspect"],
    3: ["tx_summary", "ctm_alerts", "ftm_alerts"],
    4: ["elliptic", "address_xref", "privacy_coin"],
    5: ["counterparty", "failed_fiat", "device_ip"],
    6: ["investigator_notes", "rfi"],
    7: ["tx_summary"],       # light reference data for unusual activity summary;
                              # summaries from blocks 1-6 are the primary context
    8: None,                  # decision block — summaries only, no raw data
    9: None,                  # QC block — no case data injected (investigator pastes ICR text)
}
```

**Semantics of `None`:**
- Block 1: `None` = inject ALL sections (unfiltered) for Phase 0 inventory
- Block 8: `None` = inject NO data (decision uses only step summaries)
- Block 9: `None` = inject NO data (QC reviews pasted ICR text)

**IMPORTANT:** These three `None` values have **different meanings**. The injection logic in `_rebuild_step_api_messages` (Phase 5.2) must distinguish between them:
- Block 1 (`phase == "setup"` and first block): inject full unfiltered case data
- Block 8 (`phase == "decision"`): no case data injection
- Block 9 (`phase == "qc_check"`): no case data injection (investigator pastes text as a regular message)

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

**Wiring — how `steps_covered` flows to `get_filtered_step_doc`:**

`get_step_system_prompt(step, multi_user=True)` reads `MULTI_USER_STEP_CONFIG[step]` to get both `"docs"` and `"steps_covered"`. For each doc_id in `"docs"`, it calls `get_filtered_step_doc(doc_id, steps_covered)` instead of `get_document(doc_id)`. The filtering function returns only the `## STEP` sections whose numbers intersect with `steps_covered`.

For blocks that load from **multiple docs** (e.g., Block 6 loads from both `icr-steps-analysis` and `icr-steps-decision`), each doc is filtered by the same `steps_covered` list. Steps 15-16 will only match sections in `icr-steps-analysis`; Steps 17-19 will only match sections in `icr-steps-decision`. The preamble is included from the **first** doc only (to avoid duplicating Phase 0 / SLA preambles).

For Block 9 (QC), `steps_covered` is empty and `docs` is `["qc-full-checklist"]`. Since `qc-full-checklist` has no `## STEP` headers, `get_filtered_step_doc` should fall back to returning the **full document** when `steps_covered` is empty — no filtering needed.

For non-step docs (e.g., `decision-matrix`, `mlro-escalation-matrix`), these are injected via `get_document()` as-is — no filtering. Only docs that contain `## STEP` headers go through `get_filtered_step_doc`.

### Phase 4 Testing
- Verify `MULTI_USER_STEP_CONFIG` loads correctly (9 blocks + summary)
- Verify data mapping returns correct section keys per block
- Verify Block 1 data mapping returns `None` (all data) and Block 8/9 return `None` (no data)
- Verify step doc filtering extracts correct `## STEP` sections from each doc
- Verify preamble (Phase 0, SLA, etc.) is included from first doc only
- Verify Block 6 correctly loads from two source documents with correct step filtering
- Verify Block 9 loads `qc-full-checklist` in full (no step filtering)
- Verify non-step docs (`decision-matrix`, `mlro-escalation-matrix`) are loaded unfiltered
- Verify single-user `STEP_CONFIG` is completely unaffected

---

## Phase 5: Conversation Manager — Multi-User Flow

**Goal:** Wire the multi-user step config and data injection into the conversation lifecycle.

### 5.1 Conversation Creation

**File:** `server/services/conversation_manager.py`

`create_conversation` modifications:
- Detect `case.get("case_mode") == "multi"` on the case document
- Store `case_mode` on the conversation document itself — avoids needing to re-fetch the case doc on every message just to check mode:
  ```python
  conversation_doc["case_mode"] = "multi"  # or "single" for single-user
  ```
- Use `MULTI_USER_STEP_CONFIG` for investigation state initialization (9 blocks instead of 5)
- Include `total_steps` and per-block labels in the investigation state — the frontend needs these for StepIndicator rendering without hardcoding block counts:
  ```python
  "investigation_state": {
      "current_step": 1,
      "total_steps": 9,           # 5 for single-user, 9 for multi-user
      "step_labels": {             # block number → display label
          "1": "Identity & Account Overview",
          "2": "Case History & Context",
          ...
          "9": "QC Check",
      },
      "steps": [
          {
              "step_number": 1,
              "phase": "setup",
              "label": "Identity & Account Overview",
              "status": "active",
              "summary": None,
              ...
          }
      ],
  }
  ```
  For single-user, populate from existing `STEP_CONFIG` with the same pattern (5 steps, labels from phase names). This is a **non-breaking addition** — existing fields (`current_step`, `steps`) stay the same.
- Use multi-user initial assessment instruction
- Build full case data markdown (all subjects, all sections) for Phase 0 injection — `_build_case_data_markdown(case, sections=None)` (unfiltered)
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

The callers throughout `conversation_manager.py` (`send_message_streaming`, `approve_and_continue`, etc.) should read `case_mode` from the conversation document (not the case document) to determine which config to use:
```python
is_multi = conversation.get("case_mode") == "multi"
```

### 5.2 API Message Rebuilding — Data Injection

**File:** `server/services/conversation_manager.py`

`_rebuild_step_api_messages` modifications:

**CRITICAL:** The current function gates case data injection on `current_step <= 4`:
```python
if current_step <= 4 and case:
    case_data_md = _build_case_data_markdown(case)
```

For multi-user with 9 blocks, this must change. The three `None` values in `MULTI_USER_BLOCK_DATA` have different meanings (see Phase 4.2), so use explicit phase-based logic:

```python
is_multi = conversation.get("case_mode") == "multi"

if is_multi and case:
    phase = MULTI_USER_STEP_PHASES.get(current_step)
    block_data_keys = MULTI_USER_BLOCK_DATA.get(current_step)

    if current_step == 1:
        # Block 1: inject ALL data (unfiltered) — Phase 0 needs full inventory
        case_data_md = _build_case_data_markdown(case, sections=None)
        api_messages.append({"role": "user", "content": f"[CASE DATA]\n\n{case_data_md}"})
        api_messages.append({"role": "assistant", "content": "Case data received..."})
    elif block_data_keys is not None:
        # Blocks 2-7: inject filtered data
        case_data_md = _build_case_data_markdown(case, sections=block_data_keys)
        api_messages.append({"role": "user", "content": f"[CASE DATA]\n\n{case_data_md}"})
        api_messages.append({"role": "assistant", "content": "Case data received..."})
    # else: Blocks 8-9 (decision, qc_check) — no case data, summaries only

elif not is_multi and current_step <= 4 and case:
    # Single-user — existing behavior, unchanged
    case_data_md = _build_case_data_markdown(case)
    api_messages.append({"role": "user", "content": f"[CASE DATA]\n\n{case_data_md}"})
    api_messages.append({"role": "assistant", "content": "Case data received..."})
```

This ensures:
- **Block 1:** Full unfiltered data for all subjects (Phase 0 inventory + Steps 1-3)
- **Blocks 2-7:** Only the sections relevant to that block's ICR steps
- **Block 8 (Decision):** No raw data — relies on step summaries from blocks 1-7
- **Block 9 (QC):** No case data — investigator pastes ICR text as a regular message

### 5.3 System Prompt & Step Document Injection

**File:** `server/services/knowledge_base.py`

`get_step_system_prompt(step)` currently:
1. Uses `self.case_system_prompt` as the base
2. Looks up `STEP_CONFIG[step]["docs"]` for step-specific documents
3. Includes `general_rules` and `qc_quick_reference`

For multi-user, this function needs to:
1. Accept a `multi_user: bool = False` parameter
2. Use `self.multi_user_system_prompt` instead of `self.case_system_prompt`
3. Look up from `MULTI_USER_STEP_CONFIG` instead of `STEP_CONFIG`
4. Read `config[step]["steps_covered"]` and `config[step]["docs"]`; for each doc, call `get_filtered_step_doc(doc_id, steps_covered)` instead of `get_document(doc_id)`. Non-step docs (`decision-matrix`, etc.) are loaded via `get_document()` unfiltered. Distinguish by checking if the doc_id starts with `"icr-steps-"`.
5. Include `qc_quick_reference` for **all** multi-user blocks (blocks 1-8), not just steps 1-4. The single-user gate `if step <= 4` becomes `if multi_user or step <= 4`.
6. Always include `general_rules` and `reference_index_text` (same as single-user).

```python
def get_step_system_prompt(self, step: int, multi_user: bool = False) -> str:
    config = MULTI_USER_STEP_CONFIG if multi_user else STEP_CONFIG
    step_config = config[step]
    base_prompt = self.multi_user_system_prompt if multi_user else self.case_system_prompt

    parts = [base_prompt, self.general_rules]

    # QC quick reference: all multi-user blocks, or single-user steps 1-4
    if multi_user or step <= 4:
        parts.append(self.qc_quick_reference)

    parts.append(self.reference_index_text)

    # Step-specific documents
    steps_covered = step_config.get("steps_covered", [])
    for doc_id in step_config.get("docs", []):
        if doc_id.startswith("icr-steps-") and steps_covered:
            # Filter to only the relevant ## STEP sections
            parts.append(self.get_filtered_step_doc(doc_id, steps_covered))
        else:
            # Non-step docs (decision-matrix, qc-full-checklist, etc.) — load in full
            parts.append(self.get_document(doc_id))

    return "\n\n---\n\n".join(p for p in parts if p)
```

The caller in `conversation_manager.py` reads `multi_user` from the conversation document (`conversation.get("case_mode") == "multi"`) and passes it through. This avoids an extra DB read for the case document.

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

`approve_and_continue` currently has a hardcoded guard:
```python
if current_step > 3:
    raise ValueError("Cannot advance from step {current_step}. Use QC check for step 4→5.")
```

This must be made mode-aware:
```python
is_multi = conversation.get("case_mode") == "multi"
max_approve_step = 8 if is_multi else 3  # blocks 1-8 for multi, steps 1-3 for single
if current_step > max_approve_step:
    raise ValueError(
        f"Cannot advance from step {current_step}. "
        "Use QC check for the final transition."
    )
```

The phase lookup must also switch config:
```python
step_phases = MULTI_USER_STEP_PHASES if is_multi else STEP_PHASES
next_phase = step_phases[next_step]
```

**QC transition (block 8→9):** The existing `qc_check()` function handles the 4→5 transition for single-user. For multi-user, the same function handles 8→9. Update its guard:
```python
is_multi = conversation.get("case_mode") == "multi"
expected_step = 8 if is_multi else 4
if current_step != expected_step:
    raise ValueError(f"QC check only valid at step {expected_step}, currently at {current_step}")
```

The QC paste modal (`QCPasteModal`) is reused — the investigator pastes their completed multi-user ICR text, and the AI reviews it against the full QC checklist. No changes needed to the modal itself.

Other differences:
- 9 transitions instead of 5
- At each transition, the next block's data injection is filtered via `MULTI_USER_BLOCK_DATA`
- Must use `MULTI_USER_STEP_CONFIG` for step count, labels, and summary model

### 5.6 Disable Autopilot/Auto-Execute

For multi-user cases:
- `oneshot_execute` endpoint: check case mode, return 400 with "Autopilot not available for multi-user cases"
- Auto-execute endpoint: same check, return 400
- Reset case endpoint: works as-is (no changes needed)

### Phase 5 Testing
- Open a multi-user case for investigation
- Verify conversation document has `case_mode: "multi"` and `investigation_state.total_steps: 9`
- Verify Block 1 receives full unfiltered data for all subjects (Phase 0 inventory needs everything)
- Verify Blocks 2-7 receive only their filtered section subsets for all subjects
- Verify Block 8 receives only step summaries, no raw data
- Verify Block 9 (QC) receives no case data (investigator pastes ICR text)
- Verify step summaries capture per-subject findings with UID labels
- Verify `approve_and_continue` allows blocks 1→2 through 7→8 for multi-user
- Verify `approve_and_continue` rejects block 8→9 (must use `qc_check`)
- Verify `qc_check` works for block 8→9 transition
- Step through all 9 blocks to completion
- Verify single-user investigation flow is completely unaffected (regression test — same guards, same 5-step flow)
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
- Block 1 includes ALL case data (unfiltered) for the Phase 0 inventory.
  Blocks 2-7 inject only the sections relevant to that block's steps.
  Each block's data covers ALL subjects but only the relevant section types.
  Block 8 (Decision) receives no raw data — only step summaries.
  Block 9 (QC) reviews the investigator's pasted ICR text.
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
- Block 9: QC Check (Review completed ICR against QC checklist)
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
- Review AI output quality across all 9 blocks with multi-user prompt

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

**File:** `client/src/components/shared/StepIndicator.jsx`

Currently hardcodes 5 dots via `[1,2,3,4,5].map()`. Must be made dynamic:
- Read `total_steps` from `investigation_state` (populated by Phase 5.1): 5 for single-user, 9 for multi-user
- Read step labels from `investigation_state.step_labels` for tooltip/display
- Generate dots array dynamically: `Array.from({length: totalSteps}, (_, i) => i + 1).map(...)`
- Phase label text uses the label from the investigation state instead of a hardcoded map
- Props change: add `totalSteps` (default 5 for backward compat) and `stepLabel` (optional, falls back to phase name)

**File:** `client/src/pages/InvestigationPage.jsx`

Pass `totalSteps` and `stepLabel` from the loaded investigation state to `StepIndicator`. The `getInvestigationState()` API response must include these fields (update `InvestigationStateResponse` in `schemas.py` to include `total_steps: int = 5` and `step_labels: dict = {}`).

### 7.4 Case Data Panel / Tabs

**File:** `client/src/components/investigation/CaseDataTabs.jsx`

For multi-user cases, add a top-level subject selector:
- Tab per subject: "Subject 1 — UID 123", "Subject 2 — UID 456"
- Within each subject tab, the existing tab group structure (C360 sub-tabs, Standalone sections)
- Allows investigator to reference any subject's data while reviewing AI output

Single-user cases: no change to tab structure.

### 7.5 Disable Experimental Features

**File:** `client/src/pages/InvestigationPage.jsx`, `client/src/components/investigation/ChatInput.jsx`

- The experimental popover is already hidden by default when `onAutoExecute` is null — for multi-user, simply don't pass `onAutoExecute` to ChatInput. Add an explicit `case_mode !== "multi"` guard for clarity.
- Chat input shows standard stepped controls only (approve/continue through blocks 1-8, QC paste for block 8→9)
- Autopilot execution flow: `InvestigationPage` must not enter oneshot mode for multi-user cases. Guard the `?mode=oneshot` URL param check with `case_mode !== "multi"`.

### 7.6 PDF Export

**File:** `server/services/pdf_export.py`

- For multi-user cases, include subject list in PDF header: "Multi-User Case — N Subjects: UID_001, UID_002, UID_003"
- Read `case_mode` and `subjects` from the case document
- No other PDF changes needed — the transcript body (chat messages) renders as-is

### 7.7 No Other Frontend Changes

Chat interface, message display, approval flow, step dividers, thinking display, PDF download — all work as-is. The investigator interacts with multi-user cases the same way as single-user, just with more blocks and a subject selector in the data panel.

### Phase 7 Testing
- Open a multi-user case, verify case card shows multi-user badge and no Autopilot button
- Verify investigation header shows subject list
- Verify step indicator shows 9 blocks with labels (dynamic, not hardcoded)
- Verify case data tabs show per-subject data with subject selector
- Verify autopilot/auto-execute/experimental features hidden for multi-user
- Verify QC paste modal appears for block 8→9 transition
- Full walkthrough: 9 blocks to completion, verify approval flow
- Verify PDF export includes subject list in header
- Verify single-user investigation UI is completely unchanged (5 steps, same behavior)

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
- Verify UID labelling consistency across all 9 blocks
- Verify per-subject proportionality (depth matches data availability)
- Verify combined decision correctly handles divergent recommendations per subject
- Verify step summaries capture per-subject findings adequately for downstream blocks
- Verify Phase 0A produces per-subject inventory (not a single combined inventory)
- Verify Block 9 QC check correctly reviews multi-user ICR text
- Compare AI output against manually produced multi-user ICRs for QC compliance

### 8.4 PDF Export
- Verify PDF export works for multi-user case transcripts
- Verify subject list appears in PDF header
- Verify transcript length is manageable (multi-user + 9 blocks = long transcripts)

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

**Critical path:** Phase 1 → Phase 2 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

**Parallel work:** Phase 3 (ingestion frontend) can be built in parallel with Phases 4-6 once Phase 2 is complete. Phase 7 (investigation frontend) can be built in parallel with Phase 6 once Phase 5 is complete.

---

## Files Changed Per Phase

| Phase | Files Modified | Files Created |
|-------|---------------|---------------|
| 1 | `ingestion_service.py`, `ingestion.py` (router), `ingestion_schemas.py` | — |
| 2 | `ingestion_service.py`, `conversation_manager.py`, `schemas.py`, `case_service.py` | — |
| 3 | `IngestionPage.jsx`, `ingestion_api.js`, `useIngestionStatus.js` | — |
| 4 | `config.py`, `knowledge_base.py` | — |
| 5 | `conversation_manager.py`, `conversations.py`, `schemas.py` (`InvestigationStateResponse`) | — |
| 6 | `knowledge_base.py` | `system-prompt-multi-user.md` |
| 7 | `CaseCard.jsx`, `CaseHeader.jsx`, `StepIndicator.jsx`, `CaseDataTabs.jsx`, `InvestigationPage.jsx`, `ChatInput.jsx`, `pdf_export.py` | — |
| 8 | Various (refinement) | — |

---

## Out of Scope (for now)

- Autopilot/auto-execute for multi-user cases
- Dynamic block splitting based on subject count at runtime
- Per-subject investigation state (all subjects progress through blocks together)
- Cross-case subject linking (identifying the same UID across different cases)
- Multi-user specific ingestion prompts (all existing prompts work per-subject as-is)
- Migrating `coconspirator_uids` to `subjects` for existing single-user cases (different concepts, no migration needed)
