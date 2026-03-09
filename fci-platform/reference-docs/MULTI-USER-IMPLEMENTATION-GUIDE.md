# Multi-User Implementation Guide

Companion document to `MULTI-USER-IMPLEMENTATION-PLAN.md`. Read that first — this covers how to implement it safely.

---

## Golden Rule

**After every phase, run the existing single-user flow end-to-end.** Create a single-user ingestion case, ingest a section, assemble, open for investigation, send a message, advance a step. If any of that breaks, stop and fix before continuing. Multi-user is additive — nothing in the existing single-user path should change.

---

## Session Breakdown

Each session should be a fresh chat with clear scope. Start each session by reading `MULTI-USER-IMPLEMENTATION-PLAN.md` and this guide.

### Session 1: Phase 1 (Data Model & Backend Schema)

**Why this is the highest-risk phase:** `ingestion_service.py` is the backbone of the entire data pipeline. Every function that writes to MongoDB sections needs `subject_index` plumbed through. A missed callsite silently writes to the wrong path — and you won't know until assembly produces garbage.

**Before coding:**
- Grep `ingestion.py` (the router) for every call to `update_section`, `mark_section_none`, `save_notes`, `save_text_section`, `save_text_section_with_ai`, and any direct `$set` on `sections.*`
- Grep `ingestion_service.py` for every `f'sections.{` string to find all raw dot-notation paths
- Make a checklist of every site that needs `subject_index` added

**Implementation order within Phase 1:**
1. Add `_section_path()` helper first
2. Update `_empty_sections()` — no behavior change, just verifying it still works
3. Update `create_ingestion_case()` to accept `case_mode` and `total_subjects`
4. Update `update_section()` to use `_section_path()` — this is the critical change
5. Update all other service functions that write to sections
6. Update `_check_ready_state()` and add `_check_subject_ready()`
7. Add `submit_subject()` and `set_subject_uid()`
8. Update all router endpoints to accept and pass through `subject_index`
9. Update Pydantic schemas

**Validation after Phase 1:**
```
1. Create a multi-user ingestion case with 2 subjects via API
2. For subject 0: call every section endpoint (C360 upload, mark none, save text,
   save notes, add entry, etc.) with subject_index=0
3. Read the raw MongoDB document — verify ALL data is at subjects.0.sections.*,
   NOT at sections.*
4. Submit subject 0, verify subject 1 gets _empty_sections() populated
5. Repeat section operations for subject 1 with subject_index=1
6. Verify subjects.1.sections.* has the data
7. REGRESSION: Create a single-user case (no case_mode param)
8. Run the exact same section operations WITHOUT subject_index
9. Verify data goes to top-level sections.* as before
10. Verify _check_ready_state still works for single-user
```

**Key gotcha:** The C360 background processing pipeline (`_process_c360_background` in the router) calls multiple service functions internally. Make sure `subject_index` is passed into the background task and threaded through every internal call.

---

### Session 2: Phase 2 + Phase 4 (Assembly + Step Config)

These phases don't share files and can be done together.

**Phase 2 — Assembly:**
- The `_build_case_data_markdown()` change adds a `sections` parameter with `None` default — single-user callers are unaffected
- The multi-user branch triggers on `case.get("subjects", [])` being truthy. Existing single-user cases have no `subjects` field, so `[]` is falsy — correctly falls through to single-user path
- Assembly needs to loop over each subject's sections and apply the same `C360_AI_TO_PREPROCESSED` and `SECTION_TO_PREPROCESSED` mappings that single-user uses. Don't duplicate the mapping logic — extract it into a shared helper if it isn't already

**Phase 4 — Step Config:**
- Pure additive: new constants (`MULTI_USER_STEP_CONFIG`, `MULTI_USER_STEP_PHASES`, `MULTI_USER_BLOCK_DATA`)
- Existing `STEP_CONFIG` and `STEP_PHASES` are untouched
- Use explicit sentinel constants for the data mapping instead of overloaded `None`:
  ```python
  ALL_SECTIONS = "all"     # Block 1: inject everything for Phase 0
  NO_INJECTION = "none"    # Blocks 8, 9: no case data
  ```
  This eliminates the ambiguity of three `None` values with three different meanings.

**Validation after Session 2:**
```
1. Manually craft a multi-user ingestion doc in MongoDB with 2 completed subjects
   (or use the Phase 1 flow to create one)
2. Call assemble_case_data — verify the promoted cases document has:
   - case_mode: "multi"
   - subjects array with per-subject preprocessed_data
   - assembled_case_data markdown with per-subject headers
3. Verify _build_case_data_markdown(case, sections=None) returns all data
4. Verify _build_case_data_markdown(case, sections=["tx_summary"]) returns only
   tx_summary for each subject
5. REGRESSION: Assemble a single-user case — verify identical output to before
6. Verify MULTI_USER_STEP_CONFIG has 9 numbered blocks + "summary" key
7. Verify MULTI_USER_BLOCK_DATA has correct sentinel values
```

---

### Session 3: Phase 3 (Ingestion Frontend)

**Scope:** Frontend only. Lower risk because backend is already done.

**Key considerations:**
- `useIngestionStatus` hook needs `subjectIndex` when polling. The hook calls `getCaseStatus()` which now returns the current subject's sections. The hook doesn't need to know about subjects — the backend handles filtering. But the ingestion page needs to pass `subjectIndex` to all section API calls.
- The `canAssemble` check currently looks at `caseData.sections`. For multi-user cases during ingestion, `caseData.sections` is empty (sections live in `subjects[i].sections`). The assembly button should be gated on `case_status === "ready"` from the status endpoint, not on client-side section inspection. Or the status endpoint returns the current subject's sections in the `sections` field (which it does per Phase 1.2), and `canAssemble` checks case-level readiness separately.
- Subject progress header: keep it simple. A horizontal row of badges showing subject status. Don't over-engineer navigation — clicking a completed subject can just show a read-only view of its section statuses.

**Validation after Session 3:**
```
1. Create a multi-user case from the UI
2. Ingest subject 1: upload C360, mark some sections none, complete all required
3. Submit subject 1 — verify UI shows UID entry for subject 2
4. Enter UID for subject 2, verify empty section grid appears
5. Ingest subject 2
6. Verify "Assemble Case" button appears after all subjects complete
7. Assemble — verify redirect to cases list, case appears with multi-user badge
8. REGRESSION: Create and complete a single-user case through the same UI
```

---

### Session 4: Phase 5 (Conversation Manager)

**Why this needs sub-steps:** `conversation_manager.py` is 1700+ lines with deeply interconnected functions. Changing everything at once makes it impossible to isolate which change broke something.

**Prerequisites:** Phase 4 (step config) and Phase 2 (markdown builder) must be complete.

**Sub-step order with regression checks:**

**5.0 — Knowledge base stubs**
- Create placeholder `system-prompt-multi-user.md`
- Add `self.multi_user_system_prompt` attribute to KnowledgeBase
- Add `get_filtered_step_doc()` method
- Add `multi_user` parameter to `get_step_system_prompt()` — for now, the `multi_user=True` path can return the same prompt as `multi_user=False` (just to wire the parameter through without breaking anything)
- **Test:** Restart server. Existing single-user investigation works unchanged.

**5.1 — create_conversation**
- Add `case_mode` to conversation document
- Add `total_steps`, `step_labels`, per-step `label` to investigation state
- Add multi-user initial assessment instruction
- Single-user conversations also get `total_steps: 5` and labels (non-breaking addition)
- **Test:** Create a multi-user conversation via API. Verify MongoDB doc has correct fields. Create a single-user conversation. Verify it also has `total_steps: 5` and labels. Open an existing single-user case in the UI — verify it still works (existing conversations won't have `total_steps`, frontend must default to 5).

**5.2 — _rebuild_step_api_messages**
- Add `is_multi` check
- Implement block-based data injection with sentinel handling
- **Test:** Add logging to output the injected case data key count per block. Open a multi-user case, verify Block 1 gets all sections, Block 3 gets only `tx_summary`/`ctm_alerts`/`ftm_alerts`. Open a single-user case, verify steps 1-4 get full data and step 5 gets none.

**5.3 — get_step_system_prompt (real implementation)**
- Replace the stub wiring with actual multi-user prompt selection
- Implement filtered step doc injection using `steps_covered`
- Change QC quick reference gate to `if multi_user or step <= 4`
- **Test:** Call `get_step_system_prompt(3, multi_user=True)` — verify it returns the multi-user system prompt + filtered step doc (Steps 7-8 only) + QC quick ref. Call `get_step_system_prompt(3, multi_user=False)` — verify unchanged single-user behavior.

**5.4 — Summary generation**
- Add `MULTI_USER_SUMMARY_PROMPT` with per-subject UID instructions
- Select prompt based on `is_multi`
- **Test:** Generate a summary for a multi-user block. Verify output uses UID labels.

**5.5 — approve_and_continue + qc_check guards**
- Make `approve_and_continue` guard mode-aware: `max_approve_step = 8 if is_multi else 3`
- Make `qc_check` guard mode-aware: `expected_step = 8 if is_multi else 4`
- Switch phase lookups to use correct config
- **Test:** For multi-user: verify approve works for blocks 1→8, fails for 8→9, qc_check works for 8→9. For single-user: verify approve works for steps 1→3, fails for 3→4 (wait — single-user approve goes 1→3 and qc is 4→5). Actually verify the existing behavior is unchanged: approve 1→2, 2→3, 3→4 raises error, qc_check 4→5 works.

**5.6 — Autopilot/auto-execute guards**
- Check `case_mode` on the conversation, return 400 for multi-user
- **Test:** Call oneshot-execute and auto-execute for a multi-user conversation, verify 400. Call for single-user, verify they still work.

---

### Session 5: Phase 6 (System Prompt)

**Scope:** Replace the stub `system-prompt-multi-user.md` with real content. The knowledge base loader changes are already done from Phase 5.0.

**Key consideration:** The system prompt is cached by Anthropic. After writing the file, restart the backend server for changes to take effect.

**Validation:**
```
1. Restart server after writing the prompt file
2. Open a multi-user case for investigation
3. Verify Phase 0A produces per-subject data inventory with UID labels
4. Verify Phase 0B narrative covers connections between subjects
5. Step through blocks 1-3 minimum, reviewing AI output quality
6. Verify UID labelling is consistent
7. REGRESSION: Open a single-user case — verify it uses the single-user system prompt
```

---

### Session 6: Phase 7 (Investigation Frontend)

**Key considerations:**
- `StepIndicator` currently hardcodes 5 dots. The change to dynamic rendering must handle existing conversations that don't have `total_steps` in their investigation state — default to 5.
- `CaseCard` needs `case_mode` from the cases list API. Phase 2.5 added it to the case service — verify the API actually returns it.
- All frontend multi-user checks should be `=== "multi"` (not `!== "single"`). This ensures `undefined`/`null` (existing data) is treated as single-user.
- The experimental popover (auto-execute) is already hidden when `onAutoExecute` is null. For multi-user, don't pass `onAutoExecute` to ChatInput. Add an explicit guard for clarity.
- QC paste modal for block 8→9: the frontend currently shows QC paste when `currentStep === 4`. Change to check the phase: `stepPhase === "decision"` or use the step config to determine the QC transition point.

**Validation:**
```
1. Open case list — verify multi-user cases show badge, no Autopilot button
2. Open a multi-user investigation — verify 9 dots in step indicator
3. Verify case data panel shows subject selector tabs
4. Click through each subject's data
5. Step through a few blocks, verify approval flow
6. At block 8→9, verify QC paste modal appears
7. Verify PDF export includes subject list in header
8. REGRESSION: Open a single-user case — verify 5 dots, no subject selector,
   autopilot available, experimental popover works
9. REGRESSION: Open an existing in-progress single-user conversation —
   verify StepIndicator defaults to 5 dots (no total_steps in old state)
```

---

### Session 7: Phase 8 (End-to-End Testing)

Run the full pipeline with real (or realistic) data. See Phase 8 in the main plan for test cases. Focus on:
- 2-subject case end-to-end
- Context window monitoring (log token usage per block)
- AI output quality review
- PDF export verification

---

## Backward Compatibility Checklist

Every code path must handle these cases:

| Scenario | `case_mode` value | Expected behavior |
|----------|------------------|-------------------|
| Existing single-user ingestion case | absent / `None` | `subject_index=None` → top-level `sections.*` |
| New single-user ingestion case | `"single"` | Same as above |
| New multi-user ingestion case | `"multi"` | `subject_index=N` → `subjects.N.sections.*` |
| Existing single-user conversation | absent / `None` | `is_multi` = False, 5-step flow |
| New single-user conversation | `"single"` | Same, plus `total_steps: 5` |
| New multi-user conversation | `"multi"` | `is_multi` = True, 9-block flow |
| Existing in-progress conversation (mid-step) | absent / `None` | Frontend defaults `total_steps` to 5, phase names from hardcoded map |

**All `is_multi` checks must use:**
```python
# Backend
is_multi = conversation.get("case_mode") == "multi"  # None/absent → False ✓
is_multi = doc.get("case_mode") == "multi"            # None/absent → False ✓
```
```javascript
// Frontend
const isMulti = caseData?.case_mode === "multi";      // undefined → false ✓
```

**Never use `!== "single"`** — that would treat `undefined`/`null` as multi-user.

---

## Files Touched Per Session (Quick Reference)

| Session | Backend Files | Frontend Files |
|---------|--------------|----------------|
| 1 | `ingestion_service.py`, `ingestion.py`, `ingestion_schemas.py` | — |
| 2 | `ingestion_service.py`, `conversation_manager.py`, `schemas.py`, `case_service.py`, `config.py`, `knowledge_base.py` | — |
| 3 | — | `IngestionPage.jsx`, `ingestion_api.js`, `useIngestionStatus.js` |
| 4 | `conversation_manager.py`, `conversations.py`, `knowledge_base.py`, `schemas.py` | — |
| 5 | — | `knowledge_base/system-prompt-multi-user.md` (content only) |
| 6 | `pdf_export.py` | `CaseCard.jsx`, `CaseHeader.jsx`, `StepIndicator.jsx`, `CaseDataTabs.jsx`, `InvestigationPage.jsx`, `ChatInput.jsx` |
| 7 | Various (refinement) | Various (refinement) |

---

## Common Mistakes to Watch For

1. **Forgetting `subject_index` on a router endpoint** — data writes to top-level `sections` instead of `subjects[i].sections`. Silent corruption.
2. **Using `case_mode != "single"` instead of `case_mode == "multi"`** — breaks on `None`/absent for existing data.
3. **Hardcoding step/block counts** — use config-driven values. The numbers 5, 9, 3, 8 should come from the config, not be literals scattered through the code.
4. **Testing multi-user without testing single-user regression** — the most likely failure mode is breaking the existing flow, not the new flow failing.
5. **Forgetting to restart the server after changing KB files** — system prompt is cached by Anthropic. Changes to `system-prompt-multi-user.md`, step docs, or general rules require a server restart.
6. **The C360 background task** — `_process_c360_background` runs in a background thread and makes multiple internal calls. `subject_index` must be captured in the closure and passed through every call inside the task.
7. **MongoDB dot notation depth** — `subjects.0.sections.c360.ai_outputs.tx_summary.ai_output` is deeply nested. Test that MongoDB handles these paths correctly (it does, but verify with your driver version).
