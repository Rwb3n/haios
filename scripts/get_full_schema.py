# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 17:24:08
"""
Get full schema from live database for v3 creation.
"""
import sqlite3

DB_PATH = "haios_memory.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = cursor.fetchall()

    print("-- memory_db_schema_v3.sql")
    print("-- Unified schema for the agent memory database (v3).")
    print("-- Created: 2025-11-30")
    print("-- Source: Extracted from live haios_memory.db")
    print("-- Changes from v2:")
    print("--   - Added embeddings table (Phase 4)")
    print("--   - Added reasoning_traces table (Phase 4)")
    print("--   - Added memory_metadata table (Phase 8)")
    print("--   - Added memory_relationships table (Phase 8)")
    print("--   - Added synthesis tables with constraints (Phase 9)")
    print("--   - Added space_id to artifacts (Phase 6)")
    print("")

    for name, sql in tables:
        if sql:
            print(f"-- Table: {name}")
            print(sql + ";")
            print("")

    # Get all indexes
    cursor.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='index' AND sql IS NOT NULL
        ORDER BY name
    """)
    indexes = cursor.fetchall()

    print("-- Indexes")
    for name, sql in indexes:
        if sql:
            print(sql + ";")

    conn.close()

if __name__ == "__main__":
    main()
