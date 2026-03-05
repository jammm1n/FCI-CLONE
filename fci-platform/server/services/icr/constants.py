"""
Constants used across ICR processors.
Rule codes, jurisdiction lists, file type definitions.
"""

RULE_CODES = {
    'ADA':                        {'name': 'Activity on Dormant Account',                                     'platform': '.com / Global'},
    'TLHA-I':                     {'name': 'Transaction Limit - Historic Average - Inbound',                  'platform': '.com / Global'},
    'TLHA-O':                     {'name': 'Transaction Limit - Historic Average - Outbound',                 'platform': '.com / Global'},
    'LVP-I':                      {'name': 'Low Value Payments - Inbound',                                    'platform': '.com / Global'},
    'LVP-O':                      {'name': 'Low Value Payments - Outbound',                                   'platform': '.com / Global'},
    'SAWD':                       {'name': 'Similar Amounts Withdrawal / Deposits',                           'platform': '.com / Global'},
    'HVSDLW':                     {'name': 'High Volume Small Deposits followed by Large Withdrawal',         'platform': '.com / Global'},
    'P2P-HCA':                    {'name': 'High Cumulative Amount - Inbound and Outbound for P2P',           'platform': 'ES/AU/NZ'},
    'RRN':                        {'name': 'Regulatory Reporting Netherlands',                                'platform': '.com / NL'},
    'FT9':                        {'name': 'Excessive Withdrawal',                                            'platform': '.com / EEA'},
    'FT5':                        {'name': 'Excessive Incoming FIAT/Crypto Deposits (24h) / Smurfing',        'platform': '.com / EEA'},
    'ETLT1':                      {'name': 'EDD Threshold Limit Tier 1 (>=10,000,000 EUR)',                   'platform': 'Custody'},
    'ETLT2':                      {'name': 'EDD Threshold Limit Tier 2 (>=20,000,000 EUR)',                   'platform': 'Custody'},
    'CIBO':                       {'name': 'Change in Behavior (exceed estimated investment amount)',          'platform': 'Custody'},
    'EICD30D':                    {'name': 'Excessive Incoming CRYPTO Deposits (30d)',                         'platform': 'Custody'},
    'EOCR30D':                    {'name': 'Excessive Outgoing CRYPTO Withdrawals (30d)',                      'platform': 'Custody'},
    'DORMANT':                    {'name': 'Activity on Dormant Account',                                     'platform': 'Custody'},
    'HCAHAI':                     {'name': 'High Cumulative Amount - Historic Average - Inbound',              'platform': 'Custody'},
    'HCAHAO':                     {'name': 'High Cumulative Amount - Historic Average - Outbound',             'platform': 'Custody'},
    'CIBC':                       {'name': 'Change in Behavior (exceed current estimated investment amount)',  'platform': 'Custody'},
    'BF-ADA':                     {'name': 'Activity on Dormant Account',                                     'platform': 'Bifinity'},
    'BF-TLHA-I':                  {'name': 'Transaction Limit - Historic Average - Inbound',                  'platform': 'Bifinity'},
    'BF-TLHA-O':                  {'name': 'Transaction Limit - Historic Average - Outbound',                 'platform': 'Bifinity'},
    'BF-LVP-I':                   {'name': 'Low Value Payments - Inbound',                                    'platform': 'Bifinity'},
    'BF-LVP-O':                   {'name': 'Low Value Payments - Outbound',                                   'platform': 'Bifinity'},
    'BF-SAWD':                    {'name': 'Similar Amounts Withdrawal / Deposits',                           'platform': 'Bifinity'},
    'BF-HVSDLW':                  {'name': 'High Volume Small Deposits followed by Large Withdrawal',         'platform': 'Bifinity'},
    'TCRJ':                       {'name': 'Transaction with Counterparty in High Risk Jurisdiction',         'platform': 'Bifinity'},
    'BF-STR-I':                   {'name': 'Structuring Payments - Inbound',                                  'platform': 'Bifinity'},
    'BF-STR-O':                   {'name': 'Structuring Payments - Outbound',                                 'platform': 'Bifinity'},
    'BF-ULT-I':                   {'name': 'Unusually Large Transactions - Inbound',                          'platform': 'Bifinity'},
    'BF-ULT-O':                   {'name': 'Unusually Large Transactions - Outbound',                         'platform': 'Bifinity'},
    'BF-TLHA-IC':                 {'name': 'Transaction Limit - Historic Average - Inbound (Cohort)',         'platform': 'Bifinity'},
    'BF-TLHA-OC':                 {'name': 'Transaction Limit - Historic Average - Outbound (Cohort)',        'platform': 'Bifinity'},
    'MCOC_1':                     {'name': 'Multiple Customers, One Counterparty',                            'platform': '.com / Global'},
    'OCMC_1':                     {'name': 'Multiple Counterparties, One Customer',                           'platform': '.com / Global'},
    'P-SUMCI3':                   {'name': 'High Cumulative Amount - Inbound - Counterparty',                 'platform': '.com / Global'},
    'P-SUMCO3':                   {'name': 'High Cumulative Amount - Outbound - Counterparty',                'platform': '.com / Global'},
    'NUMCCI':                     {'name': 'High Velocity - Inbound - Counterparty',                          'platform': '.com / Global'},
    'NUMCCO':                     {'name': 'High Velocity - Outbound - Counterparty',                         'platform': '.com / Global'},
    'BPSAWD':                     {'name': 'Similar Amounts Withdrawal / Deposits',                           'platform': 'Binance Pay'},
    'BPPSUMCI':                   {'name': 'High Cumulative Amount - Inbound - Counterparty',                 'platform': 'Binance Pay'},
    'BPPSUMCO':                   {'name': 'High Cumulative Amount - Outbound - Counterparty',                'platform': 'Binance Pay'},
    'BP-HRCOU':                   {'name': 'High Risk Country',                                               'platform': 'Binance Pay'},
    'KZ-ADA':                     {'name': 'Activity on Dormant Account',                                     'platform': '.KZ'},
    'KZ-LVP-I':                   {'name': 'Low Value Payments - Inbound',                                    'platform': '.KZ'},
    'KZ-LVP-O':                   {'name': 'Low Value Payments - Outbound',                                   'platform': '.KZ'},
    'KZ-SAWD':                    {'name': 'Similar Amounts Withdrawal / Deposits',                           'platform': '.KZ'},
    'KZ-HVSDL':                   {'name': 'High Volume Small Deposits followed by Large Withdrawal',         'platform': '.KZ'},
    'KZ-THAO':                    {'name': 'Transaction Limit - Historic Average - Outbound',                 'platform': '.KZ'},
    'KZ-THHI':                    {'name': 'Transaction Limit - Historic Average - Inbound',                  'platform': '.KZ'},
    'RJ_STR':                     {'name': 'Structuring - Regulated Jurisdiction',                            'platform': '.com / Licensed'},
    'P2P_UF_L':                   {'name': 'P2P - Unexpected Fiat - Retail',                                  'platform': '.com / P2P'},
    'P2P_HRC_R':                  {'name': 'P2P - High Risk Countries - Retail',                              'platform': '.com / P2P'},
    'P2P_FT_R':                   {'name': 'P2P - Flowthrough - Retail',                                      'platform': '.com / P2P'},
    'BP-HCCR':                    {'name': 'Binance Pay - High Concentration Counterparty Risk',              'platform': '.com / Binance Pay'},
    'BP-HVPT':                    {'name': 'Binance Pay - High Value Pass Through',                           'platform': '.com / Binance Pay'},
    'BP-HRC':                     {'name': 'Binance Pay - High Risk Country',                                 'platform': '.com / Binance Pay'},
    'BF-DACM':                    {'name': 'Bifinity - Daily Assets Conversion Monitoring',                   'platform': 'Bifinity'},
    'BF-WACM':                    {'name': 'Bifinity - Weekly Assets Conversion Monitoring',                  'platform': 'Bifinity'},
    'BPAYGLOB-ADA':               {'name': 'Activity on Dormant Account',                                     'platform': 'Bpay Global'},
    'BPAYGLOB-TLHA-I':            {'name': 'Transaction Limit - Historic Average - Inbound',                  'platform': 'Bpay Global'},
    'BPAYGLOB-TLHA-O':            {'name': 'Transaction Limit - Historic Average - Outbound',                 'platform': 'Bpay Global'},
    'BPAYGLOB-LVP-I':             {'name': 'Low Value Payments - Inbound',                                    'platform': 'Bpay Global'},
    'BPAYGLOB-LVP-O':             {'name': 'Low Value Payments - Outbound',                                   'platform': 'Bpay Global'},
    'BPAYGLOB-SAWD':              {'name': 'Similar Amounts Withdrawal / Deposits',                           'platform': 'Bpay Global'},
    'BPAYGLOB-HVSDLW':            {'name': 'High Volume Small Deposits followed by Large Withdrawal',         'platform': 'Bpay Global'},
    'TLHA_I_DYNAMIC_USER_COHORT': {'name': 'Transaction Limit - Historic Average - Inbound (Dynamic)',        'platform': '.com / Global'},
    'TLHA_O_DYNAMIC_USER_COHORT': {'name': 'Transaction Limit - Historic Average - Outbound (Dynamic)',       'platform': '.com / Global'},
    'SAWD_DYNAMIC_USER_COHORT':   {'name': 'Similar Amounts Withdrawal / Deposits (Dynamic)',                 'platform': '.com / Global'},
    'AU_ECM_I':                   {'name': 'Australia Enhanced Coin Monitoring - Inbound',                    'platform': '.COM_AU'},
    'AU_ECM_O':                   {'name': 'Australia Enhanced Coin Monitoring - Outbound',                   'platform': '.COM_AU'},
    'AU_LVP_I':                   {'name': 'Australia Low Value Payments - Inbound',                          'platform': '.COM_AU'},
    'AU_LVP_O':                   {'name': 'Australia Low Value Payments - Outbound',                         'platform': '.COM_AU'},
    'AU_STR_NEW':                 {'name': 'Australia Structuring New',                                       'platform': '.COM_AU'},
    'NZ_ECM_I':                   {'name': 'New Zealand Enhanced Coin Monitoring - Inbound',                  'platform': '.COM_NZ'},
    'NZ_ECM_O':                   {'name': 'New Zealand Enhanced Coin Monitoring - Outbound',                 'platform': '.COM_NZ'},
    'PIT':                        {'name': 'Physically Impossible Travel',                                    'platform': '.com / Global'},
    'FR_ABD_G1':                  {'name': 'France Age Based Detection - Group 1 (Vulnerable Population)',    'platform': '.COM_FR'},
    'FR_ABD_G2':                  {'name': 'France Age Based Detection - Group 2',                            'platform': '.COM_FR'},
    'FR_C2C_INT':                 {'name': 'France C2C Rule',                                                 'platform': 'FR_Payment_C2C'},
    'FR_ECM_I':                   {'name': 'France Enhanced Coin Monitoring - Inbound',                       'platform': '.COM_FR'},
    'FR_ECM_O':                   {'name': 'France Enhanced Coin Monitoring - Outbound',                      'platform': '.COM_FR'},
    'FR_TVEA':                    {'name': 'France Trading Volume Expected Amount',                           'platform': '.COM_FR'},
    'BR-THA-I-NEW':               {'name': 'Transaction Limit - Historic Average - Inbound',                  'platform': '.com / BR'},
    'BR-THA-O-NEW':               {'name': 'Transaction Limit - Historic Average - Outbound',                 'platform': '.com / BR'},
    'BR-SAWD-NEW':                {'name': 'Similar Amounts Withdrawal / Deposits',                           'platform': '.com / BR'},
    'BR-HVDLW-NEW':               {'name': 'High Volume Small Deposits followed by Large Withdrawal',         'platform': '.com / BR'},
    'BR-ADA-NEW':                 {'name': 'Activity on Dormant Account',                                     'platform': '.com / BR'},
    'BR-LVPIR-NEW':               {'name': 'Low Value Payments - Inbound - Retail',                           'platform': '.com / BR'},
    'BR-LVPIC-NEW':               {'name': 'Low Value Payments - Inbound - Corporate',                        'platform': '.com / BR'},
    'BR-LVPOR-NEW':               {'name': 'Low Value Payments - Outbound - Retail',                          'platform': '.com / BR'},
    'BR-LVPOC-NEW':               {'name': 'Low Value Payments - Outbound - Corporate',                       'platform': '.com / BR'},
}

SANCTIONED_JURISDICTIONS = [
    'north korea', 'cuba', 'iran', 'crimea', 'donetsk', 'luhansk',
    'kp', 'cu', 'ir'
]

RESTRICTED_JURISDICTIONS = [
    'canada', 'netherlands', 'united states', 'us', 'usa',
    'belarus', 'russia', 'ca', 'nl', 'by', 'ru'
]


def lookup_rule_code(code):
    """Look up a rule code with fallback matching for dash/underscore variants."""
    if not code:
        return {'name': 'Unknown', 'platform': 'Unknown'}
    upper = safe_str_for_lookup(code)
    if upper in RULE_CODES:
        return RULE_CODES[upper]
    underscore_version = upper.replace('-', '_')
    if underscore_version in RULE_CODES:
        return RULE_CODES[underscore_version]
    dash_version = upper.replace('_', '-')
    if dash_version in RULE_CODES:
        return RULE_CODES[dash_version]
    return {'name': code, 'platform': 'Unknown'}


def safe_str_for_lookup(value):
    """Strip and uppercase for constant lookups."""
    if value is None:
        return ''
    return str(value).strip().upper()