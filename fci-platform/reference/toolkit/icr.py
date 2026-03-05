"""
ICR (Investigation Case Review) API routes.
Thin layer — all logic lives in services/icr/.
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from typing import List, Optional
import traceback

from services.icr.session_store import session_store
from services.icr.parser import parse_uploaded_file
from services.icr.file_detector import classify_files
from services.icr.processor_registry import discover_processors
from services.icr.validation import validate_for_processing
from services.icr.field_discovery import discover_unused_fields, log_discovery, get_field_log_summary
from services.icr.utils import safe_str, safe_float, safe_int
from services.icr.elliptic_api import EllipticScreener
from services.icr.address_manager import build_address_list
from services.icr.uid_search import search_associated_uids
from services.icr.health_check import run_health_check

router = APIRouter()


def _get_ci(row, key):
    """Case-insensitive row column lookup."""
    if key in row:
        return row[key]
    key_lower = key.lower().strip()
    for k, v in row.items():
        if safe_str(k).lower().strip() == key_lower:
            return v
    return None


# ── Request / Response Models ──────────────────────────────────

class ProcessRequest(BaseModel):
    session_id: str
    params: dict = {}


class ClearRequest(BaseModel):
    session_id: str

class EllipticScreenRequest(BaseModel):
    session_id: str
    addresses: List[str]
    customer_id: str

class AddressManagerRequest(BaseModel):
    session_id: str
    manual_addresses: List[str] = []

class UidSearchRequest(BaseModel):
    session_id: str
    uids: List[str]

# ── Upload Endpoint ────────────────────────────────────────────

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Accept one or more spreadsheet files, parse them all,
    classify what we recognise, store everything in a session.
    Returns detection results and any auto-populated fields.
    """
    session_id = session_store.create_session()
    session = session_store.get_session(session_id)

    parsed_files = []
    for f in files:
        content = await f.read()
        try:
            result = parse_uploaded_file(f.filename, content)
            parsed_files.append(result)
        except Exception as e:
            parsed_files.append({
                'filename': f.filename,
                'error': str(e),
                'headers': [],
                'rows': [],
            })

    detected, undetected, uol_data = classify_files(parsed_files)

    # Store everything in session
    session['detected_files'] = detected
    session['undetected_files'] = undetected
    if uol_data:
        session['uol_data'] = uol_data

    # Extract subject UID and user info
    auto_populate = {}
    user_info_display = None
    user_info_source = None

    # Priority 1: UOL Customer Information
    if uol_data and uol_data.get('customer_info'):
        ci = uol_data['customer_info']
        if ci.get('user_id'):
            session['subject_uid'] = ci['user_id']
            user_info_source = 'UOL'
            session['user_info_source'] = 'UOL'

            if ci.get('nationality') and ci['nationality'] != '(null)':
                auto_populate['nationality'] = ci['nationality']
                auto_populate['residence'] = ci['nationality']

            auth = (ci.get('auth_type') or '').lower()
            if auth == 'personal':
                auto_populate['account_type'] = 'individual'
            elif auth in ('enterprise', 'corporate', 'company'):
                auto_populate['account_type'] = 'corporate'

            user_info_display = {
                'source': 'UOL — Customer Information tab',
                'fields': {
                    'Name': ci.get('full_name') or 'N/A',
                    'UID': ci.get('user_id', ''),
                    'Email': ci.get('email') or 'N/A',
                    'Mobile': ci.get('mobile') or 'N/A',
                    'Nationality': ci.get('nationality') or 'N/A',
                    'Reg Date': ci.get('registration_time') or 'N/A',
                    'Auth': ci.get('auth_type') or 'N/A',
                    'Status': ci.get('status') or 'N/A',
                    '2FA': ci.get('two_fa') or 'N/A',
                },
            }

    # Priority 2: C360 User Info spreadsheet
    if 'USER_INFO' in detected and detected['USER_INFO']['rows']:
        ui = detected['USER_INFO']['rows'][0]
        session['user_info'] = ui

        if not user_info_source:
            user_info_source = 'C360'
            session['user_info_source'] = 'C360'

            nat = safe_str(ui.get('Nationality', ''))
            res = safe_str(ui.get('Residency', ''))
            user_type = safe_str(ui.get('User Type', '')).lower()

            if nat and nat != '(null)':
                auto_populate['nationality'] = nat
            if res and res != '(null)':
                auto_populate['residence'] = res
            if user_type == 'retail':
                auto_populate['account_type'] = 'individual'
            elif user_type:
                auto_populate['account_type'] = 'corporate'

            def ui_val(key):
                v = safe_str(ui.get(key, ''))
                return v if v and v != '(null)' else 'N/A'

            user_info_display = {
                'source': 'C360 User Info export',
                'fields': {
                    'VIP': ui_val('VIP Level (Now/12Mth High)'),
                    'Entity Tag': ui_val('Entity Tag'),
                    'Balance': '${:,.2f}'.format(safe_float(ui.get('Total Balance', 0))),
                    'KYC Risk': ui_val('KYC Risk'),
                    'ID Type': ui_val('ID Type'),
                    'Reg Date': ui_val('Registration Date'),
                    'Email': ui_val('Email Domain'),
                    'Age': ui_val('User Age'),
                    'API Trader': ui_val('Is API Trader'),
                },
            }
        else:
            # UOL already set as primary, but use C360 for residence/nationality override
            nat = safe_str(ui.get('Nationality', ''))
            res = safe_str(ui.get('Residency', ''))
            if res and res != '(null)':
                auto_populate['residence'] = res
            if nat and nat != '(null)':
                auto_populate['nationality'] = nat

    # Auto-populate from fiat partners (devices, IP locations, system languages)
    if 'USER_INFO_FIAT_PARTNERS' in detected and detected['USER_INFO_FIAT_PARTNERS']['rows']:
        fp = detected['USER_INFO_FIAT_PARTNERS']['rows'][0]
        for col, key in [('IP location Used', 'ip_locations'),
                         ('No. of Device Used', 'devices_used'),
                         ('System Language used', 'sys_langs')]:
            val = _get_ci(fp, col)
            if val is not None:
                v = safe_int(val)
                if v > 0:
                    auto_populate[key] = v

    # Auto-populate internal transfer count from CP summary
    if 'CP_SUMMARY' in detected and detected['CP_SUMMARY']['rows']:
        cp = detected['CP_SUMMARY']['rows'][0]
        val = _get_ci(cp, 'Internal CP User Count')
        if val is not None:
            v = safe_int(val)
            if v >= 0:
                auto_populate['it_count'] = v

    # Auto-populate device link count from device link summary
    if 'DEVICE_LINK_SUMMARY' in detected and detected['DEVICE_LINK_SUMMARY']['rows']:
        dl = detected['DEVICE_LINK_SUMMARY']['rows'][0]
        val = _get_ci(dl, 'Device Linked User Count')
        if val is not None:
            v = safe_int(val)
            if v >= 0:
                auto_populate['device_link_count'] = v

    # Fallback UID detection
    if not session.get('subject_uid'):
        if 'DEVICE_SUM' in detected and detected['DEVICE_SUM']['rows']:
            session['subject_uid'] = safe_str(
                detected['DEVICE_SUM']['rows'][0].get('user_id', ''))
    if not session.get('subject_uid'):
        if 'ADDR_VALUE' in detected and detected['ADDR_VALUE']['rows']:
            session['subject_uid'] = safe_str(
                detected['ADDR_VALUE']['rows'][0].get('major_user_id', ''))

    session_store.update_session(session_id, session)

    # Build response
    detected_response = []
    for file_type, data in detected.items():
        detected_response.append({
            'filename': data['filename'],
            'type': file_type,
            'label': data['label'],
            'row_count': data['row_count'],
        })

    undetected_response = []
    for data in undetected:
        undetected_response.append({
            'filename': data['filename'],
            'row_count': data.get('row_count', 0),
            'col_count': data.get('col_count', 0),
        })

    # UOL tab info
    uol_info = None
    if uol_data:
        fw_count = len(uol_data.get('fiat_withdrawals', []))
        fw_failed = sum(1 for r in uol_data.get('fiat_withdrawals', [])
                        if r.get('status', '').upper() != 'SUCCESS')
        uol_info = {
            'sheet_names': uol_data.get('sheet_names', []),
            'has_customer_info': uol_data.get('customer_info') is not None,
            'fiat_withdrawal_count': fw_count,
            'fiat_withdrawal_failed': fw_failed,
            'crypto_withdrawal_count': len(uol_data.get('crypto_withdrawals', [])),
            'crypto_deposit_count': len(uol_data.get('crypto_deposits', [])),
            'binance_pay_count': len(uol_data.get('binance_pay', [])),
            'p2p_count': len(uol_data.get('p2p_transactions', [])),
        }

    # Data health check
    data_warnings = run_health_check(detected, undetected, uol_data)

    return {
        'session_id': session_id,
        'detected_files': detected_response,
        'undetected_files': undetected_response,
        'uol_info': uol_info,
        'subject_uid': session.get('subject_uid'),
        'user_info_source': user_info_source,
        'user_info_display': user_info_display,
        'auto_populate': auto_populate,
        'data_warnings': data_warnings,
    }


# ── Process Endpoint ───────────────────────────────────────────

@router.post("/process")
async def process_data(request: ProcessRequest):
    """
    Run all applicable processors against the uploaded data.
    Returns structured output sections for each analysis tab.
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    subject_uid = session.get('subject_uid')
    if not subject_uid:
        raise HTTPException(
            status_code=400,
            detail="No Subject UID detected. Ensure UOL, Device Summary, or Top 10 by Value is uploaded.")

    processors = discover_processors()

    # Build available file types set
    available = set(session.get('detected_files', {}).keys())
    uol_data = session.get('uol_data', {})
    if uol_data and uol_data.get('fiat_withdrawals'):
        available.add('UOL_FIAT_WITHDRAWALS')

    # Validate
    errors = validate_for_processing(session, request.params, processors)
    if errors:
        return {
            'validation_errors': errors,
            'sections': [],
            'field_discovery': [],
        }

    # Build context shared across processors
    context = {
        'subject_uid': subject_uid,
        'uol_data': uol_data,
        'user_info': session.get('user_info'),
    }

    file_data = session.get('detected_files', {})

    # Run each processor
    sections = []
    for processor in processors:
        if not processor.should_run(available, request.params):
            continue
        try:
            result = processor.process(file_data, request.params, context)

            section = {
                'id': processor.id,
                'label': processor.label,
                'content': result.content,
                'has_data': result.has_data,
            }

            # Dynamic label for Elliptic
            if processor.id == 'elliptic' and result.has_data and result.csv_content:
                line_count = len(result.csv_content.strip().split('\n')) - 1
                section['label'] = 'Elliptic Upload ({})'.format(line_count)
                section['csv_content'] = result.csv_content
                section['csv_filename'] = result.csv_filename
                if result.metadata:
                    section['elliptic_addresses'] = result.metadata.get('addresses', [])
                    section['elliptic_customer_id'] = result.metadata.get('customer_id', '')
                    # Store address data in session for cross-referencing
                    session['elliptic_addresses'] = result.metadata.get('address_map', {})
                    session['elliptic_customer_id'] = result.metadata.get('customer_id', '')

            # Dynamic label for Failed Fiat
            if processor.id == 'fiat' and uol_data and uol_data.get('fiat_withdrawals'):
                section['label'] = 'Failed Fiat (+UOL)'

            sections.append(section)

        except Exception as e:
            sections.append({
                'id': processor.id,
                'label': processor.label,
                'content': 'ERROR: {}\n\n{}'.format(str(e), traceback.format_exc()),
                'has_data': False,
            })

    # Field discovery — runs silently, logs to SQLite
    try:
        unused_report = discover_unused_fields(session, processors)
        log_discovery(request.session_id, session, unused_report)
    except Exception:
        unused_report = []

    return {
        'validation_errors': [],
        'sections': sections,
        'field_discovery': unused_report,
    }


# ── Clear Endpoint ─────────────────────────────────────────────

@router.post("/clear")
async def clear_session(request: ClearRequest):
    """Remove a session and its data."""
    session_store.delete_session(request.session_id)
    return {'status': 'cleared'}


# ── Elliptic API Screening Endpoint ───────────────────────────

@router.post("/screen-elliptic")
async def screen_elliptic(request: EllipticScreenRequest):
    """
    Screen wallet addresses via Elliptic API (or demo mode).
    Returns structured results with markdown for AI consumption.
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    screener = EllipticScreener()

    if not screener.is_configured():
        return {
            'status': 'not_configured',
            'message': 'Elliptic API credentials not configured. Set ELLIPTIC_API_KEY and ELLIPTIC_API_SECRET environment variables, or set ELLIPTIC_DEMO_MODE=true.',
        }

    if not request.addresses:
        return {
            'status': 'error',
            'message': 'No addresses provided for screening.',
        }

    if len(request.addresses) > 20:
        return {
            'status': 'error',
            'message': 'Maximum 20 addresses per screening. {} provided.'.format(len(request.addresses)),
        }

    try:
        report = screener.screen_and_report(request.addresses, request.customer_id)
        return report
    except Exception as e:
        logger.exception('Elliptic screening failed')
        return {
            'status': 'error',
            'message': 'Screening failed: {}'.format(str(e)),
        }


# ── Elliptic Address Management Endpoint ───────────────────────

@router.post("/elliptic-addresses")
async def manage_elliptic_addresses(request: AddressManagerRequest):
    """
    Build enriched address list with UOL cross-referencing.
    Combines auto-extracted addresses (from Elliptic processor)
    with manually entered addresses, cross-references all against
    UOL crypto transaction history.
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    if not session.get('elliptic_addresses') and not request.manual_addresses:
        return {
            'addresses': [],
            'narrative': 'No addresses available. Process files first or enter addresses manually.',
            'stats': {
                'total_addresses': 0,
                'uol_matched': 0,
                'uol_unmatched': 0,
                'uol_available': False,
                'uol_withdrawal_count': 0,
                'uol_deposit_count': 0,
            },
        }

    try:
        result = build_address_list(session, request.manual_addresses)
        return result
    except Exception as e:
        logger.exception('Address manager failed')
        raise HTTPException(status_code=500, detail='Address management failed: {}'.format(str(e)))


# ── Associated UID Search Endpoint ─────────────────────────────

@router.post("/uid-search")
async def uid_search(request: UidSearchRequest):
    """
    Search UOL transaction history for connections between the subject
    and associated UIDs (victims, co-suspects).
    Searches Crypto Withdrawals, Crypto Deposits, Binance Pay, and P2P tabs.
    """
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    if not session.get('uol_data'):
        return {
            'results': {},
            'narrative': 'No UOL data available. Upload a UOL file first.',
            'stats': {
                'uids_searched': len(request.uids),
                'uids_found': 0,
                'total_matches': 0,
            },
        }

    if not request.uids:
        return {
            'results': {},
            'narrative': 'No UIDs provided for search.',
            'stats': {'uids_searched': 0, 'uids_found': 0, 'total_matches': 0},
        }

    try:
        result = search_associated_uids(session, request.uids)
        return result
    except Exception as e:
        logger.exception('UID search failed')
        raise HTTPException(status_code=500, detail='UID search failed: {}'.format(str(e)))


# ── Developer Endpoint ─────────────────────────────────────────


@router.get("/dev/field-log")
async def get_field_log():
    """
    Developer-only endpoint.
    Returns aggregated report of unused fields across all user sessions.
    """
    return get_field_log_summary()