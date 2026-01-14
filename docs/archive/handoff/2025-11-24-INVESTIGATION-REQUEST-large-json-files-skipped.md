# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 15:05:18
# Investigation Request: Large JSON Files Silently Skipped

**Date:** 2025-11-24 14:54
**Investigator:** Hephaestus (Builder)
**Status:** ✅ RESOLVED (Session 34)
**Related Session:** Session 11 Follow-up

---

## Problem Statement

Three large JSON files in `HAIOS-RAW/docs/source/Cody_Reports/RAW/` are being **silently skipped** by the ETL process despite multiple full corpus runs. They exist on disk, are not changing, but never appear in processing logs or artifacts.

## Affected Files

| File | Size | Status |
|------|------|--------|
| `odin2.json` | 2.01 MB | EXISTS - Not processed |
| `rhiza.json` | 1.33 MB | EXISTS - Not processed |
| `synth.json` | 0.71 MB | EXISTS - Not processed |
| `dialogue.json` | N/A | MISSING - File deleted from disk |
| `adr.txt` | N/A | MISSING - File deleted from disk |

## Context

1. **Original Errors:** These 5 files were part of the original 7 error files from Session 11
2. **Fixes Applied:**
   - NoneType attribute handling in `extraction.py`
   - Empty file skipping in `processing.py`
3. **Verification:** Fixes worked for 2 smaller files (`CLAUDE_CODE_SDK_REFERENCE.md`, `templates/README.md`)
4. **Multiple Corpus Runs:** ETL has run through full corpus 3+ times
5. **Silent Skipping:** No processing_log entries, no error messages, files simply never touched

## Investigation Questions

### 1. Why are these files being skipped?
- Are they excluded by file pattern matching?
- Is there a size limit we're hitting?
- Are they in an excluded directory?
- Is the directory traversal reaching them?

### 2. What happens when we try to process them directly?
- Can we manually trigger processing of just these 3 files?
- Do they cause errors that aren't being logged?
- Do they timeout silently?

### 3. Are there other large files being skipped?
- Is this a pattern affecting all files > 1MB?
- Check: How many files > 1MB exist in corpus vs processed?

## Reproduction Steps

1. Run: `python -m haios_etl.cli process HAIOS-RAW`
2. Wait for completion
3. Check: `python check_error_files.py`
4. Observe: 3 large JSON files never appear in processing_log

## Expected vs Actual Behavior

**Expected:**
- ETL process attempts to process all `.json` files in `HAIOS-RAW/`
- Large files either succeed, fail with logged error, or skip with logged reason

**Actual:**
- Large JSON files silently ignored
- No processing_log entries
- No error messages
- Files never reach extraction pipeline

## Hypotheses

### Hypothesis 1: Directory Traversal Issue
The ETL might not be reaching `docs/source/Cody_Reports/RAW/` directory.

**Test:** Check if other files in same directory are being processed.

### Hypothesis 2: File Size Limit
There might be an undocumented size limit in `langextract` or preprocessing.

**Test:** Check for size-related logic in `processing.py` and `extraction.py`.

### Hypothesis 3: Silent Exception Handling
Errors might be caught and suppressed somewhere in the pipeline.

**Test:** Add debug logging around file discovery and processing initiation.

### Hypothesis 4: Path Encoding Issue
Windows path handling might fail silently on certain nested paths.

**Test:** Try processing files from a shallower directory.

## Immediate Next Steps

1. **Check directory traversal:** Verify ETL is reaching the RAW directory
2. **Check file pattern matching:** Ensure `.json` files aren't excluded
3. **Add debug logging:** Instrument `processing.py` to log all discovered files
4. **Test direct processing:** Create script to process just these 3 files
5. **Check for size limits:** Search codebase for any size-related thresholds

## Success Criteria

- [ ] Understand why 3 files are being skipped
- [ ] Either successfully process them OR document legitimate exclusion reason
- [ ] Achieve 100% processing of all existing, processable files in corpus

## Impact

**Current State:**
- 477 files on disk
- 622 artifacts in DB (includes 145 deleted files)
- 3 files silently skipped
- **Effective coverage: 474/477 = 99.4%**

**Risk:**
- If large files are systematically skipped, we may have blind spots in agent memory
- Silent failures indicate potential systemic issue in error handling

## Handoff To

**Next Investigator** (Operator or designated debugger):
1. Review this investigation request
2. Execute hypothesis tests
3. Document findings in new investigation report
4. Implement fix if root cause identified

---

**Files for Reference:**
- Investigation handoff: `docs/handoff/2025-11-24-INVESTIGATION-etl-errors-resolved.md`
- Checkpoint script: `check_error_files.py`
- ETL Status: `python -m haios_etl.cli status`
- Progress Query: `python scripts/query_progress.py`
