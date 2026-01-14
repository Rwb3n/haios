# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 22:08:51
# BUG HANDOFF: Duplicate Occurrences on File Re-processing

**Type:** Bug / Data Integrity Issue
**Severity:** High
**Priority:** High
**Date:** 2025-11-23
**Discovered By:** Hephaestus (Executor)
**Assigned To:** Implementer
**Estimated Effort:** 30-45 minutes

## Summary

When files are re-processed (file hash changed), old entity/concept occurrences are NOT cleaned up before inserting new ones, causing **duplicate occurrence records** to accumulate in the database.

## Impact

**Current State:**
- ✅ Entities de-duplicated (UNIQUE constraint working)
- ✅ Concepts de-duplicated (manual check at insert working)
- ❌ **Entity occurrences accumulating duplicates**
- ❌ **Concept occurrences accumulating duplicates**

**Data Corruption:**
- Each time a file is re-processed, NEW occurrences are added
- OLD occurrences remain in database
- Same entity appears multiple times for same artifact
- Database becomes increasingly garbled over re-runs

**Real-World Scenario:**
```
Run 1: File A processed → 10 entity occurrences inserted
File A modified → hash changes
Run 2: File A re-processed → 10 NEW occurrences inserted (20 total now) ❌
Run 3: File A re-processed → 10 NEW occurrences inserted (30 total now) ❌
```

## Root Cause

**File:** `haios_etl/database.py`
**Functions:**
- `record_entity_occurrence()` (line 169-175)
- `record_concept_occurrence()` (likely similar pattern)

**Problem Code:**
```python
def record_entity_occurrence(self, entity_id, artifact_id, context):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO entity_occurrences (entity_id, artifact_id, context_snippet)
        VALUES (?, ?, ?)
    """, (entity_id, artifact_id, context))
    # No cleanup of old occurrences for this artifact_id ❌
```

**Flow:**
1. File hash changes → `insert_artifact()` updates version (line 38-115)
2. Batch processor extracts entities/concepts again
3. `record_entity_occurrence()` called → **directly inserts without cleanup**
4. Old occurrences remain → duplicates accumulate

## Expected Behavior

When a file is re-processed (hash changed):
1. ✅ Update artifact version (already working)
2. ❌ **DELETE old occurrences for this artifact** (MISSING)
3. ✅ Insert new occurrences (already working)

## Solution

### Option A: Delete Before Insert (Recommended)

Add cleanup in `insert_artifact()` when hash changes:

```python
def insert_artifact(self, file_path, file_hash, size_bytes):
    """
    Insert or update an artifact.
    If hash changed, update hash, size, and increment version.
    """
    conn = self.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, file_hash, version FROM artifacts WHERE file_path = ?", (file_path,))
    row = cursor.fetchone()

    if row:
        artifact_id, current_hash, current_version = row
        if current_hash != file_hash:
            # File changed - clean up old occurrences
            cursor.execute("DELETE FROM entity_occurrences WHERE artifact_id = ?", (artifact_id,))
            cursor.execute("DELETE FROM concept_occurrences WHERE artifact_id = ?", (artifact_id,))

            # Update artifact
            new_version = current_version + 1
            cursor.execute("""
                UPDATE artifacts
                SET file_hash = ?, version = ?, last_processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (file_hash, new_version, artifact_id))

            conn.commit()
            return artifact_id
        else:
            return artifact_id
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO artifacts (file_path, file_hash, version)
            VALUES (?, ?, 1)
        """, (file_path, file_hash))
        conn.commit()
        return cursor.lastrowid
```

### Option B: Add UNIQUE Constraints (Alternative)

Add database constraints to prevent duplicates:
```sql
-- In schema setup
CREATE UNIQUE INDEX idx_entity_occurrence_unique
ON entity_occurrences(artifact_id, entity_id, context_snippet);

CREATE UNIQUE INDEX idx_concept_occurrence_unique
ON concept_occurrences(artifact_id, concept_id, context_snippet);
```

**Tradeoff:** Fails silently on duplicate insert vs. explicit cleanup

### Option C: Check Before Insert (Least Efficient)

Check if occurrence exists before inserting:
```python
def record_entity_occurrence(self, entity_id, artifact_id, context):
    cursor.execute("""
        SELECT id FROM entity_occurrences
        WHERE entity_id = ? AND artifact_id = ? AND context_snippet = ?
    """, (entity_id, artifact_id, context))
    if cursor.fetchone():
        return  # Already exists

    cursor.execute("""
        INSERT INTO entity_occurrences (entity_id, artifact_id, context_snippet)
        VALUES (?, ?, ?)
    """, (entity_id, artifact_id, context))
```

**Tradeoff:** Adds SELECT overhead for every occurrence

## Recommended Solution

**Option A: Delete Before Insert**

**Rationale:**
- Clean, explicit, easy to understand
- Centralized in one place (insert_artifact)
- Minimal performance impact (single DELETE per file)
- No schema changes required
- Aligns with idempotency principle (same input → same output)

## Testing Requirements

After fix, verify:
1. **Clean re-processing:** Process file, modify it, re-process → occurrence count should remain constant
2. **No duplicates:** Query occurrences for a re-processed artifact → should only show latest extractions
3. **Version tracking:** Artifact version should increment on re-process
4. **Idempotency:** Process same file multiple times (no hash change) → no duplicate occurrences

### Test SQL Queries:
```sql
-- Check for duplicate occurrences (should return 0 after fix)
SELECT artifact_id, entity_id, COUNT(*) as count
FROM entity_occurrences
GROUP BY artifact_id, entity_id
HAVING count > 1;

-- Verify occurrence count matches expectations
SELECT a.file_path, a.version, COUNT(eo.id) as occurrence_count
FROM artifacts a
LEFT JOIN entity_occurrences eo ON a.id = eo.artifact_id
GROUP BY a.id;
```

## Migration / Cleanup

**Current Database State:**
- Database likely contains duplicate occurrences from previous re-runs
- May need cleanup script or reset before fix

**Options:**
1. **Reset database:** `python -m haios_etl.cli reset` (clean slate)
2. **Cleanup script:** Delete duplicate occurrences, keep latest by artifact version
3. **Accept current state:** Fix prevents future duplicates, old duplicates remain

**Recommendation:** Reset database after implementing fix to ensure clean state.

## Files to Modify

1. `haios_etl/database.py` - Add DELETE logic to `insert_artifact()`
2. `tests/test_database.py` - Add test for re-processing behavior

## Acceptance Criteria

- [ ] Old occurrences deleted when file hash changes
- [ ] Re-processing same file (no hash change) creates no duplicates
- [ ] Re-processing modified file (hash changed) replaces old occurrences
- [ ] Test added: `test_reprocess_file_removes_old_occurrences()`
- [ ] No duplicate occurrences in database after multiple re-runs
- [ ] Documentation updated in `docs/OPERATIONS.md` (if needed)

## Related Issues

- Idempotency requirement (ADR-023)
- File hash-based change detection (TRD-ETL-v2 Section 4.4.6)
- Data quality validation (TRD-ETL-v2 Section 4.5)

## Notes

- This bug affects data quality but NOT data loss (can be fixed retroactively)
- Current ETL processing should be allowed to complete, then fix can be applied
- Consider adding data quality check in `quality_report.json` to detect duplicates
