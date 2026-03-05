"""
Failed Fiat Analysis Processor.
Processes C360 Failed Fiat spreadsheet and UOL Fiat Withdrawal History.
Identifies fraud-flagged transactions, error reason breakdown, card usage.
"""

from datetime import datetime
from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_float, fmt_usd


class FailedFiatProcessor(BaseProcessor):
    id = 'fiat'
    label = 'Failed Fiat'
    sort_order = 40

    required_file_types = ['FAILED_FIAT']
    optional_file_types = []

    required_fields = []

    consumed_fields = {
        'FAILED_FIAT': [
            'trans_time', 'error_reason', 'fiat_qty', 'fiat_token',
            'fiat_channel', 'card_no',
        ],
    }

    def should_run(self, available_file_types, params):
        has_c360 = 'FAILED_FIAT' in available_file_types
        has_uol = 'UOL_FIAT_WITHDRAWALS' in available_file_types
        return has_c360 or has_uol

    def process(self, file_data, params, context):
        c360_rows = file_data.get('FAILED_FIAT', {}).get('rows', [])
        uol_data = context.get('uol_data', {})
        uol_withdrawals = uol_data.get('fiat_withdrawals', []) if uol_data else []

        has_c360 = len(c360_rows) > 0
        has_uol_wd = len(uol_withdrawals) > 0

        if not has_c360 and not has_uol_wd:
            return ProcessorResult(
                content='No failed fiat transaction data available.',
                has_data=False,
            )

        all_sections = []

        if has_c360:
            all_sections.append(self._process_c360(c360_rows))

        if has_uol_wd:
            all_sections.append(self._process_uol_withdrawals(uol_withdrawals))

        label = 'Failed Fiat'
        if has_uol_wd:
            label += ' (+UOL)'

        return ProcessorResult(
            content='\n\n'.join(all_sections),
            has_data=True,
        )

    def _parse_date(self, date_str):
        try:
            return datetime.fromisoformat(safe_str(date_str).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            try:
                return datetime.strptime(safe_str(date_str), '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return None

    def _process_c360(self, rows):
        dates = []
        for row in rows:
            d = self._parse_date(row.get('trans_time', ''))
            if d:
                dates.append(d)
        dates.sort()
        earliest = dates[0].strftime('%Y-%m-%d') if dates else 'N/A'
        latest = dates[-1].strftime('%Y-%m-%d') if dates else 'N/A'

        reason_map = {}
        fraud_rows = []
        fraud_keywords = ['fraud', 'suspected fraud', 'scam', 'security', 'suspicious']
        empty_reasons = ['', '(空字符串)', 'null', '(null)']

        for row in rows:
            reason = safe_str(row.get('error_reason', ''))
            is_empty = any(reason.lower() == er.lower() or reason == ''
                          for er in empty_reasons)
            display_reason = '(empty/unspecified)' if is_empty else reason

            if display_reason not in reason_map:
                reason_map[display_reason] = {'count': 0, 'total_qty': 0, 'tokens': {}}
            reason_map[display_reason]['count'] += 1
            qty = safe_float(row.get('fiat_qty', 0))
            reason_map[display_reason]['total_qty'] += qty

            token = safe_str(row.get('fiat_token', '')) or 'UNKNOWN'
            reason_map[display_reason]['tokens'].setdefault(token, 0)
            reason_map[display_reason]['tokens'][token] += qty

            reason_lower = reason.lower()
            if any(kw in reason_lower for kw in fraud_keywords):
                fraud_rows.append(row)

        token_totals = {}
        for row in rows:
            token = safe_str(row.get('fiat_token', '')) or 'UNKNOWN'
            token_totals.setdefault(token, 0)
            token_totals[token] += safe_float(row.get('fiat_qty', 0))

        fraud_channels = {}
        fraud_total = 0
        for row in fraud_rows:
            ch = safe_str(row.get('fiat_channel', ''))
            if ch not in fraud_channels:
                fraud_channels[ch] = {'count': 0, 'total': 0}
            fraud_channels[ch]['count'] += 1
            fraud_channels[ch]['total'] += safe_float(row.get('fiat_qty', 0))
            fraud_total += safe_float(row.get('fiat_qty', 0))

        card_map = {}
        for row in rows:
            card = safe_str(row.get('card_no', ''))
            if card:
                card_map.setdefault(card, 0)
                card_map[card] += 1

        f = []
        f.append('=== FAILED FIAT DEPOSITS (from C360) ===')
        f.append('')
        f.append('Total failed deposit transactions: {}'.format(len(rows)))
        f.append('Date range: {} to {}'.format(earliest, latest))
        f.append('')
        f.append('Total value by currency:')
        for token, total in token_totals.items():
            f.append('  {}: {:.2f}'.format(token, total))
        f.append('')
        f.append('Error reasons:')
        sorted_reasons = sorted(reason_map.keys(),
                                key=lambda r: reason_map[r]['count'], reverse=True)
        for reason in sorted_reasons:
            r = reason_map[reason]
            token_str = ', '.join('{} {:.2f}'.format(t, v)
                                  for t, v in r['tokens'].items())
            f.append('  {}: {} tx ({})'.format(reason, r['count'], token_str))
        f.append('')

        if fraud_rows:
            f.append('\u26a0\ufe0f FRAUD-FLAGGED TRANSACTIONS: {}'.format(len(fraud_rows)))
            f.append('Fraud total value: {:.2f}'.format(fraud_total))
            f.append('Fraud channels:')
            for ch, data in fraud_channels.items():
                f.append('  {}: {} tx, value {:.2f}'.format(
                    ch, data['count'], data['total']))
            f.append('')
            f.append('Fraud transaction details:')
            for row in fraud_rows:
                f.append('  {} | {} | {} {:.2f} | {} | Card: {}'.format(
                    safe_str(row.get('trans_time', '')),
                    safe_str(row.get('fiat_channel', '')),
                    safe_str(row.get('fiat_token', '')),
                    safe_float(row.get('fiat_qty', 0)),
                    safe_str(row.get('error_reason', '')),
                    safe_str(row.get('card_no', ''))))
        else:
            f.append('No fraud-flagged error reasons detected.')

        f.append('')
        f.append('Cards used:')
        for card in sorted(card_map.keys(), key=lambda c: card_map[c], reverse=True):
            f.append('  {}: {} transaction(s)'.format(card, card_map[card]))

        return '\n'.join(f)

    def _process_uol_withdrawals(self, uol_withdrawals):
        failed_wd = [r for r in uol_withdrawals
                     if r.get('status', '').upper() != 'SUCCESS']

        if not failed_wd:
            return ('\n=== FAILED FIAT WITHDRAWALS (from UOL) ===\n\n'
                    'All fiat withdrawal transactions in UOL have SUCCESS status. '
                    'No failed withdrawals detected.')

        dates = []
        for row in failed_wd:
            d = self._parse_date(row.get('date', ''))
            if d:
                dates.append(d)
        dates.sort()
        earliest = dates[0].strftime('%Y-%m-%d') if dates else 'N/A'
        latest = dates[-1].strftime('%Y-%m-%d') if dates else 'N/A'

        currency_totals = {}
        usd_total = 0
        for row in failed_wd:
            curr = row.get('currency', '') or 'UNKNOWN'
            if curr not in currency_totals:
                currency_totals[curr] = {'count': 0, 'amount': 0, 'usd_amount': 0}
            currency_totals[curr]['count'] += 1
            currency_totals[curr]['amount'] += row.get('amount', 0)
            currency_totals[curr]['usd_amount'] += row.get('amount_usd', 0)
            usd_total += row.get('amount_usd', 0)

        channel_map = {}
        for row in failed_wd:
            ch = row.get('channel', '') or 'UNKNOWN'
            if ch not in channel_map:
                channel_map[ch] = {'count': 0, 'usd_total': 0}
            channel_map[ch]['count'] += 1
            channel_map[ch]['usd_total'] += row.get('amount_usd', 0)

        status_map = {}
        for row in failed_wd:
            st = row.get('status', '') or 'UNKNOWN'
            status_map.setdefault(st, 0)
            status_map[st] += 1

        w = []
        w.append('')
        w.append('=== FAILED FIAT WITHDRAWALS (from UOL) ===')
        w.append('')
        w.append('Total failed withdrawal transactions: {}'.format(len(failed_wd)))
        w.append('Date range: {} to {}'.format(earliest, latest))
        w.append('Total USD value: {}'.format(fmt_usd(usd_total)))
        w.append('')
        w.append('Status breakdown:')
        for st, count in status_map.items():
            w.append('  {}: {}'.format(st, count))
        w.append('')
        w.append('Value by currency:')
        for curr, ct in currency_totals.items():
            w.append('  {}: {:.2f} ({} tx) [{}]'.format(
                curr, ct['amount'], ct['count'], fmt_usd(ct['usd_amount'])))
        w.append('')
        w.append('Channel breakdown:')
        for ch in sorted(channel_map.keys(),
                         key=lambda c: channel_map[c]['count'], reverse=True):
            w.append('  {}: {} tx, {}'.format(
                ch, channel_map[ch]['count'], fmt_usd(channel_map[ch]['usd_total'])))
        w.append('')
        w.append('Transaction details:')
        for row in failed_wd:
            card_str = ''
            if row.get('card_bin') and row.get('card_last4'):
                card_str = '{}**{}'.format(row['card_bin'], row['card_last4'])
            bank_str = ''
            if row.get('bank_name'):
                bank_str = row['bank_name']
                if row.get('bank_country'):
                    bank_str += ' ({})'.format(row['bank_country'])
            iban_str = 'IBAN: {}'.format(row['iban']) if row.get('iban') else ''
            viban_str = 'VIBAN: {}'.format(row['viban']) if row.get('viban') else ''
            acct_str = 'Acct: {}'.format(row['account_number']) if row.get('account_number') else ''

            details = [
                row.get('date', ''),
                row.get('status', ''),
                row.get('channel', ''),
                '{} {:.2f} [{}]'.format(
                    row.get('currency', ''),
                    row.get('amount', 0),
                    fmt_usd(row.get('amount_usd', 0))),
            ]
            if card_str:
                details.append('Card: ' + card_str)
            if bank_str:
                details.append(bank_str)
            if iban_str:
                details.append(iban_str)
            if viban_str:
                details.append(viban_str)
            if acct_str:
                details.append(acct_str)
            w.append('  ' + ' | '.join(details))

        w.append('')
        w.append('Note: UOL does not provide error reasons for failed transactions.')
        return '\n'.join(w)