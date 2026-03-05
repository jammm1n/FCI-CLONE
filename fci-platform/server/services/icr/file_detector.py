"""
File type detection registry.
Each detection rule is a dict with a type, label, and match function.
To add a new file type, append one entry to DETECTION_RULES.
"""

from .utils import safe_str


DETECTION_RULES = [
    {
        'type': 'USER_INFO',
        'label': 'User Info',
        'match': lambda h, fn: 'nationality' in h and 'residency' in h and 'kyc risk' in h,
    },
    {
        'type': 'DEVICE_SUM',
        'label': 'Device Summary',
        'match': lambda h, fn: 'most_used_language' in h and 'vpn_usage_pct' in h,
    },
    {
        'type': 'DEVICE_MAIN',
        'label': 'Device Analysis',
        'match': lambda h, fn: (
            'fvideo_id/bnc_uuid' in h
            or ('vpn_used_count' in h and 'operation_count' in h)
        ),
    },
    {
        'type': 'FAILED_FIAT',
        'label': 'Failed Fiat',
        'match': lambda h, fn: 'error_reason' in h and 'fiat_channel' in h,
    },
    {
        'type': 'ADDR_EXPOSED',
        'label': 'Exposed Addresses',
        'match': lambda h, fn: (
            'address' in h and 'sum_amt_usd' in h and 'direction' in h
            and 'exposed' in fn
        ),
    },
    {
        'type': 'ADDR_VALUE',
        'label': 'Top 10 by Value',
        'match': lambda h, fn: (
            'address' in h and 'sum_amt_usd' in h and 'direction' in h
            and ('value' in fn or 'major_user_id' in h)
        ),
    },
    {
        # Fallback for address files that don't match exposed or value by filename
        'type': 'ADDR_EXPOSED',
        'label': 'Exposed Addresses',
        'match': lambda h, fn: 'address' in h and 'sum_amt_usd' in h and 'direction' in h,
    },
    {
        'type': 'IT',
        'label': 'Internal Transfer',
        'match': lambda h, fn: 'total_internal_crypto_trans_amt_usd' in h,
    },
    {
        'type': 'BP',
        'label': 'Binance Pay',
        'match': lambda h, fn: 'total_bpay_trans_amt_usd' in h,
    },
    {
        'type': 'P2P',
        'label': 'P2P',
        'match': lambda h, fn: 'total_p2p_trans_amt_usd' in h,
    },
    {
        'type': 'DEVICE_LINK',
        'label': 'Device Direct Link',
        'match': lambda h, fn: (
            'link_user_id' in h and 'direct_shared_bnc_uuid' in h
            and 'total_internal_crypto_trans_amt_usd' not in h
            and 'total_bpay_trans_amt_usd' not in h
            and 'total_p2p_trans_amt_usd' not in h
        ),
    },
    {
        'type': 'CTM_ALERTS',
        'label': 'CTM Alerts',
        'match': lambda h, fn: (
            'case_no' in h and 'category_group' in h and 'elliptic_risk_score' in h
        ),
    },
    {
        'type': 'FTM_ALERTS',
        'label': 'FTM Alerts',
        'match': lambda h, fn: (
            'tx_date_time' in h and 'rule_code' in h and 'token_amount' in h
        ),
    },
    {
        'type': 'BLOCKS',
        'label': 'Block/Unblock Details',
        'match': lambda h, fn: (
            'block_type' in h and 'block_status' in h and 'case_create_datetime' in h
        ),
    },
    {
        'type': 'IO_SUMMARY',
        'label': 'Inbound/Outbound Summary',
        'match': lambda h, fn: (
            'total crypto deposit amount' in h and 'total fiat deposit amount' in h
        ),
    },
    {
        'type': 'IO_COUNT',
        'label': 'Inbound/Outbound Count',
        'match': lambda h, fn: (
            'total crypto deposit count' in h and 'total fiat deposit count' in h
        ),
    },
    {
        'type': 'TRADE_SUMMARY',
        'label': 'Trade Summary',
        'match': lambda h, fn: (
            'trade type' in h and 'amt_usd' in h and 'trade_count' in h
        ),
    },
    {
        'type': 'USER_INFO_2',
        'label': 'User Info (Extended)',
        'match': lambda h, fn: (
            'ftm open case count' in h and 'last active time' in h
        ),
    },
    {
        'type': 'USER_INFO_FIAT_PARTNERS',
        'label': 'User Info (Fiat Partners)',
        'match': lambda h, fn: (
            'fiat partner' in h and 'ip location used' in h
        ),
    },
    {
        'type': 'IP_COUNTRY',
        'label': 'IP Country Used',
        'match': lambda h, fn: (
            'ip country used' in h and len(h) == 1
        ),
    },
    {
        'type': 'CP_SUMMARY',
        'label': 'Internal Transfer User Summary',
        'match': lambda h, fn: (
            'internal cp user count' in h
            and 'internal cp users total deposit amount' in h
        ),
    },
    {
        'type': 'DEVICE_LINK_SUMMARY',
        'label': 'Device Link Summary',
        'match': lambda h, fn: (
            'device linked user count' in h
            and 'device linked users total deposit amount' in h
        ),
    },
    {
        'type': 'PRIVACY_COIN',
        'label': 'Privacy Coin Breakdown',
        'match': lambda h, fn: (
            'token' in h and 'tx_amt_usd' in h and 'direction' in h
            and 'network' in h and 'privacy' in fn.lower()
        ),
    },
]


def detect_file_type(headers, filename):
    """
    Match headers against detection rules.
    Returns (type_key, label) or (None, None) if no match.
    Rules are evaluated in order — first match wins.
    """
    h = [safe_str(x).lower() for x in headers]
    fn = (filename or '').lower()

    for rule in DETECTION_RULES:
        if rule['match'](h, fn):
            return rule['type'], rule['label']

    return None, None


def classify_files(parsed_files):
    """
    Classify a list of parsed file results into detected and undetected.
    UOL files are handled separately (they have is_uol=True from the parser).

    Returns:
        detected: dict keyed by file type
        undetected: list of unrecognised files
        uol_data: UOL data dict or None
    """
    detected = {}
    undetected = []
    uol_data = None

    for parsed in parsed_files:
        # UOL files are pre-identified by the parser
        if parsed.get('is_uol'):
            uol_data = {
                'customer_info': parsed.get('customer_info'),
                'fiat_deposits': parsed.get('fiat_deposits', []),
                'fiat_withdrawals': parsed.get('fiat_withdrawals', []),
                'crypto_withdrawals': parsed.get('crypto_withdrawals', []),
                'crypto_deposits': parsed.get('crypto_deposits', []),
                'binance_pay': parsed.get('binance_pay', []),
                'p2p_transactions': parsed.get('p2p_transactions', []),
                'sheet_names': parsed.get('sheet_names', []),
            }
            continue

        # Skip files that had parse errors
        if parsed.get('error'):
            undetected.append({
                'filename': parsed['filename'],
                'headers': [],
                'rows': [],
                'row_count': 0,
                'col_count': 0,
                'error': parsed['error'],
            })
            continue

        headers = parsed.get('headers', [])
        filename = parsed.get('filename', '')
        rows = parsed.get('rows', [])

        file_type, label = detect_file_type(headers, filename)

        if file_type:
            detected[file_type] = {
                'filename': filename,
                'label': label,
                'headers': headers,
                'rows': rows,
                'row_count': len(rows),
            }
        else:
            undetected.append({
                'filename': filename,
                'headers': headers,
                'rows': rows,
                'row_count': len(rows),
                'col_count': len(headers),
            })

    return detected, undetected, uol_data