# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 11:21:19
#!/usr/bin/env python3
"""
Query ETL processing progress and generate diagnostic reports.

Usage:
    python query_progress.py                    # Current status
    python query_progress.py --errors          # Show all current errors
    python query_progress.py --timeline        # Processing timeline
    python query_progress.py --by-date         # Group by date
"""

import sqlite3
import sys
from datetime import datetime
from collections import Counter

def get_current_status():
    """Show current processing status summary."""
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()

    cursor.execute('SELECT status, COUNT(*) FROM processing_log GROUP BY status')
    statuses = dict(cursor.fetchall())

    total = sum(statuses.values())
    print(f"\n=== Current Processing Status ===")
    print(f"Total files tracked: {total}")
    for status, count in statuses.items():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  [{status.upper()}] {count:3d} ({pct:5.1f}%)")

    conn.close()

def show_errors():
    """Show all current errors with details."""
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT file_path, error_message, last_attempt_at, attempt_count
        FROM processing_log
        WHERE status = 'error'
        ORDER BY last_attempt_at DESC
    ''')

    errors = cursor.fetchall()
    print(f"\n=== Current Errors ({len(errors)}) ===")

    # Group by error type
    error_types = Counter()
    for _, msg, _, _ in errors:
        if '429 RESOURCE_EXHAUSTED' in msg:
            error_types['Quota Exceeded'] += 1
        elif '400 INVALID_ARGUMENT' in msg:
            error_types['Invalid API Key'] += 1
        elif 'Errno' in msg:
            error_types['File System Error'] += 1
        else:
            error_types['Other'] += 1

    print("\nError Types:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count}")

    print("\nSample Errors (first 5):")
    for file_path, msg, timestamp, attempts in errors[:5]:
        short_path = file_path[-70:] if len(file_path) > 70 else file_path
        short_msg = (msg[:100] + '...') if msg and len(msg) > 100 else msg
        print(f"\n  File: {short_path}")
        print(f"  Time: {timestamp}")
        print(f"  Attempts: {attempts}")
        print(f"  Error: {short_msg}")

    conn.close()

def show_timeline():
    """Show processing activity timeline."""
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            DATE(last_attempt_at) as day,
            status,
            COUNT(*) as count
        FROM processing_log
        GROUP BY day, status
        ORDER BY day DESC, status
    ''')

    print("\n=== Processing Timeline ===")
    current_day = None
    for day, status, count in cursor.fetchall():
        if day != current_day:
            print(f"\n{day}:")
            current_day = day
        print(f"  {status}: {count}")

    conn.close()

def show_by_date():
    """Show detailed breakdown by date."""
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            DATE(last_attempt_at) as day,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error,
            SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped
        FROM processing_log
        GROUP BY day
        ORDER BY day DESC
    ''')

    print("\n=== Processing by Date ===")
    print(f"{'Date':<12} {'Total':>6} {'Success':>8} {'Error':>6} {'Skipped':>8}")
    print("-" * 50)

    for day, total, success, error, skipped in cursor.fetchall():
        print(f"{day:<12} {total:>6} {success:>8} {error:>6} {skipped:>8}")

    conn.close()

if __name__ == '__main__':
    if '--errors' in sys.argv:
        show_errors()
    elif '--timeline' in sys.argv:
        show_timeline()
    elif '--by-date' in sys.argv:
        show_by_date()
    else:
        get_current_status()
