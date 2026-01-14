import sqlite3
try:
    conn = sqlite3.connect('haios_memory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='artifacts'")
    result = cursor.fetchone()
    if result:
        print(result[0])
except Exception as e:
    print(e)
