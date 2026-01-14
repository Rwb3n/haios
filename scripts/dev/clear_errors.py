# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 14:12:54
#!/usr/bin/env python3
"""Temporary script to clear error records and force reprocessing."""
import sqlite3

conn = sqlite3.connect('haios_memory.db')
cursor = conn.cursor()

# Get error file paths before deleting
cursor.execute("SELECT file_path FROM processing_log WHERE status = 'error'")
error_files = [row[0] for row in cursor.fetchall()]

print(f"Clearing {len(error_files)} error records:")
for f in error_files:
    print(f"  - {f}")

# Delete error records
cursor.execute("DELETE FROM processing_log WHERE status = 'error'")
conn.commit()

print(f"\n✓ Deleted {cursor.rowcount} error records from processing_log")
conn.close()
