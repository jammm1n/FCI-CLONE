"""
Elliptic Upload Generator Processor.
Extracts unique blockchain addresses from Top 10 by Value and Exposed
Addresses spreadsheets, generates a CSV for Elliptic batch screening.
"""

import re
from .base import BaseProcessor, ProcessorResult
from ..utils import safe_str


class EllipticProcessor(BaseProcessor):
    id = 'elliptic'
    label = 'Elliptic Upload'
    sort_order = 30

    required_file_types = ['ADDR_VALUE', 'ADDR_EXPOSED']
    optional_file_types = []

    required_fields = []

    consumed_fields = {
        'ADDR_VALUE': ['address', 'major_user_id', 'sum_amt_usd', 'direction'],
        'ADDR_EXPOSED': ['address', 'sum_amt_usd', 'direction'],
    }

    def should_run(self, available_file_types, params):
        return bool({'ADDR_VALUE', 'ADDR_EXPOSED'} & set(available_file_types))

    def process(self, file_data, params, context):
        uid = context.get('subject_uid', '')
        value_rows = file_data.get('ADDR_VALUE', {}).get('rows', [])
        exposed_rows = file_data.get('ADDR_EXPOSED', {}).get('rows', [])

        address_set = {}
        corrupted = []
        sci_notation_pattern = re.compile(r'^[0-9]\.[0-9]+[eE]\+[0-9]+$')

        def add_addresses(rows, source):
            for row in rows:
                addr = safe_str(row.get('address', ''))
                if not addr:
                    continue
                raw_val = row.get('address', '')
                if (sci_notation_pattern.match(addr)
                        or isinstance(raw_val, (int, float))):
                    corrupted.append({'address': addr, 'source': source})
                    continue
                if addr not in address_set:
                    address_set[addr] = {'address': addr, 'sources': []}
                if source not in address_set[addr]['sources']:
                    address_set[addr]['sources'].append(source)

        add_addresses(value_rows, 'Top10Value')
        add_addresses(exposed_rows, 'Exposed')

        unique_addresses = list(address_set.values())

        csv_lines = ['address,customerid,asset,blockchain']
        for a in unique_addresses:
            csv_lines.append('{},{},holistic,holistic'.format(a['address'], uid))
        csv_content = '\n'.join(csv_lines)

        e = []
        e.append('=== ELLIPTIC BATCH SCREENING CSV ===')
        e.append('')
        e.append('Subject UID: ' + uid)
        e.append('Addresses from Top 10 by Value: {}'.format(len(value_rows)))
        e.append('Addresses from Exposed: {}'.format(len(exposed_rows)))
        e.append('Total unique addresses: {}'.format(len(unique_addresses)))

        if corrupted:
            e.append('')
            e.append('\u26a0\ufe0f CORRUPTED ADDRESSES DETECTED ({}):'.format(
                len(corrupted)))
            for c in corrupted:
                e.append('  {} (from {}) \u2014 re-download as Excel format'.format(
                    c['address'], c['source']))

        e.append('')
        e.append('--- CSV PREVIEW ---')
        e.append(csv_content)

        # Build address map for cross-referencing (keyed by address string)
        address_map = {}
        for a in unique_addresses:
            address_map[a['address']] = {
                'address': a['address'],
                'sources': a['sources'],
            }

        label = 'Elliptic Upload ({})'.format(len(unique_addresses))
        return ProcessorResult(
            content='\n'.join(e),
            has_data=True,
            csv_content=csv_content,
            csv_filename='elliptic_screening_{}.csv'.format(uid),
            metadata={
                'addresses': [a['address'] for a in unique_addresses],
                'address_map': address_map,
                'customer_id': uid,
            },
        )