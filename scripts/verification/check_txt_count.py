import sqlite3
import os

try:
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()
    
    # Check for processed .txt files (renamed dialogue files)
    cursor.execute("SELECT count(*) FROM artifacts WHERE file_path LIKE '%.txt'")
    txt_count = cursor.fetchone()[0]
    
    # Check total artifacts
    cursor.execute("SELECT count(*) FROM artifacts")
    total_count = cursor.fetchone()[0]
    
    print(f"Processed TXT files: {txt_count}")
    print(f"Total Artifacts: {total_count}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
