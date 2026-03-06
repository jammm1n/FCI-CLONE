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

import logging
from datetime import datetime, timezone

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
    ('previous_icrs', 'Prior ICR Summary', 'No prior ICRs identified for this subject.'),
    ('rfis', 'RFI Summary', 'No RFIs on record for this subject.'),
    ('kyc', 'KYC Document Summary', 'KYC documents not provided.'),
    ('l1_victim', 'L1 Victim Communications Summary', 'No victim communications available.'),
    ('l1_suspect', 'L1 Suspect Communications Summary', 'No suspect communications available.'),
    ('kodex', 'Law Enforcement / Kodex Summary', 'No law enforcement cases identified.'),
    ('investigator_notes', 'Investigator Notes', 'No additional notes.'),
]


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
    # Elliptic has extra fields
    sections['elliptic']['wallet_addresses'] = []
    sections['elliptic']['manual_addresses'] = []
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
        section_statuses[key] = {
            'status': section.get('status', 'empty'),
            'updated_at': section.get('updated_at'),
        }

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
    Assemble all section outputs into the final case data markdown.

    All sections appear in the output in a fixed order. Sections
    marked 'none' produce an explicit absence statement. The AI
    never has to guess whether data is missing or not loaded.

    Raises ValueError if any required section is not in terminal state.

    Returns {assembled_case_data, sections_included, sections_none}.
    """
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

    # Build the markdown
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

    for section_key, heading, none_statement in ASSEMBLY_ORDER:
        section = sections.get(section_key, {})
        sec_status = section.get('status', 'empty')
        output = section.get('output')

        parts.append('## {}'.format(heading))
        parts.append('')

        if sec_status == 'complete' and output:
            # For C360, append cross-reference narratives
            if section_key == 'c360':
                if section.get('address_xref'):
                    output += '\n\n' + section['address_xref']
                if section.get('uid_search'):
                    output += '\n\n' + section['uid_search']
            parts.append(output)
            sections_included.append(section_key)
        else:
            parts.append(none_statement)
            sections_none.append(section_key)

        parts.append('')

    assembled = '\n'.join(parts)

    # Store the assembled output and purge UOL raw data
    now = _utcnow()
    await _collection().update_one(
        {'_id': case_id},
        {
            '$set': {
                'assembled_case_data': assembled,
                'updated_at': now,
            },
            '$unset': {'uol_raw_data': 1},
        },
    )

    return {
        'assembled_case_data': assembled,
        'sections_included': sections_included,
        'sections_none': sections_none,
    }
