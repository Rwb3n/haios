# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 11:12:46
# Duplicate Occurrences Investigation Handoff

**Date:** 2025-11-24
**Investigator:** Hephaestus (Claude)
**Status:** Investigation Complete - Fix Required
**Priority:** HIGH

## Executive Summary

After completing the first full ETL run with unlimited quota (260 successful files), discovered **2,771 duplicate occurrences** (1,446 entity + 1,325 concept) across 138 files. These duplicates are created during INITIAL extraction, not re-processing. The Session 9 bug fix only prevents duplicates on re-processing, but does not handle duplicates within a single extraction run.

## Problem Statement

### Symptoms
- **Entity occurrences:** 8,971 total with 1,446 duplicates
- **Concept occurrences:** 20,490 total with 1,325 concepts
- **Duplication rate:** ~16% of entity occurrences, ~6% of concept occurrences
- **Pattern:** High duplication counts (81x, 51x, 49x) concentrated in specific files

### Affected Files
Primary culprits are large JSON aggregation files:
- `HAIOS-RAW\docs\source\Cody_Reports\RAW\adr.json` - 81x duplicates for "aiconfig.json" filepath
- `HAIOS-RAW\docs\source\Cody_Reports\RAW\cody.json` - 51x duplicates for "Cody" agent, 51x for "global_registry_map.txt"

## Root Cause Analysis

### Code Location
**File:** `haios_etl/database.py`
**Methods:** `record_entity_occurrence()` (lines 174-181), `record_concept_occurrence()` (lines 183-190)

### The Issue

Both methods perform **unconditional INSERTs** without checking for existing occurrences:

```python
def record_entity_occurrence(self, entity_id, artifact_id, context):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO entity_occurrences (entity_id, artifact_id, context_snippet)
        VALUES (?, ?, ?)
    """, (entity_id, artifact_id, context))
    conn.commit()
```

**Problem:** When langextract returns the same entity/concept multiple times in ONE extraction result, we insert all occurrences without deduplication.

### Why Session 9 Fix Didn't Catch This

The Session 9 fix (lines 55-56) correctly handles **re-processing**:
```python
if current_hash != file_hash:
    # File changed - clean up old occurrences before re-processing
    cursor.execute("DELETE FROM entity_occurrences WHERE artifact_id = ?", (artifact_id,))
    cursor.execute("DELETE FROM concept_occurrences WHERE artifact_id = ?", (artifact_id,))
```

But this only fires when a file's hash CHANGES (re-processing). It doesn't prevent duplicates during the INITIAL extraction.

### Evidence

#### Duplicate Distribution
```
Files re-processed (version > 0): 10
Files with entity duplicates: 138
```
**Conclusion:** 128 files have duplicates despite NEVER being re-processed.

#### Sample Duplicates
Highest duplication counts:
```
Entity Duplicates:
  81x: [Filepath] "aiconfig.json" in RAW\adr.json
  51x: [Filepath] "global_registry_map.txt" in RAW\cody.json
  51x: [Agent] "Cody" in RAW\cody.json
  49x: [Filepath] "task_executor.py" in RAW\cody.json

Concept Duplicates:
  4x: [Directive] "proceed" in RAW\adr.json
  4x: [Decision] "I accept all findings" in RAW\cody.json
```

#### Database Query Results
From `check_status.py`:
```
Processing Results:
  error: 227
  skipped: 141
  success: 260

Total artifacts: 622
Total entities: 2,498
Total concepts: 17,235
Total entity occurrences: 8,971
Total concept occurrences: 20,490

Duplicate entity occurrences: 1,446
Duplicate concept occurrences: 1,325
```

## Why This Happens

### LangExtract Behavior
Langextract appears to return duplicate entities/concepts for certain file types, especially large JSON files with repeated patterns. For example, if "aiconfig.json" is mentioned 81 times in a file, langextract returns 81 separate extraction results for it.

### Our Current Logic
We blindly INSERT every extraction result without checking:
1. Is this entity/concept already recorded for this artifact?
2. Is this extraction identical to a previous one?

## Recommended Fix

### Approach 1: Database-Level Deduplication (PREFERRED)

Add deduplication logic to `record_entity_occurrence()` and `record_concept_occurrence()`:

```python
def record_entity_occurrence(self, entity_id, artifact_id, context):
    conn = self.get_connection()
    cursor = conn.cursor()

    # Check if this occurrence already exists for this entity-artifact pair
    cursor.execute("""
        SELECT id FROM entity_occurrences
        WHERE entity_id = ? AND artifact_id = ?
        LIMIT 1
    """, (entity_id, artifact_id))

    if cursor.fetchone():
        # Already recorded for this artifact, skip
        return

    cursor.execute("""
        INSERT INTO entity_occurrences (entity_id, artifact_id, context_snippet)
        VALUES (?, ?, ?)
    """, (entity_id, artifact_id, context))
    conn.commit()
```

**Pros:**
- Simple fix at database layer
- Handles all cases (initial + re-processing)
- No changes to extraction logic
- Minimal performance impact (SELECT before INSERT)

**Cons:**
- Only keeps FIRST occurrence context (loses additional context snippets)

### Approach 2: Extraction-Level Deduplication

Deduplicate in `cli.py` before calling database methods:

```python
# After extraction
seen_entities = set()
unique_entity_occurrences = []
for entity in result.entities:
    key = (entity_id, artifact_id)
    if key not in seen_entities:
        seen_entities.add(key)
        unique_entity_occurrences.append(entity)
```

**Pros:**
- Can aggregate context snippets from multiple occurrences
- More explicit control over deduplication logic

**Cons:**
- More complex
- Need to modify extraction flow
- Doesn't protect against bugs in future code paths

### Approach 3: Schema-Level Constraint

Add UNIQUE constraint to occurrence tables:

```sql
ALTER TABLE entity_occurrences
ADD CONSTRAINT unique_entity_artifact UNIQUE (entity_id, artifact_id);
```

**Pros:**
- Database enforces correctness
- Fail-fast on duplicate attempts
- Self-documenting schema

**Cons:**
- Requires database migration
- Need to handle IntegrityError in code
- Breaks existing database with duplicates

## Recommended Solution

**Hybrid Approach:**
1. **Immediate:** Implement Approach 1 (database-level deduplication)
2. **Database cleanup:** Clean existing duplicates using SQL DELETE
3. **Future:** Add UNIQUE constraint to schema v3 to prevent regressions

## Implementation Plan

### Step 1: Fix Code (5 minutes)
Modify `haios_etl/database.py`:
- Update `record_entity_occurrence()` with deduplication check
- Update `record_concept_occurrence()` with deduplication check

### Step 2: Clean Database (5 minutes)
Execute cleanup SQL to remove existing duplicates:
```sql
DELETE FROM entity_occurrences
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM entity_occurrences
    GROUP BY entity_id, artifact_id
);

DELETE FROM concept_occurrences
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM concept_occurrences
    GROUP BY concept_id, artifact_id
);
```

### Step 3: Verify Fix (2 minutes)
- Run tests to ensure deduplication works
- Query database to confirm 0 remaining duplicates

### Step 4: Re-process Failed Files (30-60 minutes)
- Re-run ETL on the 227 error files with fixed code
- Verify no new duplicates created

## Testing Requirements

### Unit Tests
Add to `tests/test_database.py`:
```python
def test_duplicate_occurrence_prevention():
    """Test that recording same occurrence twice doesn't create duplicates."""
    db = DatabaseManager("test.db")
    db.setup()

    artifact_id = db.insert_artifact("test.txt", "hash123", 100)
    entity_id = db.insert_entity("User", "Alice")

    # Record same occurrence twice
    db.record_entity_occurrence(entity_id, artifact_id, "context1")
    db.record_entity_occurrence(entity_id, artifact_id, "context2")

    # Verify only one occurrence exists
    cursor = db.get_connection().cursor()
    cursor.execute("SELECT COUNT(*) FROM entity_occurrences WHERE entity_id = ? AND artifact_id = ?",
                   (entity_id, artifact_id))
    count = cursor.fetchone()[0]
    assert count == 1, f"Expected 1 occurrence, found {count}"
```

### Integration Test
Add to `tests/test_cli.py`:
```python
def test_duplicate_extraction_handling():
    """Test that files with duplicate extractions don't create duplicate occurrences."""
    # Process a file known to have duplicate extractions (e.g., RAW/cody.json)
    # Verify occurrence counts match entity/concept counts (no duplicates)
```

## Next Steps

1. [ ] Implement database-level deduplication in `database.py`
2. [ ] Add unit test for duplicate prevention
3. [ ] Clean existing duplicates from database
4. [ ] Verify fix with test run
5. [ ] Re-process 227 error files
6. [ ] Update checkpoint document
7. [ ] Consider schema v3 with UNIQUE constraints

## Metrics

### Before Fix
- Entity occurrences: 8,971 (1,446 duplicates = 16%)
- Concept occurrences: 20,490 (1,325 duplicates = 6%)
- Affected files: 138

### After Fix (Expected)
- Entity occurrences: ~7,525 (0 duplicates = 0%)
- Concept occurrences: ~19,165 (0 duplicates = 0%)
- Affected files: 0

## References

- **Schema:** `docs/specs/memory_db_schema_v2.sql`
- **Database Code:** `haios_etl/database.py` (lines 174-190)
- **Session 9 Bug Fix:** `haios_etl/database.py` (lines 50-56)
- **Investigation Script:** `investigate_duplicates.py`
- **Session Checkpoint:** `docs/checkpoints/2025-11-24-session-10-quota-resolution-and-model-switch.md`

## Questions for Operator

1. **Which approach preferred?** Database-level, extraction-level, or hybrid?
2. **Clean database now or fresh start?** We have 622 artifacts processed but with duplicates
3. **Priority on re-processing errors?** 227 error files remain - address before or after duplicate fix?

---

**Status:** Ready for implementation approval
**Estimated Fix Time:** 15-20 minutes
**Estimated Re-processing Time:** 30-60 minutes (227 files with unlimited quota)
