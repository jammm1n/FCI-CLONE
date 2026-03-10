# Kodex PDF Extraction Pipeline — Technical Report

## Purpose

This report documents the complete Kodex/Law Enforcement PDF extraction pipeline from the FCI Investigation Platform. It is intended as a self-contained reference for rebuilding this functionality in a different environment (e.g., the SAFU Web Agent).

---

## Architecture Overview

The pipeline has **three stages**:

1. **Python pre-processing** (per PDF): extract text with pdfplumber, strip blockchain identifiers, count UIDs
2. **AI extraction** (per PDF, parallel): structured per-case extraction via Anthropic Claude API
3. **Cross-case summary** (single AI call): combines all per-case extractions into a unified summary

**Input:** One or more PDF files + a subject UID (the user under investigation).
**Output:** Per-case structured extractions + a cross-case summary.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pdfplumber` | any recent | Pure-Python PDF text extraction (no Poppler/Tesseract needed) |
| `anthropic` | SDK v4+ | `AsyncAnthropic` client for Claude API calls |

pdfplumber is synchronous — all extraction runs in a thread via `asyncio.to_thread()`.

---

## Stage 1: PDF Text Extraction

### Function: `_extract_pdf_text_sync(filename, file_bytes) -> dict`

```python
import pdfplumber
import io

def _extract_pdf_text_sync(filename: str, file_bytes: bytes) -> dict:
    try:
        pages_text = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ''
                if text.strip():
                    pages_text.append(text)

        full_text = '\n\n'.join(pages_text)
        if not full_text.strip():
            return {
                'error': f'{filename}: PDF appears to be scanned or contains no extractable text.',
                'text': '',
                'page_count': page_count,
            }

        return {
            'text': full_text,
            'page_count': page_count,
            'error': None,
        }

    except Exception as e:
        return {
            'error': f'{filename}: Failed to extract text — {e}',
            'text': '',
            'page_count': 0,
        }
```

**Key behaviors:**
- Opens PDF from raw bytes (BytesIO), not from disk
- Iterates every page, calls `page.extract_text()`
- Skips blank pages (empty string after strip)
- Joins non-blank pages with double newline
- Returns `{text, page_count, error}` — error is set if no extractable text or exception

### Async wrapper:

```python
async def extract_pdf_text(filename: str, file_bytes: bytes) -> dict:
    return await asyncio.to_thread(_extract_pdf_text_sync, filename, file_bytes)
```

---

## Stage 2: Text Cleaning

### Function: `strip_long_identifiers(text) -> str`

Removes blockchain wallet addresses and transaction hashes from extracted text. This reduces noise and token usage for the AI call.

```python
import re

def strip_long_identifiers(text: str) -> str:
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        tokens = line.split()
        kept = []
        for token in tokens:
            stripped = token.strip('.,;:()[]{}"\'-')
            if not stripped:
                kept.append(token)
                continue
            # Pure letters — always keep (English words of any length)
            if stripped.isalpha():
                kept.append(token)
                continue
            # Contains digits AND is long — likely blockchain identifier
            if len(stripped) > 11 and any(c.isdigit() for c in stripped):
                continue
            kept.append(token)

        cleaned_line = ' '.join(kept)
        cleaned_lines.append(cleaned_line)

    # Clean up excessive blank lines from stripped content
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    # Clean up orphaned commas/semicolons from stripped lists
    result = re.sub(r'(?:,\s*){2,}', ', ', result)
    result = re.sub(r'^\s*,\s*', '', result, flags=re.MULTILINE)

    return result.strip()
```

**Logic:**
- Tokenizes each line by whitespace
- For each token, strips punctuation to get the core string
- **KEEP** if: empty after strip, purely alphabetic (any length), or short (<=11 chars)
- **STRIP** if: longer than 11 chars AND contains at least one digit (catches wallet addresses 26-42 chars, tx hashes 64 chars)
- Post-processing: collapse triple+ newlines to double, clean orphaned commas

### Function: `count_subject_uid(text, uid) -> int`

```python
def count_subject_uid(text: str, uid: str) -> int:
    if not uid:
        return 0
    pattern = r'\b' + re.escape(uid) + r'\b'
    return len(re.findall(pattern, text))
```

Word-boundary match to avoid partial matches inside longer numbers.

### Function: `estimate_other_uids(text, subject_uid) -> int`

```python
def estimate_other_uids(text: str, subject_uid: str) -> int:
    matches = re.findall(r'\b\d{7,10}\b', text)
    unique = set(matches)
    if subject_uid:
        unique.discard(subject_uid)
    # Exclude obvious dates (YYYYMMDD patterns)
    date_pattern = re.compile(r'^(19|20)\d{6}$')
    unique = {m for m in unique if not date_pattern.match(m)}
    return len(unique)
```

Finds all 7-10 digit numbers, excludes subject UID and YYYYMMDD dates. Gives the AI a starting estimate of how many other UIDs appear in the document.

---

## Stage 3: Per-PDF AI Extraction

### Function: `process_single_pdf(filename, file_bytes, subject_uid) -> dict`

Orchestrates stages 1-3 for a single PDF:

```python
async def process_single_pdf(filename, file_bytes, subject_uid):
    # Stage 1: Extract text
    extraction = await extract_pdf_text(filename, file_bytes)

    if extraction.get('error') and not extraction.get('text'):
        return {
            'filename': filename,
            'page_count': extraction.get('page_count', 0),
            'error': extraction['error'],
            'ai_output': None,
            'original_length': 0,
            'cleaned_length': 0,
            'uid_count': 0,
            'approx_other_uids': 0,
        }

    raw_text = extraction['text']
    page_count = extraction['page_count']

    # Stage 2: Clean text
    cleaned_text = strip_long_identifiers(raw_text)

    # Stage 3: Count UIDs
    uid_count = count_subject_uid(cleaned_text, subject_uid)
    other_uids = estimate_other_uids(cleaned_text, subject_uid)

    # Stage 4: AI extraction
    variables = {
        'subject_uid': subject_uid,
        'uid_count': str(uid_count),
        'approx_other_uids': str(other_uids),
    }

    ai_result = await process_with_ai(
        'kodex_per_case',
        cleaned_text,
        variables=variables,
    )

    return {
        'filename': filename,
        'page_count': page_count,
        'original_length': len(raw_text),
        'cleaned_length': len(cleaned_text),
        'uid_count': uid_count,
        'approx_other_uids': other_uids,
        'ai_output': ai_result.get('ai_output'),
        'error': ai_result.get('error'),
    }
```

---

## Stage 4: Batch Processing + Cross-Case Summary

### Function: `process_kodex_batch(files, subject_uid) -> dict`

```python
async def process_kodex_batch(files, subject_uid):
    # Run all PDFs in parallel
    tasks = [
        process_single_pdf(filename, file_bytes, subject_uid)
        for filename, file_bytes in files
    ]
    per_case_results = await asyncio.gather(*tasks)

    # Collect errors vs successes
    errors = []
    successful = []
    for r in per_case_results:
        if r.get('error') and not r.get('ai_output'):
            errors.append(r['error'])
        elif r.get('ai_output'):
            successful.append(r)

    if not successful:
        return {
            'per_case': list(per_case_results),
            'summary': None,
            'case_count': len(files),
            'errors': errors,
        }

    # Build combined input for cross-case summary
    summary_parts = []
    for i, r in enumerate(per_case_results, 1):
        if r.get('ai_output'):
            summary_parts.append(
                f'--- CASE {i} ({r["filename"]}) ---\n{r["ai_output"]}'
            )
        else:
            summary_parts.append(
                f'--- CASE {i} ({r["filename"]}) ---\n'
                f'ERROR: Could not extract data — {r.get("error", "unknown error")}'
            )
    combined_input = '\n\n'.join(summary_parts)

    # Cross-case summary AI call
    variables = {
        'subject_uid': subject_uid,
        'case_count': str(len(per_case_results)),
    }

    summary_result = await process_with_ai(
        'kodex_summary',
        combined_input,
        variables=variables,
    )

    summary_error = summary_result.get('error')
    if summary_error:
        errors.append(f'Summary generation failed: {summary_error}')

    return {
        'per_case': list(per_case_results),
        'summary': summary_result.get('ai_output'),
        'case_count': len(files),
        'errors': errors,
    }
```

**Key behaviors:**
- All PDFs processed in parallel (`asyncio.gather`)
- If ALL PDFs fail, returns early with errors (no summary call)
- Combines per-case AI outputs into a numbered format: `--- CASE 1 (filename.pdf) ---` followed by the extraction text
- Failed PDFs are included in the combined input as error entries (so the summary AI knows they failed)
- Summary AI call uses `kodex_summary` prompt with the combined text

---

## AI Processing Layer

### Function: `process_with_ai(processor_id, raw_content, variables, images) -> dict`

Located in `ai_processor.py`. This is a generic prompt-dispatch function used by all ingestion sections, not just Kodex.

**How it works:**
1. Looks up the prompt file by `processor_id` in `SECTION_PROMPT_MAP`
2. Loads the prompt file from `knowledge_base/prompts/` (cached after first load)
3. Prepends `_global-rules.md` to every prompt
4. Replaces `[PLACEHOLDER]` tokens with variable values (case-insensitive key→uppercase)
5. Sends a single non-streaming `messages.create` call to Anthropic

**Kodex-specific mappings:**
```python
SECTION_PROMPT_MAP = {
    'kodex_per_case': 'prompt-15e-kodex-per-case.md',
    'kodex_summary':  'prompt-15e-kodex-summary.md',
}
```

**Variable injection:**
```python
def _inject_variables(prompt_text, variables):
    for key, value in variables.items():
        prompt_text = prompt_text.replace(f'[{key.upper()}]', str(value))
    return prompt_text
```

For `kodex_per_case`, the variables are:
- `[SUBJECT_UID]` → the subject UID
- `[UID_COUNT]` → how many times subject UID appears in the document
- `[APPROX_OTHER_UIDS]` → estimated count of other UIDs

For `kodex_summary`, the variables are:
- `[SUBJECT_UID]` → the subject UID
- `[CASE_COUNT]` → total number of PDFs processed

**API call structure:**
```python
response = await client.messages.create(
    model=model,
    max_tokens=max_tokens,
    system=prompt_text,        # prompt is the SYSTEM message
    messages=[
        {'role': 'user', 'content': raw_content},  # cleaned text is the USER message
    ],
)
```

The prompt goes in the `system` parameter. The cleaned PDF text (or combined extractions for summary) goes in the `user` message.

**Return value:**
```python
{
    'ai_output': str | None,   # Claude's text response
    'prompt_file': str,        # which prompt file was used
    'model': str,              # model ID
    'usage': {'input': int, 'output': int},  # token counts
    'error': str | None,       # error if failed
}
```

---

## Prompt Files

### `_global-rules.md` (prepended to ALL prompts)

```
- All local currency amounts must include USD equivalent in square brackets
  immediately following the original amount.
  Example: R$500,000.00 [USD $95,700.00].
- All USD amounts must use a leading $ and commas for thousands separators
  (e.g., $3,889,921.42).
- All dates must use YYYY-MM-DD format.
- Output must be clean narrative text suitable for direct copy-pasting into
  an ICR report. No citations, no source brackets, no file names, no
  grounding references.
- Write in plain language suitable for non-native English speakers.
  Short, direct sentences preferred.
- Never use the word "pending" — it is a system status term. Use "awaiting,"
  "outstanding," or equivalent.
```

### `prompt-15e-kodex-per-case.md` (per-PDF extraction)

**System role:** "You are a data extraction tool. You produce structured data only. No narrative, no risk assessment, no mitigation statements, no ICR text."

**Input description:** "Cleaned text extracted from a single Kodex/LE case PDF for subject UID [SUBJECT_UID]."

**Pre-computed statistics provided:**
- Subject UID appearance count
- Approximate other UIDs count
- Note that blockchain identifiers have been stripped

**Extraction fields (all mandatory — use "Not stated" if missing):**
1. Kodex Ref (BNB-XXXXX or other format)
2. Date (YYYY-MM-DD)
3. Agency (full name)
4. Country
5. Request Type (Subpoena / Court Order / Information Request / Data Request / Preservation Request / Other)
6. Crime Type (as stated in document)
7. Subject Role (Target / Person of Interest / Victim / Witness / Counterparty / Third Party / Not specified)
8. Total UIDs Targeted (refine the automated estimate)
9. Target UID List (every UID visible, comma-separated)
10. Freeze/Seizure Requested (Yes / No / Not stated)
11. Freeze/Seizure Imposed (Yes + specify blocks / No / Not stated)
12. Data Provided (Yes / No / Pending response / Not stated)
13. Status (Completed / Open / Rejected / Not stated)
14. Remarks (additional notes, follow-up refs, linked case numbers, or "None")
15. Subject Individually Named in Request Narrative (Yes + quote / No / Not determinable)
16. Specific Transactions Attributed to Subject by LE (Yes + describe / No / Not determinable)
17. Confiscation or Asset Recovery Directed at Subject (Yes + describe / No / Not determinable)
18. Subject Treated Differently From Other Targets (Yes + describe / No / Not determinable)

**Special instruction:** If subject UID not found in document, state this at the top as a NOTE.

### `prompt-15e-kodex-summary.md` (cross-case summary)

**System role:** Same data extraction tool identity.

**Input:** Per-case structured extractions from [CASE_COUNT] PDFs for subject UID [SUBJECT_UID].

**Summary fields produced:**
1. Total Kodex cases
2. Date range (earliest to latest)
3. Distinct agencies (count + list with countries)
4. Distinct investigations (group cases sharing same agency + crime type + overlapping UIDs)
5. Request types breakdown
6. Crime types breakdown
7. Subject's role across cases
8. Freeze/seizure cases count
9. Cases where subject is sole target vs. one of multiple
10. **LE Specificity Assessment** (HIGH / MEDIUM / LOW / MIXED) with justification:
    - HIGH: sole target, freeze/seizure directed at subject, specific transactions attributed
    - MEDIUM: small target list (2-5), freeze requested but not imposed
    - LOW: one of many (6+), no specific attribution, broad data sweeps
    - MIXED: different levels across cases (specify per case)
11. UIDs appearing in multiple cases alongside subject

**Duplicate detection:** Flags same Kodex ref appearing in multiple cases.

---

## API Endpoint (for reference)

### `POST /api/ingestion/cases/{case_id}/kodex`

**Prerequisites:**
- Subject UID must already be set on the case (from C360 processing)
- Kodex section must not be `processing` or `complete` (reset first)

**Request:** Multipart form with one or more PDF files.

**Validation:**
- Files must be `application/pdf` or have `.pdf` extension
- File bytes are read in the endpoint handler BEFORE any async processing (important for FastAPI UploadFile lifecycle)

**Processing:** Runs `process_kodex_batch()` in the foreground (not background).

**Response shape:**
```json
{
    "status": "complete" | "error",
    "case_count": 3,
    "pdf_files": [
        {
            "filename": "case1.pdf",
            "page_count": 12,
            "original_length": 45000,
            "cleaned_length": 32000,
            "uid_count": 5,
            "approx_other_uids": 3
        }
    ],
    "ai_status": "complete" | "error",
    "errors": []
}
```

**Stored in MongoDB** (per section):
- `status`, `output` (summary text), `error_message`
- `pdf_files` (metadata array), `per_case` (full per-case results with AI output), `case_count`
- `ai_status`

### `GET /api/ingestion/cases/{case_id}/kodex`

Returns stored section data.

### `POST /api/ingestion/cases/{case_id}/kodex/reset`

Resets section to empty, clears all stored data.

---

## Data Flow Summary

```
PDF files (bytes)
    │
    ├── per PDF (parallel) ─────────────────────────────────┐
    │   │                                                    │
    │   ├── pdfplumber.open(BytesIO(bytes))                 │
    │   │   └── page.extract_text() per page                │
    │   │   └── join non-blank pages with \n\n              │
    │   │                                                    │
    │   ├── strip_long_identifiers()                        │
    │   │   └── remove tokens >11 chars containing digits   │
    │   │   └── collapse blank lines, orphaned commas       │
    │   │                                                    │
    │   ├── count_subject_uid() (word-boundary regex)       │
    │   ├── estimate_other_uids() (7-10 digit numbers)     │
    │   │                                                    │
    │   └── AI call: kodex_per_case prompt                  │
    │       system = global_rules + per_case_prompt          │
    │       user = cleaned_text                              │
    │       variables: subject_uid, uid_count,               │
    │                  approx_other_uids                     │
    │       → structured extraction (17 fields)              │
    │                                                        │
    └── combine all per-case AI outputs ────────────────────┘
        │
        └── AI call: kodex_summary prompt
            system = global_rules + summary_prompt
            user = "--- CASE 1 (file.pdf) ---\n{extraction}\n\n--- CASE 2..."
            variables: subject_uid, case_count
            → cross-case summary with LE Specificity Assessment
```

---

## Porting Notes for Web App

1. **pdfplumber** is the only extraction dependency. It's pure Python, pip-installable, no system dependencies.

2. **The AI calls** are standard Anthropic `messages.create` — system prompt + single user message. No tools, no streaming, no multi-turn.

3. **The text cleaning logic** (`strip_long_identifiers`, `count_subject_uid`, `estimate_other_uids`) is pure Python with only `re` — no external dependencies.

4. **Prompt files** are self-contained markdown. Copy them as-is. The only dynamic parts are `[SUBJECT_UID]`, `[UID_COUNT]`, `[APPROX_OTHER_UIDS]`, and `[CASE_COUNT]` — simple string replacement.

5. **The pipeline is stateless** — given PDF bytes and a subject UID, it produces structured output. No database, no session, no prior context needed.

6. **For the web app**, the investigator would: upload PDFs → get back per-case extractions + summary → paste into the main investigation chat or use directly.

7. **If the web app environment doesn't support pdfplumber** (e.g., browser-only), the text extraction stage would need to be replaced with a client-side PDF library or a server endpoint. The cleaning and AI stages remain identical.
