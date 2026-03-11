"""
Constants used across ICR processors.
Rule codes, jurisdiction lists, file type definitions.
"""

import json
from pathlib import Path

_RULE_CODES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "rule_codes.json"

with open(_RULE_CODES_PATH, "r", encoding="utf-8") as _f:
    RULE_CODES = json.load(_f)

SANCTIONED_JURISDICTIONS = [
    'north korea', 'cuba', 'iran', 'crimea', 'donetsk', 'luhansk',
    'kp', 'cu', 'ir'
]

RESTRICTED_JURISDICTIONS = [
    'canada', 'netherlands', 'united states', 'us', 'usa',
    'belarus', 'russia', 'ca', 'nl', 'by', 'ru'
]


_UNKNOWN_RULE = {'name': 'Unknown', 'red_flag': '', 'platform': 'Unknown', 'status': 'Unknown'}


def lookup_rule_code(code):
    """Look up a rule code with fallback matching for dash/underscore variants."""
    if not code:
        return _UNKNOWN_RULE
    upper = safe_str_for_lookup(code)
    if upper in RULE_CODES:
        return RULE_CODES[upper]
    underscore_version = upper.replace('-', '_')
    if underscore_version in RULE_CODES:
        return RULE_CODES[underscore_version]
    dash_version = upper.replace('_', '-')
    if dash_version in RULE_CODES:
        return RULE_CODES[dash_version]
    return {**_UNKNOWN_RULE, 'name': code}


def safe_str_for_lookup(value):
    """Strip, uppercase, and remove trailing punctuation (e.g. '!') for constant lookups."""
    if value is None:
        return ''
    return str(value).strip().rstrip('!').strip().upper()