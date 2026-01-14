import sqlite3
import os

db_path = 'haios_memory.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

filenames = ['adr', 'cody', 'odin2', 'rhiza', 'synth']
print("--- Checking processing_log ---")
query_log = "SELECT file_path, status FROM processing_log WHERE " + " OR ".join([f"file_path LIKE '%{name}%'" for name in filenames])
try:
    c.execute(query_log)
    results = c.fetchall()
    for row in results:
        print(f"Log: {row}")
except Exception as e:
    print(f"Log Error: {e}")

print("\n--- Checking artifacts ---")
query_art = "SELECT file_path, version FROM artifacts WHERE " + " OR ".join([f"file_path LIKE '%{name}%'" for name in filenames])
try:
    c.execute(query_art)
    results = c.fetchall()
    for row in results:
        print(f"Artifact: {row}")
except Exception as e:
    print(f"Artifact Error: {e}")

conn.close()
