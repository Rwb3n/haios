import sqlite3
import os

def check_large_files():
    db_path = "haios_memory.db"
    if not os.path.exists(db_path):
        print("DB not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    files = ["odin2.json", "rhiza.json", "synth.json"]
    
    print("Checking DB for large files...")
    for f in files:
        cursor.execute("SELECT file_path, status, error_message FROM processing_log WHERE file_path LIKE ?", (f"%{f}",))
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                path, status, error = row
                filename = os.path.basename(path)
                print(f"[{status.upper()}] {filename}")
                if status == 'error':
                    print(f"  Error: {error}")
        else:
            print(f"[NOT FOUND] {f}")

if __name__ == "__main__":
    check_large_files()
