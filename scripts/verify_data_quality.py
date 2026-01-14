
import os
import sys
from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager
import asyncio

def check_large_files(db):
    print("\n--- Checking Large Files ---")
    files = [
        r"d:\PROJECTS\haios\HAIOS-RAW\docs\source\Cody_Reports\RAW\odin2.json",
        r"d:\PROJECTS\haios\HAIOS-RAW\docs\source\Cody_Reports\RAW\rhiza.json",
        r"d:\PROJECTS\haios\HAIOS-RAW\docs\source\Cody_Reports\RAW\synth.json"
    ]
    
    for f in files:
        fname = os.path.basename(f)
        cursor = db.get_connection().cursor()
        res = cursor.execute("SELECT id, file_path FROM artifacts WHERE file_path LIKE ?", (f"%{fname}",)).fetchone()
        if res:
            print(f"[FOUND] {fname}: ID={res[0]}, Path={res[1]}")
        else:
            print(f"[MISSING] {fname}")

def check_antipatterns(db):
    print("\n--- Checking AntiPatterns ---")
    cursor = db.get_connection().cursor()
    count = cursor.execute("SELECT COUNT(*) FROM entities WHERE type='AntiPattern'").fetchone()[0]
    print(f"Total AntiPattern entities in DB: {count}")
    
    if count == 0:
        print("Verified GAP: 0 AntiPatterns found.")
    else:
        print(f"GAP RESOLVED? {count} found.")

async def test_extraction():
    print("\n--- Testing Extraction on VISION_ANCHOR.md ---")
    # This assumes we have an extraction manager setup
    # We'll just print that we are skipping this for now unless we need it
    pass

def main():
    # Initialize DB (checking signature from view_code_item)
    # If it requires db_path, we provide it.
    try:
        db = DatabaseManager() 
    except TypeError:
        # Fallback if it needs a path
        db = DatabaseManager("haios_memory.db")
    check_large_files(db)
    check_antipatterns(db)

if __name__ == "__main__":
    main()
