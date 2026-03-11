"""
C360 Bulk Downloader — Backend Integration.

Downloads all C360 spreadsheets from DataWind/Aeolus BI for a given user ID
using captured payload templates. Produces files_bytes tuples compatible with
the existing C360 processing pipeline.

This is a temporary integration while waiting for proper backend API access.
"""

import json
import logging
from pathlib import Path

import httpx

from server.database import get_database
from server.services.ingestion.ingestion_service import _section_path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOWNLOAD_URL = "https://datawind.bdp.toolsfdg.net/bi/aeolus/vqs/api/v2/vizQuery/download"
PAYLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "c360_payloads"
REQUEST_TIMEOUT = 120  # seconds per sheet
USER_ID_FIELD_NAMES = {"user_id", "major_user_id"}


# ---------------------------------------------------------------------------
# Core functions (ported from standalone script)
# ---------------------------------------------------------------------------

def extract_template_uid(payload: dict) -> str | None:
    """
    Extract the template user ID from a payload's query.whereList.

    Looks for a whereList entry where the field name is 'user_id' or
    'major_user_id' with op 'in' and a non-empty val array.
    Returns the first value from that val array.
    """
    where_list = payload.get("query", {}).get("whereList", [])
    for entry in where_list:
        name = entry.get("name", "")
        op = entry.get("op", "")
        val = entry.get("val", [])
        if name in USER_ID_FIELD_NAMES and op == "in" and val:
            return val[0]
    return None


def prepare_payload(payload: dict, template_uid: str, target_uid: str,
                    sheet_name: str) -> dict:
    """
    Replace the template user ID with the target user ID throughout
    the payload, and update the reportName in downloadConfig.
    """
    payload_str = json.dumps(payload)
    payload_str = payload_str.replace(f'"{template_uid}"', f'"{target_uid}"')
    result = json.loads(payload_str)

    if "downloadConfig" in result and "reportName" in result["downloadConfig"]:
        result["downloadConfig"]["reportName"] = f"{sheet_name}_{target_uid}.xlsx"

    return result


def discover_payloads(payloads_dir: Path | None = None) -> list[Path]:
    """Find all JSON payload files in the payloads directory."""
    directory = payloads_dir or PAYLOADS_DIR
    if not directory.is_dir():
        raise FileNotFoundError(f"Payloads directory not found: {directory}")
    files = sorted(directory.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No .json files found in {directory}")
    return files


# ---------------------------------------------------------------------------
# Async download orchestrator
# ---------------------------------------------------------------------------

async def download_c360_sheets(
    case_id: str,
    target_uid: str,
    cookie: str,
    subject_index: int | None = None,
) -> list[tuple[str, bytes]]:
    """
    Download all C360 spreadsheets for a given user ID.

    Updates download_progress in MongoDB after each sheet so the frontend
    can display real-time progress via polling.

    Returns list of (filename, bytes) tuples — same format expected by
    _process_c360_background.

    Raises:
        C360DownloadError: If the first download fails (session expired)
                           or if all downloads fail.
    """
    payload_files = discover_payloads()
    total = len(payload_files)
    db = get_database()
    collection = db['ingestion_cases']
    prefix = _section_path('c360', subject_index)

    files_bytes: list[tuple[str, bytes]] = []
    failed_sheets: list[str] = []

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        for i, payload_file in enumerate(payload_files):
            sheet_name = payload_file.stem

            # Update progress in MongoDB
            await collection.update_one(
                {'_id': case_id},
                {'$set': {
                    f'{prefix}.download_progress': {
                        'current': i,
                        'total': total,
                        'current_sheet': sheet_name,
                        'succeeded': len(files_bytes),
                        'failed': len(failed_sheets),
                        'failed_sheets': failed_sheets,
                    },
                }},
            )

            # Load and prepare payload
            with open(payload_file, 'r', encoding='utf-8') as f:
                payload = json.load(f)

            template_uid = extract_template_uid(payload)
            if template_uid is None:
                logger.warning(
                    "C360 fetch [%s]: %s — no UID filter found, skipping",
                    case_id, sheet_name,
                )
                failed_sheets.append(sheet_name)
                continue

            payload = prepare_payload(payload, template_uid, target_uid, sheet_name)

            headers = {
                "Content-Type": "application/json",
                "Cookie": cookie,
                "Accept": "*/*",
            }

            # Download
            try:
                response = await client.post(
                    DOWNLOAD_URL,
                    json=payload,
                    headers=headers,
                )
            except httpx.TimeoutException:
                logger.warning(
                    "C360 fetch [%s]: %s — timed out", case_id, sheet_name,
                )
                if i == 0:
                    raise C360DownloadError(
                        "First C360 sheet timed out. The C360 server may be "
                        "unavailable — try again later."
                    )
                failed_sheets.append(sheet_name)
                continue
            except httpx.RequestError as exc:
                logger.warning(
                    "C360 fetch [%s]: %s — request error: %s",
                    case_id, sheet_name, exc,
                )
                if i == 0:
                    raise C360DownloadError(
                        f"Failed to connect to C360 server: {exc}"
                    )
                failed_sheets.append(sheet_name)
                continue

            # Validate response
            if response.status_code != 200:
                logger.warning(
                    "C360 fetch [%s]: %s — HTTP %d",
                    case_id, sheet_name, response.status_code,
                )
                if i == 0:
                    raise C360DownloadError(
                        "C360 session cookie appears to be expired or invalid. "
                        "Please get a fresh cookie from your browser."
                    )
                failed_sheets.append(sheet_name)
                continue

            if response.content[:2] != b"PK":
                logger.warning(
                    "C360 fetch [%s]: %s — response is not xlsx",
                    case_id, sheet_name,
                )
                if i == 0:
                    raise C360DownloadError(
                        "C360 session cookie appears to be expired. "
                        "The server returned a non-spreadsheet response. "
                        "Please get a fresh cookie from your browser."
                    )
                failed_sheets.append(sheet_name)
                continue

            # Success
            filename = f"{sheet_name}_{target_uid}.xlsx"
            files_bytes.append((filename, response.content))
            logger.info(
                "C360 fetch [%s]: %s — OK (%.1f KB)",
                case_id, sheet_name, len(response.content) / 1024,
            )

    # Final progress update
    await collection.update_one(
        {'_id': case_id},
        {'$set': {
            f'{prefix}.download_progress': {
                'current': total,
                'total': total,
                'current_sheet': '',
                'succeeded': len(files_bytes),
                'failed': len(failed_sheets),
                'failed_sheets': failed_sheets,
            },
        }},
    )

    if not files_bytes:
        raise C360DownloadError(
            f"All {total} C360 sheet downloads failed. "
            "Check your session cookie and try again."
        )

    logger.info(
        "C360 fetch [%s]: download complete — %d/%d succeeded",
        case_id, len(files_bytes), total,
    )

    return files_bytes


class C360DownloadError(Exception):
    """Raised when C360 download fails in a way that should abort."""
    pass
