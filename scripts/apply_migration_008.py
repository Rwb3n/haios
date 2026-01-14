# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30 17:30:49
"""
Apply migration 008 to add CHECK constraints to synthesis tables.

Plan: PLAN-FIX-001 (Schema Source-of-Truth Restoration)
Phase: 8

This script safely applies migration 008 which recreates the synthesis tables
with proper CHECK and FOREIGN KEY constraints.
"""
import sqlite3
import os
from pathlib import Path

def apply_migration():
    """Apply migration 008 to the live database."""
    db_path = Path("haios_memory.db")
    migration_path = Path("haios_etl/migrations/008_add_synthesis_constraints.sql")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False

    if not migration_path.exists():
        print(f"ERROR: Migration file not found at {migration_path}")
        return False

    # Read migration SQL
    with open(migration_path, "r", encoding="utf-8") as f:
        migration_sql = f.read()

    print(f"Applying migration 008 to {db_path}...")
    print(f"Migration file: {migration_path}")

    # Connect and apply
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Check if synthesis tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='synthesis_clusters'")
        if not cursor.fetchone():
            print("Synthesis tables do not exist yet - running initial schema creation")
            # Tables will be created by migration (RENAME will fail if tables don't exist)
            # Let's just create them fresh with constraints
            fresh_sql = """
            -- Create synthesis tables with constraints (for new DB without synthesis tables)
            CREATE TABLE IF NOT EXISTS synthesis_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_type TEXT NOT NULL CHECK(cluster_type IN ('concept', 'trace', 'cross')),
                centroid_embedding BLOB,
                member_count INTEGER DEFAULT 0,
                synthesized_concept_id INTEGER,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'synthesized', 'skipped')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synthesized_at TIMESTAMP,
                FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS synthesis_cluster_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id INTEGER NOT NULL,
                member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace')),
                member_id INTEGER NOT NULL,
                similarity_to_centroid REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS synthesis_provenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                synthesized_concept_id INTEGER NOT NULL,
                source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace', 'cross')),
                source_id INTEGER NOT NULL,
                contribution_weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );

            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_type ON synthesis_clusters(cluster_type);
            CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_status ON synthesis_clusters(status);
            CREATE INDEX IF NOT EXISTS idx_cluster_members_cluster ON synthesis_cluster_members(cluster_id);
            CREATE INDEX IF NOT EXISTS idx_cluster_members_type ON synthesis_cluster_members(member_type, member_id);
            CREATE INDEX IF NOT EXISTS idx_provenance_synthesized ON synthesis_provenance(synthesized_concept_id);
            CREATE INDEX IF NOT EXISTS idx_provenance_source ON synthesis_provenance(source_type, source_id);
            """
            conn.executescript(fresh_sql)
            conn.commit()
            print("Synthesis tables created with CHECK constraints")
        else:
            # Tables exist - apply full migration (rename, recreate, copy, drop)
            print("Synthesis tables exist - applying migration to add constraints...")
            conn.executescript(migration_sql)
            conn.commit()
            print("Migration 008 applied successfully")

        # Verify constraints were applied
        print("\nVerifying CHECK constraints...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='synthesis_provenance'")
        row = cursor.fetchone()
        if row and "CHECK" in row[0]:
            print("SUCCESS: synthesis_provenance has CHECK constraint")
            if "'cross'" in row[0] or '"cross"' in row[0]:
                print("SUCCESS: 'cross' value is included in CHECK constraint (DD-011)")
            else:
                print("WARNING: 'cross' may not be in CHECK constraint")
        else:
            print("WARNING: CHECK constraint not found in synthesis_provenance")
            print(f"Table definition: {row[0] if row else 'NOT FOUND'}")

        return True

    except Exception as e:
        print(f"ERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = apply_migration()
    exit(0 if success else 1)
