"""
FTM (Fiat Transaction Monitoring) Alerts Processor.
Analyses rule-triggered alerts by rule code, transaction type,
counterparty, and address.
"""

from datetime import datetime
from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_float, fmt_usd
from ..constants import lookup_rule_code


class FTMProcessor(BaseProcessor):
    id = 'ftm'
    label = 'FTM Alerts'
    sort_order = 60

    required_file_types = ['FTM_ALERTS']
    optional_file_types = []

    required_fields = []

    consumed_fields = {
        'FTM_ALERTS': [
            'tx_date_time', 'rule_code', 'token_amount', 'usd_amount',
            'tx_currency', 'address', 'tx_type', 'counterparty_id',
        ],
    }

    def process(self, file_data, params, context):
        rows = file_data.get('FTM_ALERTS', {}).get('rows', [])
        if not rows:
            return ProcessorResult(content='No FTM alert data uploaded.', has_data=False)

        out = []
        out.append('=== FTM ALERTS ===')
        out.append('')

        dates = []
        for row in rows:
            d = self._parse_date(row.get('tx_date_time', ''))
            if d:
                dates.append(d)
        dates.sort()
        earliest = dates[0].strftime('%Y-%m-%d') if dates else 'N/A'
        latest = dates[-1].strftime('%Y-%m-%d') if dates else 'N/A'

        total_usd = sum(safe_float(r.get('usd_amount', 0)) for r in rows)

        coin_set = {}
        addr_set = {}
        for row in rows:
            v = safe_str(row.get('tx_currency', ''))
            if v:
                coin_set[v] = True
            v = safe_str(row.get('address', ''))
            if v:
                addr_set[v] = True

        out.append('Total alerts:       {}'.format(len(rows)))
        out.append('Date range:         {} to {}'.format(earliest, latest))
        out.append('Total USD flagged:   {}'.format(fmt_usd(total_usd)))
        out.append('Currency:           {}'.format(', '.join(coin_set.keys())))
        out.append('Distinct addresses: {}'.format(len(addr_set)))
        out.append('')

        # By rule code
        rule_map = {}
        for row in rows:
            code = safe_str(row.get('rule_code', '')) or '(unknown)'
            if code not in rule_map:
                rule_map[code] = {'count': 0, 'usd': 0}
            rule_map[code]['count'] += 1
            rule_map[code]['usd'] += safe_float(row.get('usd_amount', 0))

        out.append('--- BY RULE CODE ---')
        for code in sorted(rule_map.keys(),
                           key=lambda c: rule_map[c]['usd'], reverse=True):
            r = rule_map[code]
            info = lookup_rule_code(code)
            out.append('{} | {} [{}]'.format(
                code.upper(), info['name'], info['platform']))
            out.append('  {} alerts | {}'.format(r['count'], fmt_usd(r['usd'])))
        out.append('')

        # By transaction type
        tx_map = {}
        for row in rows:
            tt = safe_str(row.get('tx_type', '')) or '(unknown)'
            if tt not in tx_map:
                tx_map[tt] = {'count': 0, 'usd': 0}
            tx_map[tt]['count'] += 1
            tx_map[tt]['usd'] += safe_float(row.get('usd_amount', 0))

        out.append('--- BY TRANSACTION TYPE ---')
        for tt in sorted(tx_map.keys()):
            out.append('{}: {} alerts | {}'.format(
                tt, tx_map[tt]['count'], fmt_usd(tx_map[tt]['usd'])))
        out.append('')

        # By counterparty
        cp_map = {}
        for row in rows:
            cp = safe_str(row.get('counterparty_id', ''))
            is_empty = not cp or cp == '(空字符串)' or cp == ''
            key = '(external \u2014 no counterparty)' if is_empty else cp
            if key not in cp_map:
                cp_map[key] = {'count': 0, 'usd': 0}
            cp_map[key]['count'] += 1
            cp_map[key]['usd'] += safe_float(row.get('usd_amount', 0))

        out.append('--- BY COUNTERPARTY ---')
        for cp in sorted(cp_map.keys(),
                         key=lambda c: cp_map[c]['usd'], reverse=True):
            out.append('{}: {} alerts | {}'.format(
                cp, cp_map[cp]['count'], fmt_usd(cp_map[cp]['usd'])))
        out.append('')

        # Top addresses
        addr_map = {}
        for row in rows:
            addr = safe_str(row.get('address', '')) or '(no address)'
            if addr not in addr_map:
                addr_map[addr] = {
                    'count': 0, 'usd': 0,
                    'tx_types': {}, 'rule_codes': {},
                }
            addr_map[addr]['count'] += 1
            addr_map[addr]['usd'] += safe_float(row.get('usd_amount', 0))
            addr_map[addr]['tx_types'][safe_str(row.get('tx_type', ''))] = True
            addr_map[addr]['rule_codes'][safe_str(row.get('rule_code', '')).upper()] = True

        out.append('--- TOP ADDRESSES BY VALUE ---')
        for idx, addr in enumerate(sorted(addr_map.keys(),
                                           key=lambda a: addr_map[a]['usd'],
                                           reverse=True)):
            a = addr_map[addr]
            out.append('{}. {}'.format(idx + 1, addr))
            out.append('   {} | {} | {} | {} alert(s)'.format(
                ', '.join(a['tx_types'].keys()),
                ', '.join(a['rule_codes'].keys()),
                fmt_usd(a['usd']), a['count']))
        out.append('')

        # All transactions chronological
        sorted_rows = sorted(rows, key=lambda r: safe_str(r.get('tx_date_time', '')))
        out.append('--- ALL TRANSACTIONS (chronological) ---')
        for row in sorted_rows:
            cp = safe_str(row.get('counterparty_id', ''))
            is_empty = not cp or cp == '(空字符串)' or cp == ''
            cp_str = 'CP: (external)' if is_empty else 'CP: ' + cp
            out.append('{} | {} | {} | {} | {} | {}'.format(
                safe_str(row.get('tx_date_time', '')),
                safe_str(row.get('tx_type', '')) or '-',
                safe_str(row.get('rule_code', '')).upper(),
                fmt_usd(safe_float(row.get('usd_amount', 0))),
                safe_str(row.get('address', '')) or '-',
                cp_str))

        return ProcessorResult(content='\n'.join(out), has_data=True)

    def _parse_date(self, date_str):
        try:
            return datetime.fromisoformat(
                safe_str(date_str).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            try:
                return datetime.strptime(
                    safe_str(date_str), '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return None