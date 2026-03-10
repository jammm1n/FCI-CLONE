"""
Ingestion Service — Case CRUD and Section Management.

Handles:
  - Case creation with active-case enforcement (one per investigator)
  - Section status updates (atomic MongoDB $set operations)
  - Automatic ready-state detection when all sections reach terminal
  - Investigator notes (pass-through, no AI processing)
  - Final assembly of all section outputs into a single markdown document

All state lives in the MongoDB `ingestion_cases` collection.
No in-memory session store.
"""

import base64
import io
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from server.config import settings
from server.database import get_database
from server.models.ingestion_schemas import (
    ALL_SECTION_KEYS,
    NONEABLE_SECTION_KEYS,
    REQUIRED_TERMINAL_KEYS,
    TERMINAL_STATUSES,
)

logger = logging.getLogger(__name__)


# ── Multi-User Path Helpers ───────────────────────────────────────


def _section_path(section_key: str, subject_index: int | None = None) -> str:
    """
    Build the MongoDB dot-notation prefix for a section field.

    Single-user (subject_index=None): 'sections.{key}'
    Multi-user  (subject_index=N):    'subjects.{N}.sections.{key}'
    """
    if subject_index is not None:
        return f'subjects.{subject_index}.sections.{section_key}'
    return f'sections.{section_key}'


def _get_section(doc: dict, section_key: str, subject_index: int | None = None) -> dict:
    """
    Read a section dict from a case document.

    Single-user (subject_index=None): doc['sections'][key]
    Multi-user  (subject_index=N):    doc['subjects'][N]['sections'][key]
    """
    if subject_index is not None:
        subjects = doc.get('subjects', [])
        if subject_index < len(subjects):
            return subjects[subject_index].get('sections', {}).get(section_key, {})
        return {}
    return doc.get('sections', {}).get(section_key, {})


# ── Assembly Order and None Statements ────────────────────────────

# Fixed order for the assembled case data markdown.
# Each entry: (section_key, markdown_heading, none_statement)
ASSEMBLY_ORDER = [
    ('c360', 'C360 Transaction Summary', 'C360 data not provided.'),
    ('elliptic', 'Elliptic Wallet Screening Results', 'No wallet screening performed.'),
    ('hexa_dump', 'L1 Referral Narrative', 'No L1 referral data provided.'),
    ('raw_hex_dump', 'HaoDesk Case Data', 'No HaoDesk case data provided.'),
    ('kyc', 'KYC Document Summary', 'KYC documents not provided.'),
    ('previous_icrs', 'Prior ICR Summary', 'No prior ICRs identified for this subject.'),
    ('rfis', 'RFI Summary', 'No RFIs on record for this subject.'),
    ('kodex', 'Law Enforcement / Kodex Summary', 'No law enforcement cases identified.'),
    ('l1_victim', 'L1 Victim Communications Summary', 'No victim communications available.'),
    ('l1_suspect', 'L1 Suspect Communications Summary', 'No suspect communications available.'),
    ('investigator_notes', 'Investigator Notes & OSINT', 'No additional notes or OSINT results.'),
]

# C360 sub-sections for expanded assembly markdown and preprocessed_data mapping.
# (ai_outputs key, preprocessed_data key, markdown heading)
C360_AI_TO_PREPROCESSED = [
    ('tx_summary',   'tx_summary',     'Transaction Summary'),
    ('privacy_coin', 'privacy_coin',   'Privacy Coin Breakdown'),
    ('counterparty', 'counterparty',   'Counterparty Analysis'),
    ('device',       'device_ip',      'Device & IP Analysis'),
    ('fiat',         'failed_fiat',    'Failed Fiat Withdrawals'),
    ('ctm',          'ctm_alerts',     'CTM Alerts'),
    ('ftm',          'ftm_alerts',     'FTM Alerts'),
    ('blocks',       'account_blocks', 'Account Blocks'),
]

# Standalone ingestion section → preprocessed_data key
SECTION_TO_PREPROCESSED = {
    'elliptic':           'elliptic',
    'hexa_dump':          'l1_referral',
    'raw_hex_dump':       'haoDesk',
    'kyc':                'kyc',
    'previous_icrs':      'prior_icr',
    'rfis':               'rfi',
    'kodex':              'kodex',
    'l1_victim':          'l1_victim',
    'l1_suspect':         'l1_suspect',
    'investigator_notes': 'investigator_notes',
}


def _build_preprocessed_from_sections(sections: dict) -> tuple[dict, list, list]:
    """
    Build preprocessed_data dict from an ingestion sections dict.

    Returns (preprocessed_data, sections_included, sections_none).
    Shared by single-user and multi-user assembly paths.
    """
    preprocessed_data = {}
    sections_included = []
    sections_none = []

    # C360 expanded sub-sections
    c360 = sections.get('c360', {})
    if c360.get('status') == 'complete':
        ai_outputs = c360.get('ai_outputs', {})
        processor_outputs = c360.get('processor_outputs', {})

        for ai_key, pp_key, _heading in C360_AI_TO_PREPROCESSED:
            ai_output = ai_outputs.get(ai_key, {}).get('ai_output')
            if ai_output:
                preprocessed_data[pp_key] = ai_output
                sections_included.append(pp_key)

        up = processor_outputs.get('user_profile', {})
        if up.get('content'):
            preprocessed_data['user_profile'] = up['content']
            sections_included.append('user_profile')

        if c360.get('address_xref'):
            preprocessed_data['address_xref'] = c360['address_xref']
            sections_included.append('address_xref')

        if c360.get('uid_search'):
            preprocessed_data['uid_search'] = c360['uid_search']
            sections_included.append('uid_search')
    else:
        sections_none.append('c360')

    # Standalone sections
    for section_key, _heading, _none_stmt in ASSEMBLY_ORDER:
        if section_key == 'c360':
            continue
        section = sections.get(section_key, {})
        output = section.get('output')

        # Total count qualifiers
        entries_count = len(section.get('entries', []))
        total_count = section.get('total_count')
        if section_key in ('previous_icrs', 'rfis') and total_count and total_count > entries_count:
            if section_key == 'previous_icrs':
                preprocessed_data['prior_icr_count'] = total_count
            else:
                preprocessed_data['rfi_count'] = total_count

        if section.get('status') == 'complete' and output:
            pp_key = SECTION_TO_PREPROCESSED.get(section_key, section_key)
            preprocessed_data[pp_key] = output
            sections_included.append(section_key)
        else:
            sections_none.append(section_key)

    return preprocessed_data, sections_included, sections_none


def _empty_sections():
    """Build the initial sections object with all sections set to 'empty'."""
    sections = {}
    for key in ALL_SECTION_KEYS:
        sections[key] = {
            'status': 'empty',
            'output': None,
            'error_message': None,
            'updated_at': None,
        }
    # C360 has extra fields
    sections['c360']['wallet_addresses'] = []
    sections['c360']['files_uploaded'] = 0
    sections['c360']['detected_file_types'] = []
    sections['c360']['warnings'] = []
    sections['c360']['csv_content'] = None
    sections['c360']['csv_filename'] = None
    # C360 AI processing fields
    sections['c360']['processor_outputs'] = {}
    sections['c360']['ai_outputs'] = {}
    sections['c360']['ai_status'] = 'pending'
    sections['c360']['ai_progress'] = {}
    # Elliptic has extra fields
    sections['elliptic']['wallet_addresses'] = []
    sections['elliptic']['manual_addresses'] = []
    # Image-only sections
    sections['kyc']['images'] = []
    sections['kyc']['batch_id'] = None
    # Text + image sections
    sections['l1_victim']['images'] = []
    sections['l1_victim']['batch_id'] = None
    sections['l1_suspect']['images'] = []
    sections['l1_suspect']['batch_id'] = None
    # Iterative entry sections
    sections['previous_icrs']['entries'] = []
    sections['rfis']['entries'] = []
    # Kodex / LE batch upload
    sections['kodex']['pdf_files'] = []
    sections['kodex']['per_case'] = []
    sections['kodex']['case_count'] = 0
    return sections


def _utcnow():
    return datetime.now(timezone.utc)


def _collection():
    return get_database()['ingestion_cases']


# ── Case CRUD ─────────────────────────────────────────────────────


async def create_ingestion_case(
    case_id: str,
    subject_uid: str = '',
    coconspirator_uids: list[str] | None = None,
    created_by: str = '',
    case_mode: str = 'single',
    total_subjects: int = 1,
) -> dict:
    """
    Create a new ingestion case document.

    For multi-user cases (case_mode="multi"), creates a subjects array
    with total_subjects entries. The first subject gets _empty_sections()
    and status "in_progress"; subsequent subjects start as "pending" with
    sections=None (populated when they become active).

    Raises ValueError if:
      - The investigator already has an active case (ingesting/ready)
      - The case_id already exists
      - case_mode is "multi" and total_subjects < 2
    """
    col = _collection()

    if case_mode == 'multi' and total_subjects < 2:
        raise ValueError('Multi-user cases require at least 2 subjects')

    # Check for existing active case for this investigator
    active = await col.find_one(
        {'created_by': created_by, 'status': {'$in': ['ingesting', 'ready']}},
        {'_id': 1},
    )
    if active:
        raise ValueError(f'active_case_exists:{active["_id"]}')

    # Check for duplicate case_id
    existing = await col.find_one({'_id': case_id}, {'_id': 1})
    if existing:
        raise ValueError(f'case_id_exists:{case_id}')

    now = _utcnow()
    doc = {
        '_id': case_id,
        'status': 'ingesting',
        'case_mode': case_mode,
        'created_by': created_by,
        'subject_uid': subject_uid,
        'coconspirator_uids': coconspirator_uids or [],
        'assembled_case_data': None,
        'created_at': now,
        'updated_at': now,
        'completed_at': None,
    }

    if case_mode == 'multi':
        doc['total_subjects'] = total_subjects
        doc['current_subject_index'] = 0
        subjects = []
        for i in range(total_subjects):
            if i == 0:
                subjects.append({
                    'user_id': subject_uid or None,
                    'label': f'Subject {i + 1}',
                    'status': 'in_progress',
                    'sections': _empty_sections(),
                })
            else:
                subjects.append({
                    'user_id': None,
                    'label': f'Subject {i + 1}',
                    'status': 'pending',
                    'sections': None,
                })
        doc['subjects'] = subjects
        doc['sections'] = {}  # empty for multi-user
    else:
        doc['sections'] = _empty_sections()

    await col.insert_one(doc)
    logger.info('Created ingestion case %s (mode=%s) for user %s', case_id, case_mode, created_by)
    return doc


async def get_active_case(user_id: str) -> dict | None:
    """Return the investigator's active case (ingesting/ready), or None."""
    return await _collection().find_one(
        {'created_by': user_id, 'status': {'$in': ['ingesting', 'ready']}}
    )


async def get_case(case_id: str) -> dict | None:
    """Return the full case document, or None if not found."""
    return await _collection().find_one({'_id': case_id})


async def get_case_status(case_id: str) -> dict | None:
    """
    Return a lightweight status snapshot for polling.

    Only returns section statuses and timestamps, not full outputs.
    Designed to be called every 2-3 seconds by the frontend.

    For multi-user cases, returns the current subject's sections in the
    'sections' field (preserving the existing polling hook's logic), plus
    multi-user metadata: case_mode, current_subject_index, subjects summary.
    """
    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        return None

    is_multi = doc.get('case_mode') == 'multi'
    current_si = doc.get('current_subject_index', 0) if is_multi else None

    # Determine which sections dict to read
    if is_multi:
        subjects = doc.get('subjects', [])
        if current_si < len(subjects) and subjects[current_si].get('sections'):
            raw_sections = subjects[current_si]['sections']
        else:
            raw_sections = {}
    else:
        raw_sections = doc.get('sections', {})

    section_statuses = {}
    for key in ALL_SECTION_KEYS:
        section = raw_sections.get(key, {})
        entry = {
            'status': section.get('status', 'empty'),
            'updated_at': section.get('updated_at'),
        }
        # Include AI processing fields for C360
        if key == 'c360':
            entry['ai_status'] = section.get('ai_status', 'pending')
            entry['ai_progress'] = section.get('ai_progress', {})
        # Include AI status for text sections with AI processing
        if section.get('ai_status'):
            entry['ai_status'] = section['ai_status']
        section_statuses[key] = entry

    result = {
        'case_id': doc['_id'],
        'case_status': doc.get('status', 'ingesting'),
        'case_mode': doc.get('case_mode', 'single'),
        'sections': section_statuses,
    }

    if is_multi:
        result['current_subject_index'] = current_si
        # Build per-subject summary for progress header
        subjects_summary = []
        for subj in doc.get('subjects', []):
            subj_sections = subj.get('sections') or {}
            complete_count = sum(
                1 for k in REQUIRED_TERMINAL_KEYS
                if subj_sections.get(k, {}).get('status') in TERMINAL_STATUSES
            )
            subjects_summary.append({
                'user_id': subj.get('user_id'),
                'label': subj.get('label', ''),
                'status': subj.get('status', 'pending'),
                'sections_complete': complete_count,
                'sections_total': len(REQUIRED_TERMINAL_KEYS),
            })
        result['subjects'] = subjects_summary

    return result


# ── Section Updates ───────────────────────────────────────────────


async def update_section(
    case_id: str,
    section_key: str,
    status: str,
    output: str | None = None,
    error: str | None = None,
    extra_fields: dict | None = None,
    subject_index: int | None = None,
):
    """
    Atomic section update via MongoDB $set.

    After each update, checks if all required sections have reached
    terminal state and auto-transitions the case to 'ready' if so.

    subject_index: For multi-user cases, the index into the subjects array.
                   None for single-user (writes to top-level sections).
    """
    now = _utcnow()
    prefix = _section_path(section_key, subject_index)
    update_fields = {
        f'{prefix}.status': status,
        f'{prefix}.updated_at': now,
        'updated_at': now,
    }

    if output is not None:
        update_fields[f'{prefix}.output'] = output
    if error is not None:
        update_fields[f'{prefix}.error_message'] = error

    # Extra fields (e.g. wallet_addresses, detected_file_types, warnings)
    if extra_fields:
        for k, v in extra_fields.items():
            update_fields[f'{prefix}.{k}'] = v

    await _collection().update_one(
        {'_id': case_id},
        {'$set': update_fields},
    )
    logger.info('Updated section %s.%s -> %s', case_id, section_key, status)

    # Check if case should transition to 'ready'
    await _check_ready_state(case_id, subject_index=subject_index)


async def mark_section_none(
    case_id: str, section_key: str, subject_index: int | None = None,
):
    """
    Mark a section as not applicable.

    Only allowed for sections in NONEABLE_SECTION_KEYS.
    Raises ValueError for invalid section keys.
    """
    if section_key not in NONEABLE_SECTION_KEYS:
        raise ValueError(
            f'Section "{section_key}" cannot be marked as not applicable'
        )

    await update_section(case_id, section_key, 'none', subject_index=subject_index)


async def save_notes(
    case_id: str, notes_text: str, subject_index: int | None = None,
) -> dict:
    """
    Save investigator notes. No AI processing.

    Empty string resets the section to 'empty'.
    Returns {status, updated_at}.
    """
    now = _utcnow()

    if notes_text.strip():
        status = 'complete'
        output = notes_text.strip()
    else:
        status = 'empty'
        output = None

    prefix = _section_path('investigator_notes', subject_index)
    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': status,
            f'{prefix}.output': output,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    return {'status': status, 'updated_at': now}


async def save_text_section(
    case_id: str, section_key: str, text: str,
    subject_index: int | None = None,
) -> dict:
    """
    Save a plain-text section (no AI processing).

    Empty string resets the section to 'empty'.
    Returns {status, updated_at}.
    """
    now = _utcnow()
    prefix = _section_path(section_key, subject_index)

    if text.strip():
        status = 'complete'
        output = text.strip()
    else:
        status = 'empty'
        output = None

    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': status,
            f'{prefix}.output': output,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id, subject_index=subject_index)
    return {'status': status, 'updated_at': now}


async def save_text_section_with_ai(
    case_id: str, section_key: str, text: str,
    subject_index: int | None = None,
) -> dict:
    """
    Save a text section, then run AI processing in the foreground.

    Stores both raw_text (original input) and output (AI narrative).
    If AI fails, falls back to storing the raw text as output.
    Returns {status, updated_at, ai_status, ai_error}.
    """
    from server.services.ingestion.ai_processor import process_with_ai

    now = _utcnow()
    prefix = _section_path(section_key, subject_index)

    if not text.strip():
        # Clear the section
        await _collection().update_one(
            {'_id': case_id},
            {'$set': {
                f'{prefix}.status': 'empty',
                f'{prefix}.output': None,
                f'{prefix}.raw_text': None,
                f'{prefix}.ai_status': None,
                f'{prefix}.updated_at': now,
                'updated_at': now,
            }},
        )
        await _check_ready_state(case_id, subject_index=subject_index)
        return {'status': 'empty', 'updated_at': now, 'ai_status': None, 'ai_error': None}

    raw_text = text.strip()

    # HaoDesk: skip AI processing, pass raw text straight through
    if section_key == 'raw_hex_dump':
        await _collection().update_one(
            {'_id': case_id},
            {'$set': {
                f'{prefix}.status': 'complete',
                f'{prefix}.output': raw_text,
                f'{prefix}.raw_text': raw_text,
                f'{prefix}.ai_status': 'skipped',
                f'{prefix}.ai_error': None,
                f'{prefix}.updated_at': now,
                'updated_at': now,
            }},
        )
        await _check_ready_state(case_id, subject_index=subject_index)
        return {
            'status': 'complete',
            'updated_at': now,
            'ai_status': 'skipped',
            'ai_error': None,
        }

    # Save raw text immediately, mark as processing
    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'processing',
            f'{prefix}.raw_text': raw_text,
            f'{prefix}.ai_status': 'processing',
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    # Run AI processing
    ai_result = await process_with_ai(section_key, raw_text)
    now = _utcnow()

    if ai_result.get('ai_output'):
        output = ai_result['ai_output']
        ai_status = 'complete'
        ai_error = None
    else:
        output = raw_text  # Fallback to raw
        ai_status = 'error'
        ai_error = ai_result.get('error', 'AI processing returned no output')

    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'complete',
            f'{prefix}.output': output,
            f'{prefix}.raw_text': raw_text,
            f'{prefix}.ai_status': ai_status,
            f'{prefix}.ai_error': ai_error,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id, subject_index=subject_index)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
    }


# ── Image Storage ─────────────────────────────────────────────────

EXT_MAP = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
}


def _store_ingestion_images(
    case_id: str,
    section_key: str,
    entry_id: str,
    files: list[tuple[str, bytes, str]],
) -> list[dict]:
    """
    Store uploaded images to disk for an ingestion entry.

    Args:
        case_id: The ingestion case ID.
        section_key: The section key (e.g., 'rfis').
        entry_id: The entry ID within the section.
        files: List of (filename, file_bytes, media_type) tuples.

    Returns:
        List of image reference dicts for MongoDB storage:
        [{'image_id': str, 'media_type': str, 'stored_path': str, 'filename': str}]
    """
    image_dir = (
        Path(settings.IMAGES_DIR) / 'ingestion' / case_id / section_key / entry_id
    )
    image_dir.mkdir(parents=True, exist_ok=True)

    stored = []
    for filename, file_bytes, media_type in files:
        image_id = f'img_{uuid.uuid4().hex[:12]}'
        ext = EXT_MAP.get(media_type, 'bin')
        filepath = image_dir / f'{image_id}.{ext}'

        try:
            filepath.write_bytes(file_bytes)
            logger.info('Stored ingestion image: %s (%d bytes)', filepath, len(file_bytes))
        except Exception as e:
            logger.error('Failed to store image %s: %s', image_id, e)
            continue

        stored.append({
            'image_id': image_id,
            'media_type': media_type,
            'stored_path': str(filepath),
            'filename': filename,
        })

    return stored


MAX_B64_BYTES = 4_500_000  # 4.5 MB — stay under Anthropic's 5 MB base64 limit


def _shrink_image(img_bytes: bytes, media_type: str) -> tuple[bytes, str]:
    """Resize/compress an image until its base64 encoding is under the API limit."""
    # Check if already small enough
    if len(base64.b64encode(img_bytes)) <= MAX_B64_BYTES:
        return img_bytes, media_type

    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    output_type = 'image/jpeg'

    # Try quality reduction first at original size, then progressively shrink
    for scale in (1.0, 0.75, 0.5, 0.35, 0.25):
        w, h = img.size
        if scale < 1.0:
            resized = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        else:
            resized = img
        for quality in (85, 65, 45):
            buf = io.BytesIO()
            resized.save(buf, format='JPEG', quality=quality)
            out_bytes = buf.getvalue()
            if len(base64.b64encode(out_bytes)) <= MAX_B64_BYTES:
                logger.info(
                    'Shrunk image from %d KB to %d KB (scale=%.0f%%, quality=%d)',
                    len(img_bytes) // 1024, len(out_bytes) // 1024,
                    scale * 100, quality,
                )
                return out_bytes, output_type

    # Last resort — should not reach here with 25% scale + quality 45
    logger.warning('Image still too large after all shrink attempts (%d KB)', len(img_bytes) // 1024)
    return out_bytes, output_type


def _load_entry_images_as_base64(entry: dict) -> list[dict]:
    """
    Load stored images for an entry from disk and return as base64.

    Returns list of {'base64': str, 'media_type': str} for the AI API.
    """
    images = entry.get('images', [])
    if not images:
        return []

    result = []
    for img_ref in images:
        stored_path = img_ref.get('stored_path', '')
        if not stored_path:
            continue
        path = Path(stored_path)
        if not path.is_file():
            logger.warning('Image file not found: %s', stored_path)
            continue
        try:
            img_bytes = path.read_bytes()
            img_bytes, media_type = _shrink_image(img_bytes, img_ref['media_type'])
            img_b64 = base64.b64encode(img_bytes).decode('ascii')
            result.append({
                'base64': img_b64,
                'media_type': media_type,
            })
        except Exception as e:
            logger.warning('Failed to load image %s: %s', stored_path, e)
    return result


# ── Image-Only Sections (KYC) ──────────────────────────────────────


async def save_images_with_ai(
    case_id: str, section_key: str, image_refs: list[dict], batch_id: str,
    subject_index: int | None = None,
) -> dict:
    """
    Save images to a section and run AI processing with vision.

    Stores image references and batch_id on the section, loads images
    as base64, sends to AI with the section's prompt, stores output.
    Returns {status, updated_at, ai_status, ai_error}.
    """
    from server.services.ingestion.ai_processor import process_with_ai

    now = _utcnow()
    col = _collection()
    prefix = _section_path(section_key, subject_index)

    # Store image refs, mark as processing
    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'processing',
            f'{prefix}.images': image_refs,
            f'{prefix}.batch_id': batch_id,
            f'{prefix}.ai_status': 'processing',
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    # Load images as base64
    images_b64 = _load_entry_images_as_base64({'images': image_refs})

    instruction = (
        f'Extract the identity information from these '
        f'{len(image_refs)} document image(s).'
    )
    ai_result = await process_with_ai(section_key, instruction, images=images_b64)
    now = _utcnow()

    if ai_result.get('ai_output'):
        output = ai_result['ai_output']
        ai_status = 'complete'
        ai_error = None
        status = 'complete'
    else:
        output = None
        ai_status = 'error'
        ai_error = ai_result.get('error', 'AI processing returned no output')
        status = 'error'

    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': status,
            f'{prefix}.output': output,
            f'{prefix}.ai_status': ai_status,
            f'{prefix}.ai_error': ai_error,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id, subject_index=subject_index)
    return {
        'status': status,
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
    }


# ── Text + Image Sections (L1 Victim, L1 Suspect) ─────────────────


async def save_text_and_images_with_ai(
    case_id: str,
    section_key: str,
    text: str,
    image_refs: list[dict],
    batch_id: str,
    subject_index: int | None = None,
) -> dict:
    """
    Save text and images to a section, then run AI processing with vision.

    Stores raw_text + image references on the section, loads images as
    base64, sends text + images to AI with the section's prompt, stores
    output. Variable injection for subject_type (victim/suspect).

    Returns {status, updated_at, ai_status, ai_error}.
    """
    from server.services.ingestion.ai_processor import process_with_ai

    now = _utcnow()
    col = _collection()
    prefix = _section_path(section_key, subject_index)
    raw_text = text.strip() if text else ''

    if not raw_text and not image_refs:
        # Clear the section
        await col.update_one(
            {'_id': case_id},
            {'$set': {
                f'{prefix}.status': 'empty',
                f'{prefix}.output': None,
                f'{prefix}.raw_text': None,
                f'{prefix}.images': [],
                f'{prefix}.batch_id': None,
                f'{prefix}.ai_status': None,
                f'{prefix}.ai_error': None,
                f'{prefix}.updated_at': now,
                'updated_at': now,
            }},
        )
        await _check_ready_state(case_id, subject_index=subject_index)
        return {
            'status': 'empty', 'updated_at': now,
            'ai_status': None, 'ai_error': None,
        }

    # Save raw text + images, mark as processing
    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'processing',
            f'{prefix}.raw_text': raw_text,
            f'{prefix}.images': image_refs,
            f'{prefix}.batch_id': batch_id,
            f'{prefix}.ai_status': 'processing',
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    # Load images as base64
    images_b64 = (
        _load_entry_images_as_base64({'images': image_refs})
        if image_refs else None
    )

    # Variable injection for victim/suspect
    variables = None
    if section_key == 'l1_victim':
        variables = {'subject_type': 'victim'}
    elif section_key == 'l1_suspect':
        variables = {'subject_type': 'suspect'}

    user_content = raw_text or 'Process these images.'
    ai_result = await process_with_ai(
        section_key, user_content,
        variables=variables,
        images=images_b64,
    )
    now = _utcnow()

    if ai_result.get('ai_output'):
        output = ai_result['ai_output']
        ai_status = 'complete'
        ai_error = None
    else:
        output = raw_text or None
        ai_status = 'error'
        ai_error = ai_result.get('error', 'AI processing returned no output')

    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'complete',
            f'{prefix}.output': output,
            f'{prefix}.raw_text': raw_text,
            f'{prefix}.ai_status': ai_status,
            f'{prefix}.ai_error': ai_error,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id, subject_index=subject_index)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
    }


# ── Iterative Entry Sections (Prior ICR, RFI) ─────────────────────


async def set_total_count(
    case_id: str, section_key: str, count: int | None,
    subject_index: int | None = None,
) -> None:
    """Set the total count for an iterative section (e.g. total prior ICRs)."""
    prefix = _section_path(section_key, subject_index)
    set_fields = {f'{prefix}.total_count': count, 'updated_at': _utcnow()}
    await _collection().update_one({'_id': case_id}, {'$set': set_fields})


async def add_entry(
    case_id: str,
    section_key: str,
    text: str,
    images: list[dict] | None = None,
    entry_id: str | None = None,
    subject_index: int | None = None,
) -> dict:
    """
    Add a text entry (with optional image references) to an iterative section.

    Args:
        case_id: The ingestion case ID.
        section_key: The section key (e.g., 'previous_icrs', 'rfis').
        text: The entry text.
        images: Optional list of image reference dicts (from _store_ingestion_images).
        entry_id: Optional pre-generated entry ID (used when images are stored first).
        subject_index: For multi-user cases, index into subjects array.

    Returns the new entry dict with its generated id.
    """
    now = _utcnow()
    col = _collection()
    prefix = _section_path(section_key, subject_index)

    if not entry_id:
        entry_id = f'entry_{uuid.uuid4().hex[:8]}'

    entry = {
        'id': entry_id,
        'text': text.strip(),
        'added_at': now,
    }
    if images:
        entry['images'] = images

    await col.update_one(
        {'_id': case_id},
        {
            '$push': {f'{prefix}.entries': entry},
            '$set': {
                f'{prefix}.status': 'incomplete',
                f'{prefix}.updated_at': now,
                'updated_at': now,
            },
        },
    )

    logger.info('Added entry %s to %s.%s', entry_id, case_id, section_key)
    return entry


async def remove_entry(
    case_id: str, section_key: str, entry_id: str,
    subject_index: int | None = None,
):
    """Remove an entry from an iterative section by its id."""
    now = _utcnow()
    col = _collection()
    prefix = _section_path(section_key, subject_index)

    await col.update_one(
        {'_id': case_id},
        {
            '$pull': {f'{prefix}.entries': {'id': entry_id}},
            '$set': {
                f'{prefix}.updated_at': now,
                'updated_at': now,
            },
        },
    )

    # If no entries left, reset section to empty
    doc = await col.find_one({'_id': case_id}, {f'{prefix}.entries': 1})
    entries = _get_section(doc, section_key, subject_index).get('entries', [])
    if not entries:
        await col.update_one(
            {'_id': case_id},
            {'$set': {
                f'{prefix}.status': 'empty',
                f'{prefix}.output': None,
                f'{prefix}.raw_text': None,
                f'{prefix}.ai_status': None,
            }},
        )

    logger.info('Removed entry %s from %s.%s', entry_id, case_id, section_key)


async def process_entries_with_ai(
    case_id: str, section_key: str,
    subject_index: int | None = None,
) -> dict:
    """
    Combine all entries in an iterative section and run AI processing.

    For most sections: concatenates entry texts, sends to AI, stores result.
    For RFI ('rfis'): two-stage pipeline:
      1. Each entry processed individually with prompt-22 (text + images)
      2. All per-entry narratives combined and sent to prompt-10 for summary
    """
    from server.services.ingestion.ai_processor import process_with_ai

    col = _collection()
    prefix = _section_path(section_key, subject_index)
    doc = await col.find_one({'_id': case_id}, {f'{prefix}': 1})
    entries = _get_section(doc, section_key, subject_index).get('entries', [])

    if not entries:
        return {'status': 'empty', 'ai_status': None, 'ai_error': 'No entries to process'}

    now = _utcnow()
    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'processing',
            f'{prefix}.ai_status': 'processing',
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    if section_key == 'rfis':
        return await _process_rfi_entries(
            case_id, section_key, entries, subject_index=subject_index,
        )

    # Default path: combine entries into numbered text, single AI call
    parts = []
    for i, entry in enumerate(entries, 1):
        parts.append(f'--- Entry {i} ---\n{entry["text"]}')
    combined_text = '\n\n'.join(parts)

    await col.update_one(
        {'_id': case_id},
        {'$set': {f'{prefix}.raw_text': combined_text}},
    )

    ai_result = await process_with_ai(section_key, combined_text)
    now = _utcnow()

    if ai_result.get('ai_output'):
        output = ai_result['ai_output']
        ai_status = 'complete'
        ai_error = None
    else:
        output = combined_text
        ai_status = 'error'
        ai_error = ai_result.get('error', 'AI processing returned no output')

    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'complete',
            f'{prefix}.output': output,
            f'{prefix}.raw_text': combined_text,
            f'{prefix}.ai_status': ai_status,
            f'{prefix}.ai_error': ai_error,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id, subject_index=subject_index)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
        'entry_count': len(entries),
    }


async def _process_rfi_entries(
    case_id: str, section_key: str, entries: list[dict],
    subject_index: int | None = None,
) -> dict:
    """
    Two-stage RFI processing:
      Stage 1: Each entry → prompt-22 (rfi_doc_review) with text + images
      Stage 2: All per-entry outputs combined → prompt-10 (rfis) for summary
    """
    from server.services.ingestion.ai_processor import process_with_ai

    col = _collection()
    prefix = _section_path(section_key, subject_index)

    # Stage 1: Process each entry individually
    entry_narratives = []
    entry_errors = []

    for i, entry in enumerate(entries, 1):
        # Load images from disk if this entry has them
        images_b64 = _load_entry_images_as_base64(entry)

        ai_result = await process_with_ai(
            'rfi_doc_review',
            entry['text'],
            images=images_b64 if images_b64 else None,
        )

        if ai_result.get('ai_output'):
            narrative = ai_result['ai_output']
        else:
            # Fallback: use raw text
            narrative = entry['text']
            entry_errors.append(f'Entry {i}: {ai_result.get("error", "no output")}')

        entry_narratives.append(narrative)

        # Store per-entry AI output back on the entry (positional $ operator)
        await col.update_one(
            {'_id': case_id, f'{prefix}.entries.id': entry['id']},
            {'$set': {
                f'{prefix}.entries.$.ai_output': narrative,
            }},
        )

    # Stage 2: Combine all per-entry narratives, send to prompt-10
    combined_parts = []
    for i, narrative in enumerate(entry_narratives, 1):
        combined_parts.append(f'--- RFI {i} ---\n{narrative}')
    combined_text = '\n\n'.join(combined_parts)

    await col.update_one(
        {'_id': case_id},
        {'$set': {f'{prefix}.raw_text': combined_text}},
    )

    ai_result = await process_with_ai('rfis', combined_text)
    now = _utcnow()

    if ai_result.get('ai_output'):
        output = ai_result['ai_output']
        ai_status = 'complete' if not entry_errors else 'partial'
        ai_error = '; '.join(entry_errors) if entry_errors else None
    else:
        output = combined_text
        ai_status = 'error'
        ai_error = ai_result.get('error', 'AI processing returned no output')

    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.status': 'complete',
            f'{prefix}.output': output,
            f'{prefix}.raw_text': combined_text,
            f'{prefix}.ai_status': ai_status,
            f'{prefix}.ai_error': ai_error,
            f'{prefix}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id, subject_index=subject_index)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
        'entry_count': len(entries),
    }


# ── Ready-State Detection ─────────────────────────────────────────


def _sections_all_terminal(sections: dict) -> bool:
    """Check if all required sections in a sections dict are terminal."""
    return all(
        sections.get(key, {}).get('status') in TERMINAL_STATUSES
        for key in REQUIRED_TERMINAL_KEYS
    )


async def _check_ready_state(
    case_id: str, subject_index: int | None = None,
):
    """
    Check if all required sections are in terminal state.

    Single-user: If all top-level sections are terminal, transition case to 'ready'.
    Multi-user: Checks the specified subject's sections only. The case-level
    'ready' transition happens only when ALL subjects are 'complete' (via submit_subject).
    investigator_notes is excluded — it never blocks readiness.
    """
    doc = await _collection().find_one(
        {'_id': case_id},
        {'status': 1, 'sections': 1, 'case_mode': 1, 'subjects': 1},
    )
    if not doc or doc.get('status') != 'ingesting':
        return

    if doc.get('case_mode') == 'multi':
        # Multi-user: don't auto-transition the case to ready.
        # Subject readiness is checked via _check_subject_ready() and
        # case readiness transitions happen in submit_subject().
        return

    # Single-user: check top-level sections
    sections = doc.get('sections', {})
    if _sections_all_terminal(sections):
        await _collection().update_one(
            {'_id': case_id},
            {'$set': {'status': 'ready', 'updated_at': _utcnow()}},
        )
        logger.info('Case %s auto-transitioned to ready', case_id)


async def _check_subject_ready(case_id: str, subject_index: int) -> bool:
    """
    Check if a specific subject's sections are all terminal.

    Returns True if the subject is ready for submission, False otherwise.
    Does NOT modify any state — callers decide what to do with the result.
    """
    doc = await _collection().find_one(
        {'_id': case_id},
        {f'subjects.{subject_index}.sections': 1},
    )
    if not doc:
        return False

    subjects = doc.get('subjects', [])
    if subject_index >= len(subjects):
        return False

    sections = subjects[subject_index].get('sections', {})
    if not sections:
        return False

    return _sections_all_terminal(sections)


# ── Multi-User Subject Management ─────────────────────────────────


async def submit_subject(case_id: str, subject_index: int) -> dict:
    """
    Mark a subject as complete and advance to the next subject.

    Validates that all required sections for this subject are terminal.
    If a next subject exists, populates its sections with _empty_sections()
    and sets its status to 'in_progress'. Updates current_subject_index.

    If all subjects are now complete, transitions the case to 'ready'.

    Returns {submitted_index, next_index, case_status}.
    Raises ValueError if subject is not ready or index is invalid.
    """
    col = _collection()
    doc = await col.find_one({'_id': case_id})
    if not doc:
        raise ValueError(f'Case not found: {case_id}')

    if doc.get('case_mode') != 'multi':
        raise ValueError('submit_subject is only valid for multi-user cases')

    subjects = doc.get('subjects', [])
    if subject_index >= len(subjects):
        raise ValueError(f'Invalid subject index: {subject_index}')

    subject = subjects[subject_index]
    if subject.get('status') == 'complete':
        raise ValueError(f'Subject {subject_index} is already complete')

    # Verify all required sections are terminal
    sections = subject.get('sections', {})
    if not sections or not _sections_all_terminal(sections):
        raise ValueError(
            f'Subject {subject_index} has incomplete sections. '
            'All required sections must be complete or marked N/A.'
        )

    now = _utcnow()
    update = {
        f'subjects.{subject_index}.status': 'complete',
        'updated_at': now,
    }

    next_index = subject_index + 1
    has_next = next_index < len(subjects)

    if has_next:
        # Populate next subject's sections and activate it
        update[f'subjects.{next_index}.sections'] = _empty_sections()
        update[f'subjects.{next_index}.status'] = 'in_progress'
        update['current_subject_index'] = next_index

    # Check if ALL subjects will be complete after this submission
    all_complete = all(
        s.get('status') == 'complete'
        for i, s in enumerate(subjects)
        if i != subject_index  # skip the one we're about to complete
    )
    # The current subject is being completed now, so check passes for it
    case_ready = all_complete and True  # current subject is now complete

    if case_ready:
        update['status'] = 'ready'

    await col.update_one({'_id': case_id}, {'$set': update})
    logger.info(
        'Submitted subject %d for case %s (next=%s, case_ready=%s)',
        subject_index, case_id,
        next_index if has_next else 'none',
        case_ready,
    )

    return {
        'submitted_index': subject_index,
        'next_index': next_index if has_next else None,
        'case_status': 'ready' if case_ready else 'ingesting',
    }


async def set_subject_uid(
    case_id: str, subject_index: int, user_id: str,
) -> dict:
    """
    Set the UID for a subject in a multi-user case.

    Raises ValueError if the case is not multi-user or index is invalid.
    Returns {subject_index, user_id}.
    """
    col = _collection()
    doc = await col.find_one({'_id': case_id}, {'case_mode': 1, 'subjects': 1})
    if not doc:
        raise ValueError(f'Case not found: {case_id}')

    if doc.get('case_mode') != 'multi':
        raise ValueError('set_subject_uid is only valid for multi-user cases')

    subjects = doc.get('subjects', [])
    if subject_index >= len(subjects):
        raise ValueError(f'Invalid subject index: {subject_index}')

    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'subjects.{subject_index}.user_id': user_id,
            'updated_at': _utcnow(),
        }},
    )
    logger.info(
        'Set UID for subject %d in case %s: %s',
        subject_index, case_id, user_id,
    )

    return {'subject_index': subject_index, 'user_id': user_id}


# ── Delete ────────────────────────────────────────────────────────


async def delete_case(case_id: str):
    """
    Delete an ingestion case entirely.

    Removes the document from MongoDB. Only allowed when status is
    'ingesting' or 'ready'.

    Raises ValueError if case not found or status disallows deletion.
    """
    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        raise ValueError(f'Case not found: {case_id}')

    if doc.get('status') not in ('ingesting', 'ready'):
        raise ValueError(
            f'Cannot delete case in status "{doc.get("status")}". '
            'Only ingesting or ready cases can be deleted.'
        )

    await _collection().delete_one({'_id': case_id})
    logger.info('Deleted ingestion case %s', case_id)


# ── Reset ─────────────────────────────────────────────────────────


async def reset_case(case_id: str) -> dict:
    """
    Reset an ingestion case to its initial state.

    Clears all sections, subject_uid, and assembled data.
    For multi-user cases, re-initializes the subjects array:
    first subject gets _empty_sections() + 'in_progress', others get
    sections=None + 'pending', current_subject_index resets to 0.

    Only allowed when status is 'ingesting' or 'ready'.

    Returns the reset case document.
    Raises ValueError if case not found or status disallows reset.
    """
    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        raise ValueError(f'Case not found: {case_id}')

    if doc.get('status') not in ('ingesting', 'ready'):
        raise ValueError(
            f'Cannot reset case in status "{doc.get("status")}". '
            'Only ingesting or ready cases can be reset.'
        )

    now = _utcnow()
    update_set = {
        'status': 'ingesting',
        'subject_uid': '',
        'coconspirator_uids': [],
        'assembled_case_data': None,
        'updated_at': now,
        'completed_at': None,
    }

    if doc.get('case_mode') == 'multi':
        total = doc.get('total_subjects', len(doc.get('subjects', [])))
        subjects = []
        for i in range(total):
            if i == 0:
                subjects.append({
                    'user_id': None,
                    'label': f'Subject {i + 1}',
                    'status': 'in_progress',
                    'sections': _empty_sections(),
                })
            else:
                subjects.append({
                    'user_id': None,
                    'label': f'Subject {i + 1}',
                    'status': 'pending',
                    'sections': None,
                })
        update_set['subjects'] = subjects
        update_set['current_subject_index'] = 0
        update_set['sections'] = {}
    else:
        update_set['sections'] = _empty_sections()

    await _collection().update_one(
        {'_id': case_id},
        {
            '$set': update_set,
            '$unset': {'uol_raw_data': 1},
        },
    )
    logger.info('Reset ingestion case %s', case_id)

    updated = await _collection().find_one({'_id': case_id})
    return updated


# ── Assembly ──────────────────────────────────────────────────────


def _build_assembled_markdown_single(doc: dict, sections: dict, preprocessed_data: dict) -> list[str]:
    """Build assembled markdown parts for a single-user case (or one subject)."""
    parts = []

    # C360 expanded sub-sections
    c360 = sections.get('c360', {})
    if c360.get('status') == 'complete':
        ai_outputs = c360.get('ai_outputs', {})
        processor_outputs = c360.get('processor_outputs', {})

        for ai_key, pp_key, heading in C360_AI_TO_PREPROCESSED:
            ai_output = ai_outputs.get(ai_key, {}).get('ai_output')
            if ai_output:
                parts.append('## {}'.format(heading))
                parts.append('')
                parts.append(ai_output)
                parts.append('')

        up = processor_outputs.get('user_profile', {})
        if up.get('content'):
            parts.append('## User Profile')
            parts.append('')
            parts.append(up['content'])
            parts.append('')

        if c360.get('address_xref'):
            parts.append('## Address Cross-Reference')
            parts.append('')
            parts.append(c360['address_xref'])
            parts.append('')

        if c360.get('uid_search'):
            parts.append('## UID Search Results')
            parts.append('')
            parts.append(c360['uid_search'])
            parts.append('')
    else:
        parts.append('## C360 Transaction Summary')
        parts.append('')
        parts.append('C360 data not provided.')
        parts.append('')

    # Standalone sections
    for section_key, heading, none_statement in ASSEMBLY_ORDER:
        if section_key == 'c360':
            continue
        section = sections.get(section_key, {})
        output = section.get('output')

        section_heading = heading
        entries_count = len(section.get('entries', []))
        total_count = section.get('total_count')
        if section_key in ('previous_icrs', 'rfis') and total_count and total_count > entries_count:
            section_heading = '{} ({} of {} included)'.format(
                heading, entries_count, total_count
            )

        parts.append('## {}'.format(section_heading))
        parts.append('')

        if section.get('status') == 'complete' and output:
            # Context notes for subset counts
            if section_key == 'previous_icrs' and preprocessed_data.get('prior_icr_count'):
                total = preprocessed_data['prior_icr_count']
                parts.append('*Note: {} prior ICRs exist for this subject. '
                             'The {} most recent are summarised below.*'.format(total, entries_count))
                parts.append('')
            elif section_key == 'rfis' and preprocessed_data.get('rfi_count'):
                total = preprocessed_data['rfi_count']
                parts.append('*Note: {} RFIs exist for this subject. '
                             'The {} most recent are summarised below.*'.format(total, entries_count))
                parts.append('')
            parts.append(output)
        elif section_key == 'kodex' and section.get('status') == 'extracted':
            case_count = section.get('case_count', 0)
            parts.append(
                '*{} Kodex PDF(s) extracted — LE assessment will be '
                'generated at assembly time using full case context.*'.format(case_count)
            )
        else:
            parts.append(none_statement)

        parts.append('')

    return parts


# ── Kodex Assembly-Time AI Assessment ────────────────────────────


async def _run_kodex_assessment(
    sections: dict,
    case_data_markdown: str,
    subject_uid: str,
) -> str | None:
    """
    Run the context-aware Kodex LE assessment at assembly time.

    Takes the compiled case data markdown (all sections except Kodex) and
    the raw extracted Kodex PDF texts. Sends both to the AI with the
    kodex_assessment prompt to produce a comprehensive LE risk assessment.

    Returns the AI assessment text, or None if Kodex has no extracted data.
    """
    from server.services.ingestion.ai_processor import process_with_ai

    kodex = sections.get('kodex', {})
    if kodex.get('status') != 'extracted':
        return None

    per_case = kodex.get('per_case', [])
    if not per_case:
        return None

    # Build the Kodex raw data block from extracted texts
    kodex_parts = []
    pdf_count = 0
    for i, pc in enumerate(per_case, 1):
        text = pc.get('extracted_text')
        if not text:
            continue
        pdf_count += 1
        filename = pc.get('filename', f'document_{i}.pdf')
        page_count = pc.get('page_count', 0)
        uid_count = pc.get('uid_count', 0)
        other_uids = pc.get('approx_other_uids', 0)
        kodex_parts.append(
            f'--- PDF {pdf_count}: {filename} ({page_count} pages, '
            f'subject UID appears {uid_count}x, ~{other_uids} other UIDs) ---\n'
            f'{text}'
        )

    if not kodex_parts:
        return None

    kodex_raw = '\n\n'.join(kodex_parts)

    # Build the user message: case data + Kodex raw data
    user_message = (
        f'[CASE DATA]\n\n{case_data_markdown}\n\n'
        f'---\n\n'
        f'[KODEX RAW DATA]\n\n{kodex_raw}'
    )

    variables = {
        'subject_uid': subject_uid,
        'pdf_count': str(pdf_count),
    }

    logger.info(
        'Running Kodex assessment for UID %s: %d PDFs, '
        '%d chars case data, %d chars Kodex data',
        subject_uid, pdf_count, len(case_data_markdown), len(kodex_raw),
    )

    result = await process_with_ai(
        'kodex_assessment',
        user_message,
        variables=variables,
    )

    if result.get('error'):
        logger.error('Kodex assessment failed: %s', result['error'])
        return None

    logger.info(
        'Kodex assessment complete: %d input, %d output tokens',
        result.get('usage', {}).get('input', 0),
        result.get('usage', {}).get('output', 0),
    )

    return result.get('ai_output')


async def preview_assembled_case_data(case_id: str) -> dict:
    """
    Build the assembled case data markdown without creating the case
    or marking ingestion as completed. Read-only preview.

    Returns {case_id, assembled_case_data, sections_included, sections_none,
             preprocessed_data, subjects (multi-user only)}.
    """
    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        raise ValueError(f'Case not found: {case_id}')

    is_multi = doc.get('case_mode') == 'multi'

    if is_multi:
        # ── Multi-user assembly ──
        subjects = doc.get('subjects', [])

        # Validate all subjects are complete
        incomplete_subjects = [
            i for i, s in enumerate(subjects) if s.get('status') != 'complete'
        ]
        if incomplete_subjects:
            raise ValueError(
                'Not all subjects are complete. Incomplete: {}'.format(
                    ', '.join(f'Subject {i+1}' for i in incomplete_subjects)
                )
            )

        all_sections_included = []
        all_sections_none = []
        subject_results = []

        parts = ['# Multi-User Case Data: {}'.format(case_id)]
        parts.append('')
        parts.append('**Total Subjects:** {}'.format(len(subjects)))
        parts.append('**Subject UIDs:** {}'.format(
            ', '.join(s.get('user_id', 'Unknown') for s in subjects)
        ))
        parts.append('')
        parts.append('---')
        parts.append('')

        for i, subject in enumerate(subjects):
            subj_sections = subject.get('sections', {})
            pp_data, incl, none_list = _build_preprocessed_from_sections(subj_sections)

            all_sections_included.extend(incl)
            all_sections_none.extend(none_list)

            subject_results.append({
                'user_id': subject.get('user_id', ''),
                'label': subject.get('label', f'Subject {i+1}'),
                'preprocessed_data': pp_data,
            })

            parts.append('# SUBJECT {} — UID {}'.format(i + 1, subject.get('user_id', 'Unknown')))
            parts.append('')
            parts.extend(_build_assembled_markdown_single(doc, subj_sections, pp_data))
            parts.append('---')
            parts.append('')

        assembled = '\n'.join(parts)

        return {
            'case_id': case_id,
            'assembled_case_data': assembled,
            'sections_included': all_sections_included,
            'sections_none': all_sections_none,
            'preprocessed_data': {},  # empty for multi-user — data lives in subjects
            'subjects': subject_results,
        }

    else:
        # ── Single-user assembly (unchanged) ──
        sections = doc.get('sections', {})

        # Validate all required sections are terminal
        incomplete = []
        for key in REQUIRED_TERMINAL_KEYS:
            sec_status = sections.get(key, {}).get('status', 'empty')
            if sec_status not in TERMINAL_STATUSES:
                incomplete.append(key)

        if incomplete:
            raise ValueError(f'incomplete:{",".join(incomplete)}')

        preprocessed_data, sections_included, sections_none = (
            _build_preprocessed_from_sections(sections)
        )

        parts = ['# Case Data: {}'.format(case_id)]
        parts.append('')
        parts.append('**Subject UID:** {}'.format(doc.get('subject_uid', 'Unknown')))
        if doc.get('coconspirator_uids'):
            parts.append('**Co-conspirator UIDs:** {}'.format(
                ', '.join(doc['coconspirator_uids'])
            ))
        parts.append('')
        parts.extend(_build_assembled_markdown_single(doc, sections, preprocessed_data))

        assembled = '\n'.join(parts)

        return {
            'case_id': case_id,
            'assembled_case_data': assembled,
            'sections_included': sections_included,
            'sections_none': sections_none,
            'preprocessed_data': preprocessed_data,
        }


async def _run_kodex_assessment_for_case(case_id: str) -> None:
    """
    If Kodex section has status 'extracted', run the context-aware AI
    assessment using full case data, then update the section to 'complete'.

    This must run BEFORE the normal assembly flow so that the Kodex
    assessment is included in the assembled case data.

    For multi-user cases, runs per-subject.
    """
    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        return

    is_multi = doc.get('case_mode') == 'multi'

    if is_multi:
        subjects = doc.get('subjects', [])
        for i, subject in enumerate(subjects):
            subj_sections = subject.get('sections', {})
            kodex = subj_sections.get('kodex', {})
            if kodex.get('status') != 'extracted':
                continue

            subject_uid = subject.get('user_id', '')
            if not subject_uid:
                continue

            # Build case data markdown from all non-Kodex sections for this subject
            pp_data, _, _ = _build_preprocessed_from_sections(subj_sections)
            parts = _build_assembled_markdown_single(doc, subj_sections, pp_data)
            case_data_md = '\n'.join(parts)

            assessment = await _run_kodex_assessment(
                subj_sections, case_data_md, subject_uid,
            )
            if assessment:
                await update_section(
                    case_id, 'kodex', 'complete',
                    output=assessment,
                    subject_index=i,
                )
                logger.info(
                    'Kodex assessment complete for %s subject %d (UID %s)',
                    case_id, i, subject_uid,
                )
            else:
                logger.warning(
                    'Kodex assessment returned no output for %s subject %d',
                    case_id, i,
                )
    else:
        sections = doc.get('sections', {})
        kodex = sections.get('kodex', {})
        if kodex.get('status') != 'extracted':
            return

        subject_uid = doc.get('subject_uid', '')
        if not subject_uid:
            return

        # Build case data markdown from all non-Kodex sections
        pp_data, _, _ = _build_preprocessed_from_sections(sections)
        parts = _build_assembled_markdown_single(doc, sections, pp_data)
        case_data_md = '\n'.join(parts)

        assessment = await _run_kodex_assessment(
            sections, case_data_md, subject_uid,
        )
        if assessment:
            await update_section(
                case_id, 'kodex', 'complete',
                output=assessment,
            )
            logger.info('Kodex assessment complete for %s', case_id)
        else:
            logger.warning('Kodex assessment returned no output for %s', case_id)


async def assemble_case_data(case_id: str) -> dict:
    """
    Assemble all section outputs into the final case data markdown,
    create a case document in the `cases` collection for investigation,
    and mark the ingestion case as completed.

    If Kodex section has extracted text, runs the context-aware AI
    assessment first (using full case data as context), then assembles.

    Raises ValueError if any required section is not in terminal state
    or if a case with this ID already exists in investigations.

    Returns {case_id, assembled_case_data, sections_included, sections_none}.
    """
    from server.services import case_service

    # Step 0: Run Kodex AI assessment if text was extracted
    # This updates the Kodex section from 'extracted' to 'complete' with AI output
    await _run_kodex_assessment_for_case(case_id)

    # Step 1: Build the assembled markdown (reuse preview logic)
    preview = await preview_assembled_case_data(case_id)
    assembled = preview['assembled_case_data']
    preprocessed_data = preview['preprocessed_data']
    sections_included = preview['sections_included']
    sections_none = preview['sections_none']

    # Need the doc again for metadata fields
    doc = await _collection().find_one({'_id': case_id})

    # Step 2: Create the cases collection document
    is_multi = doc.get('case_mode') == 'multi'
    now = _utcnow()
    cases_doc = {
        '_id': case_id,
        'case_name': case_id,
        'case_type': 'investigation',
        'status': 'open',
        'assigned_to': doc.get('created_by', ''),
        'subject_user_id': doc.get('subject_uid', ''),
        'summary': '',
        'conversation_id': None,
        'preprocessed_data': preprocessed_data,
        'assembled_case_data': assembled,
        'created_at': now,
        'updated_at': now,
    }

    if is_multi:
        cases_doc['case_mode'] = 'multi'
        cases_doc['total_subjects'] = doc.get('total_subjects', len(doc.get('subjects', [])))
        cases_doc['subjects'] = preview.get('subjects', [])

    await case_service.create_case(cases_doc)

    # Step 3: Mark ingestion case as completed
    await _collection().update_one(
        {'_id': case_id},
        {
            '$set': {
                'status': 'completed',
                'assembled_case_data': assembled,
                'completed_at': now,
                'updated_at': now,
            },
            '$unset': {'uol_raw_data': 1},
        },
    )

    return {
        'case_id': case_id,
        'assembled_case_data': assembled,
        'sections_included': sections_included,
        'sections_none': sections_none,
    }
