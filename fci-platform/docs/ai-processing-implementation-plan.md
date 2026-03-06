# AI Processing Layer — Implementation Plan

**Date:** 2026-03-06 (updated after gap review)
**Scope:** C360 section only — wire raw processor outputs through dedicated AI prompts, store AI-processed narratives, make them previewable in the dashboard.
**Prerequisite reading:** `docs/prompt-architecture-report.md` (prompt mapping, system prompt split strategy)

---

## Context for Fresh Chat

The ingestion dashboard currently uploads C360/UOL files, runs them through 10 synchronous processors, and produces a single assembled markdown blob stored in `sections.c360.output`. This raw output is what gets previewed and assembled into the case file.

**Goal:** Insert an AI processing step between the raw processors and storage. Each processor's output is sent individually to Claude with a dedicated prompt. The AI-processed narrative replaces the raw output as the canonical case file content. Raw output is retained for debugging but never shown to the investigator or included in assembly.

---

## Key Decisions (confirmed by user)

These were discussed and agreed before this plan was written. Do not re-open them.

1. **Trigger:** Automatic — AI processing fires immediately after raw C360 processing completes. No manual button.
2. **Execution:** Sequential API calls. Simpler code, latency is acceptable.
3. **Storage:** Case file contains ONLY AI-processed narratives. Raw output is kept for debugging only.
4. **Re-processing:** Reset the entire case and re-upload. No partial re-trigger needed.
5. **Address cross-reference:** Belongs to the Elliptic/wallet pipeline, NOT to C360. See "Important: Address Cross-Reference" section below.
6. **Preview:** Required (not optional). Per-processor collapsible sections in the preview modal so prompts can be evaluated individually during development.
7. **Prompt files:** Individual files in `knowledge_base/prompts/` with a shared global rules preamble file.

---

## Important: Address Cross-Reference and Elliptic Pipeline

The address cross-reference (`address_xref`) and UID search (`uid_search`) are part of the **wallet/Elliptic analysis pipeline**, not the C360 section. They currently piggyback on C360 because that's where addresses are extracted, but logically they belong to the Elliptic workflow.

**Current flow (stays the same for now):**
1. C360 extracts wallet addresses (Top 10 by Value + Exposed)
2. Manual wallets added by investigator
3. All deduplicated
4. Address cross-reference runs (compares wallets against UOL crypto transactions)
5. Addresses sent to Elliptic API (when API key available)

**Future target (when Elliptic AI processing is built):**
6. Elliptic screening results come back
7. **Bundle together:** Elliptic results + address cross-reference data + full address list
8. Send bundle to AI with Prompt 14E → unified wallet analysis narrative
9. That narrative goes into the case file under the Elliptic section

**For THIS implementation (C360 AI processing):**
- Address xref and UID search continue to run and be stored where they are (`sections.c360.address_xref`, `sections.c360.uid_search`)
- They are NOT included in the C360 AI-processed `output` — they are separate data
- They are NOT sent through any AI prompt yet — that happens when Elliptic AI processing is built
- The assembly function currently appends them to C360 output. **This should be revisited** when the Elliptic section gets AI processing — they should move to the Elliptic section at that point. For now, leave assembly behaviour unchanged to avoid breaking things.

---

## Important: Processors Excluded from C360 AI Processing

Two C360 processors do NOT get AI processing:

**`elliptic` processor** — Only extracts wallet addresses for the batch CSV. This is intermediate data for the Elliptic pipeline. Its output (address lists) should NOT appear in the C360 case file section. It is excluded from the assembled `output`.

**`user_profile` processor** — Produces a short text summary of user profile data (nationality, residence, account type). This is passed through as raw text in the assembled output. No AI processing needed. KYC/KYB analysis is a separate future module that will append its own output to the case file.

---

## Task 0: Extract Prompts into Individual Files

**Independent task — can be done by subagent or separate chat.**

### What
Extract the C360-relevant prompts from the monolithic `knowledge_base/core/prompt-library.md` into individual files under `knowledge_base/prompts/`. The monolith stays untouched (it's loaded live into the investigation chat system prompt).

### Files to create
```
knowledge_base/prompts/
  _global-rules.md                      ← Shared preamble (currency, dates, no citations, etc.)
  prompt-01-transaction-analysis.md
  prompt-03-account-blocks.md
  prompt-06-ctm-alerts.md
  prompt-07-privacy-coin.md
  prompt-08-failed-fiat.md
  prompt-19-counterparty-ingestion.md   ← NEW (rewritten for ingestion — see below)
  prompt-17-device-ip-ingestion.md      ← NEW (from docs/prompt-architecture-report.md Section 9)
  prompt-18-ftm-alerts-ingestion.md     ← NEW (from docs/prompt-architecture-report.md Section 9)
```

### Shared preamble: `_global-rules.md`
Extract the "GLOBAL RULES — APPLY TO ALL PROMPTS" block from the monolith into this file. The `ai_processor.py` service prepends this to every prompt at load time. Single source of truth — update once, applies everywhere. The underscore prefix sorts it first in directory listings.

### Prompt 19: Counterparty Analysis — Ingestion (NEW)
Prompt 12 from the monolith cannot be used as-is for ingestion. It references "Hexa-populated counterparty text" which is a concept from the old manual workflow. The ingestion pipeline has no Hexa text — it has the raw counterparty processor output.

**What Prompt 19 must do:**
- Accept the raw counterparty processor output (IT, BP, P2P, Device Link data — risk flags, block details, CP summaries per source, transaction volumes)
- Produce a structured factual output covering:
  - Risk-flagged counterparties with details (LE requests, ICR cases, offboarded/blocked, on-chain exposure)
  - Clean counterparty summary
  - P2P totals
  - Any self-reference errors (subject UID appearing in own CP list)
- No narrative opinions — facts only, structured for the case file
- The investigation chat will later compare this AI output against the Hexa content — that comparison is NOT this prompt's job

**What Prompt 12 (original) becomes:**
Prompt 12 stays in the monolith for the investigation chat, where it's used with Hexa text. When the system prompt split happens, it stays in the free chat prompt set. The case investigation chat will get updated instructions to compare Hexa text against the ingestion-processed counterparty data — but that's a separate task.

**Prompt 19 needs to be written.** Draft it during Task 0, modeled on Prompt 12's structure but adapted for processor output input. It should be written, tested with real data, and tweaked.

### Format for each prompt file
Each file contains ONLY the prompt text — no trigger data, no metadata headers. The file is what gets sent as the system message to the API (after the global rules preamble is prepended).

### Rules
- Copy-paste from the monolith for prompts 1, 3, 6, 7, 8 — do not rewrite or improve
- Prompts 17 and 18 come from `docs/prompt-architecture-report.md` Section 9
- Prompt 19 must be written fresh (see above)
- Do NOT modify `knowledge_base/core/prompt-library.md`
- Each file must work as a standalone system prompt when the global rules preamble is prepended

---

## Task 1: Split C360 Processor Output

### What
Modify `_run_sync_pipeline()` in `server/services/ingestion/c360_processor.py` to return **per-processor outputs** in addition to the assembled blob.

### Current return shape
```python
{
    'output': assembled_markdown,   # Single string, all processors joined by ---
    'wallet_addresses': [...],
    'csv_content': ...,
    # ... other fields
}
```

### New return shape
```python
{
    'output': assembled_markdown,           # Keep for backward compat / debugging
    'processor_outputs': {                  # NEW — keyed by processor.id
        'tx_summary': {
            'label': 'Transaction Summary',
            'content': '...',               # Raw processor output text
            'has_data': True,               # Whether processor found data
            'skipped': False,               # True if data wasn't uploaded
            'error': None,                  # Error message if processor failed
        },
        'user_profile': { ... },
        'privacy_coin': { ... },
        'counterparty': { ... },
        'device': { ... },
        'elliptic': { ... },
        'fiat': { ... },
        'ctm': { ... },
        'ftm': { ... },
        'blocks': { ... },
    },
    'wallet_addresses': [...],
    'csv_content': ...,
    # ... all other existing fields unchanged
}
```

### Implementation notes
- The loop at line 454-517 of `c360_processor.py` already iterates per-processor. Capture each result into a dict instead of only appending to `output_parts`.
- Still build the assembled `output` string for backward compatibility / debugging.
- `skipped=True` when `should_run()` returns False (data not uploaded).
- `has_data` comes from `ProcessorResult.has_data`.
- `error` captures the exception message if a processor fails.

### What NOT to change
- No changes to the processor classes themselves
- No changes to the parser, classifier, or health check
- The `wallet_addresses`, `csv_content`, and all other return fields stay the same

---

## Task 2: Create AI Processor Service

### New file: `server/services/ingestion/ai_processor.py`

### Responsibilities
1. Load the global rules preamble from `knowledge_base/prompts/_global-rules.md`
2. Load individual prompt files from `knowledge_base/prompts/`
3. Prepend global rules to each prompt at load time
4. Map processor IDs to prompt filenames
5. Call the Anthropic API with (system=prompt, user=raw_output)
6. Return the AI-generated narrative text
7. Handle errors gracefully (return error info, don't crash the pipeline)

### Prompt-to-Processor Map
```python
PROCESSOR_PROMPT_MAP = {
    'tx_summary':   'prompt-01-transaction-analysis.md',
    'blocks':       'prompt-03-account-blocks.md',
    'ctm':          'prompt-06-ctm-alerts.md',
    'privacy_coin': 'prompt-07-privacy-coin.md',
    'fiat':         'prompt-08-failed-fiat.md',
    'counterparty': 'prompt-19-counterparty-ingestion.md',
    'device':       'prompt-17-device-ip-ingestion.md',
    'ftm':          'prompt-18-ftm-alerts-ingestion.md',
}
```

Processors NOT in this map (`user_profile`, `elliptic`) get no AI processing.

### Prompt Loading
```python
# At module level — loaded once
_GLOBAL_RULES = None
_PROMPT_CACHE = {}

def _load_prompts():
    """Load global rules + all prompt files. Called once at first use."""
    prompts_dir = Path(settings.KNOWLEDGE_BASE_PATH) / 'prompts'
    global _GLOBAL_RULES
    _GLOBAL_RULES = (prompts_dir / '_global-rules.md').read_text(encoding='utf-8')
    for processor_id, filename in PROCESSOR_PROMPT_MAP.items():
        prompt_text = (prompts_dir / filename).read_text(encoding='utf-8')
        _PROMPT_CACHE[processor_id] = _GLOBAL_RULES + '\n\n' + prompt_text
```

### Dynamic Variable Injection
Prompt 17 (Device/IP) has `[NATIONALITY]` and `[RESIDENCE]` placeholders. These come from the `auto_populate` dict returned by the C360 pipeline. The AI processor must inject these before sending to the API.

```python
def _inject_variables(prompt_text: str, variables: dict) -> str:
    """Replace [PLACEHOLDER] tokens in prompt text with actual values."""
    for key, value in variables.items():
        prompt_text = prompt_text.replace(f'[{key.upper()}]', str(value))
    return prompt_text
```

If nationality/residence is not available (no USER_INFO or UOL data uploaded), inject "Unknown" as the fallback.

### API Call Pattern
```python
from anthropic import AsyncAnthropic
from server.config import settings

client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

async def process_with_ai(
    processor_id: str,
    raw_content: str,
    variables: dict | None = None,
) -> dict:
    """
    Send raw processor output through AI with the mapped prompt.

    Returns:
        {
            'ai_output': str,       # The AI-generated narrative
            'prompt_file': str,     # Which prompt was used
            'model': str,           # Which model was used
            'usage': dict,          # Token usage {input, output}
            'error': str | None,    # Error message if failed
        }
    """
```

### Key design decisions
- **Non-streaming.** This is batch processing, not interactive chat. Use `client.messages.create()` not streaming.
- **No tools.** Simple system + user message, no tool definitions.
- **Model from config.** Use `settings.ANTHROPIC_MODEL` (currently `claude-sonnet-4-6`).
- **Max tokens.** Use `settings.ANTHROPIC_MAX_TOKENS` (currently 4096 — should be sufficient for narrative paragraphs).
- **Sequential calls.** Process one prompt at a time. Simpler error handling, easier to debug, and the user is uploading other data concurrently anyway so latency is acceptable.
- **Prompt caching.** Load prompt files once at first use, not per-call. They don't change at runtime during normal operation. (During development, a reload mechanism or server restart handles prompt changes.)

---

## Task 3: Update MongoDB Schema

### Current section structure (in `_empty_sections()`)
```python
sections[key] = {
    'status': 'empty',          # empty | processing | complete | error | none
    'output': None,             # The content shown in preview / used in assembly
    'error_message': None,
    'updated_at': None,
}
```

### New C360 section fields
Add to the C360 section only (other sections unchanged for now):
```python
sections['c360']['processor_outputs'] = {}     # Raw per-processor outputs (dict keyed by processor_id)
sections['c360']['ai_outputs'] = {}            # AI-processed per-processor outputs (dict keyed by processor_id)
sections['c360']['ai_status'] = 'pending'      # pending | processing | complete | partial | error
sections['c360']['ai_progress'] = {}           # Per-processor AI status, e.g. {'tx_summary': 'complete', 'ctm': 'processing'}
```

### Status flow
```
Upload files
  → status = 'processing'
  → Raw pipeline runs
  → processor_outputs populated
  → status = 'processing' (still — AI hasn't run yet)
  → AI processing starts
  → ai_status = 'processing', ai_progress updated per-processor
  → AI processing completes
  → ai_outputs populated, ai_status = 'complete'
  → status = 'complete'
  → output = assembled AI narratives (what preview/assembly uses)
```

### The `output` field
After AI processing, `sections.c360.output` contains the assembled content:
- AI-processed narratives for the 8 processors that have prompts
- Raw text for `user_profile` (passed through, no AI)
- `elliptic` processor output EXCLUDED (it's intermediate data for the wallet pipeline)

This is what the existing preview endpoint returns and what assembly reads.

### Polling
The frontend polls `GET /cases/{case_id}/status` every 2-3 seconds. Currently it just sees `processing` → `complete`. With AI processing, the status stays `processing` longer. The `ai_status` and `ai_progress` fields let the frontend show more granular progress.

**Add to the status endpoint response:** Include `ai_status` and `ai_progress` for C360 when available.

---

## Task 4: Wire the Pipeline

### Modify `_process_c360_background()` in `server/routers/ingestion.py`

Current flow:
```
1. Run C360 pipeline → result
2. Store result['output'] as sections.c360.output
3. Set status = 'complete'
4. Auto-run address cross-reference
```

New flow:
```
1. Run C360 pipeline → result
2. Store result['processor_outputs'] in sections.c360.processor_outputs
3. Auto-run address cross-reference (unchanged — uses wallet_addresses, independent of AI)
4. Set ai_status = 'processing'
5. For each processor in PROCESSOR_PROMPT_MAP:
   a. Skip if processor has no data (skipped=True or has_data=False)
   b. Update ai_progress[processor_id] = 'processing'
   c. Call process_with_ai(processor_id, raw_content, variables)
   d. Store result in ai_outputs[processor_id]
   e. Update ai_progress[processor_id] = 'complete' (or 'error')
6. Assemble final output:
   - AI narratives for processors with prompts (in processor sort order)
   - Raw text for user_profile
   - Exclude elliptic processor output
7. Store assembled output in sections.c360.output
8. Set ai_status = 'complete', status = 'complete'
```

### Assembly of the C360 `output` field
After all AI calls complete, build the output in processor sort order:
```python
# Processor sort order (from processor classes):
# counterparty(10), user_profile(20), privacy_coin(25), device(20→40 actual),
# ctm(50), fiat(55), ftm(60→65 actual), blocks(70), tx_summary(10)
# Check actual sort_order values in the processor classes.

for processor_id, label in processors_in_sort_order:
    if processor_id == 'elliptic':
        continue  # Exclude — intermediate data for wallet pipeline
    if processor_id in ai_outputs and ai_outputs[processor_id].get('ai_output'):
        parts.append(f'### {label}\n\n{ai_outputs[processor_id]["ai_output"]}')
    elif processor_id in processor_outputs and processor_outputs[processor_id]['has_data']:
        # Fallback: raw output (for user_profile, or if AI failed)
        parts.append(f'### {label}\n\n{processor_outputs[processor_id]["content"]}')
    elif processor_outputs.get(processor_id, {}).get('skipped'):
        # Data not uploaded — include the "not uploaded" message
        parts.append(f'### {label}\n\n{processor_outputs[processor_id]["content"]}')
output = '\n\n---\n\n'.join(parts)
```

### Variables for Prompt 17
The `auto_populate` dict from the C360 pipeline contains `nationality` and `residence`. Pass these as variables to the AI processor for the device prompt:
```python
variables = {
    'nationality': result['auto_populate'].get('nationality', 'Unknown'),
    'residence': result['auto_populate'].get('residence', 'Unknown'),
}
```

### Error handling
- If an individual AI call fails, store the error in `ai_outputs[processor_id]` and continue with remaining processors.
- Set `ai_status = 'partial'` if some calls succeeded and some failed.
- The `output` field uses raw processor output as fallback for any processor whose AI call failed.
- The overall section status still becomes `complete` — a partial AI failure shouldn't block the workflow.

---

## Task 5: Frontend — AI Processing Status and Preview

### Status indicators
The frontend currently shows simple status badges per section (empty/processing/complete/error). For C360, enhance to show AI processing progress.

**During AI processing** (status=processing, ai_status=processing):
- Show "AI Processing: X/Y sections" or a progress indicator
- The `ai_progress` dict from the status endpoint tells which processors are done

**After completion:**
- Preview button works as before but now opens an enhanced modal

### Preview modal — REQUIRED for development

The preview modal must show **per-processor collapsible sections**, not one big blob. This is the primary feedback loop for prompt tuning.

Each section in the preview:
- **Section header** with processor label (e.g., "Transaction Summary", "CTM Alerts")
- **AI Output** — the AI-processed narrative (default view)
- **Raw Output toggle** — expandable/collapsible raw processor output for comparison
- **Status indicator** — complete / error / skipped / no AI (for user_profile)

This lets the user:
- Read each AI narrative individually
- Compare it against the raw data that was fed to the prompt
- Identify which prompts need tuning
- See which processors had no data or errored

### Data source for preview
The preview endpoint (`GET /cases/{case_id}/c360`) already returns the C360 section. It needs to additionally return `processor_outputs`, `ai_outputs`, and `ai_progress` so the frontend can render per-processor views.

### No new pages or routes needed
All of this fits within the existing IngestionPage and its preview modal.

---

## Task 6: Verify Assembly

### What to verify
The `assemble_case_data()` function in `ingestion_service.py` reads `sections.c360.output` and includes it in the final case markdown.

After this implementation:
- `sections.c360.output` contains AI-processed narratives (+ raw user_profile, minus elliptic)
- Assembly appends `address_xref` and `uid_search` as before (these are unchanged)
- The assembled case file should read naturally — AI narratives are investigator-ready prose

### What NOT to change in assembly (for now)
- `address_xref` and `uid_search` still get appended to C360 in assembly. This will move to the Elliptic section when that module gets AI processing. Don't change it now.

---

## File Change Summary

| File | Change Type | Description |
|---|---|---|
| `knowledge_base/prompts/_global-rules.md` | **NEW** | Shared preamble for all prompts |
| `knowledge_base/prompts/prompt-*.md` | **NEW** (9 files) | Individual prompt files (6 extracted + 3 new) |
| `server/services/ingestion/c360_processor.py` | **MODIFY** | Return per-processor outputs alongside assembled blob |
| `server/services/ingestion/ai_processor.py` | **NEW** | AI processing service — prompt loading, API calls, variable injection |
| `server/services/ingestion/ingestion_service.py` | **MODIFY** | Add AI fields to `_empty_sections()`, update status endpoint helper |
| `server/routers/ingestion.py` | **MODIFY** | Wire AI processing into `_process_c360_background()`, add ai_status to status response, update C360 GET endpoint to return per-processor data |
| `server/models/ingestion_schemas.py` | **MODIFY** | Add AI status fields to response models if needed |
| `client/src/pages/IngestionPage.jsx` | **MODIFY** | AI progress indicator, per-processor preview modal |

### Files NOT modified
- `knowledge_base/core/prompt-library.md` — untouched (live system prompt)
- `server/services/ai_client.py` — not reused (too complex for simple batch calls)
- `server/config.py` — already has `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`
- All existing platform files per CLAUDE.md rules

---

## Execution Order

Tasks 0 and 1 have no dependencies on each other and can be done in parallel.
Tasks 2-4 are sequential (each builds on the previous).
Task 5 can start after Task 3 (once the schema is defined, frontend work can begin).
Task 6 is verification — confirm assembly still works correctly.

```
Task 0 (prompts — 9 files + preamble) ─┐
                                         ├──→ Task 2 (ai_processor.py) → Task 4 (wire pipeline)
Task 1 (split processor output) ────────┘                                       ↓
                                                                           Task 6 (verify assembly)
Task 3 (schema) ──→ Task 5 (frontend — per-processor preview)
```

---

## Open Questions (for user decision during implementation)

1. **Model for ingestion AI calls** — `claude-sonnet-4-6` (current config default) or a specific override? Sonnet is cheaper and faster for development; Opus would produce better narratives for production.

2. **Token limit** — 4096 max_tokens should be enough for paragraph-length outputs. Confirm or adjust?

3. **Prompt 11 (Summary of Investigation)** — should this run automatically at assembly time as a final AI pass over all sections? Or is that a later feature?

---

## Three New Prompts to Write

The implementation requires three new prompts that don't exist yet:

1. **Prompt 17 — Device & IP Ingestion** (merges 9 + 9E): Drafted in `docs/prompt-architecture-report.md` Section 9. Ready to extract into individual file.

2. **Prompt 18 — FTM Alerts Ingestion** (adapted from Prompt 6): Drafted in `docs/prompt-architecture-report.md` Section 9. Ready to extract into individual file.

3. **Prompt 19 — Counterparty Analysis Ingestion** (replaces Prompt 12 for ingestion): NOT YET DRAFTED. Must be written during Task 0. Should process the raw counterparty processor output (IT, BP, P2P, Device Link data) and produce structured factual output. See Task 0 section for requirements.
