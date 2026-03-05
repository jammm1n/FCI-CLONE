"""
Account Blocks Processor.
Analyses block/unblock history, groups by enforcement action,
tracks current status per block type.
"""

from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_int
import re


class BlocksProcessor(BaseProcessor):
    id = 'blocks'
    label = 'Blocks'
    sort_order = 70

    required_file_types = ['BLOCKS']
    optional_file_types = []

    required_fields = []

    consumed_fields = {
        'BLOCKS': [
            'case_no', 'case_create_datetime', 'block_reason', 'block_remark',
            'create_department', 'owner_department', 'total_block_days',
            'block_type', 'block_status', 'unlock_time', 'unlock_by',
            'unlock_reason',
        ],
    }

    def process(self, file_data, params, context):
        rows = file_data.get('BLOCKS', {}).get('rows', [])
        if not rows:
            return ProcessorResult(
                content='No block/unblock data uploaded.', has_data=False)

        out = []
        out.append('=== ACCOUNT BLOCKS ===')
        out.append('')

        dates = []
        for row in rows:
            d = self._parse_date(row.get('case_create_datetime', ''))
            if d:
                dates.append(d)
        dates.sort()
        earliest = dates[0].strftime('%Y-%m-%d') if dates else 'N/A'
        latest = dates[-1].strftime('%Y-%m-%d') if dates else 'N/A'

        # Group by action ID
        action_map = {}
        for row in rows:
            action_id = self._get_action_id(safe_str(row.get('case_no', '')))
            if action_id not in action_map:
                action_map[action_id] = {
                    'action_id': action_id,
                    'datetime': safe_str(row.get('case_create_datetime', '')),
                    'reason': safe_str(row.get('block_reason', '')),
                    'remark': safe_str(row.get('block_remark', '')),
                    'create_dept': safe_str(row.get('create_department', '')),
                    'owner_dept': safe_str(row.get('owner_department', '')),
                    'days': safe_int(row.get('total_block_days', 0)),
                    'block_types': [],
                    'rows': [],
                }
            action_map[action_id]['rows'].append(row)
            bt = safe_str(row.get('block_type', ''))
            if bt and bt not in action_map[action_id]['block_types']:
                action_map[action_id]['block_types'].append(bt)

        # Current status per block type
        block_type_status = {}
        for row in rows:
            bt = safe_str(row.get('block_type', ''))
            bs = safe_str(row.get('block_status', '')).lower()
            block_type_status[bt] = 'ACTIVE' if bs == 'block' else 'RESOLVED'

        active_count = sum(1 for v in block_type_status.values() if v == 'ACTIVE')

        out.append('Total records:                {}'.format(len(rows)))
        out.append('Distinct enforcement actions: {}'.format(len(action_map)))
        out.append('Active block types:           {}'.format(active_count))
        out.append('Date range:                   {} to {}'.format(earliest, latest))
        out.append('')

        # Chronological actions
        actions_sorted = sorted(action_map.values(),
                                key=lambda a: a['datetime'])

        out.append('--- ENFORCEMENT ACTIONS (chronological) ---')
        out.append('')
        for idx, action in enumerate(actions_sorted):
            out.append('[{}] {}'.format(idx + 1, action['datetime']))
            out.append('    Reason:      {}'.format(action['reason'] or '(none)'))
            out.append('    Remark:      {}'.format(action['remark'] or '(none)'))
            out.append('    Dept:        {} \u2192 {}'.format(
                action['create_dept'], action['owner_dept']))
            out.append('    Duration:    {} day(s)'.format(action['days']))
            out.append('    Block types: {}'.format(' | '.join(action['block_types'])))

            has_unlock = False
            for row in action['rows']:
                unlock_time = safe_str(row.get('unlock_time', ''))
                unlock_by = safe_str(row.get('unlock_by', ''))
                unlock_reason = safe_str(row.get('unlock_reason', ''))
                bt = safe_str(row.get('block_type', ''))
                bs = safe_str(row.get('block_status', '')).lower()
                has_unlock_time = (unlock_time and unlock_time != '(null)'
                                   and unlock_time != '')

                if bs == 'unblock' or has_unlock_time:
                    has_unlock = True
                    out.append('    Unlock [{}]: {} by {} \u2014 {}'.format(
                        bt, unlock_time, unlock_by, unlock_reason))

            if not has_unlock:
                out.append('    Unlock:      No unlock recorded')

            all_active = all(
                safe_str(r.get('block_status', '')).lower() == 'block'
                and (not safe_str(r.get('unlock_time', ''))
                     or safe_str(r.get('unlock_time', '')) == '(null)')
                for r in action['rows']
            )
            out.append('    Status:      {}'.format(
                'ACTIVE' if all_active else 'PARTIALLY OR FULLY RESOLVED'))
            out.append('')

        # Status by block type
        out.append('--- CURRENT STATUS BY BLOCK TYPE ---')
        known_types = [
            'trade_forbidden', 'login_forbidden',
            'account_fiat_deposit_forbidden',
            'account_crypto_deposit_forbidden',
            'offboard', 'withdraw_forbidden', 'asset_freeze',
        ]
        for bt in known_types:
            if bt in block_type_status:
                out.append('{}: {}'.format(bt, block_type_status[bt]))
        for bt in block_type_status:
            if bt not in known_types:
                out.append('{}: {}'.format(bt, block_type_status[bt]))
        out.append('')

        # All raw records
        sorted_rows = sorted(rows,
                             key=lambda r: safe_str(r.get('case_create_datetime', '')))
        out.append('--- ALL RAW RECORDS (chronological) ---')
        for row in sorted_rows:
            dt = safe_str(row.get('case_create_datetime', ''))
            bs = safe_str(row.get('block_status', '')).upper()
            bt = safe_str(row.get('block_type', ''))
            reason = safe_str(row.get('block_reason', ''))
            days = safe_int(row.get('total_block_days', 0))
            cdept = safe_str(row.get('create_department', ''))
            odept = safe_str(row.get('owner_department', ''))
            unlock_t = safe_str(row.get('unlock_time', ''))
            unlock_str = ''
            if unlock_t and unlock_t != '(null)' and unlock_t != '':
                unlock_str = ' | unlocked: ' + unlock_t
            out.append('{} | {} | {} | {} | {} day(s) | {} \u2192 {}{}'.format(
                dt, bs, bt, reason, days, cdept, odept, unlock_str))

        return ProcessorResult(content='\n'.join(out), has_data=True)

    def _get_action_id(self, case_no):
        match = re.search(r'\d{10,}$', safe_str(case_no))
        return match.group(0) if match else safe_str(case_no)

    def _parse_date(self, date_str):
        from datetime import datetime as dt
        try:
            return dt.fromisoformat(
                safe_str(date_str).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            try:
                return dt.strptime(
                    safe_str(date_str), '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                return None