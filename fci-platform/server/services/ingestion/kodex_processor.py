"""
Kodex / Law Enforcement PDF & Document Processor.

Two pipelines:
  Legacy: batch PDF upload → text extraction → assembly-time AI assessment
  New:    per-entry files (PDF, DOCX, images) → per-entry AI extraction → cross-case synthesis

Dependencies: pdfplumber (PDF text), python-docx (Word doc text)
"""

import asyncio
import io
import logging
import re

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


# ── Word Document Text Extraction ──────────────────────────────────


def _extract_docx_text_sync(filename: str, file_bytes: bytes) -> dict:
    """
    Extract text from a .docx file using python-docx.

    Returns {text} or {error} if extraction fails.
    Runs synchronously — must be called via asyncio.to_thread.
    """
    from docx import Document

    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = '\n\n'.join(paragraphs)

        if not full_text.strip():
            return {
                'error': f'{filename}: Word document contains no extractable text.',
                'text': '',
            }

        return {
            'text': full_text,
            'error': None,
        }

    except Exception as e:
        logger.exception('Word doc text extraction failed for %s', filename)
        return {
            'error': f'{filename}: Failed to extract text — {e}',
            'text': '',
        }


async def extract_docx_text(filename: str, file_bytes: bytes) -> dict:
    """Async wrapper for Word doc text extraction (python-docx is synchronous)."""
    return await asyncio.to_thread(_extract_docx_text_sync, filename, file_bytes)


# ── UID Counting ────────────────────────────────────────────────────


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
    Process one PDF: extract text and count UIDs.
    No AI processing — full text is preserved for assembly-time assessment.

    Returns per-PDF data dict with extracted text and metadata.
    """
    # Extract text
    extraction = await extract_pdf_text(filename, file_bytes)

    if extraction.get('error') and not extraction.get('text'):
        return {
            'filename': filename,
            'page_count': extraction.get('page_count', 0),
            'error': extraction['error'],
            'extracted_text': None,
            'text_length': 0,
            'uid_count': 0,
            'approx_other_uids': 0,
        }

    raw_text = extraction['text']
    page_count = extraction['page_count']

    # Count UIDs (on raw text — no stripping)
    uid_count = count_subject_uid(raw_text, subject_uid)
    other_uids = estimate_other_uids(raw_text, subject_uid)

    return {
        'filename': filename,
        'page_count': page_count,
        'extracted_text': raw_text,
        'text_length': len(raw_text),
        'uid_count': uid_count,
        'approx_other_uids': other_uids,
        'error': None,
    }


# ── Batch Processing ────────────────────────────────────────────────


async def process_kodex_batch(
    files: list[tuple[str, bytes]],
    subject_uid: str,
) -> dict:
    """
    Extract text from all PDFs in parallel.

    No AI processing — extracted text is stored for assembly-time
    assessment when full case context is available.

    Args:
        files: list of (filename, file_bytes) tuples
        subject_uid: the subject UID from the case

    Returns:
        {
            per_case: [per-PDF results with extracted_text],
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
    for r in per_case_results:
        if r.get('error') and not r.get('extracted_text'):
            errors.append(r['error'])

    return {
        'per_case': list(per_case_results),
        'case_count': len(files),
        'errors': errors,
    }
