# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 22:22:36
# INVESTIGATION HANDOFF: Idempotency Behavior - Why Are Files Being Re-processed?

**Type:** Investigation
**Priority:** Medium
**Date:** 2025-11-23
**Requested By:** Operator (Ruben)
**Assigned To:** Investigator
**Estimated Effort:** 30 minutes

## Question / Mystery

**Core Question:** Are files that were previously processed being re-extracted, or is the "Processing:" stdout output misleading?

**Specific Mystery:** Cody Reports (50+ files) appear in stdout as "Processing: HAIOS-RAW\docs\source\Cody_Reports\..." but these files should have been processed in previous runs. Are they being:
1. **Skipped** (hash unchanged, idempotency working correctly), or
2. **Re-extracted** (hash changed or idempotency not working)

**Why This Matters:**
- If idempotency is broken: wasting API calls, processing time, and accumulating duplicate data
- If stdout is misleading: user confusion, hard to monitor actual progress
- If files are changing unexpectedly: need to understand why

## Context (What We Know)

### Current State
**Database:** 621 artifacts before this run
**Current Run Progress:**
- Success: 335 newly processed
- Skipped: 287 (hash unchanged)
- Errors: 6 (same as before)
- Total: 622 files encountered

### Processing History
1. **Initial run:** ~620 files processed, 64 JSON errors
2. **After preprocessor fix:** Re-ran processing
3. **Terminal crash:** Processing interrupted
4. **Current run (829194):** Started 2025-11-23 21:50, still running

### Stdout Observation
```
Processing: HAIOS-RAW\docs\source\Cody_Reports\Epoch_1\Cody_Report_0001.md
Processing: HAIOS-RAW\docs\source\Cody_Reports\Epoch_1\Cody_Report_0002.md
...
Processing: HAIOS-RAW\docs\source\Cody_Reports\Epoch_2\Cody_Report_1011.md
```

### Operator's Valid Question
"Hasn't it already gone through the Cody Reports? Wouldn't these be skipped?"

**Expected Behavior:**
- Files with unchanged hash → skip extraction, mark as "skipped"
- Files with changed hash → re-extract, mark as "success"
- New files → extract, mark as "success"

## What to Investigate

### Investigation 1: Decode Stdout Behavior
**Question:** Does "Processing: [file]" mean "encountered and checking" or "extracting"?

**How to verify:**
1. Read source code: `haios_etl/batch_processor.py` or similar
2. Find where "Processing:" is printed
3. Determine if it's printed for ALL files or only extracted files

**Expected findings:**
```python
# If printed for all files:
print(f"Processing: {file_path}")
if file_hash_unchanged:
    mark_as_skipped()
else:
    extract_and_insert()

# If printed only for extracted files:
if file_hash_unchanged:
    mark_as_skipped()
else:
    print(f"Processing: {file_path}")
    extract_and_insert()
```

### Investigation 2: Check Specific Cody Report Status
**Question:** Are Cody Reports in the database? Were they skipped or re-extracted?

**How to verify:**
```sql
-- Check if Cody Reports exist in artifacts
SELECT COUNT(*) FROM artifacts
WHERE file_path LIKE '%Cody_Report%';

-- Check their processing status
SELECT file_path, status, file_hash, last_attempt_at
FROM processing_log
WHERE file_path LIKE '%Cody_Report%'
ORDER BY file_path
LIMIT 10;

-- Check when they were last processed
SELECT file_path, last_processed_at, version
FROM artifacts
WHERE file_path LIKE '%Cody_Report%'
ORDER BY last_processed_at DESC
LIMIT 10;
```

**Expected findings:**
- If skipped: status='skipped', last_processed_at unchanged from previous run
- If re-extracted: status='success', last_processed_at = current run timestamp

### Investigation 3: File Hash Stability
**Question:** Are file hashes stable between runs, or are files being modified?

**How to verify:**
1. Check if any Cody Report files were modified recently:
   ```bash
   ls -lt HAIOS-RAW/docs/source/Cody_Reports/Epoch_1/*.md | head -10
   ```
2. Calculate hash of a known file and compare to database:
   ```python
   import hashlib
   with open('HAIOS-RAW/docs/source/Cody_Reports/Epoch_1/Cody_Report_0001.md', 'rb') as f:
       hash = hashlib.sha256(f.read()).hexdigest()
   # Compare to database hash for this file
   ```
3. Check if hooks or other processes are modifying files in HAIOS-RAW

**Expected findings:**
- If hashes match DB: idempotency should be working
- If hashes differ: find what's modifying the files

### Investigation 4: Idempotency Logic Verification
**Question:** Is the hash-checking logic actually running correctly?

**How to verify:**
1. Read code: `haios_etl/batch_processor.py` (or wherever processing happens)
2. Find hash comparison logic
3. Verify it's being called for each file
4. Check for any edge cases or bugs

**Expected code pattern:**
```python
def process_file(file_path):
    current_hash = calculate_hash(file_path)
    db_hash = get_hash_from_db(file_path)

    if current_hash == db_hash:
        mark_as_skipped(file_path)
        return  # Don't extract

    extract_and_insert(file_path, current_hash)
```

**Look for:**
- Is hash comparison happening BEFORE extraction?
- Is skip logic actually returning/continuing?
- Are there any exceptions bypassing the check?

## Expected Outputs

### Required Findings
1. **Stdout Semantics:** Clear explanation of what "Processing:" means
2. **Cody Report Status:** Definitive answer - were they skipped or extracted?
3. **File Modification:** Were any Cody Reports modified between runs?
4. **Code Verification:** Is idempotency logic correct and running?

### Deliverable Format
Create findings document: `2025-11-23-FINDINGS-idempotency-investigation.md`

**Structure:**
```markdown
# Investigation Findings: Idempotency Behavior

## Summary
[1-2 sentence answer to core question]

## Evidence

### Finding 1: Stdout Behavior
- Code location: [file:line]
- Behavior: [what "Processing:" actually means]
- Conclusion: [misleading or accurate?]

### Finding 2: Cody Report Status
- Database query results: [paste SQL output]
- Files skipped: [count]
- Files extracted: [count]
- Conclusion: [were they re-processed?]

### Finding 3: File Hash Stability
- Sample file hash: [hash]
- Database hash: [hash]
- Match: [yes/no]
- Conclusion: [files stable or changing?]

### Finding 4: Code Verification
- Hash check location: [file:line]
- Logic correctness: [correct/buggy]
- Issues found: [list or "none"]

## Conclusion
[Answer to original question with evidence]

## Recommendations
[Next steps based on findings]
```

### Possible Conclusions

**Scenario A: Idempotency Working, Stdout Misleading**
- Finding: "Processing:" printed for ALL files encountered
- Reality: 287 Cody Reports skipped, not extracted
- Issue: Stdout confusing, but behavior correct
- Recommendation: Update logging to show "Checking: [file]" vs "Extracting: [file]"

**Scenario B: Files Modified, Re-extraction Correct**
- Finding: Cody Report files modified (timestamp or content changed)
- Reality: Hash changed, re-extraction necessary
- Issue: Need to understand why files changing
- Recommendation: Investigate what's modifying HAIOS-RAW files

**Scenario C: Idempotency Broken**
- Finding: Files unchanged but being re-extracted
- Reality: Hash check not working or bypassed
- Issue: Bug in idempotency logic
- Recommendation: Fix hash comparison logic, create bug handoff

**Scenario D: New Files Added**
- Finding: More Cody Reports in HAIOS-RAW than in database
- Reality: New files legitimately being extracted
- Issue: None, expected behavior
- Recommendation: Document that corpus is growing

## Constraints

**Time:** 30 minutes max (this is exploratory, not exhaustive)
**Scope:** Focus on Cody Reports as representative sample
**Tools:** SQL queries, file hash checks, code reading

**Out of Scope:**
- Fixing any bugs found (create separate bug handoff)
- Processing entire corpus analysis
- Performance optimization

## Next Steps (Based on Findings)

### If Stdout Misleading (Scenario A)
→ Create ENHANCEMENT handoff: Improve logging clarity

### If Files Modified (Scenario B)
→ Create INVESTIGATION handoff: What's modifying HAIOS-RAW?

### If Idempotency Broken (Scenario C)
→ Create BUG handoff: Fix hash comparison logic

### If New Files (Scenario D)
→ No action needed, document in findings

## Related Issues

- Duplicate occurrences bug (may compound if re-extracting unnecessarily)
- Processing time (if re-extracting, wasting API calls)
- User confusion about progress (stdout not clear)

## Notes

- This investigation was prompted during active ETL processing
- Background process 829194 still running
- Database may be in inconsistent state mid-processing
- Some findings may change after processing completes
