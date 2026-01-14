# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21T22:42:07
#!/usr/bin/env python3
"""
One-time cleanup script for E2-130.

Removes false positive error captures from the old ErrorCapture.ps1 hook.
These have content like "[Error Capture] Tool: ..." and type='techne'.
"""
import sqlite3
from pathlib import Path

def main():
    db_path = Path(__file__).parent.parent / "haios_memory.db"
    conn = sqlite3.connect(str(db_path))

    # Count before
    count_before = conn.execute(
        "SELECT COUNT(*) FROM concepts WHERE content LIKE '%[Error Capture]%'"
    ).fetchone()[0]
    print(f"False positives before cleanup: {count_before}")

    # Delete false positives (old format used "[Error Capture]", new uses "[Tool Error]")
    cursor = conn.execute(
        "DELETE FROM concepts WHERE content LIKE '%[Error Capture]%' AND type = 'techne'"
    )
    deleted = cursor.rowcount
    conn.commit()

    # Count after
    count_after = conn.execute(
        "SELECT COUNT(*) FROM concepts WHERE content LIKE '%[Error Capture]%'"
    ).fetchone()[0]

    print(f"Deleted: {deleted}")
    print(f"Remaining: {count_after}")
    conn.close()

if __name__ == "__main__":
    main()
