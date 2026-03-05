"""
Privacy Coin Breakdown Processor.
Displays privacy coin transaction details when present.
"""

from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_float, fmt_usd


class PrivacyCoinProcessor(BaseProcessor):
    id = 'privacy_coin'
    label = 'Privacy Coins'
    sort_order = 9  # After CP/device summary, before counterparty at 10

    required_file_types = ['PRIVACY_COIN']
    optional_file_types = []

    required_fields = []

    consumed_fields = {
        'PRIVACY_COIN': [
            'user_id', 'major_user_id', 'token', 'tx_amt_token',
            'tx_amt_usd', 'tx_date', 'tx_id / order_id',
            'counterparty_major_user_id', 'address', 'type',
            'direction', 'network',
        ],
    }

    def process(self, file_data, params, context):
        rows = file_data.get('PRIVACY_COIN', {}).get('rows', [])
        if not rows:
            return ProcessorResult(
                content='No privacy coin transactions found.',
                has_data=False,
            )

        lines = []
        lines.append('=== PRIVACY COIN BREAKDOWN ===')
        lines.append('')

        total_usd = sum(safe_float(r.get('tx_amt_usd', 0)) for r in rows)

        # Group by token
        token_map = {}
        for row in rows:
            token = safe_str(row.get('token', '')) or '(unknown)'
            if token not in token_map:
                token_map[token] = {
                    'count': 0, 'usd': 0,
                    'inbound': 0, 'outbound': 0,
                    'inbound_usd': 0, 'outbound_usd': 0,
                }
            token_map[token]['count'] += 1
            amt = safe_float(row.get('tx_amt_usd', 0))
            token_map[token]['usd'] += amt
            direction = safe_str(row.get('direction', '')).lower()
            if direction in ('inbound', 'deposit', 'in'):
                token_map[token]['inbound'] += 1
                token_map[token]['inbound_usd'] += amt
            else:
                token_map[token]['outbound'] += 1
                token_map[token]['outbound_usd'] += amt

        # Dates
        dates = []
        for row in rows:
            d = safe_str(row.get('tx_date', ''))
            if d and d != '(null)':
                dates.append(d)
        dates.sort()
        earliest = dates[0] if dates else 'N/A'
        latest = dates[-1] if dates else 'N/A'

        # Networks
        networks = {}
        for row in rows:
            n = safe_str(row.get('network', ''))
            if n and n != '(null)':
                networks[n] = True

        lines.append('Total transactions: {}'.format(len(rows)))
        lines.append('Total USD value:    {}'.format(fmt_usd(total_usd)))
        lines.append('Date range:         {} to {}'.format(earliest, latest))
        lines.append('Tokens:             {}'.format(
            ', '.join(token_map.keys())))
        lines.append('Networks:           {}'.format(
            ', '.join(networks.keys()) if networks else 'N/A'))
        lines.append('')

        # Token breakdown
        lines.append('--- BY TOKEN ---')
        lines.append('')
        lines.append('{:<12s}  {:>6s}  {:>14s}  {:>4s} in  {:>12s}  {:>4s} out  {:>12s}'.format(
            'Token', 'Count', 'USD Total', '', 'USD In', '', 'USD Out'))
        lines.append('{:<12s}  {:>6s}  {:>14s}  {:>4s}     {:>12s}  {:>4s}      {:>12s}'.format(
            '-' * 12, '-' * 6, '-' * 14, '-' * 4, '-' * 12, '-' * 4, '-' * 12))

        for token in sorted(token_map.keys(),
                            key=lambda t: token_map[t]['usd'],
                            reverse=True):
            t = token_map[token]
            lines.append('{:<12s}  {:>6d}  {:>14s}  {:>4d}     {:>12s}  {:>4d}      {:>12s}'.format(
                token, t['count'], fmt_usd(t['usd']),
                t['inbound'], fmt_usd(t['inbound_usd']),
                t['outbound'], fmt_usd(t['outbound_usd'])))
        lines.append('')

        # All transactions chronological
        sorted_rows = sorted(rows,
                             key=lambda r: safe_str(r.get('tx_date', '')))

        lines.append('--- ALL TRANSACTIONS (chronological) ---')
        lines.append('')
        for row in sorted_rows:
            tx_date = safe_str(row.get('tx_date', ''))
            token = safe_str(row.get('token', ''))
            direction = safe_str(row.get('direction', ''))
            tx_type = safe_str(row.get('type', ''))
            amt_token = safe_float(row.get('tx_amt_token', 0))
            amt_usd = safe_float(row.get('tx_amt_usd', 0))
            network = safe_str(row.get('network', ''))
            addr = safe_str(row.get('address', ''))
            cp = safe_str(row.get('counterparty_major_user_id', ''))
            tx_id = safe_str(row.get('tx_id / order_id', ''))

            lines.append('{} | {} | {} | {} | {:.6f} {} | {} | {}'.format(
                tx_date, direction.upper(), tx_type, network,
                amt_token, token, fmt_usd(amt_usd),
                addr[:20] + '...' if len(addr) > 20 else addr))
            if cp and cp != '(null)':
                lines.append('  Counterparty: {}'.format(cp))
            if tx_id and tx_id != '(null)':
                lines.append('  TX ID: {}'.format(tx_id))

        return ProcessorResult(content='\n'.join(lines), has_data=True)
