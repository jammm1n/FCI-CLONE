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
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from server.config import settings
from server.database import get_database
from server.models.ingestion_schemas import (
    ALL_SECTION_KEYS,
    NONEABLE_SECTION_KEYS,
    REQUIRED_TERMINAL_KEYS,
    TERMINAL_STATUSES,
)

logger = logging.getLogger(__name__)


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
) -> dict:
    """
    Create a new ingestion case document.

    Raises ValueError if:
      - The investigator already has an active case (ingesting/ready)
      - The case_id already exists
    """
    col = _collection()

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
        'created_by': created_by,
        'subject_uid': subject_uid,
        'coconspirator_uids': coconspirator_uids or [],
        'sections': _empty_sections(),
        'assembled_case_data': None,
        'created_at': now,
        'updated_at': now,
        'completed_at': None,
    }
    await col.insert_one(doc)
    logger.info('Created ingestion case %s for user %s', case_id, created_by)
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
    """
    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        return None

    section_statuses = {}
    for key in ALL_SECTION_KEYS:
        section = doc.get('sections', {}).get(key, {})
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

    return {
        'case_id': doc['_id'],
        'case_status': doc.get('status', 'ingesting'),
        'sections': section_statuses,
    }


# ── Section Updates ───────────────────────────────────────────────


async def update_section(
    case_id: str,
    section_key: str,
    status: str,
    output: str | None = None,
    error: str | None = None,
    extra_fields: dict | None = None,
):
    """
    Atomic section update via MongoDB $set.

    After each update, checks if all required sections have reached
    terminal state and auto-transitions the case to 'ready' if so.
    """
    now = _utcnow()
    update_fields = {
        f'sections.{section_key}.status': status,
        f'sections.{section_key}.updated_at': now,
        'updated_at': now,
    }

    if output is not None:
        update_fields[f'sections.{section_key}.output'] = output
    if error is not None:
        update_fields[f'sections.{section_key}.error_message'] = error

    # Extra fields (e.g. wallet_addresses, detected_file_types, warnings)
    if extra_fields:
        for k, v in extra_fields.items():
            update_fields[f'sections.{section_key}.{k}'] = v

    await _collection().update_one(
        {'_id': case_id},
        {'$set': update_fields},
    )
    logger.info('Updated section %s.%s -> %s', case_id, section_key, status)

    # Check if case should transition to 'ready'
    await _check_ready_state(case_id)


async def mark_section_none(case_id: str, section_key: str):
    """
    Mark a section as not applicable.

    Only allowed for sections in NONEABLE_SECTION_KEYS.
    Raises ValueError for invalid section keys.
    """
    if section_key not in NONEABLE_SECTION_KEYS:
        raise ValueError(
            f'Section "{section_key}" cannot be marked as not applicable'
        )

    await update_section(case_id, section_key, 'none')


async def save_notes(case_id: str, notes_text: str) -> dict:
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

    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            'sections.investigator_notes.status': status,
            'sections.investigator_notes.output': output,
            'sections.investigator_notes.updated_at': now,
            'updated_at': now,
        }},
    )

    return {'status': status, 'updated_at': now}


async def save_text_section(case_id: str, section_key: str, text: str) -> dict:
    """
    Save a plain-text section (no AI processing).

    Empty string resets the section to 'empty'.
    Returns {status, updated_at}.
    """
    now = _utcnow()

    if text.strip():
        status = 'complete'
        output = text.strip()
    else:
        status = 'empty'
        output = None

    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            f'sections.{section_key}.status': status,
            f'sections.{section_key}.output': output,
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id)
    return {'status': status, 'updated_at': now}


async def save_text_section_with_ai(
    case_id: str, section_key: str, text: str,
) -> dict:
    """
    Save a text section, then run AI processing in the foreground.

    Stores both raw_text (original input) and output (AI narrative).
    If AI fails, falls back to storing the raw text as output.
    Returns {status, updated_at, ai_status, ai_error}.
    """
    from server.services.ingestion.ai_processor import process_with_ai

    now = _utcnow()

    if not text.strip():
        # Clear the section
        await _collection().update_one(
            {'_id': case_id},
            {'$set': {
                f'sections.{section_key}.status': 'empty',
                f'sections.{section_key}.output': None,
                f'sections.{section_key}.raw_text': None,
                f'sections.{section_key}.ai_status': None,
                f'sections.{section_key}.updated_at': now,
                'updated_at': now,
            }},
        )
        await _check_ready_state(case_id)
        return {'status': 'empty', 'updated_at': now, 'ai_status': None, 'ai_error': None}

    raw_text = text.strip()

    # Save raw text immediately, mark as processing
    await _collection().update_one(
        {'_id': case_id},
        {'$set': {
            f'sections.{section_key}.status': 'processing',
            f'sections.{section_key}.raw_text': raw_text,
            f'sections.{section_key}.ai_status': 'processing',
            f'sections.{section_key}.updated_at': now,
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
            f'sections.{section_key}.status': 'complete',
            f'sections.{section_key}.output': output,
            f'sections.{section_key}.raw_text': raw_text,
            f'sections.{section_key}.ai_status': ai_status,
            f'sections.{section_key}.ai_error': ai_error,
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id)
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
            img_b64 = base64.b64encode(img_bytes).decode('ascii')
            result.append({
                'base64': img_b64,
                'media_type': img_ref['media_type'],
            })
        except Exception as e:
            logger.warning('Failed to load image %s: %s', stored_path, e)
    return result


# ── Image-Only Sections (KYC) ──────────────────────────────────────


async def save_images_with_ai(
    case_id: str, section_key: str, image_refs: list[dict], batch_id: str,
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

    # Store image refs, mark as processing
    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'sections.{section_key}.status': 'processing',
            f'sections.{section_key}.images': image_refs,
            f'sections.{section_key}.batch_id': batch_id,
            f'sections.{section_key}.ai_status': 'processing',
            f'sections.{section_key}.updated_at': now,
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
            f'sections.{section_key}.status': status,
            f'sections.{section_key}.output': output,
            f'sections.{section_key}.ai_status': ai_status,
            f'sections.{section_key}.ai_error': ai_error,
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id)
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
    raw_text = text.strip() if text else ''

    if not raw_text and not image_refs:
        # Clear the section
        await col.update_one(
            {'_id': case_id},
            {'$set': {
                f'sections.{section_key}.status': 'empty',
                f'sections.{section_key}.output': None,
                f'sections.{section_key}.raw_text': None,
                f'sections.{section_key}.images': [],
                f'sections.{section_key}.batch_id': None,
                f'sections.{section_key}.ai_status': None,
                f'sections.{section_key}.ai_error': None,
                f'sections.{section_key}.updated_at': now,
                'updated_at': now,
            }},
        )
        await _check_ready_state(case_id)
        return {
            'status': 'empty', 'updated_at': now,
            'ai_status': None, 'ai_error': None,
        }

    # Save raw text + images, mark as processing
    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'sections.{section_key}.status': 'processing',
            f'sections.{section_key}.raw_text': raw_text,
            f'sections.{section_key}.images': image_refs,
            f'sections.{section_key}.batch_id': batch_id,
            f'sections.{section_key}.ai_status': 'processing',
            f'sections.{section_key}.updated_at': now,
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
            f'sections.{section_key}.status': 'complete',
            f'sections.{section_key}.output': output,
            f'sections.{section_key}.raw_text': raw_text,
            f'sections.{section_key}.ai_status': ai_status,
            f'sections.{section_key}.ai_error': ai_error,
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
    }


# ── Iterative Entry Sections (Prior ICR, RFI) ─────────────────────


async def set_total_count(case_id: str, section_key: str, count: int | None) -> None:
    """Set the total count for an iterative section (e.g. total prior ICRs)."""
    set_fields = {f"sections.{section_key}.total_count": count, "updated_at": _utcnow()}
    await _collection().update_one({"_id": case_id}, {"$set": set_fields})


async def add_entry(
    case_id: str,
    section_key: str,
    text: str,
    images: list[dict] | None = None,
    entry_id: str | None = None,
) -> dict:
    """
    Add a text entry (with optional image references) to an iterative section.

    Args:
        case_id: The ingestion case ID.
        section_key: The section key (e.g., 'previous_icrs', 'rfis').
        text: The entry text.
        images: Optional list of image reference dicts (from _store_ingestion_images).
        entry_id: Optional pre-generated entry ID (used when images are stored first).

    Returns the new entry dict with its generated id.
    """
    now = _utcnow()
    col = _collection()

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
            '$push': {f'sections.{section_key}.entries': entry},
            '$set': {
                f'sections.{section_key}.status': 'incomplete',
                f'sections.{section_key}.updated_at': now,
                'updated_at': now,
            },
        },
    )

    logger.info('Added entry %s to %s.%s', entry_id, case_id, section_key)
    return entry


async def remove_entry(case_id: str, section_key: str, entry_id: str):
    """Remove an entry from an iterative section by its id."""
    now = _utcnow()
    col = _collection()

    await col.update_one(
        {'_id': case_id},
        {
            '$pull': {f'sections.{section_key}.entries': {'id': entry_id}},
            '$set': {
                f'sections.{section_key}.updated_at': now,
                'updated_at': now,
            },
        },
    )

    # If no entries left, reset section to empty
    doc = await col.find_one({'_id': case_id}, {f'sections.{section_key}.entries': 1})
    entries = doc.get('sections', {}).get(section_key, {}).get('entries', [])
    if not entries:
        await col.update_one(
            {'_id': case_id},
            {'$set': {
                f'sections.{section_key}.status': 'empty',
                f'sections.{section_key}.output': None,
                f'sections.{section_key}.raw_text': None,
                f'sections.{section_key}.ai_status': None,
            }},
        )

    logger.info('Removed entry %s from %s.%s', entry_id, case_id, section_key)


async def process_entries_with_ai(case_id: str, section_key: str) -> dict:
    """
    Combine all entries in an iterative section and run AI processing.

    For most sections: concatenates entry texts, sends to AI, stores result.
    For RFI ('rfis'): two-stage pipeline:
      1. Each entry processed individually with prompt-22 (text + images)
      2. All per-entry narratives combined and sent to prompt-10 for summary
    """
    from server.services.ingestion.ai_processor import process_with_ai

    col = _collection()
    doc = await col.find_one({'_id': case_id}, {f'sections.{section_key}': 1})
    entries = doc.get('sections', {}).get(section_key, {}).get('entries', [])

    if not entries:
        return {'status': 'empty', 'ai_status': None, 'ai_error': 'No entries to process'}

    now = _utcnow()
    await col.update_one(
        {'_id': case_id},
        {'$set': {
            f'sections.{section_key}.status': 'processing',
            f'sections.{section_key}.ai_status': 'processing',
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    if section_key == 'rfis':
        return await _process_rfi_entries(case_id, section_key, entries)

    # Default path: combine entries into numbered text, single AI call
    parts = []
    for i, entry in enumerate(entries, 1):
        parts.append(f'--- Entry {i} ---\n{entry["text"]}')
    combined_text = '\n\n'.join(parts)

    await col.update_one(
        {'_id': case_id},
        {'$set': {f'sections.{section_key}.raw_text': combined_text}},
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
            f'sections.{section_key}.status': 'complete',
            f'sections.{section_key}.output': output,
            f'sections.{section_key}.raw_text': combined_text,
            f'sections.{section_key}.ai_status': ai_status,
            f'sections.{section_key}.ai_error': ai_error,
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
        'entry_count': len(entries),
    }


async def _process_rfi_entries(
    case_id: str, section_key: str, entries: list[dict],
) -> dict:
    """
    Two-stage RFI processing:
      Stage 1: Each entry → prompt-22 (rfi_doc_review) with text + images
      Stage 2: All per-entry outputs combined → prompt-10 (rfis) for summary
    """
    from server.services.ingestion.ai_processor import process_with_ai

    col = _collection()

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

        # Store per-entry AI output back on the entry
        await col.update_one(
            {'_id': case_id, f'sections.{section_key}.entries.id': entry['id']},
            {'$set': {
                f'sections.{section_key}.entries.$.ai_output': narrative,
            }},
        )

    # Stage 2: Combine all per-entry narratives, send to prompt-10
    combined_parts = []
    for i, narrative in enumerate(entry_narratives, 1):
        combined_parts.append(f'--- RFI {i} ---\n{narrative}')
    combined_text = '\n\n'.join(combined_parts)

    await col.update_one(
        {'_id': case_id},
        {'$set': {f'sections.{section_key}.raw_text': combined_text}},
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
            f'sections.{section_key}.status': 'complete',
            f'sections.{section_key}.output': output,
            f'sections.{section_key}.raw_text': combined_text,
            f'sections.{section_key}.ai_status': ai_status,
            f'sections.{section_key}.ai_error': ai_error,
            f'sections.{section_key}.updated_at': now,
            'updated_at': now,
        }},
    )

    await _check_ready_state(case_id)
    return {
        'status': 'complete',
        'updated_at': now,
        'ai_status': ai_status,
        'ai_error': ai_error,
        'entry_count': len(entries),
    }


# ── Ready-State Detection ─────────────────────────────────────────


async def _check_ready_state(case_id: str):
    """
    Check if all required sections are in terminal state.

    If so, and the case is currently 'ingesting', transition to 'ready'.
    investigator_notes is excluded — it never blocks readiness.
    """
    doc = await _collection().find_one(
        {'_id': case_id},
        {'status': 1, 'sections': 1},
    )
    if not doc or doc.get('status') != 'ingesting':
        return

    sections = doc.get('sections', {})
    all_terminal = all(
        sections.get(key, {}).get('status') in TERMINAL_STATUSES
        for key in REQUIRED_TERMINAL_KEYS
    )

    if all_terminal:
        await _collection().update_one(
            {'_id': case_id},
            {'$set': {'status': 'ready', 'updated_at': _utcnow()}},
        )
        logger.info('Case %s auto-transitioned to ready', case_id)


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
    await _collection().update_one(
        {'_id': case_id},
        {
            '$set': {
                'status': 'ingesting',
                'subject_uid': '',
                'coconspirator_uids': [],
                'sections': _empty_sections(),
                'assembled_case_data': None,
                'updated_at': now,
                'completed_at': None,
            },
            '$unset': {'uol_raw_data': 1},
        },
    )
    logger.info('Reset ingestion case %s', case_id)

    updated = await _collection().find_one({'_id': case_id})
    return updated


# ── Assembly ──────────────────────────────────────────────────────


async def assemble_case_data(case_id: str) -> dict:
    """
    Assemble all section outputs into the final case data markdown,
    create a case document in the `cases` collection for investigation,
    and mark the ingestion case as completed.

    C360 is expanded into individual sub-processor sections in both
    the assembled markdown and the preprocessed_data dict.

    Raises ValueError if any required section is not in terminal state
    or if a case with this ID already exists in investigations.

    Returns {case_id, assembled_case_data, sections_included, sections_none}.
    """
    from server.services import case_service

    doc = await _collection().find_one({'_id': case_id})
    if not doc:
        raise ValueError(f'Case not found: {case_id}')

    sections = doc.get('sections', {})

    # Validate all required sections are terminal
    incomplete = []
    for key in REQUIRED_TERMINAL_KEYS:
        sec_status = sections.get(key, {}).get('status', 'empty')
        if sec_status not in TERMINAL_STATUSES:
            incomplete.append(key)

    if incomplete:
        raise ValueError(f'incomplete:{",".join(incomplete)}')

    # ── Build preprocessed_data and assembled markdown ──────────

    preprocessed_data = {}
    parts = []
    sections_included = []
    sections_none = []

    parts.append('# Case Data: {}'.format(case_id))
    parts.append('')
    parts.append('**Subject UID:** {}'.format(doc.get('subject_uid', 'Unknown')))
    if doc.get('coconspirator_uids'):
        parts.append('**Co-conspirator UIDs:** {}'.format(
            ', '.join(doc['coconspirator_uids'])
        ))
    parts.append('')

    # ── C360 expanded sub-sections ──
    c360 = sections.get('c360', {})
    c360_status = c360.get('status', 'empty')

    if c360_status == 'complete':
        ai_outputs = c360.get('ai_outputs', {})
        processor_outputs = c360.get('processor_outputs', {})

        # AI-processed sub-sections
        for ai_key, pp_key, heading in C360_AI_TO_PREPROCESSED:
            ai_entry = ai_outputs.get(ai_key, {})
            ai_output = ai_entry.get('ai_output')
            if ai_output:
                preprocessed_data[pp_key] = ai_output
                parts.append('## {}'.format(heading))
                parts.append('')
                parts.append(ai_output)
                parts.append('')
                sections_included.append(pp_key)

        # user_profile — raw processor output, no AI
        up = processor_outputs.get('user_profile', {})
        if up.get('content'):
            preprocessed_data['user_profile'] = up['content']
            parts.append('## User Profile')
            parts.append('')
            parts.append(up['content'])
            parts.append('')
            sections_included.append('user_profile')

        # address_xref
        if c360.get('address_xref'):
            preprocessed_data['address_xref'] = c360['address_xref']
            parts.append('## Address Cross-Reference')
            parts.append('')
            parts.append(c360['address_xref'])
            parts.append('')
            sections_included.append('address_xref')

        # uid_search
        if c360.get('uid_search'):
            preprocessed_data['uid_search'] = c360['uid_search']
            parts.append('## UID Search Results')
            parts.append('')
            parts.append(c360['uid_search'])
            parts.append('')
            sections_included.append('uid_search')
    else:
        parts.append('## C360 Transaction Summary')
        parts.append('')
        parts.append('C360 data not provided.')
        parts.append('')
        sections_none.append('c360')

    # ── Standalone sections ──
    for section_key, heading, none_statement in ASSEMBLY_ORDER:
        if section_key == 'c360':
            continue  # Already handled above
        section = sections.get(section_key, {})
        sec_status = section.get('status', 'empty')
        output = section.get('output')

        # Total count qualifier (prior ICRs / RFIs)
        section_heading = heading
        entries_count = len(section.get('entries', []))
        total_count = section.get('total_count')
        if section_key in ('previous_icrs', 'rfis') and total_count and total_count > entries_count:
            section_heading = '{} ({} of {} included)'.format(
                heading, entries_count, total_count
            )
            if section_key == 'previous_icrs':
                preprocessed_data['prior_icr_count'] = total_count
            else:
                preprocessed_data['rfi_count'] = total_count

        parts.append('## {}'.format(section_heading))
        parts.append('')

        if sec_status == 'complete' and output:
            pp_key = SECTION_TO_PREPROCESSED.get(section_key, section_key)
            preprocessed_data[pp_key] = output
            # Add contextual note about subset
            if section_key == 'previous_icrs' and preprocessed_data.get('prior_icr_count'):
                total = preprocessed_data['prior_icr_count']
                parts.append('*Note: {} prior ICRs exist for this subject. '
                             'The {} most recent are summarised below.*'.format(
                                 total, entries_count))
                parts.append('')
            elif section_key == 'rfis' and preprocessed_data.get('rfi_count'):
                total = preprocessed_data['rfi_count']
                parts.append('*Note: {} RFIs exist for this subject. '
                             'The {} most recent are summarised below.*'.format(
                                 total, entries_count))
                parts.append('')
            parts.append(output)
            sections_included.append(section_key)
        else:
            parts.append(none_statement)
            sections_none.append(section_key)

        parts.append('')

    assembled = '\n'.join(parts)

    # ── Create the cases collection document ──────────────────

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

    await case_service.create_case(cases_doc)

    # ── Mark ingestion case as completed ─────────────────────

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
