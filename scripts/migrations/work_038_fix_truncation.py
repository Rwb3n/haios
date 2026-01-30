# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T20:22:22
# WORK-038: Fix Content Truncation Bug - Data Migration
#
# This script recovers ~614 concepts that were truncated at 100 characters.
# The full content is preserved in source_adr column - this script copies it back.
#
# Usage:
#   python scripts/migrations/work_038_fix_truncation.py [--dry-run]
#
# Options:
#   --dry-run    Show what would be changed without modifying database

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("haios_memory.db")

def run_migration(dry_run: bool = False):
    """Run the WORK-038 truncation fix migration."""

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Step 1: Create backup (always, even for dry-run)
    print("=" * 60)
    print("WORK-038: Content Truncation Fix Migration")
    print("=" * 60)

    if not dry_run:
        print("\n[Step 1] Creating backup table...")
        try:
            cursor.execute("DROP TABLE IF EXISTS concepts_backup_20260130")
            cursor.execute("CREATE TABLE concepts_backup_20260130 AS SELECT * FROM concepts")
            conn.commit()
            cursor.execute("SELECT COUNT(*) FROM concepts_backup_20260130")
            backup_count = cursor.fetchone()[0]
            print(f"  Backup created: concepts_backup_20260130 ({backup_count} rows)")
        except Exception as e:
            print(f"  ERROR creating backup: {e}")
            return 1
    else:
        print("\n[Step 1] Would create backup table (--dry-run)")

    # Step 2: Count candidates
    print("\n[Step 2] Counting migration candidates...")
    count_sql = """
        SELECT COUNT(*) FROM concepts
        WHERE LENGTH(content) = 100
        AND source_adr IS NOT NULL
        AND LENGTH(source_adr) > 100
        AND type NOT IN ('Decision')
        AND source_adr NOT LIKE '%/%'
        AND content = SUBSTR(source_adr, 1, 100)
    """
    cursor.execute(count_sql)
    affected_count = cursor.fetchone()[0]
    print(f"  Found {affected_count} concepts to recover")

    if affected_count == 0:
        print("\n  No concepts need recovery. Migration complete.")
        conn.close()
        return 0

    # Step 3: Show samples
    print("\n[Step 3] Sample candidates (first 3):")
    sample_sql = """
        SELECT id, type, content, LENGTH(source_adr) as full_length
        FROM concepts
        WHERE LENGTH(content) = 100
        AND source_adr IS NOT NULL
        AND LENGTH(source_adr) > 100
        AND type NOT IN ('Decision')
        AND source_adr NOT LIKE '%/%'
        AND content = SUBSTR(source_adr, 1, 100)
        LIMIT 3
    """
    cursor.execute(sample_sql)
    for row in cursor.fetchall():
        print(f"  ID {row[0]} ({row[1]}): '{row[2][:50]}...' -> will restore {row[3]} chars")

    # Step 4: Run migration
    if not dry_run:
        print("\n[Step 4] Running migration...")
        update_sql = """
            UPDATE concepts
            SET content = source_adr
            WHERE LENGTH(content) = 100
            AND source_adr IS NOT NULL
            AND LENGTH(source_adr) > 100
            AND type NOT IN ('Decision')
            AND source_adr NOT LIKE '%/%'
            AND content = SUBSTR(source_adr, 1, 100)
        """
        cursor.execute(update_sql)
        updated_count = cursor.rowcount
        conn.commit()
        print(f"  Updated {updated_count} concepts")
    else:
        print(f"\n[Step 4] Would update {affected_count} concepts (--dry-run)")

    # Step 5: Verify
    print("\n[Step 5] Verifying migration...")
    cursor.execute(count_sql)
    remaining = cursor.fetchone()[0]

    if remaining == 0:
        print("  SUCCESS: All truncated concepts recovered")
    else:
        print(f"  WARNING: {remaining} concepts still need recovery")

    conn.close()

    print("\n" + "=" * 60)
    if dry_run:
        print("DRY RUN COMPLETE - No changes made")
        print("Run without --dry-run to apply changes")
    else:
        print("MIGRATION COMPLETE")
        print(f"Recovered {affected_count} truncated concepts")
        print("Backup table: concepts_backup_20260130")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(run_migration(dry_run))
