"""
Data Health Check for uploaded spreadsheets.

Runs after parsing to detect structural changes in UOL
and C360 files that could cause silent data loss.

Returns a list of warning dicts, each with:
  - level: 'warning' or 'info'
  - source: 'UOL' or 'C360'
  - message: human-readable description
"""

from .utils import safe_str
from .processor_registry import discover_processors


# Expected UOL tabs and what a successful parse looks like
UOL_TAB_CHECKS = [
    {
        'sheet_name': 'customer information',
        'data_key': 'customer_info',
        'label': 'Customer Information',
        'check_type': 'not_none',
    },
    {
        'sheet_name': 'fiat deposit history',
        'data_key': 'fiat_deposits',
        'label': 'Fiat Deposit History',
        'check_type': 'has_rows',
        'critical_fields': ['status', 'date', 'currency', 'amount'],
    },
    {
        'sheet_name': 'fiat withdrawal history',
        'data_key': 'fiat_withdrawals',
        'label': 'Fiat Withdrawal History',
        'check_type': 'has_rows',
        'critical_fields': ['status', 'date', 'currency', 'amount'],
    },
    {
        'sheet_name': 'withdrawal history',
        'data_key': 'crypto_withdrawals',
        'label': 'Withdrawal History (crypto)',
        'check_type': 'has_rows',
        'critical_fields': ['destination_address', 'currency', 'amount', 'usdt_value', 'network', 'tx_id'],
    },
    {
        'sheet_name': 'deposit history',
        'data_key': 'crypto_deposits',
        'label': 'Deposit History (crypto)',
        'check_type': 'has_rows',
        'critical_fields': ['source_address', 'deposit_address', 'currency', 'amount', 'usdt_value', 'network', 'tx_id'],
    },
]


def run_health_check(detected_files, undetected_files, uol_data):
    """
    Check parsed data for signs of structural changes.

    Args:
        detected_files: dict of detected C360 files keyed by type
        undetected_files: list of unrecognised file dicts
        uol_data: parsed UOL data dict or None

    Returns:
        List of warning dicts. Empty list = all healthy.
    """
    warnings = []

    if uol_data:
        warnings.extend(_check_uol(uol_data))

    warnings.extend(_check_c360(detected_files, undetected_files))

    return warnings


def _check_uol(uol_data):
    """Run all UOL health checks."""
    warnings = []
    sheet_names = [n.lower().strip() for n in uol_data.get('sheet_names', [])]

    for check in UOL_TAB_CHECKS:
        tab_exists = check['sheet_name'] in sheet_names

        if not tab_exists:
            if check['sheet_name'] in ('customer information',):
                warnings.append({
                    'level': 'warning',
                    'source': 'UOL',
                    'message': '"{}" tab not found in UOL workbook. '
                               'Available tabs: {}'.format(
                                   check['label'],
                                   ', '.join(uol_data.get('sheet_names', [])),
                               ),
                })
            continue

        data = uol_data.get(check['data_key'])

        # Check 1: Did parsing return anything?
        if check['check_type'] == 'not_none':
            if data is None:
                warnings.append({
                    'level': 'warning',
                    'source': 'UOL',
                    'message': '"{}" tab found but could not be parsed. '
                               'Column structure may have changed.'.format(
                                   check['label']),
                })

        elif check['check_type'] == 'has_rows':
            if data is None or (isinstance(data, list) and len(data) == 0):
                warnings.append({
                    'level': 'warning',
                    'source': 'UOL',
                    'message': '"{}" tab found but 0 records parsed. '
                               'Column headers may have changed. '
                               'Verify data manually.'.format(
                                   check['label']),
                })
                continue

            # Check 2: Did critical columns actually have data?
            critical_fields = check.get('critical_fields', [])
            if critical_fields and isinstance(data, list) and len(data) > 0:
                empty_fields = _find_empty_critical_fields(data, critical_fields)
                if empty_fields:
                    warnings.append({
                        'level': 'warning',
                        'source': 'UOL',
                        'message': '"{}" tab parsed {} record(s) but column(s) '
                                   '{} are empty in ALL records. These columns '
                                   'may have been renamed or removed.'.format(
                                       check['label'],
                                       len(data),
                                       ', '.join('"{}"'.format(f) for f in empty_fields),
                                   ),
                    })

    return warnings


def _find_empty_critical_fields(records, field_names):
    """
    Check which critical fields are empty across ALL records.

    A string field is empty if every record has '' or None.
    A numeric field is suspicious if every record has 0 (the default
    when safe_float/safe_int can't find the column).

    Returns list of field names that appear to be missing.
    """
    empty_fields = []

    for field in field_names:
        has_real_value = False

        for record in records:
            value = record.get(field)

            if value is None:
                continue

            if isinstance(value, str):
                if value.strip() != '':
                    has_real_value = True
                    break
                continue

            if isinstance(value, (int, float)):
                if value != 0:
                    has_real_value = True
                    break
                continue

            if value:
                has_real_value = True
                break

        if not has_real_value:
            empty_fields.append(field)

    return empty_fields


def _check_c360(detected_files, undetected_files):
    """Run all C360 health checks."""
    warnings = []

    # ── Check undetected files ─────────────────────────────────
    for uf in (undetected_files or []):
        row_count = uf.get('row_count', 0)
        col_count = uf.get('col_count', 0)
        filename = uf.get('filename', 'Unknown')
        error = uf.get('error', '')

        if error:
            warnings.append({
                'level': 'warning',
                'source': 'C360',
                'message': '"{}" could not be read: {}'.format(filename, error),
            })
        elif col_count > 3 and row_count > 0:
            warnings.append({
                'level': 'warning',
                'source': 'C360',
                'message': '"{}" ({} rows, {} columns) was not recognised. '
                           'C360 export format may have changed.'.format(
                               filename, row_count, col_count),
            })

    # ── Check detected files with zero rows ────────────────────
    for file_type, data in (detected_files or {}).items():
        if data.get('row_count', 0) == 0:
            warnings.append({
                'level': 'warning',
                'source': 'C360',
                'message': '"{}" detected as {} but contains 0 data rows.'.format(
                    data.get('filename', 'Unknown'),
                    data.get('label', file_type),
                ),
            })

    # ── Check detected files for missing expected columns ──────
    expected_columns = _build_expected_columns()

    for file_type, data in (detected_files or {}).items():
        if file_type not in expected_columns:
            continue

        actual_headers = set(
            safe_str(h).lower() for h in data.get('headers', [])
        )

        if not actual_headers:
            continue

        expected = expected_columns[file_type]
        missing = []
        for col in expected:
            if col.lower() not in actual_headers:
                missing.append(col)

        if missing:
            warnings.append({
                'level': 'warning',
                'source': 'C360',
                'message': '"{}" detected as {} but is missing expected column(s): {}. '
                           'C360 export format may have changed.'.format(
                               data.get('filename', 'Unknown'),
                               data.get('label', file_type),
                               ', '.join('"{}"'.format(c) for c in missing),
                           ),
            })

    return warnings


def _build_expected_columns():
    """
    Build a map of file_type -> set of expected column names
    from all processor consumed_fields declarations.

    This means any column a processor reads will be checked
    against what's actually in the uploaded file headers.
    """
    processors = discover_processors()
    expected = {}

    for processor in processors:
        if not processor.consumed_fields:
            continue
        for file_type, columns in processor.consumed_fields.items():
            if file_type not in expected:
                expected[file_type] = set()
            for col in columns:
                expected[file_type].add(col)

    return expected