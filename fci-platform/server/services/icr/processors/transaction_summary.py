"""
Transaction Summary Processor.
Combines Inbound/Outbound Summary (amounts), Inbound/Outbound Count Summary,
and Trade Summary into a single overview tab.
"""

from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_float, safe_int, fmt_usd


class TransactionSummaryProcessor(BaseProcessor):
    id = 'tx_summary'
    label = 'Transaction Summary'
    sort_order = 5  # Show first — it's the overview

    required_file_types = ['IO_SUMMARY', 'IO_COUNT', 'TRADE_SUMMARY']
    optional_file_types = ['USER_INFO', 'USER_INFO_2']

    required_fields = []

    consumed_fields = {
        'IO_SUMMARY': [
            'total crypto deposit amount', 'total crypto withdraw amount',
            'total fiat deposit amount', 'total fiat withdraw amount',
            'total p2p inbound amount', 'total p2p outbound amount',
            'total bpay inbound amount', 'total bpay outbound amount',
            'total bcard inbound amount', 'total bcard outbound amount',
            '----total inbound amount', '----total outbound amount',
            'outbound to inbound ratio',
        ],
        'IO_COUNT': [
            'total crypto deposit count', 'total crypto withdraw count',
            'total fiat deposit count', 'total fiat withdraw count',
            'total p2p inbound count', 'total p2p outbound count',
            'total bpay inbound count', 'total bpay outbound count',
            'total bcard inbound count', 'total bcard outbound count',
            '----total inbound count', '----total outbound count',
        ],
        'TRADE_SUMMARY': [
            'trade type', 'amt_usd', 'trade_count',
        ],
    }

    def should_run(self, available_file_types, params):
        return bool({'IO_SUMMARY', 'IO_COUNT', 'TRADE_SUMMARY'} & set(available_file_types))

    def process(self, file_data, params, context):
        io_sum_rows = file_data.get('IO_SUMMARY', {}).get('rows', [])
        io_cnt_rows = file_data.get('IO_COUNT', {}).get('rows', [])
        trade_rows = file_data.get('TRADE_SUMMARY', {}).get('rows', [])

        has_amounts = len(io_sum_rows) > 0
        has_counts = len(io_cnt_rows) > 0
        has_trade = len(trade_rows) > 0

        if not has_amounts and not has_counts and not has_trade:
            return ProcessorResult(
                content='No transaction summary data available.',
                has_data=False,
            )

        sections = []

        # Date range from USER_INFO (reg date) and USER_INFO_2 (last active)
        date_range = self._build_date_range(file_data, context)
        if date_range:
            sections.append(date_range)

        if has_amounts or has_counts:
            sections.append(self._build_io_section(
                io_sum_rows[0] if has_amounts else {},
                io_cnt_rows[0] if has_counts else {},
                has_amounts, has_counts))

        if has_trade:
            sections.append(self._build_trade_section(trade_rows))

        return ProcessorResult(
            content='\n\n'.join(sections),
            has_data=True,
        )

    def _get_amt(self, row, key):
        """Get a float value from a row, matching case-insensitively."""
        # Headers are stored as-is from the spreadsheet, so try original case
        # and common variations
        for k in [key, key.lower(), key.title()]:
            if k in row:
                return safe_float(row[k])
        # Also try case-insensitive match
        key_lower = key.lower()
        for k, v in row.items():
            if safe_str(k).lower() == key_lower:
                return safe_float(v)
        return 0

    def _get_int(self, row, key):
        """Get an int value from a row, matching case-insensitively."""
        for k in [key, key.lower(), key.title()]:
            if k in row:
                return safe_int(row[k])
        key_lower = key.lower()
        for k, v in row.items():
            if safe_str(k).lower() == key_lower:
                return safe_int(v)
        return 0

    def _build_date_range(self, file_data, context):
        """Extract date range from USER_INFO (reg date) and USER_INFO_2 (last active)."""
        reg_date = ''
        last_active = ''

        # Registration date from USER_INFO (passed via context)
        user_info = context.get('user_info')
        if user_info:
            reg_date = safe_str(user_info.get('Registration Date', ''))
            if reg_date == '(null)':
                reg_date = ''

        # Last active time from USER_INFO_2
        ui2_rows = file_data.get('USER_INFO_2', {}).get('rows', [])
        if ui2_rows:
            row = ui2_rows[0]
            for key in ['Last Active Time', 'last active time']:
                if key in row:
                    last_active = safe_str(row[key])
                    break
            if not last_active:
                for k, v in row.items():
                    if safe_str(k).lower().strip() == 'last active time':
                        last_active = safe_str(v)
                        break
            if last_active == '(null)':
                last_active = ''

        if not reg_date and not last_active:
            return None

        parts = []
        if reg_date and last_active:
            parts.append('Date Range: {} to {}'.format(reg_date, last_active))
        elif reg_date:
            parts.append('Registration Date: {}'.format(reg_date))
        elif last_active:
            parts.append('Last Active: {}'.format(last_active))

        return '\n'.join(parts)

    def _build_io_section(self, amt_row, cnt_row, has_amounts, has_counts):
        channels = [
            ('Crypto Deposit',  'Total Crypto Deposit Amount',  'Total Crypto Deposit Count',  'inbound'),
            ('Crypto Withdraw', 'Total Crypto Withdraw Amount', 'Total Crypto Withdraw Count', 'outbound'),
            ('Fiat Deposit',    'Total Fiat Deposit Amount',    'Total Fiat Deposit Count',    'inbound'),
            ('Fiat Withdraw',   'Total Fiat Withdraw Amount',   'Total Fiat Withdraw Count',   'outbound'),
            ('P2P Inbound',     'Total P2P Inbound Amount',     'Total P2P Inbound Count',     'inbound'),
            ('P2P Outbound',    'Total P2P Outbound Amount',    'Total P2P Outbound Count',    'outbound'),
            ('BPay Inbound',    'Total Bpay Inbound Amount',    'Total Bpay Inbound Count',    'inbound'),
            ('BPay Outbound',   'Total Bpay Outbound Amount',   'Total Bpay Outbound Count',   'outbound'),
            ('BCard Inbound',   'Total Bcard Inbound Amount',   'Total Bcard Inbound Count',   'inbound'),
            ('BCard Outbound',  'Total Bcard Outbound Amount',  'Total Bcard Outbound Count',  'outbound'),
        ]

        lines = []
        lines.append('=== INBOUND / OUTBOUND SUMMARY ===')
        lines.append('')

        # Totals
        total_in_amt = self._get_amt(amt_row, '----Total Inbound Amount') if has_amounts else 0
        total_out_amt = self._get_amt(amt_row, '----Total Outbound Amount') if has_amounts else 0
        ratio = self._get_amt(amt_row, 'Outbound to Inbound Ratio') if has_amounts else 0
        total_in_cnt = self._get_int(cnt_row, '----Total Inbound Count') if has_counts else 0
        total_out_cnt = self._get_int(cnt_row, '----Total Outbound Count') if has_counts else 0

        if has_amounts:
            lines.append('Total Inbound:  {} ({} transactions)'.format(
                fmt_usd(total_in_amt), total_in_cnt if has_counts else 'N/A'))
            lines.append('Total Outbound: {} ({} transactions)'.format(
                fmt_usd(total_out_amt), total_out_cnt if has_counts else 'N/A'))
            net = total_in_amt - total_out_amt
            net_label = 'Net Inflow' if net >= 0 else 'Net Outflow'
            lines.append('{}: {}'.format(net_label, fmt_usd(abs(net))))
            if ratio:
                lines.append('Outbound/Inbound Ratio: {:.2f}'.format(ratio))
            lines.append('')

        # Channel breakdown
        lines.append('--- CHANNEL BREAKDOWN ---')
        lines.append('')

        # Header
        if has_amounts and has_counts:
            lines.append('{:<20s}  {:>16s}  {:>8s}'.format('Channel', 'Amount (USD)', 'Count'))
            lines.append('{:<20s}  {:>16s}  {:>8s}'.format('-' * 20, '-' * 16, '-' * 8))
        elif has_amounts:
            lines.append('{:<20s}  {:>16s}'.format('Channel', 'Amount (USD)'))
            lines.append('{:<20s}  {:>16s}'.format('-' * 20, '-' * 16))
        else:
            lines.append('{:<20s}  {:>8s}'.format('Channel', 'Count'))
            lines.append('{:<20s}  {:>8s}'.format('-' * 20, '-' * 8))

        not_observed = []

        for label, amt_key, cnt_key, direction in channels:
            amt = self._get_amt(amt_row, amt_key) if has_amounts else 0
            cnt = self._get_int(cnt_row, cnt_key) if has_counts else 0

            # Skip zero rows but track them for negative confirmation
            if amt == 0 and cnt == 0:
                not_observed.append(label)
                continue

            if has_amounts and has_counts:
                lines.append('{:<20s}  {:>16s}  {:>8d}'.format(label, fmt_usd(amt), cnt))
            elif has_amounts:
                lines.append('{:<20s}  {:>16s}'.format(label, fmt_usd(amt)))
            else:
                lines.append('{:<20s}  {:>8d}'.format(label, cnt))

        # Add total row
        lines.append('')
        if has_amounts and has_counts:
            lines.append('{:<20s}  {:>16s}  {:>8d}'.format(
                'TOTAL INBOUND', fmt_usd(total_in_amt), total_in_cnt))
            lines.append('{:<20s}  {:>16s}  {:>8d}'.format(
                'TOTAL OUTBOUND', fmt_usd(total_out_amt), total_out_cnt))
        elif has_amounts:
            lines.append('{:<20s}  {:>16s}'.format('TOTAL INBOUND', fmt_usd(total_in_amt)))
            lines.append('{:<20s}  {:>16s}'.format('TOTAL OUTBOUND', fmt_usd(total_out_amt)))
        else:
            lines.append('{:<20s}  {:>8d}'.format('TOTAL INBOUND', total_in_cnt))
            lines.append('{:<20s}  {:>8d}'.format('TOTAL OUTBOUND', total_out_cnt))

        # Negative confirmation — list channels with no activity
        if not_observed:
            lines.append('')
            lines.append('Channels Not Observed: {}'.format(', '.join(not_observed)))
        else:
            lines.append('')
            lines.append('Channels Not Observed: None — all channels had activity')

        return '\n'.join(lines)

    def _build_trade_section(self, trade_rows):
        lines = []
        lines.append('=== TRADE SUMMARY ===')
        lines.append('')

        total_usd = 0
        total_count = 0

        lines.append('{:<20s}  {:>16s}  {:>10s}'.format('Trade Type', 'Amount (USD)', 'Count'))
        lines.append('{:<20s}  {:>16s}  {:>10s}'.format('-' * 20, '-' * 16, '-' * 10))

        # Sort by amount descending
        sorted_rows = sorted(trade_rows,
                             key=lambda r: safe_float(r.get('amt_usd', 0)),
                             reverse=True)

        for row in sorted_rows:
            trade_type = safe_str(row.get('Trade Type', row.get('trade type', '')))
            amt = safe_float(row.get('amt_usd', 0))
            count = safe_int(row.get('trade_count', 0))
            total_usd += amt
            total_count += count
            lines.append('{:<20s}  {:>16s}  {:>10d}'.format(
                trade_type, fmt_usd(amt), count))

        lines.append('{:<20s}  {:>16s}  {:>10s}'.format('-' * 20, '-' * 16, '-' * 10))
        lines.append('{:<20s}  {:>16s}  {:>10d}'.format(
            'TOTAL', fmt_usd(total_usd), total_count))

        return '\n'.join(lines)
