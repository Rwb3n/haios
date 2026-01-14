import sqlite3
import os

DB_PATH = "test_schema_validation.db"

# Remove old test DB if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)

# Try to load the schema
try:
    with open("docs/specs/memory_db_schema_v3.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    print("✓ Schema loaded successfully!")
    conn.commit()
    
    # Verify new tables exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✓ Found {len(tables)} tables")
    if "agent_registry" in tables:
        print("✓ agent_registry table exists")
    if "skill_registry" in tables:
        print("✓ skill_registry table exists")
        
except sqlite3.Error as e:
    print(f"✗ Error loading schema: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
    # Clean up
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
