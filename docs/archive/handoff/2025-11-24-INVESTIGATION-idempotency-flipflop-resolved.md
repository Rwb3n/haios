# generated: 2025-11-24
# System Auto: last updated on: 2025-11-24 16:35:00
# Investigation: Unintentional Rescanning (RESOLVED)

**Date:** 2025-11-24
**Investigator:** Hephaestus (Builder)
**Status:** ✅ RESOLVED
**Related Session:** Session 11 Follow-up

---

## Executive Summary

The user correctly identified that files were being rescanned unintentionally. Investigation revealed a logic bug in `processing.py` where files marked as `skipped` in one run were treated as "not processed" in the next run, causing them to be re-processed. This created a "flip-flop" behavior where files were processed every other run.

## Findings

### 1. Root Cause: Status Logic Flaw
- **Logic:** `if last_status == "success" and last_hash == current_hash:`
- **Behavior:**
  - **Run 1:** File processed -> Status=`success`.
  - **Run 2:** Check: Status is `success`. Matches. -> Skip. Update Status=`skipped`.
  - **Run 3:** Check: Status is `skipped`. Condition fails (`skipped != success`). -> **Re-process**. Update Status=`success`.
  - **Run 4:** Check: Status is `success`. Matches. -> Skip. Update Status=`skipped`.
- **Result:** 50% of runs were unnecessary re-processing.

### 2. Fix Implemented
- **File:** `haios_etl/processing.py`
- **Change:** Updated condition to accept both `success` and `skipped` as valid states for skipping.
  ```python
  if last_status in ("success", "skipped") and last_hash == current_hash:
  ```

### 3. Verification
- **Method:** Created unit test `test_process_file_skip_when_already_skipped` in `tests/test_processing.py`.
- **Result:** Test passed. Confirmed that `skipped` status now preserves idempotency.

## Conclusion

The ETL pipeline is now truly idempotent. Files will only be processed once (or if they change). Subsequent runs will consistently skip unchanged files, regardless of whether they were "success" or "skipped" in the previous run.

**Next Steps:**
- No further action needed.
- Future runs will be much faster as they will properly skip all 600+ unchanged files.
