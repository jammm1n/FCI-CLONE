"""
C360 Bulk Spreadsheet Downloader
=================================
Downloads all C360 spreadsheets for a given user ID using captured
payload templates from the payloads/ directory.

Usage:
    python c360_download.py <user_id> [cookie_string]

    If cookie_string is not provided as an argument, it will be read
    from the C360_COOKIE environment variable.

Requirements:
    - Python 3.9+
    - requests
"""

import sys
import os
import json
import requests
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOWNLOAD_URL = "https://datawind.bdp.toolsfdg.net/bi/aeolus/vqs/api/v2/vizQuery/download"
SCRIPT_DIR = Path(__file__).parent
PAYLOADS_DIR = SCRIPT_DIR / "payloads"
DOWNLOADS_DIR = SCRIPT_DIR / "downloads"
REQUEST_TIMEOUT = 120  # seconds

# Known user ID field names in whereList entries
USER_ID_FIELD_NAMES = {"user_id", "major_user_id"}


def get_cookie_string() -> str:
    """Get the cookie string from CLI arg or environment variable."""
    if len(sys.argv) >= 3:
        return sys.argv[2]
    cookie = os.environ.get("C360_COOKIE", "")
    if not cookie:
        print("ERROR: No cookie provided.")
        print("Either:")
        print('  python c360_download.py <user_id> "<cookie_string>"')
        print("  or: export C360_COOKIE=\"<cookie_string>\"")
        sys.exit(1)
    return cookie


def discover_payloads() -> list[Path]:
    """Find all JSON payload files in the payloads directory."""
    if not PAYLOADS_DIR.is_dir():
        print(f"ERROR: Payloads directory not found: {PAYLOADS_DIR}")
        sys.exit(1)
    files = sorted(PAYLOADS_DIR.glob("*.json"))
    if not files:
        print(f"ERROR: No .json files found in {PAYLOADS_DIR}")
        sys.exit(1)
    return files


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

    # Replace all occurrences of the template UID (as a quoted string value)
    payload_str = payload_str.replace(f'"{template_uid}"', f'"{target_uid}"')

    result = json.loads(payload_str)

    # Update reportName
    if "downloadConfig" in result and "reportName" in result["downloadConfig"]:
        result["downloadConfig"]["reportName"] = f"{sheet_name}_{target_uid}.xlsx"

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python c360_download.py <user_id> [cookie_string]")
        print('Example: python c360_download.py 466492707 "session=eyJ..."')
        sys.exit(1)

    target_uid = sys.argv[1]
    cookie = get_cookie_string()

    # Discover payloads
    payload_files = discover_payloads()
    total = len(payload_files)

    # Create output directory
    output_dir = DOWNLOADS_DIR / target_uid
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nC360 Bulk Downloader")
    print(f"====================")
    print(f"User ID:  {target_uid}")
    print(f"Sheets:   {total}")
    print(f"Output:   {output_dir}\n")

    succeeded = []
    failed = []

    for i, payload_file in enumerate(payload_files, 1):
        sheet_name = payload_file.stem

        # Load payload
        with open(payload_file, "r", encoding="utf-8") as f:
            payload = json.load(f)

        # Extract template UID from this specific file
        template_uid = extract_template_uid(payload)
        if template_uid is None:
            msg = "Could not find user ID filter in payload"
            print(f"  [{i}/{total}] {sheet_name}... SKIP ({msg})")
            failed.append((sheet_name, msg))
            continue

        # Prepare payload with target UID
        payload = prepare_payload(payload, template_uid, target_uid, sheet_name)

        # Download
        print(f"  [{i}/{total}] {sheet_name}...", end=" ", flush=True)

        headers = {
            "Content-Type": "application/json",
            "Cookie": cookie,
            "Accept": "*/*",
        }

        try:
            response = requests.post(
                DOWNLOAD_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            msg = "Request timed out"
            print(f"FAIL ({msg})")
            failed.append((sheet_name, msg))
            continue
        except requests.exceptions.RequestException as e:
            msg = f"Request error: {e}"
            print(f"FAIL ({msg})")
            failed.append((sheet_name, msg))
            continue

        # Check for session expiry on first request
        if response.status_code != 200:
            body_preview = response.text[:300]
            msg = f"HTTP {response.status_code}"

            if i == 1:
                print(f"FAIL ({msg})")
                print(f"\n  Response: {body_preview}")
                print(f"\n  Session cookie appears to be expired — "
                      f"grab a fresh one from the browser.\n")
                sys.exit(1)

            print(f"FAIL ({msg})")
            failed.append((sheet_name, msg))
            continue

        # Validate xlsx
        if response.content[:2] != b"PK":
            # Could be a JSON error response even with 200 status
            body_preview = response.content[:200]

            if i == 1:
                print(f"FAIL (not xlsx)")
                print(f"\n  Response: {body_preview}")
                print(f"\n  Session cookie may be expired — "
                      f"grab a fresh one from the browser.\n")
                sys.exit(1)

            msg = "Response is not an xlsx file"
            print(f"FAIL ({msg})")
            failed.append((sheet_name, msg))
            continue

        # Save
        output_path = output_dir / f"{sheet_name}_{target_uid}.xlsx"
        with open(output_path, "wb") as f:
            f.write(response.content)

        size_kb = len(response.content) / 1024
        print(f"OK ({size_kb:.1f} KB)")
        succeeded.append(sheet_name)

    # Summary
    print(f"\n{'='*40}")
    print(f"Download complete: {len(succeeded)}/{total} succeeded")

    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name, reason in failed:
            print(f"  - {name}: {reason}")

    print()


if __name__ == "__main__":
    main()
