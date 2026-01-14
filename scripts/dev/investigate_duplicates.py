# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 11:03:08
import sqlite3

conn = sqlite3.connect('haios_memory.db')
cursor = conn.cursor()

print("=== Investigating New Duplicates ===\n")

# Sample entity duplicates
print("Sample Entity Duplicates:")
cursor.execute('''
    SELECT e.type, e.value, a.file_path, COUNT(*) as cnt
    FROM entity_occurrences eo
    JOIN entities e ON eo.entity_id = e.id
    JOIN artifacts a ON eo.artifact_id = a.id
    GROUP BY eo.entity_id, eo.artifact_id
    HAVING cnt > 1
    ORDER BY cnt DESC
    LIMIT 10
''')
for row in cursor.fetchall():
    print(f'  {row[3]}x: [{row[0]}] "{row[1]}" in {row[2]}')

print("\n\nSample Concept Duplicates:")
cursor.execute('''
    SELECT c.type, c.content, a.file_path, COUNT(*) as cnt
    FROM concept_occurrences co
    JOIN concepts c ON co.concept_id = c.id
    JOIN artifacts a ON co.artifact_id = a.id
    GROUP BY co.concept_id, co.artifact_id
    HAVING cnt > 1
    ORDER BY cnt DESC
    LIMIT 10
''')
for row in cursor.fetchall():
    content_preview = row[1][:50] + '...' if len(row[1]) > 50 else row[1]
    print(f'  {row[3]}x: [{row[0]}] "{content_preview}" in {row[2]}')

# Check if duplicates are from re-processed files
print("\n\n=== Checking Artifact Versions ===")
cursor.execute('''
    SELECT file_path, version, last_processed_at
    FROM artifacts
    WHERE version > 0
    ORDER BY version DESC
    LIMIT 10
''')
reprocessed = cursor.fetchall()
print(f"Files re-processed (version > 0): {len(reprocessed)}")
for row in reprocessed:
    print(f'  v{row[1]}: {row[0]} (processed: {row[2]})')

# Check how many duplicates are in re-processed vs first-time files
print("\n\n=== Duplicate Distribution ===")
cursor.execute('''
    SELECT
        CASE WHEN a.version > 0 THEN 'Re-processed' ELSE 'First-time' END as file_type,
        COUNT(DISTINCT eo.artifact_id) as artifact_count
    FROM entity_occurrences eo
    JOIN artifacts a ON eo.artifact_id = a.id
    WHERE EXISTS (
        SELECT 1
        FROM entity_occurrences eo2
        WHERE eo2.entity_id = eo.entity_id
        AND eo2.artifact_id = eo.artifact_id
        GROUP BY eo2.entity_id, eo2.artifact_id
        HAVING COUNT(*) > 1
    )
    GROUP BY file_type
''')
for row in cursor.fetchall():
    print(f'{row[0]} files with entity duplicates: {row[1]}')

conn.close()
