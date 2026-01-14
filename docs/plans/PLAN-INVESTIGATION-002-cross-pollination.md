# Implementation Plan - Cross-Pollination Investigation
> **Goal:** Diagnose and fix the "zero results" issue in the memory synthesis cross-pollination stage.

## Problem
The synthesis pipeline reported 0 cross-pollination pairs despite having valid concept and trace clusters.
- **Current Threshold:** 0.85 (Cos Sim)
- **Suspected Cause:** Threshold is too high for cross-modal comparison (Concept Content vs Trace Query).
- **Missing Visibility:** No logs showing *why* pairs are rejected or what the actual similarity distribution looks like.

## Proposed Changes

### 1. `haios_etl/synthesis.py`

#### [MODIFY] Add Diagnostic Logging
Instrument `find_cross_type_overlaps()` to track similarity stats:
- detailed distribution of scores (min, max, avg).
- log top 10 "near misses" (pairs with highest similarity that failed threshold).

#### [MODIFY] Tuning Thresholds
 Introduce a separate threshold for cross-pollination:
```python
CROSS_POLLINATION_THRESHOLD = 0.75  # Lower than cluster threshold (0.85)
```

## Verification Plan

### 1. Dry Run with Logging
Run the synthesis pipeline in dry-run mode and observe the new logs.
```bash
python -m haios_etl.cli synthesis run --dry-run --limit 50
```
**Success Criteria:**
- Output shows "Max similarity found: X.XX"
- Output shows "Rejected pair (Concept X, Trace Y) with score Z.ZZ"
- If max similarity > new threshold (0.75), we confirm the fix.

### 2. Live Run (Optional)
If dry run looks good, run live to generate bridge insights.
```bash
python -m haios_etl.cli synthesis run --limit 50 --skip-clustering
```

## Risk Assessment
- **False Positives:** Lowering threshold too much will create nonsense bridges. We need to find the "sweet spot" where meaningful connections appear.
- **Performance:** Logging might be verbose. Will limit to "top N" or summary stats.
