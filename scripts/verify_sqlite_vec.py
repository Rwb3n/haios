import sys
import os
import sqlite3
import logging

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.database import DatabaseManager

def verify_sqlite_vec():
    logging.basicConfig(level=logging.INFO)
    
    db_path = "haios_memory.db"
    db = DatabaseManager(db_path)
    conn = db.get_connection()
    
    # 1. Check vec_version()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT vec_version()")
        version = cursor.fetchone()[0]
        print(f"SUCCESS: sqlite-vec loaded. Version: {version}")
    except Exception as e:
        print(f"FAIL: Could not get vec_version: {e}")
        return

    # 2. Test vector distance function
    try:
        # Create dummy vectors
        import struct
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        
        # Serialize
        b1 = struct.pack(f'{len(v1)}f', *v1)
        b2 = struct.pack(f'{len(v2)}f', *v2)
        
        cursor.execute("SELECT vec_distance_cosine(?, ?)", (b1, b2))
        dist = cursor.fetchone()[0]
        print(f"SUCCESS: vec_distance_cosine([1,0,0], [0,1,0]) = {dist}")
        
        # Expected cosine distance between orthogonal vectors is 1.0
        if abs(dist - 1.0) < 0.001:
             print("PASS: Distance calculation is correct.")
        else:
             print("FAIL: Distance calculation incorrect.")
             
    except Exception as e:
        print(f"FAIL: Vector distance calculation failed: {e}")

if __name__ == "__main__":
    verify_sqlite_vec()
