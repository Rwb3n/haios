# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 14:50:00
#!/usr/bin/env python3
"""Check if the 7 original error files have been processed."""
import sqlite3
import os

conn = sqlite3.connect('haios_memory.db')
c = conn.cursor()

# The 7 original error files (excluding binary)
error_files = [
    r'HAIOS-RAW\docs\source\Cody_Reports\RAW\odin2.json',
    r'HAIOS-RAW\docs\source\Cody_Reports\RAW\rhiza.json',
    r'HAIOS-RAW\docs\source\Cody_Reports\RAW\synth.json',
    r'HAIOS-RAW\fleet\projects\agents\2a_agent\CLAUDE_CODE_SDK_REFERENCE.md',
    r'HAIOS-RAW\fleet\projects\agents\2a_agent\output_2A\__archive\session_20250717_133239\dialogue.json',
    r'HAIOS-RAW\templates\README.md',
    r'HAIOS-RAW\docs\source\Cody_Reports\RAW\adr.txt'
]

print('=== Checking Original Error Files ===\n')

processed_count = 0
for f in error_files:
    filename = os.path.basename(f)

    # Check artifacts
    c.execute('SELECT id FROM artifacts WHERE file_path = ?', (f,))
    in_artifacts = c.fetchone() is not None

    # Check processing_log
    c.execute('SELECT status, error_message FROM processing_log WHERE file_path = ?', (f,))
    log_result = c.fetchone()

    if in_artifacts:
        processed_count += 1
        print(f'[YES] PROCESSED: {filename}')
        if log_result:
            print(f'      Status: {log_result[0]}')
    else:
        print(f'[NO]  NOT PROCESSED: {filename}')
        if log_result:
            status, error = log_result
            print(f'      Log status: {status}')
            if error:
                print(f'      Error: {error[:80]}...')
        else:
            print(f'      No processing log entry')
    print()

print(f'\n=== Summary ===')
print(f'Processed: {processed_count}/7')
print(f'Remaining: {7 - processed_count}/7')

conn.close()
