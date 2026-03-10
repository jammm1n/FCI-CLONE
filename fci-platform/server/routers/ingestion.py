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
  PUT    /cases/{case_id}/text-section/{key}  Save text section with AI processing
  GET    /cases/{case_id}/text-section/{key}  Get text section output + AI status
  POST   /cases/{case_id}/submit-subject     Submit current subject (multi-user)
  PATCH  /cases/{case_id}/subjects/{i}/uid  Set subject UID (multi-user)
  POST   /cases/{case_id}/reset             Reset case to initial state
  POST   /cases/{case_id}/assemble          Assemble final case markdown
"""

import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse

from server.routers.auth import get_current_user
from server.services.ingestion import ingestion_service
from server.services.ingestion import c360_processor
from server.services.ingestion import elliptic_processor
from server.services.ingestion.ai_processor import (
    process_with_ai, PROCESSOR_PROMPT_MAP,
)
from server.services.ingestion.ingestion_service import _section_path, _get_section
from server.services.icr.address_manager import build_address_list
from server.services.icr.uid_search import search_associated_uids
from server.models.ingestion_schemas import (
    CreateIngestionCaseRequest,
    ManualAddressesRequest,
    EllipticSubmitRequest,
    NotesRequest,
    TextSectionRequest,
    SetSubjectUidRequest,
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
    doc.pop('uol_raw_data', None)  # Don't send raw UOL data to frontend
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
            case_mode=body.case_mode,
            total_subjects=body.total_subjects,
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
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload C360 spreadsheet files and trigger background processing.

    Returns extracted UID and user info synchronously (fast parse),
    then runs the full processor pipeline in the background.
    """
    case = await _get_case_or_404(case_id)

    # Guard: don't reprocess if already complete or processing
    c360 = _get_section(case, 'c360', subject_index)
    c360_status = c360.get('status', 'empty')
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

    # Quick extraction: parse files, extract UID + user info (fast, ~1s)
    quick_info = await c360_processor.extract_quick_info(files_bytes)

    # Write extracted UID to the case document immediately
    file_uid = quick_info.get('file_uid', '')
    if file_uid:
        from server.database import get_database
        update_uid = {'subject_uid': file_uid}
        if subject_index is not None:
            update_uid[f'subjects.{subject_index}.user_id'] = file_uid
        await get_database()['ingestion_cases'].update_one(
            {'_id': case_id},
            {'$set': update_uid},
        )

    # Record upload + quick extraction results, set status to processing
    await ingestion_service.update_section(
        case_id, 'c360', 'processing',
        extra_fields={
            'files_uploaded': len(files_bytes),
            'detected_uid': file_uid,
            'user_info': quick_info.get('user_info'),
            'detected_file_types': quick_info.get('detected_file_types', []),
        },
        subject_index=subject_index,
    )

    # Kick off full processor pipeline in background
    # CRITICAL: subject_index captured here, passed as parameter to task
    params = {'subject_uid': file_uid or case.get('subject_uid', '')}
    background_tasks.add_task(
        _process_c360_background, case_id, files_bytes, params, subject_index,
    )

    return {
        'accepted': True,
        'files_received': len(files_bytes),
        'section_status': 'processing',
        'file_uid': file_uid,
        'user_info': quick_info.get('user_info'),
        'detected_file_types': quick_info.get('detected_file_types', []),
    }


async def _process_c360_background(
    case_id: str, files_bytes: list, params: dict,
    subject_index: int | None = None,
):
    """Background task: run C360 pipeline, AI processing, update MongoDB."""
    # subject_index is captured in the closure at task creation time
    c360_prefix = _section_path('c360', subject_index)

    try:
        result = await c360_processor.process_c360_files(files_bytes, params)

        # Update the case's subject_uid if the pipeline detected one
        # and the case didn't already have one
        if result.get('subject_uid'):
            case = await ingestion_service.get_case(case_id)
            if case and not case.get('subject_uid'):
                from server.database import get_database
                update_uid = {'subject_uid': result['subject_uid']}
                if subject_index is not None:
                    update_uid[f'subjects.{subject_index}.user_id'] = result['subject_uid']
                await get_database()['ingestion_cases'].update_one(
                    {'_id': case_id},
                    {'$set': update_uid},
                )

        # Build user_info: prefer UOL customer_info (has name, email, etc.)
        # over quick extraction (which skipped UOL)
        user_info = result.get('uol_customer_info')
        if not user_info:
            case_now = await ingestion_service.get_case(case_id)
            user_info = (
                _get_section(case_now, 'c360', subject_index).get('user_info')
                if case_now else None
            )

        processor_outputs = result.get('processor_outputs', {})

        # Store raw processor outputs and metadata (status stays 'processing')
        await ingestion_service.update_section(
            case_id, 'c360', 'processing',
            extra_fields={
                'processor_outputs': processor_outputs,
                'wallet_addresses': result['wallet_addresses'],
                'detected_file_types': result['detected_file_types'],
                'undetected_files': result['undetected_files'],
                'warnings': result['warnings'],
                'auto_populate': result['auto_populate'],
                'uol_info': result['uol_info'],
                'csv_content': result['csv_content'],
                'csv_filename': result['csv_filename'],
                'detected_uid': result.get('file_uid', ''),
                'user_info': user_info,
            },
            subject_index=subject_index,
        )

        # Store UOL raw data for cross-referencing (address manager, UID search)
        if result.get('uol_raw_data'):
            from server.database import get_database
            await get_database()['ingestion_cases'].update_one(
                {'_id': case_id},
                {'$set': {'uol_raw_data': result['uol_raw_data']}},
            )

        # Auto-run address cross-reference with extracted wallet addresses
        if result.get('wallet_addresses'):
            try:
                address_map = {
                    e['address']: e for e in result['wallet_addresses']
                }
                session_like = {
                    'elliptic_addresses': address_map,
                    'uol_data': result.get('uol_raw_data') or {},
                }
                xref = await asyncio.to_thread(
                    build_address_list, session_like, [],
                )
                from server.database import get_database
                await get_database()['ingestion_cases'].update_one(
                    {'_id': case_id},
                    {'$set': {f'{c360_prefix}.address_xref': xref['narrative']}},
                )
            except Exception:
                logger.exception('Auto address xref failed for %s', case_id)

        # ── AI Processing ─────────────────────────────────────────
        # Sequential API calls for each processor that has a prompt.
        # Variables for Prompt 17 (device/IP)
        auto_pop = result.get('auto_populate', {})
        variables = {
            'nationality': auto_pop.get('nationality', 'Unknown'),
            'residence': auto_pop.get('residence', 'Unknown'),
        }

        from server.database import get_database
        db = get_database()['ingestion_cases']

        await db.update_one(
            {'_id': case_id},
            {'$set': {
                f'{c360_prefix}.ai_status': 'processing',
                f'{c360_prefix}.ai_progress': {},
            }},
        )

        ai_outputs = {}
        ai_had_error = False

        # Processor sort order for assembly
        PROCESSOR_SORT_ORDER = [
            ('tx_summary', 'Transaction Summary'),
            ('user_profile', 'User Profile'),
            ('privacy_coin', 'Privacy Coin Breakdown'),
            ('counterparty', 'Counterparty Analysis'),
            ('device', 'Device & IP Analysis'),
            ('elliptic', 'Wallet Address Extraction'),
            ('fiat', 'Failed Fiat Withdrawals'),
            ('ctm', 'CTM Alerts'),
            ('ftm', 'FTM Alerts'),
            ('blocks', 'Account Blocks'),
        ]

        for processor_id in PROCESSOR_PROMPT_MAP:
            po = processor_outputs.get(processor_id, {})

            # Skip processors with no data or that were skipped
            if po.get('skipped') or not po.get('has_data') or not po.get('content'):
                ai_outputs[processor_id] = {
                    'ai_output': None,
                    'skipped': True,
                    'error': None,
                }
                await db.update_one(
                    {'_id': case_id},
                    {'$set': {
                        f'{c360_prefix}.ai_progress.{processor_id}': 'skipped',
                    }},
                )
                continue

            # Update progress: processing
            await db.update_one(
                {'_id': case_id},
                {'$set': {
                    f'{c360_prefix}.ai_progress.{processor_id}': 'processing',
                }},
            )

            # Pass variables only for prompt 17 (device)
            proc_vars = variables if processor_id == 'device' else None

            ai_result = await process_with_ai(
                processor_id, po['content'], proc_vars,
            )
            ai_outputs[processor_id] = ai_result

            if ai_result.get('error'):
                ai_had_error = True
                await db.update_one(
                    {'_id': case_id},
                    {'$set': {
                        f'{c360_prefix}.ai_progress.{processor_id}': 'error',
                    }},
                )
            else:
                await db.update_one(
                    {'_id': case_id},
                    {'$set': {
                        f'{c360_prefix}.ai_progress.{processor_id}': 'complete',
                    }},
                )

        # ── Assemble final output from AI narratives ──────────────
        parts = []
        for processor_id, label in PROCESSOR_SORT_ORDER:
            if processor_id == 'elliptic':
                continue  # Exclude — intermediate data for wallet pipeline

            ai_entry = ai_outputs.get(processor_id, {})
            po = processor_outputs.get(processor_id, {})

            if ai_entry.get('ai_output'):
                # AI narrative available
                parts.append('### {}\n\n{}'.format(label, ai_entry['ai_output']))
            elif processor_id == 'user_profile' and po.get('has_data') and po.get('content'):
                # user_profile: pass through raw (no AI)
                parts.append('### {}\n\n{}'.format(po.get('label', label), po['content']))
            elif po.get('has_data') and po.get('content'):
                # Fallback: raw output (AI failed or no prompt)
                parts.append('### {}\n\n{}'.format(po.get('label', label), po['content']))
            elif po.get('skipped') and po.get('content'):
                # Data not uploaded
                parts.append('### {}\n\n{}'.format(po.get('label', label), po['content']))

        assembled_output = '\n\n---\n\n'.join(parts)

        # Determine AI status
        any_complete = any(
            r.get('ai_output') for r in ai_outputs.values()
        )
        if ai_had_error and any_complete:
            ai_status = 'partial'
        elif ai_had_error:
            ai_status = 'error'
        else:
            ai_status = 'complete'

        # Final update: store AI outputs and assembled output
        await ingestion_service.update_section(
            case_id, 'c360', 'complete',
            output=assembled_output,
            extra_fields={
                'ai_outputs': ai_outputs,
                'ai_status': ai_status,
            },
            subject_index=subject_index,
        )

        logger.info('C360 processing + AI complete for case %s', case_id)

    except Exception as e:
        logger.exception('C360 processing failed for case %s', case_id)
        await ingestion_service.update_section(
            case_id, 'c360', 'error',
            error=str(e),
            subject_index=subject_index,
        )


@router.get('/cases/{case_id}/c360')
async def get_c360_output(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return the C360 section data after processing, including cross-references."""
    case = await _get_case_or_404(case_id)
    c360 = _get_section(case, 'c360', subject_index)

    # Concatenate processor output + address xref + uid search narratives
    output = c360.get('output') or ''
    if c360.get('address_xref'):
        output += '\n\n---\n\n' + c360['address_xref']
    if c360.get('uid_search'):
        output += '\n\n---\n\n' + c360['uid_search']

    return {
        'status': c360.get('status', 'empty'),
        'output': output,
        'detected_file_types': c360.get('detected_file_types', []),
        'undetected_files': c360.get('undetected_files', []),
        'warnings': c360.get('warnings', []),
        'wallet_addresses': c360.get('wallet_addresses', []),
        'updated_at': c360.get('updated_at'),
        'processor_outputs': c360.get('processor_outputs', {}),
        'ai_outputs': c360.get('ai_outputs', {}),
        'ai_status': c360.get('ai_status', 'pending'),
        'ai_progress': c360.get('ai_progress', {}),
    }


@router.get('/cases/{case_id}/c360/csv')
async def download_c360_csv(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Download the Elliptic batch screening CSV.

    Rebuilds the CSV at download time to include any manual wallet
    addresses added after C360 processing.
    """
    case = await _get_case_or_404(case_id)
    c360 = _get_section(case, 'c360', subject_index)
    elliptic_sec = _get_section(case, 'elliptic', subject_index)

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
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Add or replace manual wallet addresses for Elliptic screening."""
    await _get_case_or_404(case_id)

    ell_prefix = _section_path('elliptic', subject_index)
    from server.database import get_database
    await get_database()['ingestion_cases'].update_one(
        {'_id': case_id},
        {'$set': {f'{ell_prefix}.manual_addresses': body.manual_addresses}},
    )

    # Get total count (C360-extracted + manual)
    case = await ingestion_service.get_case(case_id)
    c360_addrs = _get_section(case, 'c360', subject_index).get('wallet_addresses', [])
    total = len(c360_addrs) + len(body.manual_addresses)

    return {
        'manual_addresses': body.manual_addresses,
        'total_addresses': total,
    }


@router.post('/cases/{case_id}/elliptic/submit', status_code=202)
async def submit_elliptic(
    case_id: str,
    background_tasks: BackgroundTasks,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Submit all wallet addresses to Elliptic for screening.

    Combines C360-extracted addresses with any manual additions.
    No request body needed — addresses come from the case document.
    """
    case = await _get_case_or_404(case_id)

    # Guard: C360 must be complete first
    c360_status = _get_section(case, 'c360', subject_index).get('status', 'empty')
    if c360_status != 'complete':
        raise HTTPException(
            status_code=400,
            detail='C360 processing must complete before Elliptic screening.',
        )

    # Guard: don't resubmit if already processing
    ell_status = _get_section(case, 'elliptic', subject_index).get('status', 'empty')
    if ell_status == 'processing':
        raise HTTPException(status_code=409, detail='Elliptic screening is already processing.')

    # Combine C360-extracted + manual addresses
    c360_addrs = _get_section(case, 'c360', subject_index).get('wallet_addresses', [])
    manual_addrs = _get_section(case, 'elliptic', subject_index).get('manual_addresses', [])

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
        subject_index=subject_index,
    )

    background_tasks.add_task(
        _process_elliptic_background, case_id, unique_addresses, customer_id,
        subject_index,
    )

    return {
        'accepted': True,
        'addresses_submitted': len(unique_addresses),
        'section_status': 'processing',
    }


async def _process_elliptic_background(
    case_id: str, addresses: list[str], customer_id: str,
    subject_index: int | None = None,
):
    """Background task: run Elliptic screening, update MongoDB."""
    try:
        result = await elliptic_processor.screen_addresses(addresses, customer_id)

        if result.get('status') == 'not_configured':
            await ingestion_service.update_section(
                case_id, 'elliptic', 'error',
                error=result.get('message', 'Elliptic API not configured'),
                subject_index=subject_index,
            )
            return

        await ingestion_service.update_section(
            case_id, 'elliptic', 'complete',
            output=result.get('output', ''),
            extra_fields={
                'summary': result.get('summary', {}),
                'demo_mode': result.get('demo_mode', False),
            },
            subject_index=subject_index,
        )
        logger.info('Elliptic screening complete for case %s', case_id)

    except Exception as e:
        logger.exception('Elliptic screening failed for case %s', case_id)
        await ingestion_service.update_section(
            case_id, 'elliptic', 'error',
            error=str(e),
            subject_index=subject_index,
        )


@router.get('/cases/{case_id}/elliptic')
async def get_elliptic_output(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return the Elliptic section data after screening."""
    case = await _get_case_or_404(case_id)
    ell = _get_section(case, 'elliptic', subject_index)
    return {
        'status': ell.get('status', 'empty'),
        'output': ell.get('output'),
        'wallet_addresses': ell.get('wallet_addresses', []),
        'manual_addresses': ell.get('manual_addresses', []),
        'updated_at': ell.get('updated_at'),
    }


# ── Address Cross-Reference & UID Search ──────────────────────────


@router.post('/cases/{case_id}/address-xref')
async def run_address_xref(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Cross-reference all wallet addresses against UOL crypto transaction history.

    Combines C360-extracted + manual addresses, matches them against UOL
    crypto withdrawal and deposit tabs. Stores the narrative in the C360
    section for preview and assembly.
    """
    case = await _get_case_or_404(case_id)

    uol_raw = case.get('uol_raw_data')
    if not uol_raw:
        return {
            'narrative': 'No UOL data available for cross-referencing.',
            'stats': {'total_addresses': 0, 'uol_matched': 0, 'uol_unmatched': 0},
        }

    # Reconstruct address map from stored wallet addresses
    c360_addrs = _get_section(case, 'c360', subject_index).get('wallet_addresses', [])
    address_map = {e['address']: e for e in c360_addrs if isinstance(e, dict)}

    # Get manual addresses
    manual_addrs = _get_section(case, 'elliptic', subject_index).get('manual_addresses', [])

    session_like = {
        'elliptic_addresses': address_map,
        'uol_data': uol_raw,
    }

    result = await asyncio.to_thread(build_address_list, session_like, manual_addrs)

    # Store narrative on the c360 section
    c360_prefix = _section_path('c360', subject_index)
    from server.database import get_database
    await get_database()['ingestion_cases'].update_one(
        {'_id': case_id},
        {'$set': {f'{c360_prefix}.address_xref': result['narrative']}},
    )

    return {
        'narrative': result['narrative'],
        'stats': result['stats'],
    }


@router.post('/cases/{case_id}/uid-search')
async def run_uid_search(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Search UOL transaction history for connections to coconspirator UIDs.

    Searches Crypto Withdrawals, Crypto Deposits, Binance Pay, and P2P
    tabs for transactions involving the specified UIDs. Stores the
    narrative in the C360 section for preview and assembly.
    """
    case = await _get_case_or_404(case_id)

    uol_raw = case.get('uol_raw_data')
    if not uol_raw:
        return {
            'narrative': 'No UOL data available for UID search.',
            'stats': {'uids_searched': 0, 'uids_found': 0, 'total_matches': 0},
        }

    # For multi-user: collect UIDs from other subjects instead of coconspirator_uids
    if case.get('case_mode') == 'multi':
        uids = []
        for i, subj in enumerate(case.get('subjects', [])):
            if i != subject_index and subj.get('user_id'):
                uids.append(subj['user_id'])
    else:
        uids = case.get('coconspirator_uids', [])

    if not uids:
        return {
            'narrative': 'No UIDs to search for.',
            'stats': {'uids_searched': 0, 'uids_found': 0, 'total_matches': 0},
        }

    session_like = {
        'uol_data': uol_raw,
        'subject_uid': case.get('subject_uid', ''),
    }

    result = await asyncio.to_thread(search_associated_uids, session_like, uids)

    # Store narrative on the c360 section
    c360_prefix = _section_path('c360', subject_index)
    from server.database import get_database
    await get_database()['ingestion_cases'].update_one(
        {'_id': case_id},
        {'$set': {f'{c360_prefix}.uid_search': result['narrative']}},
    )

    return {
        'narrative': result['narrative'],
        'stats': result['stats'],
    }


# ── Co-conspirator UIDs ───────────────────────────────────────────


@router.put('/cases/{case_id}/uids')
async def update_coconspirator_uids(
    case_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """Update the co-conspirator / additional UIDs list and optionally subject_uid."""
    await _get_case_or_404(case_id)
    update = {}
    if 'coconspirator_uids' in body:
        update['coconspirator_uids'] = body['coconspirator_uids']
    if 'subject_uid' in body:
        update['subject_uid'] = body['subject_uid']
    if update:
        from server.database import get_database
        await get_database()['ingestion_cases'].update_one(
            {'_id': case_id},
            {'$set': update},
        )
    return update


# ── Section Management ────────────────────────────────────────────


@router.post('/cases/{case_id}/sections/{section_key}/none')
async def mark_section_none(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
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
        await ingestion_service.mark_section_none(
            case_id, section_key, subject_index=subject_index,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {'section': section_key, 'status': 'none'}


@router.post('/cases/{case_id}/sections/{section_key}/reopen')
async def reopen_section(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Reopen a section that was marked as N/A, setting it back to empty."""
    await _get_case_or_404(case_id)
    await ingestion_service.update_section(
        case_id, section_key, 'empty', subject_index=subject_index,
    )
    return {'section': section_key, 'status': 'empty'}


# ── Investigator Notes ────────────────────────────────────────────


@router.put('/cases/{case_id}/notes')
async def save_notes(
    case_id: str,
    body: NotesRequest,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Save investigator notes. Empty string resets to 'empty'."""
    await _get_case_or_404(case_id)
    result = await ingestion_service.save_notes(
        case_id, body.notes, subject_index=subject_index,
    )
    return result


# ── Text Sections with AI Processing ─────────────────────────────

# Allowed section keys for the generic text+AI endpoint.
_TEXT_AI_SECTIONS = {'hexa_dump', 'raw_hex_dump'}


@router.put('/cases/{case_id}/text-section/{section_key}')
async def save_text_section(
    case_id: str,
    section_key: str,
    body: TextSectionRequest,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Save a text section and run AI processing.

    Stores raw text + AI-generated narrative. Falls back to raw text
    if AI fails. Supports: hexa_dump, raw_hex_dump.
    """
    if section_key not in _TEXT_AI_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid section key: {section_key}. '
                   f'Allowed: {", ".join(sorted(_TEXT_AI_SECTIONS))}',
        )
    await _get_case_or_404(case_id)
    result = await ingestion_service.save_text_section_with_ai(
        case_id, section_key, body.text, subject_index=subject_index,
    )
    return result


@router.get('/cases/{case_id}/text-section/{section_key}')
async def get_text_section(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return a text section's output, raw text, and AI status."""
    if section_key not in _TEXT_AI_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid section key: {section_key}.',
        )
    case = await _get_case_or_404(case_id)
    section = _get_section(case, section_key, subject_index)
    return {
        'status': section.get('status', 'empty'),
        'output': section.get('output'),
        'raw_text': section.get('raw_text'),
        'ai_status': section.get('ai_status'),
        'ai_error': section.get('ai_error'),
        'updated_at': section.get('updated_at'),
    }


# ── Iterative Entry Sections (Prior ICR) ─────────────────────────

_ITERATIVE_SECTIONS = {'previous_icrs', 'rfis'}


@router.post('/cases/{case_id}/entries/{section_key}')
async def add_entry(
    case_id: str,
    section_key: str,
    body: TextSectionRequest,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Add a text entry to an iterative section."""
    if section_key not in _ITERATIVE_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid section key: {section_key}. '
                   f'Allowed: {", ".join(sorted(_ITERATIVE_SECTIONS))}',
        )
    await _get_case_or_404(case_id)
    if not body.text.strip():
        raise HTTPException(status_code=400, detail='Text cannot be empty.')
    entry = await ingestion_service.add_entry(
        case_id, section_key, body.text, subject_index=subject_index,
    )
    return entry


@router.delete('/cases/{case_id}/entries/{section_key}/{entry_id}')
async def remove_entry(
    case_id: str,
    section_key: str,
    entry_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Remove an entry from an iterative section."""
    if section_key not in _ITERATIVE_SECTIONS:
        raise HTTPException(status_code=400, detail=f'Invalid section key: {section_key}.')
    await _get_case_or_404(case_id)
    await ingestion_service.remove_entry(
        case_id, section_key, entry_id, subject_index=subject_index,
    )
    return {'deleted': True, 'entry_id': entry_id}


@router.post('/cases/{case_id}/entries/{section_key}/process')
async def process_entries(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Combine all entries and run AI processing to generate the summary."""
    if section_key not in _ITERATIVE_SECTIONS:
        raise HTTPException(status_code=400, detail=f'Invalid section key: {section_key}.')
    await _get_case_or_404(case_id)
    result = await ingestion_service.process_entries_with_ai(
        case_id, section_key, subject_index=subject_index,
    )
    return result


@router.get('/cases/{case_id}/entries/{section_key}')
async def get_entries(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return all entries and AI output for an iterative section."""
    if section_key not in _ITERATIVE_SECTIONS:
        raise HTTPException(status_code=400, detail=f'Invalid section key: {section_key}.')
    case = await _get_case_or_404(case_id)
    section = _get_section(case, section_key, subject_index)
    return {
        'status': section.get('status', 'empty'),
        'entries': section.get('entries', []),
        'output': section.get('output'),
        'raw_text': section.get('raw_text'),
        'ai_status': section.get('ai_status'),
        'ai_error': section.get('ai_error'),
        'updated_at': section.get('updated_at'),
        'total_count': section.get('total_count'),
    }


@router.patch('/cases/{case_id}/entries/{section_key}/total-count')
async def set_total_count(
    case_id: str,
    section_key: str,
    body: dict,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Set the total count for an iterative section (e.g. total prior ICRs for a subject)."""
    if section_key not in _ITERATIVE_SECTIONS:
        raise HTTPException(status_code=400, detail=f'Invalid section key: {section_key}.')
    await _get_case_or_404(case_id)
    count = body.get('count')
    await ingestion_service.set_total_count(
        case_id, section_key, count, subject_index=subject_index,
    )
    return {'ok': True, 'total_count': count}


# ── Text + Image Sections (L1 Victim, L1 Suspect) ────────────────

_TEXT_IMAGE_SECTIONS = {'l1_victim', 'l1_suspect'}


@router.put('/cases/{case_id}/text-image-section/{section_key}')
async def save_text_image_section(
    case_id: str,
    section_key: str,
    text: str = Form(''),
    files: Optional[List[UploadFile]] = File(None),
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Save a text + image section and run AI processing.

    Accepts multipart form data: text field + optional image files.
    AI translates, organizes, and condenses into a case-file summary.
    """
    if section_key not in _TEXT_IMAGE_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid section key: {section_key}. '
                   f'Allowed: {", ".join(sorted(_TEXT_IMAGE_SECTIONS))}',
        )

    case = await _get_case_or_404(case_id)

    # Guard: don't reprocess if already complete or processing
    sec_status = _get_section(case, section_key, subject_index).get('status', 'empty')
    if sec_status == 'processing':
        raise HTTPException(status_code=409, detail=f'{section_key} is currently processing.')
    if sec_status == 'complete':
        raise HTTPException(
            status_code=409,
            detail=f'{section_key} is already complete. Reset before reprocessing.',
        )

    if not text.strip() and not files:
        raise HTTPException(status_code=400, detail='Text or at least one image is required.')

    # Read and validate image files
    import uuid as _uuid
    from server.services.ingestion.ingestion_service import _store_ingestion_images

    image_refs = []
    batch_id = f'batch_{_uuid.uuid4().hex[:8]}'

    if files:
        file_data = []
        for f in files:
            if not f.content_type or f.content_type not in _ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f'Only image files (JPEG, PNG, GIF, WebP) accepted. '
                           f'Got: {f.content_type} for {f.filename}',
                )
            content = await f.read()
            file_data.append((f.filename or 'image', content, f.content_type))

        image_refs = _store_ingestion_images(case_id, section_key, batch_id, file_data)

    result = await ingestion_service.save_text_and_images_with_ai(
        case_id, section_key, text, image_refs, batch_id,
        subject_index=subject_index,
    )
    return result


@router.get('/cases/{case_id}/text-image-section/{section_key}')
async def get_text_image_section(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return a text+image section's output, raw text, images, and AI status."""
    if section_key not in _TEXT_IMAGE_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid section key: {section_key}.',
        )
    case = await _get_case_or_404(case_id)
    section = _get_section(case, section_key, subject_index)
    return {
        'status': section.get('status', 'empty'),
        'output': section.get('output'),
        'raw_text': section.get('raw_text'),
        'images': section.get('images', []),
        'batch_id': section.get('batch_id'),
        'ai_status': section.get('ai_status'),
        'ai_error': section.get('ai_error'),
        'updated_at': section.get('updated_at'),
    }


@router.post('/cases/{case_id}/text-image-section/{section_key}/reset')
async def reset_text_image_section(
    case_id: str,
    section_key: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Reset a text+image section to empty."""
    if section_key not in _TEXT_IMAGE_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid section key: {section_key}.',
        )
    await _get_case_or_404(case_id)
    await ingestion_service.update_section(
        case_id, section_key, 'empty',
        extra_fields={
            'output': None,
            'raw_text': None,
            'images': [],
            'batch_id': None,
            'ai_status': None,
            'ai_error': None,
        },
        subject_index=subject_index,
    )
    return {'section': section_key, 'status': 'empty'}


# ── KYC Document Upload (Image-Only) ─────────────────────────────


@router.post('/cases/{case_id}/kyc')
async def upload_kyc(
    case_id: str,
    files: List[UploadFile] = File(...),
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload KYC document images and run AI extraction.

    Accepts image files (JPEG, PNG, GIF, WebP). AI identifies each
    document/screenshot and extracts identity fields verbatim.
    """
    case = await _get_case_or_404(case_id)

    # Guard: don't reprocess if already complete or processing
    kyc_status = _get_section(case, 'kyc', subject_index).get('status', 'empty')
    if kyc_status == 'processing':
        raise HTTPException(status_code=409, detail='KYC section is currently processing.')
    if kyc_status == 'complete':
        raise HTTPException(
            status_code=409,
            detail='KYC section is already complete. Reset before reprocessing.',
        )

    if not files:
        raise HTTPException(status_code=400, detail='At least one image file is required.')

    # Read and validate image files
    import uuid as _uuid
    from server.services.ingestion.ingestion_service import _store_ingestion_images

    file_data = []
    for f in files:
        if not f.content_type or f.content_type not in _ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f'Only image files (JPEG, PNG, GIF, WebP) accepted. '
                       f'Got: {f.content_type} for {f.filename}',
            )
        content = await f.read()
        file_data.append((f.filename or 'image', content, f.content_type))

    batch_id = f'batch_{_uuid.uuid4().hex[:8]}'
    image_refs = _store_ingestion_images(case_id, 'kyc', batch_id, file_data)

    result = await ingestion_service.save_images_with_ai(
        case_id, 'kyc', image_refs, batch_id, subject_index=subject_index,
    )
    return result


@router.get('/cases/{case_id}/kyc')
async def get_kyc_output(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return KYC section data including output and image references."""
    case = await _get_case_or_404(case_id)
    section = _get_section(case, 'kyc', subject_index)
    return {
        'status': section.get('status', 'empty'),
        'output': section.get('output'),
        'images': section.get('images', []),
        'batch_id': section.get('batch_id'),
        'ai_status': section.get('ai_status'),
        'ai_error': section.get('ai_error'),
        'updated_at': section.get('updated_at'),
    }


@router.post('/cases/{case_id}/kyc/reset')
async def reset_kyc(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Reset KYC section to empty, clearing images and AI output."""
    await _get_case_or_404(case_id)
    await ingestion_service.update_section(
        case_id, 'kyc', 'empty',
        extra_fields={
            'images': [],
            'batch_id': None,
            'output': None,
            'ai_status': None,
            'ai_error': None,
        },
        subject_index=subject_index,
    )
    return {'section': 'kyc', 'status': 'empty'}


# ── Kodex / LE (PDF batch upload + 3-stage pipeline) ─────────────


_ALLOWED_PDF_TYPES = {'application/pdf'}


@router.post('/cases/{case_id}/kodex')
async def upload_kodex(
    case_id: str,
    files: List[UploadFile] = File(...),
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload Kodex/LE case PDFs and extract text.

    Accepts multiple PDF files. Requires subject_uid to be set on the case
    (populated by C360 processing). Text extraction runs in the foreground.
    AI assessment is deferred to assembly time when full case context is available.
    """
    case = await _get_case_or_404(case_id)

    # Hard gate: subject UID must be present
    subject_uid = case.get('subject_uid', '')
    if not subject_uid:
        raise HTTPException(
            status_code=400,
            detail='Subject UID is required for Kodex processing. '
                   'Upload C360 data first to identify the subject.',
        )

    # Guard: don't reprocess if already extracted or processing
    kodex_status = _get_section(case, 'kodex', subject_index).get('status', 'empty')
    if kodex_status == 'processing':
        raise HTTPException(status_code=409, detail='Kodex section is currently processing.')
    if kodex_status in ('complete', 'extracted'):
        raise HTTPException(
            status_code=409,
            detail='Kodex section already has data. Reset before reprocessing.',
        )

    if not files:
        raise HTTPException(status_code=400, detail='At least one PDF file is required.')

    # Read and validate PDF files (MUST read bytes before any async work)
    files_bytes = []
    for f in files:
        content_type = f.content_type or ''
        filename = f.filename or 'document.pdf'
        # Accept application/pdf or files ending in .pdf
        if content_type not in _ALLOWED_PDF_TYPES and not filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f'Only PDF files accepted. Got: {content_type} for {filename}',
            )
        content = await f.read()
        files_bytes.append((filename, content))

    # Mark as processing
    await ingestion_service.update_section(
        case_id, 'kodex', 'processing',
        subject_index=subject_index,
    )

    # Extract text from all PDFs (no AI processing)
    from server.services.ingestion.kodex_processor import process_kodex_batch

    try:
        result = await process_kodex_batch(files_bytes, subject_uid)
    except Exception as e:
        logger.exception('Kodex text extraction failed for %s', case_id)
        await ingestion_service.update_section(
            case_id, 'kodex', 'error',
            error=str(e),
            subject_index=subject_index,
        )
        raise HTTPException(status_code=500, detail=f'Text extraction failed: {e}')

    # Build pdf_files metadata
    pdf_files = []
    for r in result['per_case']:
        pdf_files.append({
            'filename': r['filename'],
            'page_count': r['page_count'],
            'text_length': r['text_length'],
            'uid_count': r['uid_count'],
            'approx_other_uids': r['approx_other_uids'],
        })

    # Check for extraction errors
    has_text = any(r.get('extracted_text') for r in result['per_case'])

    if not has_text:
        error = '; '.join(result['errors']) if result['errors'] else 'No text extracted from PDFs'
        await ingestion_service.update_section(
            case_id, 'kodex', 'error',
            error=error,
            extra_fields={
                'pdf_files': pdf_files,
                'per_case': result['per_case'],
                'case_count': result['case_count'],
            },
            subject_index=subject_index,
        )
        return {
            'status': 'error',
            'case_count': result['case_count'],
            'pdf_files': pdf_files,
            'errors': result.get('errors', []),
        }

    # Store extracted text — mark as 'extracted' (AI deferred to assembly)
    await ingestion_service.update_section(
        case_id, 'kodex', 'extracted',
        extra_fields={
            'pdf_files': pdf_files,
            'per_case': result['per_case'],
            'case_count': result['case_count'],
        },
        subject_index=subject_index,
    )

    return {
        'status': 'extracted',
        'case_count': result['case_count'],
        'pdf_files': pdf_files,
        'errors': result.get('errors', []),
    }


@router.get('/cases/{case_id}/kodex')
async def get_kodex_output(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Return Kodex section data including per-PDF extractions and metadata."""
    case = await _get_case_or_404(case_id)
    section = _get_section(case, 'kodex', subject_index)
    return {
        'status': section.get('status', 'empty'),
        'output': section.get('output'),
        'pdf_files': section.get('pdf_files', []),
        'per_case': section.get('per_case', []),
        'case_count': section.get('case_count', 0),
        'error': section.get('error_message'),
        'updated_at': section.get('updated_at'),
    }


@router.post('/cases/{case_id}/kodex/reset')
async def reset_kodex(
    case_id: str,
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """Reset Kodex section to empty, clearing all PDF data."""
    await _get_case_or_404(case_id)
    await ingestion_service.update_section(
        case_id, 'kodex', 'empty',
        extra_fields={
            'output': None,
            'error_message': None,
            'pdf_files': [],
            'per_case': [],
            'case_count': 0,
        },
        subject_index=subject_index,
    )
    return {'section': 'kodex', 'status': 'empty'}


# ── Entry with Images (RFI) ───────────────────────────────────────

_IMAGE_SECTIONS = {'rfis'}
_ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}


@router.post('/cases/{case_id}/entries/{section_key}/with-images')
async def add_entry_with_images(
    case_id: str,
    section_key: str,
    text: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    subject_index: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Add an entry with optional image attachments to an iterative section.

    Accepts multipart form data: text field + optional image files.
    Images are stored to disk; MongoDB stores references only.
    """
    if section_key not in _IMAGE_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f'Image entries not supported for section: {section_key}. '
                   f'Allowed: {", ".join(sorted(_IMAGE_SECTIONS))}',
        )
    await _get_case_or_404(case_id)

    if not text.strip():
        raise HTTPException(status_code=400, detail='Text cannot be empty.')

    # Read and validate image files
    image_refs = []
    entry_id = None
    if files:
        from server.services.ingestion.ingestion_service import _store_ingestion_images
        import uuid

        entry_id = f'entry_{uuid.uuid4().hex[:8]}'

        file_data = []
        for f in files:
            if not f.content_type or f.content_type not in _ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f'Only image files (JPEG, PNG, GIF, WebP) accepted. '
                           f'Got: {f.content_type} for {f.filename}',
                )
            content = await f.read()
            file_data.append((f.filename or 'image', content, f.content_type))

        image_refs = _store_ingestion_images(case_id, section_key, entry_id, file_data)

    # Add entry with image references
    entry = await ingestion_service.add_entry(
        case_id, section_key, text,
        images=image_refs if image_refs else None,
        entry_id=entry_id,
        subject_index=subject_index,
    )
    return entry


# ── Ingestion Image Serving ───────────────────────────────────────


@router.get('/images/{case_id}/{section_key}/{entry_id}/{image_id}')
async def get_ingestion_image(
    case_id: str,
    section_key: str,
    entry_id: str,
    image_id: str,
):
    """Serve a stored ingestion image file."""
    from server.config import settings

    image_dir = (
        Path(settings.IMAGES_DIR) / 'ingestion' / case_id / section_key / entry_id
    )
    if not image_dir.is_dir():
        raise HTTPException(status_code=404, detail='Image not found')

    matches = list(image_dir.glob(f'{image_id}.*'))
    if not matches:
        raise HTTPException(status_code=404, detail='Image not found')

    filepath = matches[0]
    media_type = mimetypes.guess_type(str(filepath))[0] or 'application/octet-stream'
    return FileResponse(filepath, media_type=media_type)


# ── Multi-User Subject Management ─────────────────────────────────


@router.post('/cases/{case_id}/submit-subject')
async def submit_subject(
    case_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Mark the current subject as complete and advance to the next subject.

    Only valid for multi-user cases. Checks that all required sections are
    terminal for the current subject before marking complete.
    """
    try:
        # Look up current_subject_index from the case
        case_doc = await ingestion_service.get_case(case_id)
        if not case_doc:
            raise HTTPException(status_code=404, detail='Case not found')
        current_index = case_doc.get('current_subject_index', 0)
        result = await ingestion_service.submit_subject(case_id, current_index)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch('/cases/{case_id}/subjects/{subject_index}/uid')
async def set_subject_uid(
    case_id: str,
    subject_index: int,
    body: SetSubjectUidRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Set the UID for a subject in a multi-user case.

    Called when the investigator enters the UID for a subsequent subject
    (subject 0's UID is set at case creation or via C360 processing).
    """
    try:
        await ingestion_service.set_subject_uid(case_id, subject_index, body.user_id)
        return {'ok': True, 'subject_index': subject_index, 'user_id': body.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Reset ─────────────────────────────────────────────────────────


@router.post('/cases/{case_id}/reset')
async def reset_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Reset an ingestion case to its initial state, clearing all sections."""
    try:
        doc = await ingestion_service.reset_case(case_id)
        return _serialize_case(doc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/cases/{case_id}')
async def delete_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an ingestion case entirely. Returns to square one."""
    try:
        await ingestion_service.delete_case(case_id)
        return {'deleted': True, 'case_id': case_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Assembly ──────────────────────────────────────────────────────


@router.get('/cases/{case_id}/assemble/preview')
async def preview_assembly(case_id: str, current_user: dict = Depends(get_current_user)):
    """Preview the assembled case data markdown without creating the case."""
    await _get_case_or_404(case_id)

    try:
        result = await ingestion_service.preview_assembled_case_data(case_id)
        return {
            'assembled_case_data': result['assembled_case_data'],
            'sections_included': result['sections_included'],
            'sections_none': result['sections_none'],
        }
    except ValueError as e:
        msg = str(e)
        if msg.startswith('incomplete:'):
            incomplete = msg.split(':', 1)[1].split(',')
            raise HTTPException(
                status_code=409,
                detail={
                    'message': 'Cannot preview: sections not complete',
                    'incomplete_sections': incomplete,
                },
            )
        raise HTTPException(status_code=400, detail=msg)


@router.post('/cases/{case_id}/assemble')
async def assemble_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Assemble section outputs, create investigation case, mark ingestion completed."""
    await _get_case_or_404(case_id)

    try:
        result = await ingestion_service.assemble_case_data(case_id)
        return {
            'case_id': result['case_id'],
            'status': 'completed',
            'sections_included': result['sections_included'],
            'sections_none': result['sections_none'],
        }
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
        if 'already exists in investigations' in msg:
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=str(e))
