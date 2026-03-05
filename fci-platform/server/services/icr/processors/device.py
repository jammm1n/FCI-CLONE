"""
Device & IP Analysis Processor.
Processes Device Analysis, Device Summary, and Device Direct Link spreadsheets.
Analyses login locations, languages, timezones, VPN usage, and shared devices.
"""

from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str, safe_float, safe_int, safe_bool, parse_array, fmt_usd, fmt_pct
from ..constants import SANCTIONED_JURISDICTIONS, RESTRICTED_JURISDICTIONS


class DeviceProcessor(BaseProcessor):
    id = 'device'
    label = 'Device & IP Analysis'
    sort_order = 20

    required_file_types = ['DEVICE_MAIN', 'DEVICE_SUM']
    optional_file_types = ['DEVICE_LINK', 'IT', 'BP', 'P2P']

    required_fields = [
        {
            'field': 'nationality',
            'message': 'Nationality is required for Device & IP analysis',
            'when': 'always',
        },
        {
            'field': 'residence',
            'message': 'Residence is required for Device & IP analysis',
            'when': 'always',
        },
        {
            'field': 'devices_used',
            'message': 'Devices Used is required when Device spreadsheet is uploaded',
            'when': 'always',
        },
        {
            'field': 'ip_locations',
            'message': 'Distinct IP Locations is required when Device spreadsheet is uploaded',
            'when': 'always',
        },
        {
            'field': 'sys_langs',
            'message': 'Distinct System Languages is required when Device spreadsheet is uploaded',
            'when': 'always',
        },
    ]

    consumed_fields = {
        'DEVICE_MAIN': [
            'fvideo_id/bnc_uuid', 'top_10_ip_locations', 'top_10_system_lang',
            'top_10_device_timezones', 'operation_count', 'vpn_used_count',
        ],
        'DEVICE_SUM': [
            'user_id', 'top_country_access', 'most_used_language',
            'vpn_usage_pct', 'sanctioned_locations', 'restricted_locations',
        ],
        'DEVICE_LINK': [
            'link_user_id', 'direct_shared_bnc_uuid', 'direct_shared_ip',
            'direct_shared_fvideo_id', 'is_kyc', 'is_offboard',
            'offboard_reason_plus_remarks', 'nationality/reg_country',
            'residence/op_country', 'sar_case', 'kodex_case_details',
            'is_account_block', 'is_trade_block', 'is_withdraw_forbidden',
        ],
    }

    def should_run(self, available_file_types, params):
        return bool({'DEVICE_MAIN', 'DEVICE_SUM'} & set(available_file_types))

    def process(self, file_data, params, context):
        uid = context.get('subject_uid', '')
        main_rows = file_data.get('DEVICE_MAIN', {}).get('rows', [])
        sum_rows = file_data.get('DEVICE_SUM', {}).get('rows', [])
        device_link_rows = file_data.get('DEVICE_LINK', {}).get('rows', [])

        nationality = safe_str(params.get('nationality', '')).upper()
        residence = safe_str(params.get('residence', '')).upper()
        devices_used = safe_int(params.get('devices_used', 0))
        ip_locations = safe_int(params.get('ip_locations', 0))
        sys_langs = safe_int(params.get('sys_langs', 0))

        sum_data = sum_rows[0] if sum_rows else {}
        top_country = safe_str(sum_data.get('top_country_access', ''))
        top_lang = safe_str(sum_data.get('most_used_language', ''))
        vpn_pct = safe_float(sum_data.get('vpn_usage_pct', 0))
        sanctioned_locs = safe_str(sum_data.get('sanctioned_locations', ''))
        restricted_locs = safe_str(sum_data.get('restricted_locations', ''))

        # Parse location data
        loc_map, total_logins = self._parse_locations(main_rows)
        loc_arr = sorted(loc_map.values(), key=lambda x: x['logins'], reverse=True)
        country_totals = {}
        for loc in loc_arr:
            country_totals.setdefault(loc['country'], 0)
            country_totals[loc['country']] += loc['logins']
        country_sorted = sorted(country_totals.keys(),
                                key=lambda c: country_totals[c], reverse=True)

        # Parse language data
        lang_map = self._parse_languages(main_rows)
        lang_keys = sorted(lang_map.keys(), key=lambda l: lang_map[l], reverse=True)

        # Parse timezone data
        tz_map = self._parse_timezones(main_rows)
        tz_keys = sorted(tz_map.keys(), key=lambda t: tz_map[t], reverse=True)

        # VPN totals
        total_ops = sum(safe_int(r.get('operation_count', 0)) for r in main_rows)
        total_vpn = sum(safe_int(r.get('vpn_used_count', 0)) for r in main_rows)

        # Shared device data from counterparty files
        cp_with_devices = self._find_cp_shared_devices(file_data, uid)

        sections = []
        sections.append(self._build_profile(
            devices_used, ip_locations, sys_langs,
            sanctioned_locs, restricted_locs))
        sections.append(self._build_location_breakdown(
            country_sorted, country_totals, loc_arr))
        sections.append(self._build_language_summary(lang_keys, lang_map))
        sections.append(self._build_shared_device_analysis(
            device_link_rows, cp_with_devices, uid))
        sections.append(self._build_device_summary(
            top_lang, top_country, devices_used, ip_locations, sys_langs,
            vpn_pct, total_vpn, total_ops, country_sorted, country_totals,
            lang_keys, loc_arr, nationality, residence,
            device_link_rows, cp_with_devices, tz_keys, tz_map, uid))

        return ProcessorResult(
            content='\n\n'.join(sections),
            has_data=True,
        )

    def _parse_locations(self, main_rows):
        loc_map = {}
        total_logins = 0
        for row in main_rows:
            locs = safe_str(row.get('top_10_ip_locations', ''))
            entries = [e.strip() for e in locs.split('||') if e.strip()]
            for entry in entries:
                import re
                country_match = re.search(r'Country:([^;]+)', entry)
                city_match = re.search(r'City:([^;]+)', entry)
                login_match = re.search(r'Login_Count:\s*(\d+)', entry)
                if country_match:
                    country = country_match.group(1).strip()
                    city = city_match.group(1).strip() if city_match else 'Unknown'
                    logins = int(login_match.group(1)) if login_match else 0
                    key = country + '|' + city
                    if key not in loc_map:
                        loc_map[key] = {'country': country, 'city': city, 'logins': 0}
                    loc_map[key]['logins'] += logins
                    total_logins += logins
        return loc_map, total_logins

    def _parse_languages(self, main_rows):
        lang_map = {}
        for row in main_rows:
            langs = safe_str(row.get('top_10_system_lang', ''))
            if not langs:
                continue
            langs = langs.strip().lstrip('[').rstrip(']')
            entries = [e.strip() for e in langs.split('||') if e.strip()]
            for entry in entries:
                entry = entry.strip('"\'')
                parts = entry.split(';')
                if len(parts) >= 2:
                    import re
                    lang = parts[0].strip().strip('"\'[]')
                    count_match = re.search(r'Login_Count:\s*(\d+)', parts[1])
                    count = int(count_match.group(1)) if count_match else 0
                    if lang:
                        lang_map.setdefault(lang, 0)
                        lang_map[lang] += count
        return lang_map

    def _parse_timezones(self, main_rows):
        import re
        tz_map = {}
        for row in main_rows:
            tzs = safe_str(row.get('top_10_device_timezones', ''))
            if not tzs:
                continue
            tzs = tzs.strip().lstrip('[').rstrip(']')
            raw_entries = tzs.split('||')
            entries = []
            for chunk in raw_entries:
                for sub in chunk.split(','):
                    cleaned = sub.strip().strip('"\'')
                    if cleaned:
                        entries.append(cleaned)
            for entry in entries:
                parts = entry.split(';')
                if len(parts) >= 2:
                    tz = parts[0].strip().strip('"\'[]')
                    count_match = re.search(r'Login_Count:\s*(\d+)', parts[1])
                    count = int(count_match.group(1)) if count_match else 0
                    if tz in ('GMT+', 'GMT', 'UTC', 'GMT+0', 'GMT+00'):
                        tz = 'GMT+0'
                    if tz and count > 0:
                        tz_map.setdefault(tz, 0)
                        tz_map[tz] += count
        return tz_map

    def _find_cp_shared_devices(self, file_data, uid):
        cp_with_devices = []
        for ft in ['IT', 'BP', 'P2P']:
            rows = file_data.get(ft, {}).get('rows', [])
            for row in rows:
                lid = safe_str(row.get('link_user_id', ''))
                if not lid or lid == uid:
                    continue
                uuids = parse_array(row.get('direct_shared_bnc_uuid', ''))
                ips = parse_array(row.get('direct_shared_ip', ''))
                fvids = parse_array(row.get('direct_shared_fvideo_id', ''))
                if uuids or ips or fvids:
                    cp_with_devices.append({
                        'uid': lid, 'uuids': uuids,
                        'ips': ips, 'fvids': fvids,
                    })
        return cp_with_devices

    def _build_profile(self, devices_used, ip_locations, sys_langs,
                       sanctioned_locs, restricted_locs):
        p = []
        p.append('=== DEVICE PROFILE ===')
        p.append('')
        p.append('Headline Figures (from C360 front end):')
        p.append('  Devices Used: {}'.format(devices_used))
        p.append('  Distinct IP Locations: {}'.format(ip_locations))
        p.append('  Distinct System Languages: {}'.format(sys_langs))
        p.append('')
        if sanctioned_locs and sanctioned_locs != '(null)':
            p.append('\u26a0\ufe0f Sanctioned Locations: ' + sanctioned_locs)
        if restricted_locs and restricted_locs != '(null)':
            p.append('\u26a0\ufe0f Restricted Locations: ' + restricted_locs)
        return '\n'.join(p)

    def _build_location_breakdown(self, country_sorted, country_totals, loc_arr):
        lines = []
        lines.append('=== LOCATION BREAKDOWN ===')
        lines.append('')
        for c in country_sorted:
            lines.append('  {}: {} logins'.format(c, country_totals[c]))
            c_lower = c.lower()
            for s in SANCTIONED_JURISDICTIONS:
                if s in c_lower:
                    lines.append('    \u26a0\ufe0f SANCTIONED JURISDICTION')
            for r in RESTRICTED_JURISDICTIONS:
                if r in c_lower:
                    lines.append('    \u26a0\ufe0f RESTRICTED JURISDICTION')
        lines.append('')
        lines.append('By City (top 15):')
        for loc in loc_arr[:15]:
            lines.append('  {} / {}: {} logins'.format(
                loc['country'], loc['city'], loc['logins']))
        return '\n'.join(lines)

    def _build_language_summary(self, lang_keys, lang_map):
        la = []
        la.append('=== LANGUAGE SUMMARY ===')
        la.append('')
        if lang_keys:
            for lang in lang_keys:
                la.append('  {}: {} sessions'.format(lang, lang_map[lang]))
        else:
            la.append('  No language data available.')
        return '\n'.join(la)

    def _build_shared_device_analysis(self, device_link_rows, cp_with_devices, uid):
        sh = []
        sh.append('=== SHARED DEVICE ANALYSIS ===')
        sh.append('')
        if device_link_rows:
            sh.append('Device Direct Link Users: {}'.format(len(device_link_rows)))
            sh.append('')
            for row in device_link_rows:
                lid = safe_str(row.get('link_user_id', ''))
                if not lid or lid == uid:
                    continue
                shared_uuids = parse_array(row.get('direct_shared_bnc_uuid', ''))
                shared_ips = parse_array(row.get('direct_shared_ip', ''))
                shared_fvideo = parse_array(row.get('direct_shared_fvideo_id', ''))
                is_kyc = safe_bool(row.get('is_kyc', True))
                is_offboard = safe_bool(row.get('is_offboard', False))
                off_reason = safe_str(row.get('offboard_reason_plus_remarks', ''))
                nat = safe_str(row.get('nationality/reg_country', ''))
                res = safe_str(row.get('residence/op_country', ''))
                sars = parse_array(row.get('sar_case', ''))
                kodex = parse_array(row.get('kodex_case_details', ''))
                blocked = (safe_bool(row.get('is_account_block', False))
                           or safe_bool(row.get('is_trade_block', False))
                           or safe_bool(row.get('is_withdraw_forbidden', False)))

                sh.append('UID {}{} | {}/{}'.format(
                    lid, '' if is_kyc else ' [NO KYC]',
                    nat or '?', res or '?'))
                sh.append('  Shared: {} UUID(s), {} IP(s), {} FaceVideo(s)'.format(
                    len(shared_uuids), len(shared_ips), len(shared_fvideo)))
                if shared_uuids:
                    sh.append('  UUIDs: ' + ', '.join(shared_uuids))
                if shared_ips:
                    sh.append('  IPs: ' + ', '.join(shared_ips))
                if shared_fvideo:
                    sh.append('  FaceVideo: ' + ', '.join(shared_fvideo))
                if is_offboard:
                    sh.append('  \u26a0\ufe0f OFFBOARDED: ' + off_reason)
                if blocked:
                    sh.append('  \u26a0\ufe0f BLOCKED')
                if sars:
                    sh.append('  ICR: ' + ', '.join(sars))
                if kodex:
                    sh.append('  LE: {} request(s)'.format(len(kodex)))
                sh.append('')
        else:
            sh.append('No device direct link users found.')

        if cp_with_devices:
            sh.append('--- COUNTERPARTIES WITH SHARED DEVICES ---')
            sh.append('')
            for cp in cp_with_devices:
                sh.append('UID {}: {} UUID(s), {} IP(s), {} FaceVideo(s)'.format(
                    cp['uid'], len(cp['uuids']), len(cp['ips']), len(cp['fvids'])))
                if cp['uuids']:
                    sh.append('  UUIDs: ' + ', '.join(cp['uuids']))
                if cp['ips']:
                    sh.append('  IPs: ' + ', '.join(cp['ips']))

        return '\n'.join(sh)

    def _build_device_summary(self, top_lang, top_country, devices_used,
                               ip_locations, sys_langs, vpn_pct, total_vpn,
                               total_ops, country_sorted, country_totals,
                               lang_keys, loc_arr, nationality, residence,
                               device_link_rows, cp_with_devices,
                               tz_keys, tz_map, uid):
        ds = []
        ds.append('=== DEVICE SUMMARY ===')
        ds.append('')
        ds.append('The user has used {} primarily and accessed from {}.'.format(
            top_lang or 'en-US', top_country or 'unknown'))
        ds.append('')
        ds.append('Headline: {} device(s), {} distinct IP location(s), {} system language(s).'.format(
            devices_used, ip_locations, sys_langs))
        ds.append('VPN usage: {} of total accesses ({} of {} operations).'.format(
            fmt_pct(vpn_pct), total_vpn, total_ops))
        ds.append('')

        sanctioned_found = []
        restricted_found = []
        for c in country_sorted:
            c_lower = c.lower()
            for s in SANCTIONED_JURISDICTIONS:
                if s in c_lower:
                    sanctioned_found.append('{} ({} logins)'.format(
                        c, country_totals[c]))
            for r in RESTRICTED_JURISDICTIONS:
                if r in c_lower:
                    restricted_found.append('{} ({} logins)'.format(
                        c, country_totals[c]))

        if sanctioned_found:
            ds.append('\u26a0\ufe0f SANCTIONED JURISDICTION ACCESS: ' + ', '.join(sanctioned_found))
        else:
            ds.append('Sanctioned jurisdiction access: None detected.')
        if restricted_found:
            ds.append('\u26a0\ufe0f RESTRICTED JURISDICTION ACCESS: ' + ', '.join(restricted_found))
        else:
            ds.append('Restricted jurisdiction access: None detected.')
        ds.append('')

        country_count = len(country_sorted)
        lang_count = len(lang_keys)
        city_count = len(loc_arr)

        top_country_norm = (top_country or '').lower()
        nat_norm = nationality.lower()
        res_norm = residence.lower()
        nat_mismatch = False
        if top_country_norm and nat_norm and res_norm:
            top_matches_nat = (top_country_norm.find(nat_norm) >= 0
                               or nat_norm.find(top_country_norm[:2]) >= 0)
            top_matches_res = (top_country_norm.find(res_norm) >= 0
                               or res_norm.find(top_country_norm[:2]) >= 0)
            nat_mismatch = not top_matches_nat and not top_matches_res

        multi_score = 0
        if country_count <= 3:
            multi_score += 0
        elif country_count <= 5:
            multi_score += 1
        elif country_count <= 10:
            multi_score += 2
        else:
            multi_score += 3
        if lang_count <= 1:
            multi_score += 0
        elif lang_count <= 3:
            multi_score += 1
        else:
            multi_score += 2
        if city_count <= 5:
            multi_score += 0
        elif city_count <= 15:
            multi_score += 1
        else:
            multi_score += 2
        if nat_mismatch:
            multi_score += 2

        multi_risk = 'LOW'
        if multi_score >= 3:
            multi_risk = 'MEDIUM'
        if multi_score >= 5:
            multi_risk = 'HIGH'

        factors = []
        factors.append('{} countries'.format(country_count))
        factors.append('{} languages'.format(lang_count))
        factors.append('{} distinct cities'.format(city_count))
        if nat_mismatch:
            factors.append('nationality/residence MISMATCH with primary access country')

        ds.append('Multi-person access likelihood: {} (score: {}/9 \u2014 {})'.format(
            multi_risk, multi_score, ', '.join(factors)))
        ds.append('')

        dl_count = len([r for r in device_link_rows
                        if safe_str(r.get('link_user_id', '')) != uid])
        ds.append('Device-linked UIDs: {}'.format(dl_count))
        if cp_with_devices:
            ds.append('Counterparties sharing devices: {}'.format(len(cp_with_devices)))
            ds.append('  UIDs: ' + ', '.join(c['uid'] for c in cp_with_devices))

        if tz_keys:
            ds.append('')
            ds.append('Timezones:')
            for tz in tz_keys:
                ds.append('  {}: {} login sessions'.format(tz, tz_map[tz]))

        return '\n'.join(ds)