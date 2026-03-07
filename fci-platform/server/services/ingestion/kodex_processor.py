"""
Kodex / Law Enforcement PDF Processor.

Three-stage pipeline:
  1. Python pre-processing per PDF: extract text, strip blockchain identifiers,
     count subject UID occurrences, estimate other unique UIDs
  2. Parallel AI extraction per PDF: structured per-case extraction
  3. Cross-case summary: single AI call combining all per-case extractions

Dependencies: pdfplumber (pure Python PDF text extraction)
"""

import asyncio
import io
import logging
import re

from server.services.ingestion.ai_processor import process_with_ai

logger = logging.getLogger(__name__)


# ── Text Extraction ─────────────────────────────────────────────────


def _extract_pdf_text_sync(filename: str, file_bytes: bytes) -> dict:
    """
    Extract text from a PDF using pdfplumber.

    Returns {text, page_count} or {error} if extraction fails.
    Runs synchronously — must be called via asyncio.to_thread.
    """
    import pdfplumber

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
        logger.exception('PDF text extraction failed for %s', filename)
        return {
            'error': f'{filename}: Failed to extract text — {e}',
            'text': '',
            'page_count': 0,
        }


async def extract_pdf_text(filename: str, file_bytes: bytes) -> dict:
    """Async wrapper for PDF text extraction (pdfplumber is synchronous)."""
    return await asyncio.to_thread(_extract_pdf_text_sync, filename, file_bytes)


# ── Text Cleaning ───────────────────────────────────────────────────


def strip_long_identifiers(text: str) -> str:
    """
    Remove blockchain identifiers (wallet addresses, transaction hashes)
    from extracted PDF text.

    Keeps: all English words (pure alpha), UIDs (7-10 digit numbers),
    dates, amounts, short reference numbers, agency names.

    Strips: wallet addresses (26-42 chars hex/base58), transaction hashes
    (64 chars hex), and any other long alphanumeric strings >11 chars
    that contain digits.
    """
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


def count_subject_uid(text: str, uid: str) -> int:
    """Count exact occurrences of the subject UID in text."""
    if not uid:
        return 0
    # Word-boundary match to avoid partial matches
    pattern = r'\b' + re.escape(uid) + r'\b'
    return len(re.findall(pattern, text))


def estimate_other_uids(text: str, subject_uid: str) -> int:
    """
    Count unique 7-10 digit numbers in text, excluding the subject UID.

    This gives a rough estimate of how many other UIDs appear in the
    document. The AI can refine this estimate.
    """
    # Find all 7-10 digit numbers
    matches = re.findall(r'\b\d{7,10}\b', text)
    unique = set(matches)

    # Exclude subject UID
    if subject_uid:
        unique.discard(subject_uid)

    # Exclude obvious dates (YYYYMMDD patterns)
    date_pattern = re.compile(r'^(19|20)\d{6}$')
    unique = {m for m in unique if not date_pattern.match(m)}

    return len(unique)


# ── Per-PDF Processing ──────────────────────────────────────────────


async def process_single_pdf(
    filename: str,
    file_bytes: bytes,
    subject_uid: str,
) -> dict:
    """
    Full pipeline for one PDF:
      1. Extract text with pdfplumber
      2. Strip blockchain identifiers
      3. Count UIDs
      4. AI extraction via per-case prompt

    Returns per-case structured data dict.
    """
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


# ── Batch Processing ────────────────────────────────────────────────


async def process_kodex_batch(
    files: list[tuple[str, bytes]],
    subject_uid: str,
) -> dict:
    """
    Process all PDFs in parallel, then run cross-case summary.

    Args:
        files: list of (filename, file_bytes) tuples
        subject_uid: the subject UID from the case

    Returns:
        {
            per_case: [per-case results],
            summary: str (cross-case summary),
            case_count: int,
            errors: [error messages],
        }
    """
    # Run all PDFs in parallel
    tasks = [
        process_single_pdf(filename, file_bytes, subject_uid)
        for filename, file_bytes in files
    ]
    per_case_results = await asyncio.gather(*tasks)

    # Collect errors
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
