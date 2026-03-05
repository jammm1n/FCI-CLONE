"""
User Profile Processor.
Combines User Info 2 (alert counts, block statuses, last active time),
Fiat Partners (fiat partners, device/IP/language counts), and IP Country
into a single "User Profile" overview tab.
"""

from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_int, safe_bool, parse_array


class UserInfoExtendedProcessor(BaseProcessor):
    id = 'user_profile'
    label = 'User Profile'
    sort_order = 6  # Right after transaction summary

    required_file_types = ['USER_INFO_2', 'USER_INFO_FIAT_PARTNERS']
    optional_file_types = ['USER_INFO', 'IP_COUNTRY']

    required_fields = []

    consumed_fields = {
        'USER_INFO_2': [
            'ftm open case count', 'ftm total alerts count',
            'ctm total alerts count', 'sar total case count',
            'sar open case count', 'account block status',
            'login block status', 'trade block status',
            'asset freeze', 'withdraw forbidden',
            'fiat withdraw forbidden', 'offboard status',
            'kodex case count', 'last active time', 'deleted status',
        ],
        'USER_INFO_FIAT_PARTNERS': [
            'fiat partner', 'fiat fail vs. success',
            'unique card bind count', 'partner_ct',
            'doc integrity rejects', 'ip location used',
            'no. of device used', 'system language used',
        ],
        'IP_COUNTRY': [
            'ip country used',
        ],
    }

    def should_run(self, available_file_types, params):
        return bool({'USER_INFO_2', 'USER_INFO_FIAT_PARTNERS'} & set(available_file_types))

    def process(self, file_data, params, context):
        ui2_rows = file_data.get('USER_INFO_2', {}).get('rows', [])
        fp_rows = file_data.get('USER_INFO_FIAT_PARTNERS', {}).get('rows', [])

        has_ui2 = len(ui2_rows) > 0
        has_fp = len(fp_rows) > 0

        if not has_ui2 and not has_fp:
            return ProcessorResult(
                content='No user profile data available.',
                has_data=False,
            )

        sections = []

        if has_ui2:
            sections.append(self._build_ui2_section(ui2_rows[0], context))

        if has_fp:
            ip_rows = file_data.get('IP_COUNTRY', {}).get('rows', [])
            sections.append(self._build_fiat_partners_section(fp_rows[0], ip_rows))

        return ProcessorResult(
            content='\n\n'.join(sections),
            has_data=True,
        )

    def _build_ui2_section(self, row, context):
        lines = []
        lines.append('=== USER INFO (EXTENDED) ===')
        lines.append('')

        # Registration date from USER_INFO if available
        user_info = context.get('user_info')
        reg_date = None
        if user_info:
            reg_date = safe_str(user_info.get('Registration Date', ''))
        last_active = self._get_str(row, 'Last Active Time')

        if reg_date and reg_date != '(null)':
            lines.append('Registration Date: {}'.format(reg_date))
        if last_active and last_active != '(null)':
            lines.append('Last Active Time:  {}'.format(last_active))
        if reg_date or last_active:
            lines.append('')

        # Alert / case counts
        lines.append('--- ALERT & CASE COUNTS ---')
        lines.append('')
        ftm_open = self._get_int(row, 'FTM Open Case Count')
        ftm_total = self._get_int(row, 'FTM Total Alerts Count')
        ctm_total = self._get_int(row, 'CTM Total Alerts Count')
        sar_total = self._get_int(row, 'SAR Total Case Count')
        sar_open = self._get_int(row, 'SAR Open Case Count')
        kodex = self._get_int(row, 'Kodex Case Count')

        lines.append('FTM Alerts:  {} total, {} open case(s)'.format(
            ftm_total, ftm_open))
        lines.append('CTM Alerts:  {} total'.format(ctm_total))
        lines.append('SAR Cases:   {} total, {} open'.format(
            sar_total, sar_open))
        lines.append('Kodex Cases: {}'.format(kodex))
        lines.append('')

        # Account restrictions
        lines.append('--- ACCOUNT RESTRICTIONS ---')
        lines.append('')
        restrictions = [
            ('Account Block', 'Account Block Status'),
            ('Login Block', 'Login Block Status'),
            ('Trade Block', 'Trade Block Status'),
            ('Asset Freeze', 'Asset Freeze'),
            ('Withdraw Forbidden', 'Withdraw Forbidden'),
            ('Fiat Withdraw Forbidden', 'Fiat Withdraw Forbidden'),
            ('Offboard', 'Offboard Status'),
        ]

        active_restrictions = []
        for label, key in restrictions:
            val = self._get_bool(row, key)
            status = 'YES' if val else 'No'
            lines.append('{:<25s} {}'.format(label + ':', status))
            if val:
                active_restrictions.append(label)

        lines.append('')
        if active_restrictions:
            lines.append('ACTIVE RESTRICTIONS: {}'.format(
                ', '.join(active_restrictions)))
        else:
            lines.append('ACTIVE RESTRICTIONS: None')

        # Deleted status
        deleted = self._get_bool(row, 'Deleted Status')
        if deleted:
            lines.append('')
            lines.append('*** ACCOUNT DELETED ***')

        return '\n'.join(lines)

    def _build_fiat_partners_section(self, row, ip_rows):
        lines = []
        lines.append('=== FIAT PARTNERS & IP SUMMARY ===')
        lines.append('')

        # Fiat partners
        partners_raw = self._get_str(row, 'Fiat Partner')
        partners = parse_array(partners_raw)
        partner_ct = self._get_int(row, 'partner_ct')

        lines.append('--- FIAT PARTNERS ---')
        lines.append('')
        if partners:
            lines.append('Partners ({}):{}'.format(
                partner_ct or len(partners),
                ''.join('\n  - {}'.format(p) for p in partners)))
        else:
            lines.append('Partners: None')
        lines.append('')

        # Fiat fail vs success
        fail_success = self._get_str(row, 'Fiat Fail vs. Success')
        if fail_success:
            lines.append('Fiat Fail vs. Success: {}'.format(fail_success))

        # Card binds
        card_binds = self._get_int(row, 'Unique Card Bind Count')
        lines.append('Unique Card Binds:     {}'.format(card_binds))

        # Doc integrity rejects
        doc_rejects_raw = self._get_str(row, 'Doc Integrity Rejects')
        doc_rejects = parse_array(doc_rejects_raw)
        if doc_rejects:
            lines.append('Doc Integrity Rejects: {}'.format(
                ', '.join(doc_rejects)))
        else:
            lines.append('Doc Integrity Rejects: None')
        lines.append('')

        # Device/IP/Language metrics
        ip_locs = self._get_int(row, 'IP location Used')
        devices = self._get_int(row, 'No. of Device Used')
        sys_langs = self._get_int(row, 'System Language used')

        lines.append('--- DEVICE & IP METRICS ---')
        lines.append('')
        lines.append('IP Locations Used:       {}'.format(ip_locs))
        lines.append('Devices Used:            {}'.format(devices))
        lines.append('System Languages Used:   {}'.format(sys_langs))
        lines.append('')

        # IP Country Used (optional)
        if ip_rows:
            ip_countries = []
            for r in ip_rows:
                val = self._get_str(r, 'IP Country Used')
                if val and val != '(load_json_fail)' and val != '(null)':
                    ip_countries.append(val)

            if ip_countries:
                lines.append('--- IP COUNTRIES USED ---')
                lines.append('')
                for country in ip_countries:
                    lines.append('  {}'.format(country))
                lines.append('')

        return '\n'.join(lines)

    def _get_str(self, row, key):
        for k in [key, key.lower(), key.strip()]:
            if k in row:
                return safe_str(row[k])
        key_lower = key.lower().strip()
        for k, v in row.items():
            if safe_str(k).lower().strip() == key_lower:
                return safe_str(v)
        return ''

    def _get_int(self, row, key):
        for k in [key, key.lower(), key.strip()]:
            if k in row:
                return safe_int(row[k])
        key_lower = key.lower().strip()
        for k, v in row.items():
            if safe_str(k).lower().strip() == key_lower:
                return safe_int(v)
        return 0

    def _get_bool(self, row, key):
        for k in [key, key.lower(), key.strip()]:
            if k in row:
                return safe_bool(row[k])
        key_lower = key.lower().strip()
        for k, v in row.items():
            if safe_str(k).lower().strip() == key_lower:
                return safe_bool(v)
        return False
