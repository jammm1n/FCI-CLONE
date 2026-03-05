"""
Counterparty Analysis Processor.
Processes Internal Transfer, Binance Pay, P2P, and Device Link spreadsheets.
Identifies risk-flagged counterparties, validates header counts, and
produces a full counterparty review output.
"""

from .base import BaseProcessor, ProcessorResult
from ..utils import (
    safe_str, safe_float, safe_int, safe_bool,
    parse_array, fmt_usd, fmt_pct_display, extract_block_reasons,
)


class CounterpartyProcessor(BaseProcessor):
    id = 'counterparty'
    label = 'Counterparty Analysis'
    sort_order = 10

    required_file_types = ['IT', 'BP', 'P2P']
    optional_file_types = ['DEVICE_LINK', 'CP_SUMMARY', 'DEVICE_LINK_SUMMARY']

    required_fields = [
        {
            'field': 'it_count',
            'message': 'IT Direct Link Users count is required when IT spreadsheet is uploaded',
            'when': lambda available, params: 'IT' in available,
        },
    ]

    consumed_fields = {
        'IT': [
            'link_user_id', 'total_internal_crypto_trans_amt_usd',
            'total_internal_crypto_trans_amt_usd%',
            'is_kyc', 'is_offboard', 'offboard_reason_plus_remarks',
            'nationality/reg_country', 'residence/op_country',
            'link_user_net_asset_holding_usdt',
            'sar_case', 'kodex_case_details', 'onchain_alert_summary',
            'block_case_cnt', 'block_case_details',
            'is_account_block', 'is_login_block', 'is_trade_block',
            'is_asset_freeze', 'is_withdraw_forbidden',
            'is_fiat_withdraw_forbidden',
            'counterparty_company_user_flag', 'counterparty_sub_account_flag',
            'partical_freeze_details', 'withdraw_black_list_details',
            'direct_shared_bnc_uuid', 'direct_shared_ip', 'direct_shared_fvideo_id',
            'crypto_deposit_count_from_link_user', 'crypto_deposit_amt_usdt_from_link_user',
            'crypto_withdraw_count_to_link_user', 'crypto_withdraw_amt_usdt_to_link_user',
        ],
        'BP': [
            'link_user_id', 'total_bpay_trans_amt_usd',
            'total_bpay_trans_amt_usd%',
            'is_kyc', 'is_offboard', 'offboard_reason_plus_remarks',
            'nationality/reg_country', 'residence/op_country',
            'link_user_net_asset_holding_usdt',
            'sar_case', 'kodex_case_details', 'onchain_alert_summary',
            'block_case_cnt', 'block_case_details',
            'is_account_block', 'is_login_block', 'is_trade_block',
            'is_asset_freeze', 'is_withdraw_forbidden',
            'is_fiat_withdraw_forbidden',
            'counterparty_company_user_flag', 'counterparty_sub_account_flag',
            'partical_freeze_details', 'withdraw_black_list_details',
            'direct_shared_bnc_uuid', 'direct_shared_ip', 'direct_shared_fvideo_id',
            'crypto_deposit_count_from_link_user', 'crypto_deposit_amt_usdt_from_link_user',
            'crypto_withdraw_count_to_link_user', 'crypto_withdraw_amt_usdt_to_link_user',
        ],
        'P2P': [
            'link_user_id', 'total_p2p_trans_amt_usd',
            'total_p2p_trans_amt_usd%',
            'is_kyc', 'is_offboard', 'offboard_reason_plus_remarks',
            'nationality/reg_country', 'residence/op_country',
            'link_user_net_asset_holding_usdt',
            'sar_case', 'kodex_case_details', 'onchain_alert_summary',
            'block_case_cnt', 'block_case_details',
            'is_account_block', 'is_login_block', 'is_trade_block',
            'is_asset_freeze', 'is_withdraw_forbidden',
            'is_fiat_withdraw_forbidden',
            'p2p_deposit_count_from_link_user', 'p2p_withdraw_count_to_link_user',
        ],
        'DEVICE_LINK': [
            'link_user_id', 'direct_shared_bnc_uuid', 'direct_shared_ip',
            'direct_shared_fvideo_id',
        ],
        'CP_SUMMARY': [
            'internal cp user count',
            'internal cp users total deposit amount',
            'internal cp users total withdraw amount',
            'internal cp user also with le request count',
            'internal cp user count also share ip',
            'internal cp user count with sar case',
            'internal cp user also blocked count',
        ],
        'DEVICE_LINK_SUMMARY': [
            'device linked user count',
            'device linked users total deposit amount',
            'device linked users total withdraw amount',
            'device linked user also with le request count',
            'device linked user count also share ip',
            'device linked user count with sar case',
            'device linked user also share internal cp count',
            'device linked user also share ext wallet count',
            'device linked user also blocked count',
        ],
    }

    def should_run(self, available_file_types, params):
        return bool({'IT', 'BP', 'P2P'} & set(available_file_types))

    def process(self, file_data, params, context):
        uid = context.get('subject_uid', '')
        it_rows = file_data.get('IT', {}).get('rows', [])
        bp_rows = file_data.get('BP', {}).get('rows', [])
        p2p_rows = file_data.get('P2P', {}).get('rows', [])
        device_link_rows = file_data.get('DEVICE_LINK', {}).get('rows', [])

        cp_map = {}

        def add_to_map(rows, source, vol_col, pct_col):
            for row in rows:
                lid = safe_str(row.get('link_user_id', ''))
                if not lid or lid == uid or lid == '(null)':
                    continue
                if lid not in cp_map:
                    cp_map[lid] = self._empty_cp(lid)
                cp = cp_map[lid]
                if source not in cp['sources']:
                    cp['sources'].append(source)
                cp['total_vol'] += safe_float(row.get(vol_col, 0))
                if pct_col:
                    raw_pct = row.get(pct_col, '')
                    if raw_pct is not None and raw_pct != '':
                        pct_num = safe_float(str(raw_pct).replace('%', ''))
                        if pct_num > 1:
                            pct_num = pct_num / 100
                        cp['pct_by_source'][source] = pct_num
                self._merge_cp_flags(cp, row)

        add_to_map(it_rows, 'IT', 'total_internal_crypto_trans_amt_usd',
                   'total_internal_crypto_trans_amt_usd%')
        add_to_map(bp_rows, 'BP', 'total_bpay_trans_amt_usd',
                   'total_bpay_trans_amt_usd%')

        # P2P handled separately
        p2p_map = {}
        p2p_self_ref = False
        for row in p2p_rows:
            lid = safe_str(row.get('link_user_id', ''))
            if not lid or lid == '(null)':
                continue
            if lid == uid:
                p2p_self_ref = True
                continue
            if lid not in p2p_map:
                p2p_map[lid] = {
                    'uid': lid, 'total_vol': 0, 'tx_count': 0,
                    'row': row, 'pct': 0,
                }
            p2p_map[lid]['total_vol'] += safe_float(
                row.get('total_p2p_trans_amt_usd', 0))
            raw_pct = row.get('total_p2p_trans_amt_usd%', '')
            if raw_pct is not None and raw_pct != '':
                pct_num = safe_float(str(raw_pct).replace('%', ''))
                if pct_num > 1:
                    pct_num = pct_num / 100
                p2p_map[lid]['pct'] = pct_num
            p2p_map[lid]['tx_count'] += (
                safe_int(row.get('p2p_deposit_count_from_link_user', 0))
                + safe_int(row.get('p2p_withdraw_count_to_link_user', 0))
            )

        # Self-reference check for IT/BP
        self_ref_found = False
        for row in it_rows + bp_rows:
            if safe_str(row.get('link_user_id', '')) == uid:
                self_ref_found = True
                break

        # Count and volume per source
        it_cp_count, it_vol = 0, 0
        for row in it_rows:
            lid = safe_str(row.get('link_user_id', ''))
            if lid and lid != uid and lid != '(null)':
                it_cp_count += 1
                it_vol += safe_float(row.get('total_internal_crypto_trans_amt_usd', 0))

        bp_cp_count, bp_vol = 0, 0
        for row in bp_rows:
            lid = safe_str(row.get('link_user_id', ''))
            if lid and lid != uid and lid != '(null)':
                bp_cp_count += 1
                bp_vol += safe_float(row.get('total_bpay_trans_amt_usd', 0))

        # Duplicate detection
        it_uids = set()
        bp_uids = set()
        dupes = []
        for r in it_rows:
            lid = safe_str(r.get('link_user_id', ''))
            if lid and lid != uid and lid != '(null)':
                it_uids.add(lid)
        for r in bp_rows:
            lid = safe_str(r.get('link_user_id', ''))
            if lid and lid != uid and lid != '(null)':
                bp_uids.add(lid)
                if lid in it_uids:
                    dupes.append(lid)

        unique_count = len(cp_map)
        combined_vol = it_vol + bp_vol
        hexa_it_count = safe_int(params.get('it_count', 0))

        # Classify IT/BP counterparties
        flagged, clean = self._classify_counterparties(cp_map, uid)

        # Classify P2P counterparties
        p2p_flagged, p2p_clean = self._classify_p2p(p2p_map, uid)

        # Sort by volume
        flagged.sort(key=lambda c: c['total_vol'], reverse=True)
        p2p_flagged.sort(key=lambda c: c['total_vol'], reverse=True)

        # Build output sections
        sections = []

        # CP and device link summaries at the top (if available)
        cp_dl_section = self._build_cp_dl_summary(file_data)
        if cp_dl_section:
            sections.append(cp_dl_section)

        sections.append(self._build_header_validation(
            it_cp_count, it_vol, bp_cp_count, bp_vol, dupes,
            unique_count, combined_vol, hexa_it_count,
            self_ref_found, p2p_self_ref, uid))
        sections.append(self._build_flagged_section(flagged, p2p_flagged))
        sections.append(self._build_clean_section(
            clean, p2p_clean, flagged, p2p_flagged))
        sections.append(self._build_p2p_totals(p2p_map))
        sections.append(self._build_summary(
            it_cp_count, bp_cp_count, p2p_map, device_link_rows,
            unique_count, combined_vol, flagged, p2p_flagged,
            clean, p2p_clean, self_ref_found, uid))

        return ProcessorResult(
            content='\n\n'.join(sections),
            has_data=True,
        )

    def _empty_cp(self, lid):
        return {
            'uid': lid, 'sources': [], 'total_vol': 0, 'is_kyc': True,
            'is_offboard': False, 'offboard_reason': '',
            'nationality': '', 'residence': '',
            'balance': 0, 'sar_cases': [], 'kodex_cases': [],
            'onchain_alerts': [], 'block_count': 0, 'block_details': [],
            'is_account_block': False, 'is_login_block': False,
            'is_trade_block': False, 'is_asset_freeze': False,
            'is_withdraw_forbidden': False, 'is_fiat_withdraw_forbidden': False,
            'is_crypto_deposit_forbidden': False, 'is_fiat_deposit_forbidden': False,
            'is_company_user': False, 'is_sub_account': False,
            'partial_freeze': [], 'withdraw_blacklist': [],
            'shared_uuids': [], 'shared_ips': [], 'shared_fvideo': [],
            'deposit_count': 0, 'deposit_amt': 0,
            'withdraw_count': 0, 'withdraw_amt': 0,
            'pct_by_source': {},
        }

    def _merge_cp_flags(self, cp, row):
        cp['is_kyc'] = cp['is_kyc'] and safe_bool(row.get('is_kyc', True))
        if safe_bool(row.get('is_offboard', False)):
            cp['is_offboard'] = True
            cp['offboard_reason'] = (
                safe_str(row.get('offboard_reason_plus_remarks', ''))
                or cp['offboard_reason']
            )
        nat = safe_str(row.get('nationality/reg_country', ''))
        res = safe_str(row.get('residence/op_country', ''))
        if nat and nat != 'NONE':
            cp['nationality'] = nat
        if res and res != 'NONE':
            cp['residence'] = res
        cp['balance'] = max(
            cp['balance'],
            safe_float(row.get('link_user_net_asset_holding_usdt', 0)))

        for s in parse_array(row.get('sar_case', '')):
            if s not in cp['sar_cases']:
                cp['sar_cases'].append(s)
        for k in parse_array(row.get('kodex_case_details', '')):
            if k not in cp['kodex_cases']:
                cp['kodex_cases'].append(k)
        for o in parse_array(row.get('onchain_alert_summary', '')):
            if o not in cp['onchain_alerts']:
                cp['onchain_alerts'].append(o)

        cp['block_count'] = max(
            cp['block_count'],
            safe_int(row.get('block_case_cnt', 0)))
        for b in parse_array(row.get('block_case_details', '')):
            if b not in cp['block_details']:
                cp['block_details'].append(b)
                b_lower = b.lower()
                if 'account_crypto_deposit_forbidden' in b_lower:
                    cp['is_crypto_deposit_forbidden'] = True
                if 'account_fiat_deposit_forbidden' in b_lower:
                    cp['is_fiat_deposit_forbidden'] = True

        if safe_bool(row.get('is_account_block', False)):
            cp['is_account_block'] = True
        if safe_bool(row.get('is_login_block', False)):
            cp['is_login_block'] = True
        if safe_bool(row.get('is_trade_block', False)):
            cp['is_trade_block'] = True
        if safe_bool(row.get('is_asset_freeze', False)):
            cp['is_asset_freeze'] = True
        if safe_bool(row.get('is_withdraw_forbidden', False)):
            cp['is_withdraw_forbidden'] = True
        if safe_bool(row.get('is_fiat_withdraw_forbidden', False)):
            cp['is_fiat_withdraw_forbidden'] = True
        if safe_bool(row.get('counterparty_company_user_flag', False)):
            cp['is_company_user'] = True
        if safe_bool(row.get('counterparty_sub_account_flag', False)):
            cp['is_sub_account'] = True

        for p in parse_array(row.get('partical_freeze_details', '')):
            if p not in cp['partial_freeze']:
                cp['partial_freeze'].append(p)
        for w in parse_array(row.get('withdraw_black_list_details', '')):
            if w not in cp['withdraw_blacklist']:
                cp['withdraw_blacklist'].append(w)
        for u in parse_array(row.get('direct_shared_bnc_uuid', '')):
            if u not in cp['shared_uuids']:
                cp['shared_uuids'].append(u)
        for ip in parse_array(row.get('direct_shared_ip', '')):
            if ip not in cp['shared_ips']:
                cp['shared_ips'].append(ip)
        for fv in parse_array(row.get('direct_shared_fvideo_id', '')):
            if fv not in cp['shared_fvideo']:
                cp['shared_fvideo'].append(fv)

        cp['deposit_count'] += safe_int(
            row.get('crypto_deposit_count_from_link_user', 0))
        cp['deposit_amt'] += safe_float(
            row.get('crypto_deposit_amt_usdt_from_link_user', 0))
        cp['withdraw_count'] += safe_int(
            row.get('crypto_withdraw_count_to_link_user', 0))
        cp['withdraw_amt'] += safe_float(
            row.get('crypto_withdraw_amt_usdt_to_link_user', 0))

    def _classify_counterparties(self, cp_map, uid):
        flagged = []
        clean = []
        for lid, cp in cp_map.items():
            flags = self._get_flags(cp)
            if flags:
                cp['flags'] = flags
                flagged.append(cp)
            else:
                clean.append(cp)
        return flagged, clean

    def _get_flags(self, cp):
        flags = []
        if cp['kodex_cases']:
            flags.append('LE: {} requests'.format(len(cp['kodex_cases'])))
        if cp['sar_cases']:
            flags.append('ICR: {}'.format(len(cp['sar_cases'])))
        if cp['is_offboard']:
            flags.append('OFFBOARDED: {}'.format(cp['offboard_reason']))

        has_block = (
            cp['is_account_block'] or cp['is_trade_block']
            or cp['is_withdraw_forbidden'] or cp['is_login_block']
            or cp['is_asset_freeze'] or cp['is_crypto_deposit_forbidden']
            or cp['is_fiat_deposit_forbidden']
        )
        if has_block:
            bt = []
            if cp['is_account_block']:
                bt.append('account')
            if cp['is_login_block']:
                bt.append('login')
            if cp['is_trade_block']:
                bt.append('trade')
            if cp['is_withdraw_forbidden']:
                bt.append('withdraw')
            if cp['is_asset_freeze']:
                bt.append('asset_freeze')
            if cp['is_fiat_withdraw_forbidden']:
                bt.append('fiat_withdraw')
            if cp['is_crypto_deposit_forbidden']:
                bt.append('crypto_deposit')
            if cp['is_fiat_deposit_forbidden']:
                bt.append('fiat_deposit')
            block_reasons = extract_block_reasons(cp['block_details'])
            block_line = 'BLOCKED: ' + ', '.join(bt)
            if block_reasons:
                block_line += ' | Reason: ' + '; '.join(block_reasons)
            flags.append(block_line)

        if cp['partial_freeze']:
            flags.append('PARTIAL FREEZE: {} entries'.format(
                len(cp['partial_freeze'])))
        if cp['withdraw_blacklist']:
            flags.append('WITHDRAW BLACKLIST: {} entries'.format(
                len(cp['withdraw_blacklist'])))

        sig_onchain = []
        info_onchain = []
        for a in cp['onchain_alerts']:
            al = a.lower()
            if any(kw in al for kw in ['sanctioned', 'fraudulent', 'illicit', 'sanctioncountries']):
                sig_onchain.append(a)
            else:
                info_onchain.append(a)
        if sig_onchain:
            flags.append('ON-CHAIN (HIGH RISK): ' + ', '.join(sig_onchain))
        if info_onchain:
            flags.append('ON-CHAIN (OTHER): ' + ', '.join(info_onchain))

        return flags

    def _classify_p2p(self, p2p_map, uid):
        flagged = []
        clean = []
        for lid, p in p2p_map.items():
            row = p['row']
            flags = []

            kodex = parse_array(row.get('kodex_case_details', ''))
            if kodex:
                flags.append('LE: {} requests'.format(len(kodex)))
            sars = parse_array(row.get('sar_case', ''))
            if sars:
                flags.append('ICR: {}'.format(len(sars)))
            if safe_bool(row.get('is_offboard', False)):
                flags.append('OFFBOARDED: {}'.format(
                    safe_str(row.get('offboard_reason_plus_remarks', ''))))

            p2p_blocks = parse_array(row.get('block_case_details', ''))
            p2p_crypto_deposit = False
            p2p_fiat_deposit = False
            for b in p2p_blocks:
                b_lower = b.lower()
                if 'account_crypto_deposit_forbidden' in b_lower:
                    p2p_crypto_deposit = True
                if 'account_fiat_deposit_forbidden' in b_lower:
                    p2p_fiat_deposit = True

            has_block = (
                safe_bool(row.get('is_account_block', False))
                or safe_bool(row.get('is_trade_block', False))
                or safe_bool(row.get('is_withdraw_forbidden', False))
                or safe_bool(row.get('is_login_block', False))
                or safe_bool(row.get('is_asset_freeze', False))
                or p2p_crypto_deposit or p2p_fiat_deposit
            )
            if has_block:
                bt = []
                if safe_bool(row.get('is_account_block', False)):
                    bt.append('account')
                if safe_bool(row.get('is_login_block', False)):
                    bt.append('login')
                if safe_bool(row.get('is_trade_block', False)):
                    bt.append('trade')
                if safe_bool(row.get('is_withdraw_forbidden', False)):
                    bt.append('withdraw')
                if safe_bool(row.get('is_asset_freeze', False)):
                    bt.append('asset_freeze')
                if safe_bool(row.get('is_fiat_withdraw_forbidden', False)):
                    bt.append('fiat_withdraw')
                if p2p_crypto_deposit:
                    bt.append('crypto_deposit')
                if p2p_fiat_deposit:
                    bt.append('fiat_deposit')
                block_reasons = extract_block_reasons(p2p_blocks)
                block_line = 'BLOCKED: ' + ', '.join(bt)
                if block_reasons:
                    block_line += ' | Reason: ' + '; '.join(block_reasons)
                flags.append(block_line)

            onchain = parse_array(row.get('onchain_alert_summary', ''))
            sig_oc = []
            info_oc = []
            for a in onchain:
                al = a.lower()
                if any(kw in al for kw in ['sanctioned', 'fraudulent', 'illicit', 'sanctioncountries']):
                    sig_oc.append(a)
                else:
                    info_oc.append(a)
            if sig_oc:
                flags.append('ON-CHAIN (HIGH RISK): ' + ', '.join(sig_oc))
            if info_oc:
                flags.append('ON-CHAIN (OTHER): ' + ', '.join(info_oc))

            p['is_kyc'] = safe_bool(row.get('is_kyc', True))
            p['nationality'] = safe_str(row.get('nationality/reg_country', ''))
            p['residence'] = safe_str(row.get('residence/op_country', ''))
            p['balance'] = safe_float(
                row.get('link_user_net_asset_holding_usdt', 0))

            if flags:
                p['flags'] = flags
                p['kodex'] = kodex
                p['sars'] = sars
                p['onchain'] = onchain
                flagged.append(p)
            else:
                clean.append(p)

        return flagged, clean

    def _format_cp_entry(self, cp):
        lines = []
        kyc_tag = ' [NO KYC]' if cp['is_kyc'] is False else ''
        company_tag = ' [COMPANY]' if cp.get('is_company_user') else ''
        sub_tag = ' [SUB-ACCOUNT]' if cp.get('is_sub_account') else ''
        nat_res = (cp.get('nationality') or '?') + '/' + (cp.get('residence') or '?')

        conc_str = ''
        if cp.get('pct_by_source'):
            conc_parts = []
            for src, p in cp['pct_by_source'].items():
                display = fmt_pct_display(p)
                if display:
                    conc_parts.append('{}: {}'.format(src, display))
            if conc_parts:
                conc_str = ' | Conc: ' + ', '.join(conc_parts)

        lines.append('UID {}{}{}{} | {} | {} | Vol: {}{} | Bal: {}'.format(
            cp['uid'], kyc_tag, company_tag, sub_tag,
            '+'.join(cp.get('sources', [])),
            nat_res, fmt_usd(cp['total_vol']), conc_str,
            fmt_usd(cp.get('balance', 0))))

        for flag in cp.get('flags', []):
            lines.append('  \u2192 ' + flag)

        kodex = cp.get('kodex_cases', [])
        if kodex:
            for k in kodex[:3]:
                lines.append('    ' + k)
            if len(kodex) > 3:
                lines.append('    (+{} more)'.format(len(kodex) - 3))

        sars = cp.get('sar_cases', [])
        if sars:
            lines.append('  ICR refs: ' + ', '.join(sars))

        if cp.get('shared_uuids'):
            lines.append('  \u2139 SHARED DEVICES: {} UUID(s), {} IP(s)'.format(
                len(cp['shared_uuids']), len(cp.get('shared_ips', []))))

        lines.append('')
        return '\n'.join(lines)

    def _build_cp_dl_summary(self, file_data):
        """Build combined CP and Device Link summary section."""
        cp_rows = file_data.get('CP_SUMMARY', {}).get('rows', [])
        dl_rows = file_data.get('DEVICE_LINK_SUMMARY', {}).get('rows', [])

        if not cp_rows and not dl_rows:
            return None

        parts = []

        if cp_rows:
            row = cp_rows[0]
            lines = []
            lines.append('=== INTERNAL TRANSFER (CP) SUMMARY ===')
            lines.append('')
            count = safe_int(self._ci(row, 'Internal CP User Count'))
            dep = safe_float(self._ci(row, 'Internal CP Users Total Deposit Amount'))
            wd = safe_float(self._ci(row, 'Internal CP Users Total Withdraw Amount'))
            le = safe_int(self._ci(row, 'Internal CP user also with LE request Count'))
            ip = safe_int(self._ci(row, 'Internal CP User Count also share IP'))
            sar = safe_int(self._ci(row, 'Internal CP User Count with SAR Case'))
            blocked = safe_int(self._ci(row, 'Internal CP User also blocked Count'))

            lines.append('Internal CP Users:         {}'.format(count))
            lines.append('Total Deposit Amount:      {}'.format(fmt_usd(dep)))
            lines.append('Total Withdraw Amount:     {}'.format(fmt_usd(wd)))
            lines.append('')
            lines.append('Also with LE Request:      {}'.format(le))
            lines.append('Also Share IP:             {}'.format(ip))
            lines.append('With SAR Case:             {}'.format(sar))
            lines.append('Also Blocked:              {}'.format(blocked))
            parts.append('\n'.join(lines))

        if dl_rows:
            row = dl_rows[0]
            lines = []
            lines.append('=== DEVICE LINK SUMMARY ===')
            lines.append('')
            count = safe_int(self._ci(row, 'Device Linked User Count'))
            dep = safe_float(self._ci(row, 'Device Linked Users Total Deposit Amount'))
            wd = safe_float(self._ci(row, 'Device Linked Users Total Withdraw Amount'))
            le = safe_int(self._ci(row, 'Device Linked user also with LE request Count'))
            ip = safe_int(self._ci(row, 'Device Linked User Count also share IP'))
            sar = safe_int(self._ci(row, 'Device Linked User Count with SAR Case'))
            cp_count = safe_int(self._ci(row, 'Device Linked User also share internal CP Count'))
            ext = safe_int(self._ci(row, 'Device Linked User also share ext wallet Count'))
            blocked = safe_int(self._ci(row, 'Device Linked User also blocked Count'))

            lines.append('Device Linked Users:       {}'.format(count))
            if dep or wd:
                lines.append('Total Deposit Amount:      {}'.format(fmt_usd(dep)))
                lines.append('Total Withdraw Amount:     {}'.format(fmt_usd(wd)))
            lines.append('')
            lines.append('Also with LE Request:      {}'.format(le))
            lines.append('Also Share IP:             {}'.format(ip))
            lines.append('With SAR Case:             {}'.format(sar))
            lines.append('Also Share Internal CP:    {}'.format(cp_count))
            lines.append('Also Share Ext Wallet:     {}'.format(ext))
            lines.append('Also Blocked:              {}'.format(blocked))
            parts.append('\n'.join(lines))

        return '\n\n'.join(parts)

    def _ci(self, row, key):
        """Case-insensitive row lookup, returns raw value."""
        if key in row:
            return row[key]
        key_lower = key.lower().strip()
        for k, v in row.items():
            if safe_str(k).lower().strip() == key_lower:
                return v
        return 0

    def _build_header_validation(self, it_cp_count, it_vol, bp_cp_count,
                                  bp_vol, dupes, unique_count, combined_vol,
                                  hexa_it_count, self_ref_found,
                                  p2p_self_ref, uid):
        v = []
        v.append('=== TASK 1: HEADER VALIDATION ===')
        v.append('')
        v.append('IT counterparties: {} | Total: {}'.format(
            it_cp_count, fmt_usd(it_vol)))
        v.append('BP counterparties: {} | Total: {}'.format(
            bp_cp_count, fmt_usd(bp_vol)))
        if dupes:
            v.append('Duplicates (in both IT and BP): {} \u2014 UIDs: {}'.format(
                len(dupes), ', '.join(dupes)))
        v.append('Unique counterparties (IT+BP): {}'.format(unique_count))
        v.append('Combined volume (IT+BP): {}'.format(fmt_usd(combined_vol)))
        v.append('')
        if hexa_it_count > 0:
            match_str = 'MATCH \u2713' if hexa_it_count == it_cp_count else 'MISMATCH \u2717'
            v.append('Hexa IT count: {} | Actual IT: {} | {}'.format(
                hexa_it_count, it_cp_count, match_str))
        self_ref_str = ('FOUND \u2014 UID {} appears in own CP list. REMOVE.'.format(uid)
                        if self_ref_found else 'CLEAR \u2713')
        v.append('Self-reference check: ' + self_ref_str)
        if p2p_self_ref:
            v.append('P2P self-reference: FOUND \u2014 UID {} appears in P2P. Excluded.'.format(uid))
        return '\n'.join(v)

    def _build_flagged_section(self, flagged, p2p_flagged):
        f = []
        f.append('=== TASK 2: RISK-FLAGGED COUNTERPARTIES ===')
        f.append('')
        for cp in flagged:
            f.append(self._format_cp_entry(cp))
        if p2p_flagged:
            f.append('--- P2P FLAGGED ---')
            f.append('')
            for p in p2p_flagged:
                lines = []
                kyc_tag = ' [NO KYC]' if not p.get('is_kyc', True) else ''
                conc_str = ''
                if p.get('pct') and p['pct'] > 0:
                    display = fmt_pct_display(p['pct'])
                    if display:
                        conc_str = ' | Conc: P2P: ' + display
                lines.append('UID {}{} | P2P | {}/{} | Vol: {}{} | Bal: {}'.format(
                    p['uid'], kyc_tag,
                    p.get('nationality') or '?', p.get('residence') or '?',
                    fmt_usd(p['total_vol']), conc_str,
                    fmt_usd(p.get('balance', 0))))
                for fl in p.get('flags', []):
                    lines.append('  \u2192 ' + fl)
                kodex = p.get('kodex', [])
                if kodex:
                    for k in kodex[:3]:
                        lines.append('    ' + k)
                    if len(kodex) > 3:
                        lines.append('    (+{} more)'.format(len(kodex) - 3))
                sars = p.get('sars', [])
                if sars:
                    lines.append('  ICR refs: ' + ', '.join(sars))
                lines.append('')
                f.append('\n'.join(lines))
        f.append('TOTAL FLAGGED: {}'.format(len(flagged) + len(p2p_flagged)))
        return '\n'.join(f)

    def _build_clean_section(self, clean, p2p_clean, flagged, p2p_flagged):
        c = []
        c.append('=== TASK 3: CLEAN COUNTERPARTIES ===')
        c.append('')
        c.append('Clean IT+BP counterparties: {}'.format(len(clean)))

        no_kyc_clean = []
        clean_entries = []
        for cp in clean:
            if not cp['is_kyc']:
                no_kyc_clean.append(cp['uid'])
            conc = ''
            if cp.get('pct_by_source'):
                conc_parts = []
                for src, p in cp['pct_by_source'].items():
                    display = fmt_pct_display(p)
                    if display:
                        conc_parts.append(display)
                if conc_parts:
                    conc = ' ' + '/'.join(conc_parts)
            clean_entries.append('{} ({}/{}{})'.format(
                cp['uid'], cp.get('nationality') or '?',
                cp.get('residence') or '?', conc))
        c.append('  ' + ', '.join(clean_entries))
        c.append('')

        if p2p_clean:
            c.append('Clean P2P counterparties: {}'.format(len(p2p_clean)))
            p2p_entries = []
            for p in p2p_clean:
                if not p.get('is_kyc', True):
                    no_kyc_clean.append(p['uid'])
                conc = ''
                if p.get('pct') and p['pct'] > 0:
                    display = fmt_pct_display(p['pct'])
                    if display:
                        conc = ' ' + display
                p2p_entries.append('{} ({}/{}{})'.format(
                    p['uid'], p.get('nationality') or '?',
                    p.get('residence') or '?', conc))
            c.append('  ' + ', '.join(p2p_entries))
            c.append('')

        no_kyc_flagged = []
        for cp in flagged:
            if not cp['is_kyc']:
                no_kyc_flagged.append(cp['uid'])
        for p in p2p_flagged:
            if not p.get('is_kyc', True):
                no_kyc_flagged.append(p['uid'])

        all_no_kyc = no_kyc_flagged + no_kyc_clean
        if all_no_kyc:
            c.append('No KYC (all): ' + ', '.join(all_no_kyc))

        return '\n'.join(c)

    def _build_p2p_totals(self, p2p_map):
        pt = []
        pt.append('=== TASK 4: P2P TOTALS ===')
        pt.append('')
        p2p_total_vol = 0
        p2p_total_tx = 0
        for lid, p in p2p_map.items():
            p2p_total_vol += p['total_vol']
            p2p_total_tx += p['tx_count']
        pt.append('P2P counterparties: {} totaling {} across {} transactions.'.format(
            len(p2p_map), fmt_usd(p2p_total_vol), p2p_total_tx))
        return '\n'.join(pt)

    def _build_summary(self, it_cp_count, bp_cp_count, p2p_map,
                       device_link_rows, unique_count, combined_vol,
                       flagged, p2p_flagged, clean, p2p_clean,
                       self_ref_found, uid):
        no_kyc_all = []
        for cp in flagged:
            if not cp['is_kyc']:
                no_kyc_all.append(cp['uid'])
        for p in p2p_flagged:
            if not p.get('is_kyc', True):
                no_kyc_all.append(p['uid'])
        for cp in clean:
            if not cp['is_kyc']:
                no_kyc_all.append(cp['uid'])
        for p in p2p_clean:
            if not p.get('is_kyc', True):
                no_kyc_all.append(p['uid'])

        s = []
        s.append('=== SUMMARY ===')
        s.append('')
        s.append('IT rows processed: {}'.format(it_cp_count))
        s.append('BP rows processed: {}'.format(bp_cp_count))
        s.append('P2P rows processed: {}'.format(len(p2p_map)))
        s.append('Device link rows: {}'.format(len(device_link_rows)))
        s.append('Unique counterparties (IT+BP): {}'.format(unique_count))
        s.append('Combined IT+BP volume: {}'.format(fmt_usd(combined_vol)))
        s.append('Risk-flagged: {}'.format(len(flagged) + len(p2p_flagged)))
        s.append('Clean: {}'.format(len(clean) + len(p2p_clean)))
        if no_kyc_all:
            s.append('No KYC: ' + ', '.join(no_kyc_all))
        s.append('Self-reference: {}'.format(
            'YES \u2014 removed' if self_ref_found else 'No'))
        return '\n'.join(s)