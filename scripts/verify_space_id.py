import sys
import os
import sqlite3

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.database import DatabaseManager

def verify_space_id():
    db_path = "haios_memory.db"
    db = DatabaseManager(db_path)
    
    # 1. Check if column exists
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT space_id FROM artifacts LIMIT 1")
        print("SUCCESS: space_id column exists.")
    except sqlite3.OperationalError:
        print("FAIL: space_id column missing.")
        return

    # 2. Insert dummy data with space_id
    # We need to manually insert an artifact and embedding because we don't have a tool for it yet
    # Or we can update an existing artifact
    
    # Let's pick an artifact
    cursor.execute("SELECT id FROM artifacts LIMIT 1")
    row = cursor.fetchone()
    if not row:
        print("SKIP: No artifacts to test.")
        return
        
    artifact_id = row[0]
    
    # Set space_id = 'test_space'
    cursor.execute("UPDATE artifacts SET space_id = ? WHERE id = ?", ('test_space', artifact_id))
    conn.commit()
    print(f"Updated artifact {artifact_id} with space_id='test_space'")
    
    # 3. Search with space_id
    # We need an embedding for this artifact. 
    # Check if it has one.
    cursor.execute("SELECT vector FROM embeddings WHERE artifact_id = ?", (artifact_id,))
    if not cursor.fetchone():
        # Insert dummy embedding
        import struct
        vector = [0.1] * 768
        vector_bytes = struct.pack(f'{len(vector)}f', *vector)
        cursor.execute("INSERT INTO embeddings (artifact_id, vector, model, dimensions) VALUES (?, ?, ?, ?)", 
                       (artifact_id, vector_bytes, 'test-model', 768))
        conn.commit()
        print("Inserted dummy embedding.")

    # Now search
    # Note: search_memories uses vector search. Since we don't have sqlite-vec, it falls back to empty list.
    # But we want to verify the SQL generation logic.
    # We can inspect the code or trust the unit test (which I should write).
    # But for this script, if search_memories returns [], we can't verify filtering.
    
    # However, I can verify that it DOESN'T crash.
    try:
        results = db.search_memories([0.1]*768, space_id='test_space')
        print("Search with space_id executed without error.")
    except Exception as e:
        print(f"FAIL: Search with space_id failed: {e}")

if __name__ == "__main__":
    verify_space_id()
