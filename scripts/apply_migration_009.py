
import sqlite3
import os
import sys

def apply_migration():
    db_path = "haios_memory.db"
    migration_path = "haios_etl/migrations/009_fix_synthesis_member_constraint.sql"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        sys.exit(1)
        
    print(f"Applying migration {migration_path}...")
    
    with open(migration_path, 'r') as f:
        sql_script = f.read()
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        print("Migration applied successfully.")
        
        # Verify
        print("Verifying constraint...")
        cursor.execute("PRAGMA table_info(synthesis_cluster_members)")
        cols = cursor.fetchall()
        for col in cols:
            if col[1] == 'member_type':
                print(f"Column verified: {col}")
                
        conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
