"""
CTM (Counterparty Transaction Monitoring) Alerts Processor.
Analyses on-chain alerts by case, category, exposure type, and address.
"""

from datetime import datetime
from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_float, fmt_usd


class CTMProcessor(BaseProcessor):
    id = 'ctm'
    label = 'CTM Alerts'
    sort_order = 50

    required_file_types = ['CTM_ALERTS']
    optional_file_types = []

    required_fields = []

    consumed_fields = {
        'CTM_ALERTS': [
            'case_no', 'create_time', 'busd_amt', 'address', 'coin',
            'channel', 'transaction_type', 'category', 'category_group',
            'exposure', 'elliptic_risk_score', 'case_status',
            'final_case_outcome',
        ],
    }

    def process(self, file_data, params, context):
        rows = file_data.get('CTM_ALERTS', {}).get('rows', [])
        if not rows:
            return ProcessorResult(content='No CTM alert data uploaded.', has_data=False)

        out = []
        out.append('=== CTM ALERTS ===')
        out.append('')

        dates = []
        for row in rows:
            d = self._parse_date(row.get('create_time', ''))
            if d:
                dates.append(d)
        dates.sort()
        earliest = dates[0].strftime('%Y-%m-%d') if dates else 'N/A'
        latest = dates[-1].strftime('%Y-%m-%d') if dates else 'N/A'

        total_usd = sum(safe_float(r.get('busd_amt', 0)) for r in rows)

        case_set = {}
        addr_set = {}
        coin_set = {}
        channel_set = {}
        tx_type_set = {}
        for row in rows:
            v = safe_str(row.get('case_no', ''))
            if v:
                case_set[v] = True
            v = safe_str(row.get('address', ''))
            if v:
                addr_set[v] = True
            v = safe_str(row.get('coin', ''))
            if v:
                coin_set[v] = True
            v = safe_str(row.get('channel', ''))
            if v:
                channel_set[v] = True
            v = safe_str(row.get('transaction_type', ''))
            if v:
                tx_type_set[v] = True

        out.append('Total alerts:       {}'.format(len(rows)))
        out.append('Date range:         {} to {}'.format(earliest, latest))
        out.append('Total USD exposure: {}'.format(fmt_usd(total_usd)))
        out.append('Distinct cases:     {}'.format(len(case_set)))
        out.append('Distinct addresses: {}'.format(len(addr_set)))
        out.append('Coins:              {}'.format(', '.join(coin_set.keys())))
        out.append('Channels:           {}'.format(', '.join(channel_set.keys())))
        out.append('Transaction types:  {}'.format(', '.join(tx_type_set.keys())))
        out.append('')

        # By case
        case_map = {}
        for row in rows:
            cn = safe_str(row.get('case_no', '')) or '(no case)'
            if cn not in case_map:
                case_map[cn] = {
                    'count': 0, 'usd': 0,
                    'direct': 0, 'indirect': 0,
                    'direct_usd': 0, 'indirect_usd': 0,
                }
            case_map[cn]['count'] += 1
            amt = safe_float(row.get('busd_amt', 0))
            case_map[cn]['usd'] += amt
            if safe_str(row.get('exposure', '')).lower() == 'direct':
                case_map[cn]['direct'] += 1
                case_map[cn]['direct_usd'] += amt
            else:
                case_map[cn]['indirect'] += 1
                case_map[cn]['indirect_usd'] += amt

        out.append('--- BY CASE ---')
        for cn, c in case_map.items():
            out.append('{}: {} alerts | {} total | Direct: {} ({}) | Indirect: {} ({})'.format(
                cn, c['count'], fmt_usd(c['usd']),
                c['direct'], fmt_usd(c['direct_usd']),
                c['indirect'], fmt_usd(c['indirect_usd'])))
        out.append('')

        # By category
        cat_map = {}
        for row in rows:
            cat = safe_str(row.get('category', '')) or '(unspecified)'
            grp = safe_str(row.get('category_group', '')) or '(unspecified)'
            key = grp + ' | ' + cat
            if key not in cat_map:
                cat_map[key] = {'count': 0, 'usd': 0}
            cat_map[key]['count'] += 1
            cat_map[key]['usd'] += safe_float(row.get('busd_amt', 0))

        out.append('--- BY CATEGORY ---')
        for key in sorted(cat_map.keys(), key=lambda k: cat_map[k]['usd'], reverse=True):
            out.append('{}: {} alerts | {}'.format(
                key, cat_map[key]['count'], fmt_usd(cat_map[key]['usd'])))
        out.append('')

        # By exposure type
        exp_map = {}
        for row in rows:
            exp = safe_str(row.get('exposure', '')) or '(unknown)'
            if exp not in exp_map:
                exp_map[exp] = {'count': 0, 'usd': 0, 'scores': []}
            exp_map[exp]['count'] += 1
            exp_map[exp]['usd'] += safe_float(row.get('busd_amt', 0))
            score = safe_float(row.get('elliptic_risk_score', 0))
            if score > 0:
                exp_map[exp]['scores'].append(score)

        out.append('--- BY EXPOSURE TYPE ---')
        for exp, e in exp_map.items():
            avg = ('{:.2f}'.format(sum(e['scores']) / len(e['scores']))
                   if e['scores'] else 'N/A')
            out.append('{}: {} alerts | {} | avg risk score: {}'.format(
                exp, e['count'], fmt_usd(e['usd']), avg))
        out.append('')

        # Case status
        status_map = {}
        for row in rows:
            cs = safe_str(row.get('case_status', '')) or '(unknown)'
            fo = safe_str(row.get('final_case_outcome', '')) or '(unknown)'
            key = cs + ' / ' + fo
            status_map.setdefault(key, 0)
            status_map[key] += 1

        out.append('--- CASE STATUS ---')
        for key, count in status_map.items():
            out.append('{}: {} alerts'.format(key, count))
        out.append('')

        # Top addresses
        addr_map = {}
        for row in rows:
            addr = safe_str(row.get('address', '')) or '(no address)'
            if addr not in addr_map:
                addr_map[addr] = {
                    'count': 0, 'usd': 0,
                    'category': safe_str(row.get('category', '')) or '(unspecified)',
                    'exposure': safe_str(row.get('exposure', '')),
                    'cases': {},
                }
            addr_map[addr]['count'] += 1
            addr_map[addr]['usd'] += safe_float(row.get('busd_amt', 0))
            addr_map[addr]['cases'][safe_str(row.get('case_no', ''))] = True

        out.append('--- TOP ADDRESSES BY EXPOSURE ---')
        for idx, addr in enumerate(sorted(addr_map.keys(),
                                           key=lambda a: addr_map[a]['usd'],
                                           reverse=True)):
            a = addr_map[addr]
            out.append('{}. {}'.format(idx + 1, addr))
            out.append('   Category: {} | Exposure: {} | {} | {} alert(s)'.format(
                a['category'], a['exposure'], fmt_usd(a['usd']), a['count']))
            out.append('   Cases: {}'.format(', '.join(a['cases'].keys())))
        out.append('')

        # All alerts chronological
        sorted_rows = sorted(rows, key=lambda r: safe_str(r.get('create_time', '')))
        out.append('--- ALL ALERTS (chronological) ---')
        for row in sorted_rows:
            parts = safe_str(row.get('create_time', '')).split(' ')
            date_part = parts[0] if parts else ''
            time_part = parts[1] if len(parts) > 1 else ''
            out.append('{} {} | {} | {} | {} | score: {} | {} | {} | {}'.format(
                date_part, time_part,
                safe_str(row.get('transaction_type', '')) or '-',
                safe_str(row.get('category', '')) or '(unspecified)',
                safe_str(row.get('exposure', '')) or '-',
                safe_str(row.get('elliptic_risk_score', '')),
                fmt_usd(safe_float(row.get('busd_amt', 0))),
                safe_str(row.get('address', '')) or '-',
                safe_str(row.get('case_no', '')) or '-'))

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