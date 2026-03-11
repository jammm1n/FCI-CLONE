# C360 Bulk Downloader — Integration Handover

## What This Is

A standalone Python script that programmatically downloads all 26 C360 (DataWind/Aeolus BI) spreadsheets for a given Binance user ID. It replaces the manual process of clicking "download" on each embedded spreadsheet in the C360 dashboard.

**Location:** `working_files/c360-downloader/`

## How It Works

### The API

C360 runs on DataWind/Aeolus BI. Each spreadsheet download is a single synchronous POST request:

- **Endpoint:** `https://datawind.bdp.toolsfdg.net/bi/aeolus/vqs/api/v2/vizQuery/download`
- **Method:** POST
- **Content-Type:** application/json
- **Authentication:** Full browser `Cookie` header (multiple cookies, not just one)
- **Response:** Raw `.xlsx` file bytes (synchronous — no polling, the response body IS the file)
- **Timeout:** Some sheets take up to 60s for large datasets; script uses 120s timeout

### Payload Templates

The `payloads/` directory contains 26 JSON files — one per spreadsheet. Each is a complete POST body captured from the browser's Network tab. These are large (500–1800 lines each) and define the sheet structure, columns, filters, and query parameters.

**The 26 sheets:**

| Filename | User ID Field |
|----------|--------------|
| `CP_summary.json` | `user_id` |
| `Device Analysis Summary.json` | `user_id` |
| `IP Country Used.json` | `user_id` |
| `InboundOutbound_Summary.json` | `major_user_id` |
| `InboundOutbound_count_summary.json` | `major_user_id` |
| `Lifetime Block-Unblock Details.json` | `user_id` |
| `Lifetime CTM Alerts Details.json` | `major_user_id` |
| `Lifetime FTM Alerts Details.json` | `user_id` |
| `Lifetime Failed Fiat Deposit Transaction Details.json` | `major_user_id` |
| `Lifetime RFI Details.json` | `user_id` |
| `Lifetime SAR Alerted User Device Analysis.json` | `user_id` |
| `Lifetime SAR Internal Transfer Direct Link User Details.json` | `user_id` |
| `Lifetime SAR Top 10 Binance Pay Direct Link User Details.json` | `user_id` |
| `Lifetime SAR Top 10 P2P Direct Link User Details.json` | `user_id` |
| `Lifetime Top 10 Address by Value.json` | `major_user_id` |
| `Lifetime Top 10 Exposed Address.json` | `major_user_id` |
| `Privacy Coin Breakdown.json` | `major_user_id` |
| `SAR Case Details.json` | `user_id` |
| `SAR Device Direct Link User Details based on Last 12 Months Login.json` | `user_id` |
| `device_summary.json` | `user_id` |
| `poa_link_summary.json` | `user_id` |
| `sar_360_trade_summary.json` | `user_id` |
| `user_info.json` | `user_id` |
| `user_info_2.json` | `user_id` |
| `user_info_codex.json` | `user_id` |
| `user_info_fiat_partners.json` | `user_id` |

### User ID Replacement

Each payload contains a template user ID in two locations:
1. `query.whereList` — an entry with `"op": "in"` and `"val": ["<template_uid>"]`
2. `schema.whereList` — mirror of the same filter

The script extracts the template UID from each file individually (important: `user_info.json` was captured with UID `10091951`, all others with `466492707`). It then does a string replacement on the serialised JSON, swapping `"<template_uid>"` → `"<target_uid>"`. This catches both occurrences cleanly.

The user ID field name is either `user_id` or `major_user_id` depending on the sheet's dataset. The script identifies the field by checking `query.whereList` entries where `name` is in `{"user_id", "major_user_id"}` and `op` is `"in"`.

### Report Name Update

Each payload has `downloadConfig.reportName` set to something like `"user_info_1-2026-03-11 08-08-18.xlsx"`. The script replaces this with `"{sheet_name}_{user_id}.xlsx"`.

### Cookie Authentication

The server requires the full browser `Cookie` header — multiple cookies separated by semicolons. The script passes it as-is in the `Cookie` header. It is NOT a single named cookie. Typical value:

```
login_type=SAML2; sessionid=abc123; session=eyJ...; sensorsdata2015jssdkcross=...
```

Session cookies expire (duration unknown — works while the browser session is active).

## Core Functions to Reuse

The script (`c360_download.py`) has four functions that can be extracted into a backend module:

### `extract_template_uid(payload: dict) -> str | None`
Parses `query.whereList` to find and return the template user ID from a payload. Returns `None` if not found.

### `prepare_payload(payload: dict, template_uid: str, target_uid: str, sheet_name: str) -> dict`
Takes a loaded payload template, swaps the user ID everywhere via string replacement, and updates the `reportName`. Returns a ready-to-POST dict.

### `discover_payloads() -> list[Path]`
Finds all `.json` files in the payloads directory. For integration, this would need to be parameterised to accept a directory path.

### The download logic (inline in `main()`)
POSTs the prepared payload with the cookie header. Validates HTTP 200 + `PK` magic bytes. Saves the `.xlsx` response.

## Integration Plan

### What the backend endpoint needs to do

1. Accept a request with `user_id` (string) and `cookie` (string)
2. Load all 26 payload templates from a known directory
3. For each template: extract template UID → prepare payload → POST to C360 → validate → save `.xlsx`
4. Feed the saved `.xlsx` files into the existing spreadsheet ingestion pipeline
5. Return progress/status to the frontend

### Suggested backend endpoint

```
POST /api/c360/fetch
Body: { "user_id": "466492707", "cookie": "login_type=SAML2; sessionid=..." }
```

### Frontend needs

- A form with two fields: User ID input + Cookie textarea (cookie strings are long)
- A submit button that triggers the fetch
- Progress indicator (26 sheets, show which are downloading)
- Error display if the session is expired

### Key integration considerations

1. **The payloads directory** needs to be bundled with or accessible to the backend. The 26 JSON files are ~1.5 MB total. They should be treated as static assets — they don't change unless C360's dashboard schema changes.

2. **Session expiry detection:** If the first request fails (non-200 or non-xlsx response), abort immediately and tell the user to refresh their cookie. Don't burn time on the other 25.

3. **Sequential downloads are fine.** The C360 API doesn't seem to rate-limit, but there's no benefit to parallelising — total time is 2–5 minutes for all 26 sheets. If you want to show real-time progress on the frontend, consider using WebSocket or SSE to push status updates per sheet.

4. **The downloaded .xlsx files are identical** to what you get by clicking download in the browser. They can go straight into the existing spreadsheet ingestion pipeline with no modification.

5. **File naming:** The script saves files as `{sheet_name}_{user_id}.xlsx`. The sheet name comes from the JSON filename (minus `.json`). Some have spaces (e.g., `Device Analysis Summary_466492707.xlsx`). Your ingestion pipeline may need to handle this or you can normalise the names.

6. **No additional dependencies** beyond `requests` (which you likely already have in your FastAPI backend).

## Files in This Directory

```
c360-downloader/
├── c360_download.py              # The bulk download script (standalone CLI)
├── c360_download_test.py         # Original single-sheet test script
├── C360-DOWNLOADER-HANDOVER.md   # This document
├── REQUEST URL.md                # The captured API endpoint
├── SESSION COOKIE.md             # Example session cookie (expired)
├── payloads/                     # 26 JSON payload templates
│   ├── CP_summary.json
│   ├── Device Analysis Summary.json
│   ├── IP Country Used.json
│   ├── InboundOutbound_Summary.json
│   ├── InboundOutbound_count_summary.json
│   ├── Lifetime Block-Unblock Details.json
│   ├── Lifetime CTM Alerts Details.json
│   ├── Lifetime FTM Alerts Details.json
│   ├── Lifetime Failed Fiat Deposit Transaction Details.json
│   ├── Lifetime RFI Details.json
│   ├── Lifetime SAR Alerted User Device Analysis.json
│   ├── Lifetime SAR Internal Transfer Direct Link User Details.json
│   ├── Lifetime SAR Top 10 Binance Pay Direct Link User Details.json
│   ├── Lifetime SAR Top 10 P2P Direct Link User Details.json
│   ├── Lifetime Top 10 Address by Value.json
│   ├── Lifetime Top 10 Exposed Address.json
│   ├── Privacy Coin Breakdown.json
│   ├── SAR Case Details.json
│   ├── SAR Device Direct Link User Details based on Last 12 Months Login.json
│   ├── device_summary.json
│   ├── poa_link_summary.json
│   ├── sar_360_trade_summary.json
│   ├── user_info.json
│   ├── user_info_2.json
│   ├── user_info_codex.json
│   └── user_info_fiat_partners.json
└── downloads/                    # Output directory (created by script)
    └── <user_id>/                # One subfolder per user
        ├── CP_summary_<uid>.xlsx
        └── ... (26 files)
```

## What to Copy to the Main Project

1. **`payloads/` directory** — all 26 JSON files, unchanged
2. **The core logic from `c360_download.py`** — specifically `extract_template_uid()`, `prepare_payload()`, and the download/validation logic

The CLI wrapper (`main()`, `get_cookie_string()`, argument parsing) is not needed for backend integration — replace it with a FastAPI endpoint.
