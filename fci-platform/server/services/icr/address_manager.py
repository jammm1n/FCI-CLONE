"""
Address Manager for Elliptic workflow.

Handles:
  - Combining auto-extracted and manual addresses
  - Cross-referencing against UOL crypto transaction history
  - Generating narrative text for AI consumption
"""

from .utils import safe_str, fmt_usd


def build_address_list(session, manual_addresses=None):
    """
    Build a unified address list from auto-extracted and manual addresses,
    cross-referenced against UOL crypto transaction history.

    Args:
        session: The session dict containing detected_files and uol_data.
        manual_addresses: List of manually entered address strings (optional).

    Returns:
        Dict with:
          - addresses: list of enriched address dicts
          - narrative: str of cross-reference narrative text
          - stats: dict with summary counts
    """
    # 1. Gather auto-extracted addresses from session
    auto_addresses = session.get('elliptic_addresses', {})

    # 2. Add manual addresses
    manual_addresses = manual_addresses or []
    for addr_str in manual_addresses:
        addr_clean = safe_str(addr_str)
        if not addr_clean:
            continue
        if addr_clean not in auto_addresses:
            auto_addresses[addr_clean] = {
                'address': addr_clean,
                'sources': ['Manual'],
            }
        else:
            if 'Manual' not in auto_addresses[addr_clean]['sources']:
                auto_addresses[addr_clean]['sources'].append('Manual')

    # 3. Get UOL crypto data
    uol_data = session.get('uol_data') or {}
    crypto_withdrawals = uol_data.get('crypto_withdrawals', [])
    crypto_deposits = uol_data.get('crypto_deposits', [])
    attempted_withdrawals = uol_data.get('attempted_withdrawals', [])

    # 4. Build lookup indexes for fast matching
    withdrawal_index = {}
    for tx in crypto_withdrawals:
        dest = safe_str(tx.get('destination_address', '')).lower()
        if dest:
            if dest not in withdrawal_index:
                withdrawal_index[dest] = []
            withdrawal_index[dest].append(tx)

    deposit_index = {}
    for tx in crypto_deposits:
        source = safe_str(tx.get('source_address', '')).lower()
        deposit_addr = safe_str(tx.get('deposit_address', '')).lower()
        if source:
            if source not in deposit_index:
                deposit_index[source] = []
            deposit_index[source].append(tx)
        if deposit_addr and deposit_addr != source:
            if deposit_addr not in deposit_index:
                deposit_index[deposit_addr] = []
            deposit_index[deposit_addr].append(tx)

    attempted_index = {}
    for tx in attempted_withdrawals:
        addr = safe_str(tx.get('address', '')).lower()
        if addr:
            if addr not in attempted_index:
                attempted_index[addr] = []
            attempted_index[addr].append(tx)

    # 5. Cross-reference each address
    enriched = []
    for addr_key, addr_info in auto_addresses.items():
        addr_lower = addr_key.lower()

        withdrawal_matches = withdrawal_index.get(addr_lower, [])
        deposit_matches = deposit_index.get(addr_lower, [])
        attempted_matches = attempted_index.get(addr_lower, [])

        # Deduplicate deposit matches
        seen_tx_ids = set()
        unique_deposits = []
        for tx in deposit_matches:
            tx_id = tx.get('tx_id', '')
            dedup_key = tx_id if tx_id else '{}-{}-{}'.format(
                tx.get('create_time', ''),
                tx.get('currency', ''),
                tx.get('amount', ''),
            )
            if dedup_key not in seen_tx_ids:
                seen_tx_ids.add(dedup_key)
                unique_deposits.append(tx)

        has_uol_match = (len(withdrawal_matches) > 0
                         or len(unique_deposits) > 0
                         or len(attempted_matches) > 0)

        # Compute summary stats for this address
        w_total_usd = sum(tx.get('usdt_value', 0) for tx in withdrawal_matches)
        d_total_usd = sum(tx.get('usdt_value', 0) for tx in unique_deposits)
        a_total_usd = sum(tx.get('usdt_value', 0) for tx in attempted_matches)

        w_networks = sorted(set(
            safe_str(tx.get('network', '')) for tx in withdrawal_matches
            if safe_str(tx.get('network', ''))
        ))
        d_networks = sorted(set(
            safe_str(tx.get('network', '')) for tx in unique_deposits
            if safe_str(tx.get('network', ''))
        ))
        a_networks = sorted(set(
            safe_str(tx.get('network', '')) for tx in attempted_matches
            if safe_str(tx.get('network', ''))
        ))

        w_dates = [safe_str(tx.get('apply_time', ''))[:10] for tx in withdrawal_matches
                    if safe_str(tx.get('apply_time', ''))]
        d_dates = [safe_str(tx.get('create_time', ''))[:10] for tx in unique_deposits
                    if safe_str(tx.get('create_time', ''))]
        a_dates = [safe_str(tx.get('date', ''))[:10] for tx in attempted_matches
                    if safe_str(tx.get('date', ''))]

        entry = {
            'address': addr_info['address'],
            'sources': addr_info['sources'],
            'has_uol_match': has_uol_match,
            'withdrawal_count': len(withdrawal_matches),
            'deposit_count': len(unique_deposits),
            'attempted_withdrawal_count': len(attempted_matches),
            'withdrawal_total_usd': w_total_usd,
            'deposit_total_usd': d_total_usd,
            'attempted_withdrawal_total_usd': a_total_usd,
            'withdrawal_networks': w_networks,
            'deposit_networks': d_networks,
            'attempted_withdrawal_networks': a_networks,
            'withdrawal_date_range': _date_range(w_dates),
            'deposit_date_range': _date_range(d_dates),
            'attempted_withdrawal_date_range': _date_range(a_dates),
            'withdrawals': _format_withdrawal_matches(withdrawal_matches),
            'deposits': _format_deposit_matches(unique_deposits),
            'attempted_withdrawals': _format_attempted_withdrawal_matches(attempted_matches),
        }
        enriched.append(entry)

    # 6. Sort: UOL matches first, then alphabetical
    enriched.sort(key=lambda x: (
        0 if x['has_uol_match'] else 1,
        x['address'].lower(),
    ))

    # 7. Generate narrative
    has_uol = (len(crypto_withdrawals) > 0
               or len(crypto_deposits) > 0
               or len(attempted_withdrawals) > 0)
    narrative = _generate_narrative(
        enriched, has_uol,
        len(crypto_withdrawals), len(crypto_deposits), len(attempted_withdrawals),
    )

    # 8. Stats
    total = len(enriched)
    matched = sum(1 for e in enriched if e['has_uol_match'])
    stats = {
        'total_addresses': total,
        'uol_matched': matched,
        'uol_unmatched': total - matched,
        'uol_available': has_uol,
        'uol_withdrawal_count': len(crypto_withdrawals),
        'uol_deposit_count': len(crypto_deposits),
        'uol_attempted_withdrawal_count': len(attempted_withdrawals),
    }

    return {
        'addresses': enriched,
        'narrative': narrative,
        'stats': stats,
    }


def _date_range(date_strings):
    """Return (earliest, latest) from a list of date strings, or None."""
    filtered = [d for d in date_strings if d]
    if not filtered:
        return None
    filtered.sort()
    if filtered[0] == filtered[-1]:
        return filtered[0]
    return '{} to {}'.format(filtered[0], filtered[-1])


def _format_withdrawal_matches(matches):
    """Format withdrawal transaction matches for response."""
    formatted = []
    for tx in matches:
        formatted.append({
            'date': tx.get('apply_time', ''),
            'currency': tx.get('currency', ''),
            'amount': tx.get('amount', 0),
            'usdt_value': tx.get('usdt_value', 0),
            'network': tx.get('network', ''),
            'tx_id': tx.get('tx_id', ''),
            'status': tx.get('status', ''),
            'counterparty_id': tx.get('counterparty_id', ''),
            'destination_address': tx.get('destination_address', ''),
        })
    return formatted


def _format_deposit_matches(matches):
    """Format deposit transaction matches for response."""
    formatted = []
    for tx in matches:
        formatted.append({
            'date': tx.get('create_time', ''),
            'currency': tx.get('currency', ''),
            'amount': tx.get('amount', 0),
            'usdt_value': tx.get('usdt_value', 0),
            'network': tx.get('network', ''),
            'tx_id': tx.get('tx_id', ''),
            'status': tx.get('status', ''),
            'counterparty_id': tx.get('counterparty_id', ''),
            'source_address': tx.get('source_address', ''),
            'deposit_address': tx.get('deposit_address', ''),
        })
    return formatted


def _format_attempted_withdrawal_matches(matches):
    """Format attempted withdrawal transaction matches for response."""
    formatted = []
    for tx in matches:
        formatted.append({
            'date': tx.get('date', ''),
            'currency': tx.get('currency', ''),
            'amount': tx.get('amount', 0),
            'usdt_value': tx.get('usdt_value', 0),
            'network': tx.get('network', ''),
            'address': tx.get('address', ''),
            'business_type': tx.get('business_type', ''),
            'source': tx.get('source', ''),
        })
    return formatted


# ── Narrative constants ────────────────────────────────────────

# When an address has more than this many transactions in one
# direction, show the first N and last N with a summary in between.
DETAIL_THRESHOLD = 10
DETAIL_HEAD = 5
DETAIL_TAIL = 3


def _generate_narrative(enriched, has_uol, total_withdrawals, total_deposits,
                        total_attempted_withdrawals=0):
    """
    Generate a structured narrative of UOL cross-reference findings.
    This text feeds an AI system for case assessment.

    Format:
      - Summary header with UOL stats
      - Per-address summary line (count, total USD, date range, networks)
      - Condensed transaction lines (capped for high-count addresses)
      - Explicit statement for addresses not found in UOL
    """
    lines = []
    lines.append('=== UOL CRYPTO TRANSACTION CROSS-REFERENCE ===')
    lines.append('')

    if not has_uol:
        lines.append('No UOL file was uploaded, or the UOL did not contain crypto')
        lines.append('Withdrawal History / Deposit History tabs.')
        lines.append('Cross-referencing could not be performed.')
        lines.append('')
        lines.append('Addresses extracted from C360 spreadsheets:')
        for entry in enriched:
            source_str = ', '.join(entry['sources'])
            lines.append('  - {} (source: {})'.format(entry['address'], source_str))
        return '\n'.join(lines)

    uol_parts = ['{} crypto withdrawal(s)'.format(total_withdrawals),
                  '{} crypto deposit(s)'.format(total_deposits)]
    if total_attempted_withdrawals:
        uol_parts.append('{} attempted withdrawal(s)'.format(total_attempted_withdrawals))
    lines.append('UOL data: {}'.format(', '.join(uol_parts)))
    lines.append('')

    matched = [e for e in enriched if e['has_uol_match']]
    unmatched = [e for e in enriched if not e['has_uol_match']]

    lines.append('Addresses analysed: {} | Found in UOL: {} | Not found: {}'.format(
        len(enriched), len(matched), len(unmatched)))
    lines.append('')

    # ── Matched addresses ──────────────────────────────────────
    if matched:
        lines.append('--- ADDRESSES FOUND IN UOL ---')
        lines.append('')

        for entry in matched:
            source_str = ', '.join(entry['sources'])
            lines.append('ADDRESS: {} [{}]'.format(entry['address'], source_str))

            # Summary line
            summary_parts = []
            if entry['withdrawal_count'] > 0:
                summary_parts.append('{} withdrawal(s) totalling {} ({}, {})'.format(
                    entry['withdrawal_count'],
                    fmt_usd(entry['withdrawal_total_usd']),
                    ', '.join(entry['withdrawal_networks']) or 'N/A',
                    entry['withdrawal_date_range'] or 'N/A',
                ))
            if entry['deposit_count'] > 0:
                summary_parts.append('{} deposit(s) totalling {} ({}, {})'.format(
                    entry['deposit_count'],
                    fmt_usd(entry['deposit_total_usd']),
                    ', '.join(entry['deposit_networks']) or 'N/A',
                    entry['deposit_date_range'] or 'N/A',
                ))
            if entry.get('attempted_withdrawal_count', 0) > 0:
                summary_parts.append('{} attempted withdrawal(s) totalling {} ({}, {})'.format(
                    entry['attempted_withdrawal_count'],
                    fmt_usd(entry['attempted_withdrawal_total_usd']),
                    ', '.join(entry['attempted_withdrawal_networks']) or 'N/A',
                    entry['attempted_withdrawal_date_range'] or 'N/A',
                ))
            for part in summary_parts:
                lines.append('  ' + part)

            # Withdrawal detail
            if entry['withdrawals']:
                lines.append('  Withdrawals TO this address:')
                _append_tx_lines(lines, entry['withdrawals'], 'W', _fmt_withdrawal_line)

            # Deposit detail
            if entry['deposits']:
                lines.append('  Deposits FROM this address:')
                _append_tx_lines(lines, entry['deposits'], 'D', _fmt_deposit_line)

            # Attempted withdrawal detail
            if entry.get('attempted_withdrawals'):
                lines.append('  Attempted Withdrawals TO this address:')
                _append_tx_lines(lines, entry['attempted_withdrawals'], 'A', _fmt_attempted_withdrawal_line)

            lines.append('')

    # ── Unmatched addresses ────────────────────────────────────
    if unmatched:
        lines.append('--- ADDRESSES NOT FOUND IN UOL ---')
        lines.append('')
        for entry in unmatched:
            source_str = ', '.join(entry['sources'])
            lines.append('{} [{}] — not in UOL withdrawal, deposit, or attempted withdrawal history'.format(
                entry['address'], source_str))
        lines.append('')

    return '\n'.join(lines)


def _append_tx_lines(lines, transactions, prefix, formatter):
    """
    Append transaction detail lines with capping for high-count addresses.
    Shows all if <= DETAIL_THRESHOLD, otherwise head + summary + tail.
    """
    count = len(transactions)
    if count <= DETAIL_THRESHOLD:
        for i, tx in enumerate(transactions, 1):
            lines.append('    [{}{}] {}'.format(prefix, i, formatter(tx)))
    else:
        # Show first N
        for i in range(DETAIL_HEAD):
            lines.append('    [{}{}] {}'.format(prefix, i + 1, formatter(transactions[i])))
        # Summary of skipped
        skipped = count - DETAIL_HEAD - DETAIL_TAIL
        lines.append('    ... {} more transaction(s) ...'.format(skipped))
        # Show last N
        for i in range(count - DETAIL_TAIL, count):
            lines.append('    [{}{}] {}'.format(prefix, i + 1, formatter(transactions[i])))


def _fmt_withdrawal_line(tx):
    """Format a single withdrawal transaction as a concise one-liner."""
    parts = []
    parts.append(tx.get('date', 'N/A')[:19])
    parts.append(tx.get('currency', ''))
    parts.append(str(tx.get('amount', 0)))
    usdt = tx.get('usdt_value', 0)
    if usdt:
        parts.append(fmt_usd(usdt))
    parts.append(tx.get('network', ''))
    parts.append(tx.get('status', ''))
    tx_id = tx.get('tx_id', '')
    if tx_id:
        parts.append(tx_id)
    cp = tx.get('counterparty_id', '')
    if cp:
        parts.append('CP:{}'.format(cp))
    return ' | '.join(p for p in parts if p)


def _fmt_deposit_line(tx):
    """Format a single deposit transaction as a concise one-liner."""
    parts = []
    parts.append(tx.get('date', 'N/A')[:19])
    parts.append(tx.get('currency', ''))
    parts.append(str(tx.get('amount', 0)))
    usdt = tx.get('usdt_value', 0)
    if usdt:
        parts.append(fmt_usd(usdt))
    parts.append(tx.get('network', ''))
    parts.append(tx.get('status', ''))
    tx_id = tx.get('tx_id', '')
    if tx_id:
        parts.append(tx_id)
    cp = tx.get('counterparty_id', '')
    if cp:
        parts.append('CP:{}'.format(cp))
    return ' | '.join(p for p in parts if p)


def _fmt_attempted_withdrawal_line(tx):
    """Format a single attempted withdrawal transaction as a concise one-liner."""
    parts = []
    parts.append(tx.get('date', 'N/A')[:19])
    parts.append(tx.get('currency', ''))
    parts.append(str(tx.get('amount', 0)))
    usdt = tx.get('usdt_value', 0)
    if usdt:
        parts.append(fmt_usd(usdt))
    parts.append(tx.get('network', ''))
    biz = tx.get('business_type', '')
    if biz:
        parts.append(biz)
    source = tx.get('source', '')
    if source:
        parts.append('src:{}'.format(source))
    return ' | '.join(p for p in parts if p)