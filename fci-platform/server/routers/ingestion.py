"""
FCI Platform — Ingestion Router

Endpoints for the Data Ingestion Dashboard.
All endpoints require Bearer token authentication via get_current_user.

Endpoint overview:
  POST   /cases                              Create new ingestion case
  GET    /cases/active                       Get investigator's active case
  GET    /cases/{case_id}                    Full case document
  GET    /cases/{case_id}/status             Lightweight polling endpoint
  POST   /cases/{case_id}/c360              Upload + process C360 files
  GET    /cases/{case_id}/c360              Get C360 section output
  GET    /cases/{case_id}/c360/csv          Download Elliptic batch CSV
  POST   /cases/{case_id}/elliptic/addresses  Add manual wallet addresses
  POST   /cases/{case_id}/elliptic/submit   Submit addresses to Elliptic API
  GET    /cases/{case_id}/elliptic          Get Elliptic section output
  POST   /cases/{case_id}/sections/{key}/none  Mark section as N/A
  PUT    /cases/{case_id}/notes             Save investigator notes
  POST   /cases/{case_id}/assemble          Assemble final case markdown
"""

import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse

from server.routers.auth import get_current_user
from server.services.ingestion import ingestion_service
from server.services.ingestion import c360_processor
from server.services.ingestion import elliptic_processor
from server.models.ingestion_schemas import (
    CreateIngestionCaseRequest,
    ManualAddressesRequest,
    EllipticSubmitRequest,
    NotesRequest,
    NONEABLE_SECTION_KEYS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


# ── Helpers ───────────────────────────────────────────────────────


async def _get_case_or_404(case_id: str) -> dict:
    """Fetch case document or raise 404."""
    case = await ingestion_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f'Case not found: {case_id}')
    return case


def _serialize_case(doc: dict) -> dict:
    """Convert MongoDB document to JSON-safe response."""
    doc['case_id'] = doc.pop('_id')
    return doc


# ── Case Management ───────────────────────────────────────────────


@router.post('/cases', status_code=201)
async def create_case(
    body: CreateIngestionCaseRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new ingestion case."""
    try:
        doc = await ingestion_service.create_ingestion_case(
            case_id=body.case_id,
            subject_uid=body.subject_uid,
            coconspirator_uids=body.coconspirator_uids,
            created_by=current_user['user_id'],
        )
        return _serialize_case(doc)
    except ValueError as e:
        msg = str(e)
        if msg.startswith('active_case_exists:'):
            existing_id = msg.split(':', 1)[1]
            raise HTTPException(
                status_code=409,
                detail={'message': 'Active case exists', 'existing_case_id': existing_id},
            )
        elif msg.startswith('case_id_exists:'):
            raise HTTPException(
                status_code=409,
                detail=f'Case {body.case_id} already exists',
            )
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/cases/active')
async def get_active_case(current_user: dict = Depends(get_current_user)):
    """Return the investigator's active case, or {case_id: null}."""
    doc = await ingestion_service.get_active_case(current_user['user_id'])
    if doc:
        return _serialize_case(doc)
    return {'case_id': None}


@router.get('/cases/{case_id}')
async def get_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Return the full case document."""
    doc = await _get_case_or_404(case_id)
    return _serialize_case(doc)


@router.get('/cases/{case_id}/status')
async def get_case_status(case_id: str, current_user: dict = Depends(get_current_user)):
    """Lightweight status snapshot for polling (every 2-3 seconds)."""
    status = await ingestion_service.get_case_status(case_id)
    if not status:
        raise HTTPException(status_code=404, detail=f'Case not found: {case_id}')
    return status


# ── C360 Processing ───────────────────────────────────────────────


@router.post('/cases/{case_id}/c360', status_code=202)
async def upload_c360(
    case_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload C360 spreadsheet files and trigger background processing."""
    case = await _get_case_or_404(case_id)

    # Guard: don't reprocess if already complete or processing
    c360_status = case.get('sections', {}).get('c360', {}).get('status', 'empty')
    if c360_status == 'processing':
        raise HTTPException(status_code=409, detail='C360 section is currently processing.')
    if c360_status == 'complete':
        raise HTTPException(
            status_code=409,
            detail='C360 section is already complete. Reprocessing not supported in Phase 1.',
        )

    # Validate file types
    for f in files:
        if not f.filename:
            continue
        lower = f.filename.lower()
        if not lower.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail=f'Only .xlsx and .csv files are accepted. Got: {f.filename}',
            )

    # CRITICAL: Read file bytes HERE — UploadFile objects are closed
    # by the time the background task executes.
    files_bytes = []
    for f in files:
        content = await f.read()
        files_bytes.append((f.filename, content))

    params = {'subject_uid': case.get('subject_uid', '')}

    # Record upload count immediately
    await ingestion_service.update_section(
        case_id, 'c360', 'processing',
        extra_fields={'files_uploaded': len(files_bytes)},
    )

    background_tasks.add_task(_process_c360_background, case_id, files_bytes, params)

    return {
        'accepted': True,
        'files_received': len(files_bytes),
        'section_status': 'processing',
        'message': 'Processing started. Poll /status for updates.',
    }


async def _process_c360_background(case_id: str, files_bytes: list, params: dict):
    """Background task: run C360 pipeline, update MongoDB on completion."""
    try:
        result = await c360_processor.process_c360_files(files_bytes, params)

        # Update the case's subject_uid if the pipeline detected one
        # and the case didn't already have one
        if result.get('subject_uid'):
            case = await ingestion_service.get_case(case_id)
            if case and not case.get('subject_uid'):
                from server.database import get_database
                await get_database()['ingestion_cases'].update_one(
                    {'_id': case_id},
                    {'$set': {'subject_uid': result['subject_uid']}},
                )

        await ingestion_service.update_section(
            case_id, 'c360', 'complete',
            output=result['output'],
            extra_fields={
                'wallet_addresses': result['wallet_addresses'],
                'detected_file_types': result['detected_file_types'],
                'undetected_files': result['undetected_files'],
                'warnings': result['warnings'],
                'auto_populate': result['auto_populate'],
                'uol_info': result['uol_info'],
                'csv_content': result['csv_content'],
                'csv_filename': result['csv_filename'],
            },
        )
        logger.info('C360 processing complete for case %s', case_id)

    except Exception as e:
        logger.exception('C360 processing failed for case %s', case_id)
        await ingestion_service.update_section(
            case_id, 'c360', 'error',
            error=str(e),
        )


@router.get('/cases/{case_id}/c360')
async def get_c360_output(case_id: str, current_user: dict = Depends(get_current_user)):
    """Return the C360 section data after processing."""
    case = await _get_case_or_404(case_id)
    c360 = case.get('sections', {}).get('c360', {})
    return {
        'status': c360.get('status', 'empty'),
        'output': c360.get('output'),
        'detected_file_types': c360.get('detected_file_types', []),
        'undetected_files': c360.get('undetected_files', []),
        'warnings': c360.get('warnings', []),
        'wallet_addresses': c360.get('wallet_addresses', []),
        'updated_at': c360.get('updated_at'),
    }


@router.get('/cases/{case_id}/c360/csv')
async def download_c360_csv(case_id: str, current_user: dict = Depends(get_current_user)):
    """
    Download the Elliptic batch screening CSV.

    Rebuilds the CSV at download time to include any manual wallet
    addresses added after C360 processing.
    """
    case = await _get_case_or_404(case_id)
    c360 = case.get('sections', {}).get('c360', {})
    elliptic_sec = case.get('sections', {}).get('elliptic', {})

    # Collect all addresses: C360-extracted + manual
    c360_addrs = c360.get('wallet_addresses', [])
    manual_addrs = elliptic_sec.get('manual_addresses', [])
    customer_id = case.get('subject_uid', '')

    # Deduplicate while preserving order
    seen = set()
    all_addresses = []
    for entry in c360_addrs:
        addr = entry['address'] if isinstance(entry, dict) else entry
        if addr not in seen:
            seen.add(addr)
            all_addresses.append(addr)
    for addr in manual_addrs:
        if addr not in seen:
            seen.add(addr)
            all_addresses.append(addr)

    if not all_addresses:
        raise HTTPException(
            status_code=404,
            detail='No wallet addresses available for CSV export.',
        )

    # Build CSV
    csv_lines = ['address,customerid,asset,blockchain']
    for addr in all_addresses:
        csv_lines.append(f'{addr},{customer_id},holistic,holistic')
    csv_content = '\n'.join(csv_lines)

    csv_filename = c360.get('csv_filename', f'elliptic_screening_{customer_id}.csv')

    return PlainTextResponse(
        content=csv_content,
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{csv_filename}"'},
    )


# ── Elliptic Screening ───────────────────────────────────────────


@router.post('/cases/{case_id}/elliptic/addresses')
async def add_manual_addresses(
    case_id: str,
    body: ManualAddressesRequest,
    current_user: dict = Depends(get_current_user),
):
    """Add or replace manual wallet addresses for Elliptic screening."""
    await _get_case_or_404(case_id)

    from server.database import get_database
    await get_database()['ingestion_cases'].update_one(
        {'_id': case_id},
        {'$set': {'sections.elliptic.manual_addresses': body.manual_addresses}},
    )

    # Get total count (C360-extracted + manual)
    case = await ingestion_service.get_case(case_id)
    c360_addrs = case.get('sections', {}).get('c360', {}).get('wallet_addresses', [])
    total = len(c360_addrs) + len(body.manual_addresses)

    return {
        'manual_addresses': body.manual_addresses,
        'total_addresses': total,
    }


@router.post('/cases/{case_id}/elliptic/submit', status_code=202)
async def submit_elliptic(
    case_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Submit all wallet addresses to Elliptic for screening.

    Combines C360-extracted addresses with any manual additions.
    No request body needed — addresses come from the case document.
    """
    case = await _get_case_or_404(case_id)

    # Guard: C360 must be complete first
    c360_status = case.get('sections', {}).get('c360', {}).get('status', 'empty')
    if c360_status != 'complete':
        raise HTTPException(
            status_code=400,
            detail='C360 processing must complete before Elliptic screening.',
        )

    # Guard: don't resubmit if already processing
    ell_status = case.get('sections', {}).get('elliptic', {}).get('status', 'empty')
    if ell_status == 'processing':
        raise HTTPException(status_code=409, detail='Elliptic screening is already processing.')

    # Combine C360-extracted + manual addresses
    c360_addrs = case.get('sections', {}).get('c360', {}).get('wallet_addresses', [])
    manual_addrs = case.get('sections', {}).get('elliptic', {}).get('manual_addresses', [])

    all_addresses = [a['address'] for a in c360_addrs if isinstance(a, dict)]
    all_addresses.extend(manual_addrs)
    # Deduplicate while preserving order
    seen = set()
    unique_addresses = []
    for addr in all_addresses:
        if addr not in seen:
            seen.add(addr)
            unique_addresses.append(addr)

    customer_id = case.get('subject_uid', '')

    await ingestion_service.update_section(
        case_id, 'elliptic', 'processing',
        extra_fields={'wallet_addresses': unique_addresses},
    )

    background_tasks.add_task(
        _process_elliptic_background, case_id, unique_addresses, customer_id,
    )

    return {
        'accepted': True,
        'addresses_submitted': len(unique_addresses),
        'section_status': 'processing',
    }


async def _process_elliptic_background(
    case_id: str, addresses: list[str], customer_id: str,
):
    """Background task: run Elliptic screening, update MongoDB."""
    try:
        result = await elliptic_processor.screen_addresses(addresses, customer_id)

        if result.get('status') == 'not_configured':
            await ingestion_service.update_section(
                case_id, 'elliptic', 'error',
                error=result.get('message', 'Elliptic API not configured'),
            )
            return

        await ingestion_service.update_section(
            case_id, 'elliptic', 'complete',
            output=result.get('output', ''),
            extra_fields={
                'summary': result.get('summary', {}),
                'demo_mode': result.get('demo_mode', False),
            },
        )
        logger.info('Elliptic screening complete for case %s', case_id)

    except Exception as e:
        logger.exception('Elliptic screening failed for case %s', case_id)
        await ingestion_service.update_section(
            case_id, 'elliptic', 'error',
            error=str(e),
        )


@router.get('/cases/{case_id}/elliptic')
async def get_elliptic_output(case_id: str, current_user: dict = Depends(get_current_user)):
    """Return the Elliptic section data after screening."""
    case = await _get_case_or_404(case_id)
    ell = case.get('sections', {}).get('elliptic', {})
    return {
        'status': ell.get('status', 'empty'),
        'output': ell.get('output'),
        'wallet_addresses': ell.get('wallet_addresses', []),
        'manual_addresses': ell.get('manual_addresses', []),
        'updated_at': ell.get('updated_at'),
    }


# ── Co-conspirator UIDs ───────────────────────────────────────────


@router.put('/cases/{case_id}/uids')
async def update_coconspirator_uids(
    case_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """Update the co-conspirator / additional UIDs list."""
    await _get_case_or_404(case_id)
    uids = body.get('coconspirator_uids', [])
    from server.database import get_database
    await get_database()['ingestion_cases'].update_one(
        {'_id': case_id},
        {'$set': {'coconspirator_uids': uids}},
    )
    return {'coconspirator_uids': uids}


# ── Section Management ────────────────────────────────────────────


@router.post('/cases/{case_id}/sections/{section_key}/none')
async def mark_section_none(
    case_id: str,
    section_key: str,
    current_user: dict = Depends(get_current_user),
):
    """Mark a section as not applicable."""
    await _get_case_or_404(case_id)

    if section_key not in NONEABLE_SECTION_KEYS:
        raise HTTPException(
            status_code=400,
            detail=f'Section "{section_key}" cannot be marked as not applicable. '
                   f'Valid sections: {", ".join(NONEABLE_SECTION_KEYS)}',
        )

    try:
        await ingestion_service.mark_section_none(case_id, section_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {'section': section_key, 'status': 'none'}


# ── Investigator Notes ────────────────────────────────────────────


@router.put('/cases/{case_id}/notes')
async def save_notes(
    case_id: str,
    body: NotesRequest,
    current_user: dict = Depends(get_current_user),
):
    """Save investigator notes. Empty string resets to 'empty'."""
    await _get_case_or_404(case_id)
    result = await ingestion_service.save_notes(case_id, body.notes)
    return result


# ── Assembly ──────────────────────────────────────────────────────


@router.post('/cases/{case_id}/assemble')
async def assemble_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Assemble all section outputs into the final case data markdown."""
    await _get_case_or_404(case_id)

    try:
        result = await ingestion_service.assemble_case_data(case_id)
        return result
    except ValueError as e:
        msg = str(e)
        if msg.startswith('incomplete:'):
            incomplete = msg.split(':', 1)[1].split(',')
            raise HTTPException(
                status_code=409,
                detail={
                    'message': 'Cannot assemble: sections not complete',
                    'incomplete_sections': incomplete,
                },
            )
        raise HTTPException(status_code=400, detail=str(e))
