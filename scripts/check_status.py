# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 11:30:04
#!/usr/bin/env python3
"""
Quick database health check for HAIOS ETL system.

Purpose:
    Simplified status checker showing key metrics:
    - Processing log summary (success/error/skipped counts)
    - Database contents (artifacts, entities, concepts)
    - Duplicate detection (entity/concept occurrences)

Usage:
    python scripts/check_status.py

Output Example:
    Processing Results:
      success: 306
      error: 227
      skipped: 95

    Total artifacts: 622
    Total entities: 2,618
    Total concepts: 19,295

    Duplicate entity occurrences: 0
    Duplicate concept occurrences: 0

See also:
    - scripts/README.md - Full utility documentation
    - scripts/query_progress.py - Detailed diagnostics
    - docs/OPERATIONS.md - Operations manual
"""
import sqlite3

conn = sqlite3.connect('haios_memory.db')
cursor = conn.cursor()

print("Processing Results:")
cursor.execute('SELECT status, COUNT(*) FROM processing_log GROUP BY status')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

cursor.execute('SELECT COUNT(*) FROM artifacts')
print(f'\nTotal artifacts: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM entities')
print(f'Total entities: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM concepts')
print(f'Total concepts: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM entity_occurrences')
print(f'Total entity occurrences: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM concept_occurrences')
print(f'Total concept occurrences: {cursor.fetchone()[0]}')

# Check for duplicates
cursor.execute('''
    SELECT entity_id, artifact_id, COUNT(*) as cnt
    FROM entity_occurrences
    GROUP BY entity_id, artifact_id
    HAVING cnt > 1
''')
dup_entities = cursor.fetchall()

cursor.execute('''
    SELECT concept_id, artifact_id, COUNT(*) as cnt
    FROM concept_occurrences
    GROUP BY concept_id, artifact_id
    HAVING cnt > 1
''')
dup_concepts = cursor.fetchall()

print(f'\nDuplicate entity occurrences: {len(dup_entities)}')
print(f'Duplicate concept occurrences: {len(dup_concepts)}')

conn.close()
