# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 17:31:14
"""Verify CHECK constraints are working on live database."""
import sqlite3

def verify():
    conn = sqlite3.connect("haios_memory.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    print("=== Live Database Constraint Verification ===\n")

    # 1. Show table definitions with constraints
    tables = ['synthesis_clusters', 'synthesis_cluster_members', 'synthesis_provenance']
    for table in tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        row = cursor.fetchone()
        print(f"Table: {table}")
        if row:
            sql = row[0]
            # Check for CHECK constraints
            if "CHECK" in sql:
                print("  - CHECK constraint: YES")
            else:
                print("  - CHECK constraint: NO (PROBLEM!)")
        else:
            print("  - NOT FOUND")
        print()

    # 2. Test constraint enforcement
    print("=== Testing Constraint Enforcement ===\n")

    # Test 1: Invalid cluster_type should fail
    print("Test 1: Insert invalid cluster_type...")
    try:
        cursor.execute("INSERT INTO synthesis_clusters (cluster_type, member_count) VALUES ('invalid', 1)")
        print("  FAIL - Invalid value accepted!")
    except sqlite3.IntegrityError as e:
        print(f"  PASS - Rejected with: {e}")

    # Test 2: Valid 'cross' should succeed
    print("\nTest 2: Insert valid 'cross' cluster_type...")
    try:
        cursor.execute("INSERT INTO synthesis_clusters (cluster_type, member_count) VALUES ('cross', 1)")
        print("  PASS - 'cross' accepted (DD-011)")
        # Clean up test data
        cursor.execute("DELETE FROM synthesis_clusters WHERE cluster_type='cross' AND member_count=1")
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"  FAIL - 'cross' rejected: {e}")

    # Test 3: Invalid provenance source_type should fail
    print("\nTest 3: Insert invalid provenance source_type...")
    try:
        cursor.execute("INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id) VALUES (1, 'invalid', 1)")
        print("  FAIL - Invalid value accepted!")
    except sqlite3.IntegrityError as e:
        print(f"  PASS - Rejected with: {e}")

    # Test 4: 'cross' provenance should succeed
    print("\nTest 4: Insert 'cross' provenance source_type...")
    # First ensure we have a concept to reference
    cursor.execute("SELECT id FROM concepts LIMIT 1")
    concept_row = cursor.fetchone()
    if concept_row:
        try:
            cursor.execute("INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id) VALUES (?, 'cross', 999)", (concept_row[0],))
            print("  PASS - 'cross' accepted (DD-011)")
            # Clean up
            cursor.execute("DELETE FROM synthesis_provenance WHERE source_id=999")
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"  FAIL - 'cross' rejected: {e}")
    else:
        print("  SKIPPED - No concepts in database to reference")

    conn.close()
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify()
