"""
Associated UID Search.

Searches UOL transaction tabs (Crypto Withdrawals, Crypto Deposits,
Binance Pay, P2P) for transactions involving specified counterparty UIDs.
Used to find links between the subject and victims or co-suspects.
"""

from .utils import safe_str, safe_float, fmt_usd


def search_associated_uids(session, uids):
    """
    Search UOL data for transactions involving the given UIDs.

    Args:
        session: Session dict containing uol_data.
        uids: List of UID strings to search for.

    Returns:
        Dict with:
          - results: dict keyed by UID, each containing matched transactions
          - narrative: formatted text output
          - stats: summary counts
    """
    uol_data = session.get('uol_data') or {}
    subject_uid = session.get('subject_uid', '')

    crypto_withdrawals = uol_data.get('crypto_withdrawals', [])
    crypto_deposits = uol_data.get('crypto_deposits', [])
    binance_pay = uol_data.get('binance_pay', [])
    p2p_transactions = uol_data.get('p2p_transactions', [])

    # Normalise search UIDs — strip whitespace, reject empties
    uid_set = set()
    for uid in uids:
        cleaned = safe_str(uid).strip()
        if cleaned:
            uid_set.add(cleaned)

    if not uid_set:
        return {
            'results': {},
            'narrative': 'No UIDs provided for search.',
            'stats': {'uids_searched': 0, 'uids_found': 0, 'total_matches': 0},
        }

    # Initialise result buckets per UID
    results = {}
    for uid in uid_set:
        results[uid] = {
            'uid': uid,
            'crypto_withdrawals': [],
            'crypto_deposits': [],
            'binance_pay': [],
            'p2p_transactions': [],
        }

    # Search crypto withdrawals — match on counterparty_id
    for tx in crypto_withdrawals:
        cp = safe_str(tx.get('counterparty_id', ''))
        if cp in uid_set:
            results[cp]['crypto_withdrawals'].append(tx)

    # Search crypto deposits — match on counterparty_id
    for tx in crypto_deposits:
        cp = safe_str(tx.get('counterparty_id', ''))
        if cp in uid_set:
            results[cp]['crypto_deposits'].append(tx)

    # Search Binance Pay — match on counterparty_binance_id
    for tx in binance_pay:
        cp = safe_str(tx.get('counterparty_binance_id', ''))
        if cp in uid_set:
            results[cp]['binance_pay'].append(tx)

    # Search P2P — match on taker_id OR ad_publisher_id
    # A row could match different UIDs on each column, so check both
    for tx in p2p_transactions:
        taker = safe_str(tx.get('taker_id', ''))
        publisher = safe_str(tx.get('ad_publisher_id', ''))
        matched = set()
        if taker in uid_set:
            matched.add(taker)
        if publisher in uid_set:
            matched.add(publisher)
        for matched_uid in matched:
            results[matched_uid]['p2p_transactions'].append(tx)

    # Build stats
    uids_found = 0
    total_matches = 0
    for uid, data in results.items():
        count = (len(data['crypto_withdrawals']) + len(data['crypto_deposits'])
                 + len(data['binance_pay']) + len(data['p2p_transactions']))
        if count > 0:
            uids_found += 1
        total_matches += count

    stats = {
        'uids_searched': len(uid_set),
        'uids_found': uids_found,
        'total_matches': total_matches,
        'tabs_available': {
            'crypto_withdrawals': len(crypto_withdrawals),
            'crypto_deposits': len(crypto_deposits),
            'binance_pay': len(binance_pay),
            'p2p_transactions': len(p2p_transactions),
        },
    }

    narrative = _generate_narrative(results, stats, subject_uid)

    return {
        'results': results,
        'narrative': narrative,
        'stats': stats,
    }


def _generate_narrative(results, stats, subject_uid):
    """Generate formatted text output of UID search results."""
    lines = []
    lines.append('=== ASSOCIATED UID SEARCH RESULTS ===')
    lines.append('')
    lines.append('Subject UID: {}'.format(subject_uid))
    lines.append('UIDs searched: {}'.format(stats['uids_searched']))
    lines.append('UIDs with matches: {}'.format(stats['uids_found']))
    lines.append('Total matching transactions: {}'.format(stats['total_matches']))
    lines.append('')

    tabs = stats['tabs_available']
    lines.append('UOL tabs searched:')
    lines.append('  Crypto Withdrawals: {} rows'.format(tabs['crypto_withdrawals']))
    lines.append('  Crypto Deposits: {} rows'.format(tabs['crypto_deposits']))
    lines.append('  Binance Pay: {} rows'.format(tabs['binance_pay']))
    lines.append('  P2P: {} rows'.format(tabs['p2p_transactions']))

    if tabs['binance_pay'] == 0 and tabs['p2p_transactions'] == 0:
        lines.append('')
        lines.append('NOTE: Binance Pay and P2P tabs were not found in the UOL.')
        lines.append('Only crypto withdrawal/deposit history was searched.')

    lines.append('')

    for uid in sorted(results.keys()):
        data = results[uid]
        total = (len(data['crypto_withdrawals']) + len(data['crypto_deposits'])
                 + len(data['binance_pay']) + len(data['p2p_transactions']))

        if total == 0:
            lines.append('--- UID {} --- NO MATCHES ---'.format(uid))
            lines.append('')
            continue

        lines.append('--- UID {} --- {} match(es) ---'.format(uid, total))
        lines.append('')

        # Crypto Withdrawals
        if data['crypto_withdrawals']:
            lines.append('  Crypto Withdrawals ({} transactions):'.format(
                len(data['crypto_withdrawals'])))
            for tx in data['crypto_withdrawals']:
                lines.append('    {} | {} {} | {} | {} | dest: {} | status: {}'.format(
                    tx.get('apply_time', 'N/A'),
                    tx.get('currency', ''),
                    tx.get('amount', 0),
                    fmt_usd(tx.get('usdt_value', 0)),
                    tx.get('network', ''),
                    tx.get('destination_address', ''),
                    tx.get('status', ''),
                ))
            lines.append('')

        # Crypto Deposits
        if data['crypto_deposits']:
            lines.append('  Crypto Deposits ({} transactions):'.format(
                len(data['crypto_deposits'])))
            for tx in data['crypto_deposits']:
                lines.append('    {} | {} {} | {} | {} | source: {} | status: {}'.format(
                    tx.get('create_time', 'N/A'),
                    tx.get('currency', ''),
                    tx.get('amount', 0),
                    fmt_usd(tx.get('usdt_value', 0)),
                    tx.get('network', ''),
                    tx.get('source_address', ''),
                    tx.get('status', ''),
                ))
            lines.append('')

        # Binance Pay
        if data['binance_pay']:
            lines.append('  Binance Pay ({} transactions):'.format(
                len(data['binance_pay'])))
            for tx in data['binance_pay']:
                lines.append('    {} | {} | {} {} | type: {} | order: {} | tx: {}'.format(
                    tx.get('transaction_time', 'N/A'),
                    tx.get('merchant_name', '') or '-',
                    tx.get('currency', ''),
                    tx.get('amount', 0),
                    tx.get('transaction_type', ''),
                    tx.get('order_id', ''),
                    tx.get('transaction_id', ''),
                ))
            lines.append('')

        # P2P
        if data['p2p_transactions']:
            lines.append('  P2P ({} transactions):'.format(
                len(data['p2p_transactions'])))
            for tx in data['p2p_transactions']:
                role = ''
                if safe_str(tx.get('taker_id', '')) == uid:
                    role = 'Taker'
                elif safe_str(tx.get('ad_publisher_id', '')) == uid:
                    role = 'Ad Publisher'
                lines.append('    {} | {} {} | {} {} | price: {} | role: {} | {} | status: {}'.format(
                    tx.get('create_time', 'N/A'),
                    tx.get('buy_or_sell', ''),
                    tx.get('crypto', ''),
                    tx.get('fiat_currency', ''),
                    tx.get('total_amount', 0),
                    tx.get('unit_price', 0),
                    role,
                    tx.get('payment_method', ''),
                    tx.get('status', ''),
                ))
            lines.append('')

    return '\n'.join(lines)
