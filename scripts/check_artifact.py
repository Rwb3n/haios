import sys
import os
import sqlite3

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.database import DatabaseManager

def check_artifact():
    db_path = "haios_memory.db"
    db = DatabaseManager(db_path)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    filename = "Cody_Report_1005.md"
    print(f"Checking for {filename}...")
    
    cursor.execute("SELECT id, file_path, last_processed_at FROM artifacts WHERE file_path LIKE ?", (f"%{filename}",))
    row = cursor.fetchone()
    
    if not row:
        print("Artifact NOT found in DB.")
        return
        
    artifact_id, path, last_processed = row
    print(f"Found artifact: ID={artifact_id}, Last Processed={last_processed}")
    
    # Check entities
    cursor.execute("""
        SELECT e.type, e.value 
        FROM entities e
        JOIN entity_occurrences eo ON e.id = eo.entity_id
        WHERE eo.artifact_id = ?
    """, (artifact_id,))
    
    entities = cursor.fetchall()
    print(f"Entities ({len(entities)}):")
    ap_count = 0
    for type_, name in entities:
        print(f"  [{type_}] {name}")
        if type_ == "AntiPattern":
            ap_count += 1
            
    print(f"AntiPatterns in DB: {ap_count}")

if __name__ == "__main__":
    check_artifact()
