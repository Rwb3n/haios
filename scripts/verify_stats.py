import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.database import DatabaseManager

def verify_stats():
    db_path = "haios_memory.db"
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    db = DatabaseManager(db_path)
    try:
        stats = db.get_stats()
        print("Database Stats:")
        print(json.dumps(stats, indent=2))
        
        # Basic validation
        if 'artifacts' not in stats:
            print("FAIL: 'artifacts' missing from stats")
            sys.exit(1)
        if 'reasoning_traces' not in stats:
            print("FAIL: 'reasoning_traces' missing from stats")
            sys.exit(1)
            
        print("SUCCESS: Stats retrieved successfully.")
        
    except Exception as e:
        print(f"FAIL: Exception occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_stats()
