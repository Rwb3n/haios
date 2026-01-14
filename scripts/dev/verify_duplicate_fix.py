# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 11:21:15
import sqlite3
import time

def check_duplicates():
    """Check for duplicate occurrences in the database."""
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()

    # Check entity duplicates
    cursor.execute('''
        SELECT COUNT(*)
        FROM (
            SELECT entity_id, artifact_id, COUNT(*) as cnt
            FROM entity_occurrences
            GROUP BY entity_id, artifact_id
            HAVING cnt > 1
        )
    ''')
    entity_dupes = cursor.fetchone()[0]

    # Check concept duplicates
    cursor.execute('''
        SELECT COUNT(*)
        FROM (
            SELECT concept_id, artifact_id, COUNT(*) as cnt
            FROM concept_occurrences
            GROUP BY concept_id, artifact_id
            HAVING cnt > 1
        )
    ''')
    concept_dupes = cursor.fetchone()[0]

    # Get total counts
    cursor.execute('SELECT COUNT(*) FROM entity_occurrences')
    total_entity_occ = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM concept_occurrences')
    total_concept_occ = cursor.fetchone()[0]

    # Get success count
    cursor.execute("SELECT COUNT(*) FROM processing_log WHERE status = 'success'")
    success_count = cursor.fetchone()[0]

    conn.close()

    return {
        'entity_dupes': entity_dupes,
        'concept_dupes': concept_dupes,
        'total_entity_occ': total_entity_occ,
        'total_concept_occ': total_concept_occ,
        'success_files': success_count
    }

def check_recent_files(limit=5):
    """Check the most recently processed files for duplicates."""
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()

    # Get most recent successful files
    cursor.execute("""
        SELECT a.id, a.file_path, a.last_processed_at
        FROM artifacts a
        JOIN processing_log pl ON a.file_path = pl.file_path
        WHERE pl.status = 'success'
        ORDER BY a.last_processed_at DESC
        LIMIT ?
    """, (limit,))

    recent_files = cursor.fetchall()

    print(f"\n=== Checking {len(recent_files)} Most Recent Files ===")

    for artifact_id, file_path, processed_at in recent_files:
        # Check entity duplicates for this artifact
        cursor.execute('''
            SELECT entity_id, COUNT(*) as cnt
            FROM entity_occurrences
            WHERE artifact_id = ?
            GROUP BY entity_id
            HAVING cnt > 1
        ''', (artifact_id,))
        entity_dupes = cursor.fetchall()

        # Check concept duplicates for this artifact
        cursor.execute('''
            SELECT concept_id, COUNT(*) as cnt
            FROM concept_occurrences
            WHERE artifact_id = ?
            GROUP BY concept_id
            HAVING cnt > 1
        ''', (artifact_id,))
        concept_dupes = cursor.fetchall()

        status = "[OK] CLEAN" if not entity_dupes and not concept_dupes else "[ERROR] HAS DUPLICATES"
        print(f"{status}: {file_path}")
        if entity_dupes:
            print(f"  Entity duplicates: {len(entity_dupes)}")
        if concept_dupes:
            print(f"  Concept duplicates: {len(concept_dupes)}")

    conn.close()

if __name__ == "__main__":
    print("Verifying Duplicate Fix (Safe for Running Process)")
    print("=" * 60)

    stats = check_duplicates()

    print(f"\nCurrent Database State:")
    print(f"  Success files: {stats['success_files']}")
    print(f"  Total entity occurrences: {stats['total_entity_occ']}")
    print(f"  Total concept occurrences: {stats['total_concept_occ']}")
    print(f"\nDuplicate Check:")
    print(f"  Entity duplicates: {stats['entity_dupes']}")
    print(f"  Concept duplicates: {stats['concept_dupes']}")

    if stats['entity_dupes'] == 0 and stats['concept_dupes'] == 0:
        print("\n[OK] FIX VERIFIED: No duplicates found!")
    else:
        print(f"\n[ERROR] DUPLICATES STILL PRESENT: {stats['entity_dupes'] + stats['concept_dupes']} total")

    check_recent_files(5)

    print("\n" + "=" * 60)
    print("This script is safe to run repeatedly while ETL is processing.")
    print("Run again in a few minutes to verify ongoing processing.")
