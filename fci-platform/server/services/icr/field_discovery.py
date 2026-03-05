"""
Field discovery engine.
Tracks unused spreadsheet columns across all user sessions.
Each unique field is stored once and updated on subsequent sightings.
"""

import os
import json
import sqlite3
import threading
from datetime import datetime


DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'field_discovery.db')

_db_lock = threading.Lock()


def _get_connection():
    """Get a SQLite connection, creating the database and tables if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS unused_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT,
            field_name TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            times_seen INTEGER DEFAULT 1,
            sample_values TEXT,
            UNIQUE(file_type, field_name)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS discovery_stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_runs INTEGER DEFAULT 0,
            first_run TEXT,
            last_run TEXT
        )
    ''')
    # Ensure the single stats row exists
    conn.execute('''
        INSERT OR IGNORE INTO discovery_stats (id, total_runs, first_run, last_run)
        VALUES (1, 0, NULL, NULL)
    ''')
    conn.commit()
    return conn


def discover_unused_fields(session_data, processors):
    """
    Compare uploaded file columns against consumed fields from all processors.

    Returns:
        List of unused field report dicts
    """
    all_consumed = {}
    for processor in processors:
        for file_type, fields in processor.consumed_fields.items():
            if file_type not in all_consumed:
                all_consumed[file_type] = set()
            all_consumed[file_type].update(f.lower() for f in fields)

    unused_report = []

    for file_type, file_data in session_data.get('detected_files', {}).items():
        headers = file_data.get('headers', [])
        consumed = all_consumed.get(file_type, set())
        unused_headers = [h for h in headers if h.lower() not in consumed]

        if unused_headers:
            samples = {}
            rows = file_data.get('rows', [])
            for header in unused_headers:
                values = []
                for row in rows[:3]:
                    val = row.get(header, '')
                    if val and str(val) != '(null)':
                        values.append(str(val))
                samples[header] = values

            unused_report.append({
                'file_type': file_type,
                'label': file_data.get('label', file_type),
                'filename': file_data.get('filename', ''),
                'total_columns': len(headers),
                'consumed_columns': len(headers) - len(unused_headers),
                'unused_columns': unused_headers,
                'samples': samples,
            })

    for undetected in session_data.get('undetected_files', []):
        headers = undetected.get('headers', [])
        if headers:
            samples = {}
            rows = undetected.get('rows', [])
            for header in headers[:15]:
                values = []
                for row in rows[:3]:
                    val = row.get(header, '')
                    if val and str(val) != '(null)':
                        values.append(str(val))
                samples[header] = values

            unused_report.append({
                'file_type': None,
                'label': 'UNDETECTED FILE',
                'filename': undetected.get('filename', ''),
                'total_columns': len(headers),
                'consumed_columns': 0,
                'unused_columns': headers,
                'samples': samples,
            })

    return unused_report


def log_discovery(session_id, session_data, unused_report):
    """
    Update the discovery ledger. Each unique field is stored once.
    Subsequent sightings update the count, last_seen date, and sample values.
    """
    now = datetime.utcnow().isoformat()

    with _db_lock:
        conn = _get_connection()
        try:
            # Update run stats
            conn.execute('''
                UPDATE discovery_stats SET
                    total_runs = total_runs + 1,
                    first_run = COALESCE(first_run, ?),
                    last_run = ?
                WHERE id = 1
            ''', (now, now))

            for report in unused_report:
                file_type = report.get('file_type')
                for field_name in report.get('unused_columns', []):
                    sample_vals = report.get('samples', {}).get(field_name, [])
                    sample_json = json.dumps(sample_vals)

                    # Try to update existing row
                    cursor = conn.execute('''
                        UPDATE unused_fields SET
                            times_seen = times_seen + 1,
                            last_seen = ?,
                            sample_values = ?
                        WHERE file_type IS ? AND field_name = ?
                    ''', (now, sample_json, file_type, field_name))

                    # If no row existed, insert new one
                    if cursor.rowcount == 0:
                        conn.execute('''
                            INSERT INTO unused_fields
                                (file_type, field_name, first_seen, last_seen, times_seen, sample_values)
                            VALUES (?, ?, ?, ?, 1, ?)
                        ''', (file_type, field_name, now, now, sample_json))

            conn.commit()
        finally:
            conn.close()


def get_field_log_summary():
    """
    Return the discovery ledger. One row per unique unused field.
    """
    with _db_lock:
        conn = _get_connection()
        try:
            # Stats
            stats = conn.execute(
                'SELECT total_runs, first_run, last_run FROM discovery_stats WHERE id = 1'
            ).fetchone()

            total_runs = stats[0] or 0
            first_run = stats[1] or 'N/A'
            last_run = stats[2] or 'N/A'

            # All unused fields, ordered by times seen
            rows = conn.execute('''
                SELECT file_type, field_name, first_seen, last_seen,
                       times_seen, sample_values
                FROM unused_fields
                ORDER BY times_seen DESC, last_seen DESC
            ''').fetchall()

            fields = []
            for r in rows:
                try:
                    samples = json.loads(r[5]) if r[5] else []
                except json.JSONDecodeError:
                    samples = []
                fields.append({
                    'file_type': r[0],
                    'field_name': r[1],
                    'first_seen': r[2],
                    'last_seen': r[3],
                    'times_seen': r[4],
                    'sample_values': samples,
                })

            # Newly seen = first appeared with 5 or fewer sightings
            newly_seen = [f for f in fields if f['times_seen'] <= 5]

            return {
                'summary': {
                    'total_processing_runs': total_runs,
                    'first_run': first_run,
                    'last_run': last_run,
                    'unique_unused_fields': len(fields),
                },
                'unused_fields': fields,
                'newly_seen': newly_seen,
            }
        finally:
            conn.close()