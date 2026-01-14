# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 22:00:50
# Handoff: Improve Status Command Display Clarity

**Date:** 2025-11-23
**From:** Hephaestus (Executor)
**To:** Implementer
**Priority:** Low
**Estimated Effort:** 15 minutes

## Problem

The `python -m haios_etl.cli status` command displays ambiguous metrics that mix cumulative and per-run statistics without clear labels, causing confusion about actual progress.

### Current Output (Confusing):
```
Database: haios_memory.db
Artifacts: 621
Entities: 1883
Concepts: 11736

Processing Status:
  error: 6
  skipped: 361
  success: 261
```

### Why It's Confusing:
- User sees "success: 437" in one run, then "success: 261" in the next
- Appears like 176 files failed ❌ when they're actually "skipped" (idempotency working ✅)
- No distinction between:
  - **All-time totals** (how many artifacts exist in database)
  - **Processing log stats** (cumulative status counts from all runs)
  - **Current run stats** (what happened in this specific execution)

## Solution

Update `haios_etl/cli.py` lines 40-43 to provide clearer context and labeling.

### Desired Output Format:
```
Database: haios_memory.db

Database Contents:
  Artifacts: 621
  Entities: 1,883
  Concepts: 11,736

Processing Log (All-Time):
  Total processed: 622 files
  ├─ Success: 616
  ├─ Skipped: 0
  └─ Errors: 6

Errors:
  HAIOS-RAW\docs\source\Cody_Reports\RAW\cody.json: [Errno 22] Invalid argument
  ...
```

### Alternative Simpler Format:
```
Database: haios_memory.db
  Artifacts: 621  |  Entities: 1,883  |  Concepts: 11,736

Processing Log:
  ✅ Success: 616
  ⏭️  Skipped: 0
  ❌ Errors: 6

Errors:
  ...
```

## Implementation Location

**File:** `haios_etl/cli.py`
**Function:** `cmd_status(args)` (lines 15-52)
**Lines to modify:** 40-43

### Current Code:
```python
# Processing stats
print("\nProcessing Status:")
cursor.execute("SELECT status, COUNT(*) FROM processing_log GROUP BY status")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
```

### Suggested Change:
```python
# Processing stats
print("\nProcessing Log (All-Time):")
cursor.execute("SELECT status, COUNT(*) FROM processing_log GROUP BY status")
stats = {row[0]: row[1] for row in cursor.fetchall()}

# Show in consistent order with emojis for clarity
print(f"  ✅ Success: {stats.get('success', 0)}")
print(f"  ⏭️  Skipped: {stats.get('skipped', 0)}")
print(f"  ❌ Errors: {stats.get('error', 0)}")
```

## Acceptance Criteria

- [ ] Status output clearly labels metrics as "Database Contents" and "Processing Log (All-Time)"
- [ ] User can distinguish between total artifacts vs processing log counts
- [ ] Status display uses consistent formatting (emojis optional but helpful)
- [ ] No functional changes to underlying database queries
- [ ] Existing error display remains unchanged

## Context

This issue was discovered while monitoring ETL processing progress. The idempotency feature (file hash-based skipping) works correctly, but the status display makes it look like files are being "lost" when they're actually being correctly skipped.

**Current ETL Status:**
- Preprocessor successfully handling malformed JSON
- 621 artifacts processed, 6 persistent errors
- Idempotency working (361 files skipped on re-run)

## Notes

- This is a display-only improvement, no logic changes needed
- Consider using emoji indicators (✅ ⏭️ ❌) for better visual scanning
- Could also add comma separators for large numbers (1,883 vs 1883)
- Low priority - does not block ETL functionality

## Additional Enhancement: Logging Configuration

**Context:** During T015 execution, preprocessor logs were not visible because `cli.py` lacks logging configuration. Python's default logging level is `WARNING`, which suppresses `INFO` level logs from the preprocessor system.

**Problem:**
- Preprocessor logs at `INFO` level (e.g., "Applying preprocessor: GeminiDumpPreprocessor")
- These logs provide valuable diagnostic information during processing
- Currently invisible during execution

**Solution:**
Add logging configuration to `cli.py` after imports:

```python
import logging

# Configure logging for ETL pipeline visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Expected Output:**
```
2025-11-23 21:20:00 - haios_etl.preprocessors.gemini_dump - INFO - Applying preprocessor: GeminiDumpPreprocessor
2025-11-23 21:20:01 - haios_etl.preprocessors.gemini_dump - INFO - Gemini dump preprocessor: extracted 191 text blocks
Processing: HAIOS-RAW\docs\source\Cody_Reports\RAW\adr.json
...
```

**Benefits:**
- ✅ Visibility into which preprocessors are triggered
- ✅ Confirmation of text extraction success
- ✅ Better diagnosis of processing issues
- ✅ More informative progress monitoring

**File:** `haios_etl/cli.py`
**Location:** After line 5 (after imports, before functions)
**Estimated Effort:** 2 minutes

