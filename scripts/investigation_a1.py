# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 16:55:25
"""
Investigation A.1: Verify Bug Exists
PLAN-INVESTIGATION-001
"""
import sqlite3
import sys

DB_PATH = "haios_memory.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("A.1.1: Query synthesis_provenance schema")
    print("=" * 60)
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='synthesis_provenance'")
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print("TABLE NOT FOUND")

    print("\n" + "=" * 60)
    print("A.1.1b: Query synthesis_clusters schema (for comparison)")
    print("=" * 60)
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='synthesis_clusters'")
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print("TABLE NOT FOUND")

    print("\n" + "=" * 60)
    print("A.1.2: Test INSERT with source_type='concept'")
    print("=" * 60)
    try:
        cursor.execute("""
            INSERT INTO synthesis_provenance
            (synthesized_concept_id, source_type, source_id)
            VALUES (99999, 'concept', 1)
        """)
        print("SUCCESS: 'concept' INSERT accepted")
        cursor.execute("DELETE FROM synthesis_provenance WHERE synthesized_concept_id = 99999")
        conn.commit()
    except Exception as e:
        print(f"FAILED: {e}")
        conn.rollback()

    print("\n" + "=" * 60)
    print("A.1.3: Test INSERT with source_type='cross'")
    print("=" * 60)
    try:
        cursor.execute("""
            INSERT INTO synthesis_provenance
            (synthesized_concept_id, source_type, source_id)
            VALUES (99999, 'cross', 1)
        """)
        print("SUCCESS: 'cross' INSERT accepted")
        print(">>> BUG NOT PRESENT - constraint allows 'cross'")
        cursor.execute("DELETE FROM synthesis_provenance WHERE synthesized_concept_id = 99999")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"REJECTED: {e}")
        print(">>> BUG CONFIRMED - CHECK constraint rejects 'cross'")
        conn.rollback()
    except Exception as e:
        print(f"OTHER ERROR: {e}")
        conn.rollback()

    print("\n" + "=" * 60)
    print("A.3.1: Check existing data counts")
    print("=" * 60)
    tables = [
        ("synthesis_provenance", "SELECT COUNT(*) FROM synthesis_provenance"),
        ("synthesis_clusters", "SELECT COUNT(*) FROM synthesis_clusters"),
        ("synthesis_cluster_members", "SELECT COUNT(*) FROM synthesis_cluster_members"),
        ("SynthesizedInsight concepts", "SELECT COUNT(*) FROM concepts WHERE type = 'SynthesizedInsight'"),
    ]
    for name, query in tables:
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  {name}: {count}")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")

    conn.close()
    print("\n" + "=" * 60)
    print("Investigation A.1 Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
