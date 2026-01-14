import sqlite3
import os
import sys

DB_PATH = "haios_memory.db"
DB_PATH = "haios_memory.db"

def apply_migration():
    if len(sys.argv) < 2:
        print("Usage: python apply_migration.py <migration_file>")
        sys.exit(1)

    migration_file = sys.argv[1]

    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        sys.exit(1)
        
    if not os.path.exists(migration_file):
        print(f"Error: Migration file {migration_file} not found.")
        sys.exit(1)

    print(f"Applying migration: {migration_file}...")
    
    try:
        with open(migration_file, 'r') as f:
            sql_script = f.read()
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        print("Migration applied successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
