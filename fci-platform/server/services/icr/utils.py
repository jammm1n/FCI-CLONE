"""
Utility functions for data parsing and formatting.
All processors use these for consistent data handling.
"""


def safe_float(value):
    """Safely convert any value to float. Returns 0.0 on failure."""
    if value is None or value == '' or value == '(null)':
        return 0.0
    try:
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return 0.0


def safe_int(value):
    """Safely convert any value to int. Returns 0 on failure."""
    if value is None or value == '' or value == '(null)':
        return 0
    try:
        return int(float(str(value).replace(',', '')))
    except (ValueError, TypeError):
        return 0


def safe_str(value):
    """Safely convert any value to stripped string."""
    if value is None:
        return ''
    return str(value).strip()


def safe_bool(value):
    """Safely convert any value to boolean."""
    if isinstance(value, bool):
        return value
    s = safe_str(value).lower()
    return s == 'true'


def parse_array(value):
    """
    Parse a string representation of an array into a Python list.

    Handles formats like:
      ['item1', 'item2']
      [item1, item2]
      item1
      (null)
      []
    """
    import json

    s = safe_str(value)
    if not s or s == '[]' or s == '(null)':
        return []

    # Try JSON parse with normalised quotes
    normalised = s.replace("'", '"')
    try:
        parsed = json.loads(normalised)
        if isinstance(parsed, list):
            return [safe_str(item) for item in parsed]
    except (json.JSONDecodeError, TypeError):
        pass

    # Manual parse for bracket-wrapped content
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1].strip()
        if not s:
            return []
        results = []
        current = ''
        in_quote = False
        quote_char = ''
        for ch in s:
            if not in_quote and ch in ('"', "'"):
                in_quote = True
                quote_char = ch
            elif in_quote and ch == quote_char:
                in_quote = False
            elif not in_quote and ch == ',':
                trimmed = current.strip()
                if trimmed:
                    results.append(trimmed)
                current = ''
            else:
                current += ch
        last = current.strip()
        if last:
            results.append(last)
        return results

    # Single value
    return [s] if s else []


def fmt_usd(n):
    """Format a number as USD string: $1,234.56"""
    return '${:,.2f}'.format(n)


def fmt_pct(n):
    """Format a decimal as percentage string: 12.34%"""
    return '{:.2f}%'.format(n * 100)


def fmt_pct_display(decimal_value):
    """
    Format percentage for display, showing '<0.1%' for very small values.
    Input is a decimal (0.0005 = 0.05%).
    """
    if decimal_value <= 0:
        return None
    pct = decimal_value * 100
    if pct < 0.1:
        return '<0.1%'
    return '{:.1f}%'.format(pct)


def extract_block_reasons(block_details):
    """
    Extract human-readable block reasons from block_case_details entries.
    Each entry is formatted as: part1->part2->part3->reason->remark
    """
    reasons = []
    for entry in block_details:
        parts = entry.split('->')
        if len(parts) >= 5:
            reason = parts[3].strip()
            remark = parts[4].strip()
            if reason and reason != 'empty block reason':
                display = reason
                if remark and remark != 'empty block remark':
                    display += ' (' + remark + ')'
                if display not in reasons:
                    reasons.append(display)
    return reasons