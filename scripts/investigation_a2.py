# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 16:56:15
"""
Investigation A.2: Schema Drift Analysis
PLAN-INVESTIGATION-001
"""
import sqlite3

DB_PATH = "haios_memory.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("A.2.1: Find ALL tables with CHECK constraints in live DB")
    print("=" * 60)
    cursor.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='table' AND sql LIKE '%CHECK%'
    """)
    results = cursor.fetchall()

    if results:
        print(f"Found {len(results)} tables with CHECK constraints:\n")
        for name, sql in results:
            print(f"Table: {name}")
            print("-" * 40)
            print(sql)
            print()
    else:
        print("NO tables have CHECK constraints in the live database!")

    print("\n" + "=" * 60)
    print("A.2.2: Check how migration was applied")
    print("=" * 60)

    # Check if there's a migrations table
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE '%migration%'
    """)
    migration_tables = cursor.fetchall()
    print(f"Migration tracking tables: {migration_tables}")

    print("\n" + "=" * 60)
    print("A.2.3: Full schema comparison for synthesis tables")
    print("=" * 60)

    synthesis_tables = [
        'synthesis_clusters',
        'synthesis_cluster_members',
        'synthesis_provenance'
    ]

    for table in synthesis_tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
        result = cursor.fetchone()
        print(f"\n{table}:")
        print("-" * 40)
        if result:
            sql = result[0]
            print(sql)
            # Check if CHECK is present
            if 'CHECK' in sql:
                print(">>> HAS CHECK constraint")
            else:
                print(">>> NO CHECK constraint")
        else:
            print("TABLE NOT FOUND")

    conn.close()

if __name__ == "__main__":
    main()
