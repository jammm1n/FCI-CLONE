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
- Option A for section storage: flat sections array with `subject_index` field

---

## Phase 1: Data Model & Backend Schema

**Goal:** Establish the multi-user data model in MongoDB without breaking single-user cases.

### 1.1 Ingestion Case Schema Changes

**File:** `server/services/ingestion/ingestion_service.py`

Update `create_ingestion_case` to accept multi-user parameters:

```python
# New fields on ingestion_cases documents:
{
    "case_mode": "single" | "multi",      # default "single"
    "total_subjects": 1,                   # 1 for single, N for multi
    "current_subject_index": 0,            # which subject is being ingested
    "subjects": [                          # empty array for single-user
        {
            "user_id": "UID_001",
            "label": "Subject 1",
            "status": "in_progress"        # pending | in_progress | complete
        },
        {
            "user_id": null,
            "label": "Subject 2",
            "status": "pending"
        }
    ]
}
```

Single-user cases: `case_mode: "single"`, `total_subjects: 1`, `subjects: []` (empty — backward compatible, existing code paths unchanged).

Multi-user cases: `subjects` array populated at creation. Only Subject 1 has a UID; subsequent UIDs entered when the investigator starts that subject.

### 1.2 Section Schema Changes

**File:** `server/services/ingestion/ingestion_service.py`

All section CRUD operations gain a `subject_index` parameter:

```python
# Existing section document:
{
    "section_type": "c360",
    "status": "completed",
    "content": "...",
    ...
}

# Multi-user addition:
{
    "section_type": "c360",
    "subject_index": 0,        # NEW — which subject this section belongs to
    "status": "completed",
    "content": "...",
    ...
}
```

For single-user cases, `subject_index` defaults to `0` or is absent — existing queries continue to work.

For multi-user cases, all section queries filter by `subject_index` in addition to `case_id` and `section_type`.

### 1.3 Ingestion Service Updates

**File:** `server/services/ingestion/ingestion_service.py`

New/modified functions:

- `create_ingestion_case()` — accept `case_mode`, `total_subjects`, initial subject UID
- `add_section()` / `update_section()` / `get_sections()` — accept `subject_index` parameter, filter accordingly
- `submit_subject(case_id, subject_index)` — mark subject complete, advance `current_subject_index`, return next subject info
- `set_subject_uid(case_id, subject_index, user_id)` — set UID for a pending subject
- `get_ingestion_case()` — return subjects array with status for progress display

Assembly function changes deferred to Phase 2.

### 1.4 Ingestion Router Updates

**File:** `server/routers/ingestion.py`

- `POST /api/ingestion/cases` — accept `case_mode` and `total_subjects` in request body
- All section endpoints — accept `subject_index` query param (default 0)
- `POST /api/ingestion/cases/{id}/submit-subject` — new endpoint for subject submission
- `PATCH /api/ingestion/cases/{id}/subjects/{index}/uid` — new endpoint for setting subsequent UIDs

### 1.5 Backward Compatibility

All changes must be backward compatible:
- Single-user cases omit `subjects` array or have it empty
- `subject_index` defaults to 0 when not provided
- Existing section queries work without modification for single-user
- No migration needed for existing data

### Phase 1 Testing
- Create a multi-user ingestion case via API
- Verify sections are stored with correct `subject_index`
- Verify single-user cases are unaffected
- Submit subjects, verify status transitions

---

## Phase 2: Case Assembly — Multi-User

**Goal:** Assemble a multi-user case into a combined case document and promote to investigations.

### 2.1 Assembly Logic

**File:** `server/services/ingestion/ingestion_service.py`

The `assemble_case` function currently collects all sections and builds `preprocessed_data` (flat dict). For multi-user:

1. Gate: all subjects must have status `complete`
2. For each subject, collect sections filtered by `subject_index`
3. Build per-subject `preprocessed_data` dicts
4. Store on the promoted case as a `subjects` array

### 2.2 Promoted Case Schema (cases collection)

```python
# Single-user (unchanged):
{
    "_id": case_id,
    "case_mode": "single",
    "subject_user_id": "UID_001",
    "preprocessed_data": { "tx_summary": "...", ... }
}

# Multi-user:
{
    "_id": case_id,
    "case_mode": "multi",
    "subject_user_id": "UID_001",    # primary subject for display
    "total_subjects": 3,
    "subjects": [
        {
            "user_id": "UID_001",
            "label": "Subject 1",
            "preprocessed_data": { "tx_summary": "...", ... }
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
    "preprocessed_data": {}    # empty for multi-user — data lives in subjects
}
```

### 2.3 Case Data Markdown Builder

**File:** `server/services/conversation_manager.py`

Update `_build_case_data_markdown()` to handle multi-user:

```python
def _build_case_data_markdown(case: dict, sections: list[str] | None = None) -> str:
    subjects = case.get("subjects", [])

    if not subjects:
        # Single-user — existing behavior
        return _build_single_user_markdown(case, sections)

    # Multi-user
    parts = [
        f"# Multi-User Case — Case ID {case.get('_id')}",
        f"**Total Subjects:** {len(subjects)}",
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
                # Include count annotations (prior_icr_count, rfi_count) same as single-user
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

- Update `CaseDetailResponse` to include `case_mode`, `total_subjects`, `subjects`
- `PreprocessedData` model stays unchanged — it's reused per subject
- Add `SubjectData` model: `user_id`, `label`, `preprocessed_data: PreprocessedData`

### Phase 2 Testing
- Assemble a multi-user case with 2-3 subjects
- Verify promoted case has correct structure
- Verify `_build_case_data_markdown` produces correct output with and without section filtering
- Verify single-user assembly is unaffected

---

## Phase 3: Ingestion Frontend

**Goal:** Update the ingestion page to support the multi-user creation and sequential ingestion flow.

### 3.1 Case Creation Form

**File:** `client/src/pages/IngestionPage.jsx`

Add to the case creation form:
- Toggle/select: "Single User" (default) / "Multi-User"
- When multi-user: numeric input for total subjects (min 2, no max)
- Subject UID field label changes to "Subject 1 UID"
- Calls updated `createIngestionCase` API with `case_mode` and `total_subjects`

### 3.2 Subject Progress Header

When viewing a multi-user case, display a progress bar/header above the section grid:

```
Subject 1 of 3 — UID 123456 [complete] → Subject 2 of 3 — UID 789012 [in progress] → Subject 3 of 3 [pending]
```

Clicking a completed subject shows its sections in read-only mode. The current subject's sections are editable.

### 3.3 Section Grid — Subject Filtering

The section grid stays identical in layout. The data source changes:
- All section API calls include `subject_index` as a query parameter
- `useIngestionStatus` hook passes `subject_index` when polling
- Section content display filters by current subject

### 3.4 Subject Lifecycle Buttons

Replace the single "Assemble Case" button with conditional buttons:

- **During subject ingestion:** "Submit Subject & Continue" — calls `submit_subject` endpoint
- **After subject submission:** Shows UID entry form for next subject, then reloads empty section grid
- **All subjects complete:** "Assemble Case" button appears (same as current, calls assembly endpoint)

### 3.5 Subject Navigation

Allow navigating back to completed subjects:
- Click a completed subject in the progress header to view its sections (read-only)
- Option to re-process a section if needed (marks subject as `in_progress` again)

### 3.6 Ingestion API Updates

**File:** `client/src/services/ingestion_api.js`

- `createIngestionCase()` — accept `caseMode`, `totalSubjects`
- All section functions — accept `subjectIndex` parameter
- `submitSubject(caseId, subjectIndex)` — new
- `setSubjectUid(caseId, subjectIndex, userId)` — new

### Phase 3 Testing
- Create multi-user case from UI
- Ingest 2 subjects sequentially, verify section isolation
- Navigate between completed and in-progress subjects
- Assemble and verify promotion to cases collection

---

## Phase 4: Multi-User Step Configuration

**Goal:** Define the block structure and data injection mapping for multi-user investigations.

### 4.1 Step Configuration

**File:** `server/config.py`

```python
MULTI_USER_STEP_CONFIG = {
    1: {  # Block 1: Header, KYC, Account Summary
        "phase": "setup",
        "label": "Identity & Account Overview",
        "steps_covered": [1, 2, 3],
        "model": "claude-opus-4-6",
    },
    2: {  # Block 2: L1, Prior ICR, LE
        "phase": "setup",
        "label": "Case History & Context",
        "steps_covered": [4, 5, 6],
        "model": "claude-opus-4-6",
    },
    3: {  # Block 3: Transactions, Alerts
        "phase": "analysis",
        "label": "Transaction & Alert Analysis",
        "steps_covered": [7, 8],
        "model": "claude-opus-4-6",
    },
    4: {  # Block 4: Elliptic, Privacy Coins
        "phase": "analysis",
        "label": "On-Chain Analysis",
        "steps_covered": [9, 10, 11],
        "model": "claude-opus-4-6",
    },
    5: {  # Block 5: Counterparties, Fiat, Device/IP
        "phase": "analysis",
        "label": "Counterparty & Device Analysis",
        "steps_covered": [12, 13, 14],
        "model": "claude-opus-4-6",
    },
    6: {  # Block 6: OSINT, Comms, RFI
        "phase": "analysis",
        "label": "Communications & OSINT",
        "steps_covered": [15, 16, 17, 18, 19],
        "model": "claude-opus-4-6",
    },
    7: {  # Block 7: Unusual Activity Summary
        "phase": "summary",
        "label": "Summary of Unusual Activity",
        "steps_covered": [20],
        "model": "claude-opus-4-6",
    },
    8: {  # Block 8: Decision
        "phase": "decision",
        "label": "Decision & Recommendation",
        "steps_covered": [21],
        "model": "claude-opus-4-6",
    },
}
```

All blocks default to Opus — multi-user cases need the stronger model due to complexity.

### 4.2 Block-to-Data Mapping

**File:** `server/services/conversation_manager.py` (or `server/config.py`)

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
def get_filtered_step_doc(step_doc_content: str, step_numbers: list[int]) -> str:
    """
    Extract preamble + specific ## STEP N sections from a step document.
    Used for multi-user cases to send only relevant steps per block.
    """
    # Parse document into preamble (everything before first ## STEP)
    # and individual step sections (split on ## STEP \d+)
    # Return preamble + requested step sections
```

This allows Block 1 to receive only Steps 1-3 from `icr-steps-setup.md` rather than the full Steps 1-6 document.

### Phase 4 Testing
- Verify step config loads correctly for multi-user
- Verify data mapping returns correct sections per block
- Verify step doc filtering extracts correct sections
- Verify single-user step config is unaffected

---

## Phase 5: Conversation Manager — Multi-User Flow

**Goal:** Wire the multi-user step config and data injection into the conversation lifecycle.

### 5.1 Conversation Creation

**File:** `server/services/conversation_manager.py`

`create_conversation` modifications:
- Detect `case_mode == "multi"` on the case document
- Use `MULTI_USER_STEP_CONFIG` for investigation state initialization (8 blocks)
- Use multi-user initial assessment instruction
- Build full case data markdown (all subjects, all sections) for Phase 0 injection
- Select `system-prompt-multi-user.md`

```python
MULTI_USER_INITIAL_ASSESSMENT = (
    "Case data loaded. This is a multi-user case with {n} subjects. "
    "Execute Phase 0A from icr-steps-setup.md: case type classification, "
    "data inventory for EACH subject (hard blockers, soft gaps, received), "
    "anomalies, connections between subjects, and clarifying questions. "
    "Do NOT produce a narrative yet — that comes in Phase 0B."
)
```

### 5.2 API Message Rebuilding

**File:** `server/services/conversation_manager.py`

`_rebuild_step_api_messages` modifications:
- For multi-user cases, determine current block from step number
- Look up `MULTI_USER_BLOCK_DATA` for the section filter
- Call `_build_case_data_markdown(case, sections=filter)` to get filtered data
- Inject filtered case data as a system message alongside the step doc
- For Block 8 (decision): inject only step summaries, no case data

For single-user cases, this function continues to work as-is.

### 5.3 Step Document Injection

`_rebuild_step_api_messages` currently loads the full step doc for the current phase. For multi-user:
- Determine which step document covers the current block's steps
- Use `get_filtered_step_doc()` to extract only relevant step sections
- Inject the filtered doc instead of the full doc

### 5.4 Summary Generation

Step summaries work the same mechanically. The summary prompt should include:

```
"Summarize the findings from this block for all subjects.
Use UID labels to distinguish per-subject findings.
This summary will be used as context for subsequent blocks."
```

This ensures Block 8 receives structured per-subject summaries it can synthesize into a combined decision.

### 5.5 Block Transitions

`approve_and_continue` works the same — advances step counter, generates summary. The only difference is 8 transitions instead of 4, and at each transition the next block's data injection is filtered differently.

### 5.6 Disable Autopilot/Auto-Execute

For multi-user cases:
- `oneshot_execute` endpoint returns 400 with "Autopilot not available for multi-user cases"
- Auto-execute endpoint returns 400 with same message
- Frontend hides these options when `case_mode == "multi"`

### Phase 5 Testing
- Open a multi-user case for investigation
- Verify Phase 0 receives full data for all subjects
- Verify subsequent blocks receive filtered data
- Verify step summaries capture per-subject findings
- Step through all 8 blocks to completion
- Verify single-user investigation flow is unaffected
- Verify autopilot/auto-execute are blocked for multi-user

---

## Phase 6: System Prompt — Multi-User

**Goal:** Create a dedicated system prompt for multi-user investigations.

### 6.1 Create `system-prompt-multi-user.md`

**File:** `knowledge_base/system-prompt-multi-user.md`

Structure (shared sections can be copied from `system-prompt-case.md`):

```markdown
# SYSTEM PROMPT — MULTI-USER INVESTIGATION
---
### IDENTITY & ROLE
You are FCI-GPT, a Senior Compliance Investigator Copilot for Binance L2
Investigations. You are investigating a multi-user case with {N} linked
subjects. You guide investigators through ICR cases step by step, producing
copy-paste-ready ICR text that meets QC standards for multi-user ICRs.
---
### MULTI-USER CASE RULES
- This case contains multiple linked subjects. All subjects must be covered
  at every analytical step.
- Always prefix data and analysis with `UID [X]:` labels. Never let the
  reader guess which subject a paragraph refers to.
- Proportionality: full analysis for all subjects, but depth matches
  available data. A subject with no activity at a given step gets a one-line
  confirmation, not a paragraph.
- You will receive data for all subjects at Phase 0, then filtered by
  relevant sections per block for subsequent steps. Each block contains
  data for ALL subjects but only the sections relevant to that block's steps.
- Decision (Block 8): produce a combined recommendation. If subjects have
  divergent risk profiles, state the recommendation per subject with
  rationale for each.
---
### DOCUMENT HIERARCHY (Priority Order)
[Same as system-prompt-case.md]
---
### STEP BOUNDARIES
[Same as system-prompt-case.md but referencing 8 blocks instead of 4]
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
[Same as system-prompt-case.md]
---
### OPERATIONAL OVERRIDE HANDLING
[Same as system-prompt-case.md]
---
### FCI / FCMI TERMINOLOGY
[Same as system-prompt-case.md]
```

### 6.2 Knowledge Base Loader

**File:** `server/services/knowledge_base.py`

- Register `"multi-user"` as a valid mode in `get_system_prompt()`
- Load `system-prompt-multi-user.md` when mode is `"multi-user"`

### 6.3 Phase 0 — Multi-User Specifics

Phase 0A for multi-user must additionally:
- Run the data inventory for EACH subject independently
- Flag connections between subjects (shared counterparties, overlapping addresses, same device/IP)
- The narrative theory (Phase 0B) should establish how the subjects are linked

The existing Phase 0A/0B structure in `icr-steps-setup.md` works — the multi-user system prompt adds the per-subject requirement on top.

### Phase 6 Testing
- Verify system prompt loads for multi-user cases
- Verify Phase 0A produces per-subject inventory
- Verify Phase 0B narrative covers all subjects and their connections
- Review AI output quality across all 8 blocks

---

## Phase 7: Investigation Frontend — Multi-User

**Goal:** Update the investigation page to handle multi-user display and controls.

### 7.1 Case Header

**File:** `client/src/components/investigation/CaseHeader.jsx`

For multi-user cases, display:
- "Multi-User Case — [N] Subjects"
- List of subject UIDs

### 7.2 Step Indicator

**File:** `client/src/components/investigation/StepIndicator.jsx`

Update to show 8 blocks with labels instead of 4/5. Block labels from `MULTI_USER_STEP_CONFIG`.

### 7.3 Case Data Panel / Tabs

**File:** `client/src/components/investigation/CaseDataTabs.jsx`

For multi-user cases, add a top-level subject selector:
- Tab per subject: "Subject 1 — UID 123", "Subject 2 — UID 456"
- Within each subject tab, the existing tab group structure (C360, Standalone sections)
- Allows investigator to reference any subject's data while reviewing AI output

### 7.4 Disable Autopilot/Auto-Execute

**File:** `client/src/pages/InvestigationPage.jsx`, `client/src/components/cases/CaseCard.jsx`

- Hide "Autopilot" button on CaseCard when `case_mode == "multi"`
- Hide experimental popover (auto-execute, express) when multi-user
- Chat input shows standard stepped controls only

### 7.5 No Other Changes

Chat interface, message display, approval flow, step dividers — all work as-is. The investigator interacts with multi-user cases the same way as single-user, just with more blocks.

### Phase 7 Testing
- Open a multi-user case, verify header and step indicator
- Verify case data tabs show per-subject data
- Verify autopilot/auto-execute hidden
- Full walkthrough: 8 blocks to completion

---

## Phase 8: End-to-End Testing & Refinement

**Goal:** Run real multi-user cases through the full pipeline and refine.

### 8.1 Test Cases
- 2-subject case (common scenario)
- 3-4 subject case (stress test)
- Same-individual multi-user case (two UIDs, one person)
- Mixed data completeness (Subject 1 has full data, Subject 3 has minimal)

### 8.2 Context Window Monitoring
- Measure token usage per block for 2, 3, 4+ subject cases
- Identify if/where context limits are hit
- Adjust block boundaries or data filtering if needed
- Consider whether certain blocks need further splitting for high-subject-count cases

### 8.3 Output Quality Review
- Verify UID labelling consistency across all blocks
- Verify per-subject proportionality (depth matches data)
- Verify combined decision correctly handles divergent recommendations
- Verify step summaries capture per-subject findings adequately
- Compare against manually produced multi-user ICRs for QC compliance

### 8.4 Refinement
- Adjust block boundaries based on testing
- Tune system prompt based on output quality
- Update multi-user rules in `icr-general-rules.md` if platform-specific additions needed
- Document any new gotchas

---

## Dependency Chain

```
Phase 1 (Data Model)
    → Phase 2 (Assembly)
        → Phase 3 (Ingestion Frontend)
            → Ready to ingest multi-user cases

Phase 4 (Step Config)
    → Phase 5 (Conversation Manager)
        → Phase 6 (System Prompt)
            → Phase 7 (Investigation Frontend)
                → Phase 8 (Testing)
```

Phases 1-3 (ingestion) and Phases 4-6 (investigation backend) can be developed in parallel once Phase 1 is complete, since Phase 4 doesn't depend on the ingestion frontend.

---

## Files Changed Per Phase

| Phase | Files Modified | Files Created |
|-------|---------------|---------------|
| 1 | `ingestion_service.py`, `ingestion.py`, `ingestion_schemas.py` | — |
| 2 | `ingestion_service.py`, `conversation_manager.py`, `schemas.py` | — |
| 3 | `IngestionPage.jsx`, `ingestion_api.js` | — |
| 4 | `config.py`, `knowledge_base.py` | — |
| 5 | `conversation_manager.py`, `conversations.py`, `ai_client.py` | — |
| 6 | `knowledge_base.py` | `system-prompt-multi-user.md` |
| 7 | `CaseHeader.jsx`, `StepIndicator.jsx`, `CaseDataTabs.jsx`, `InvestigationPage.jsx`, `CaseCard.jsx` | — |
| 8 | Various (refinement) | — |

---

## Out of Scope (for now)

- Autopilot/auto-execute for multi-user cases
- Dynamic block splitting based on subject count at runtime
- Per-subject investigation state (all subjects progress through blocks together)
- Cross-case subject linking (identifying the same UID across different cases)
