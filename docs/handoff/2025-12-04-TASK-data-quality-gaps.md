---
template: handoff
version: 1.0
type: task
date: 2025-12-04
author: Antigravity (Implementer)
status: complete
priority: medium
estimated_effort: 3 hours
generated: 2025-12-04
last_updated: 2025-12-04
---

# Task Handoff: Data Quality Gaps (Category B)

## Task Summary

Address remaining Category B (Data Quality) gaps, specifically focusing on the "Large File Silent Skipping" issue and "AntiPattern Extraction" verification.

---

## Context

**Source:** @docs/epistemic_state.md (Risks & Mitigations)

**Gaps:**
1.  **Large File Silent Skipping (Risk 2):** 3 large JSON files (`odin2.json`, `rhiza.json`, `synth.json`) are skipped during processing.
2.  **AntiPattern Extraction (Risk 1):** Zero AntiPattern entities detected across the corpus. Need to verify if this is a data reality or an extraction failure.

---

## Implementation Spec

### 1. Investigate Large File Skipping
- **Hypothesis:** File size limit or JSON parsing timeout.
- **Action:**
    - Create a reproduction test case with a large dummy JSON.
    - Trace `BatchProcessor` logic for these specific files.
    - Fix the issue (likely in `preprocessors/gemini_dump.py` or `processing.py`).

### 2. Verify AntiPattern Extraction
- **Hypothesis:** Regex/Prompt in `extraction.py` is not catching "Anti-Pattern" or "AP-" markers.
- **Action:**
    - Manually inspect a file known to contain an AntiPattern (e.g., `docs/VISION_ANCHOR.md`).
    - Run extraction on that file specifically.
    - Adjust `langextract` schema or prompt if needed.

---

## Acceptance Criteria

- [x] Large JSON files are successfully processed (Verified: IDs 623, 624, 625 found).
- [x] AntiPattern extraction is verified (Verified: 127 entities found).
- [x] `docs/epistemic_state.md` updated with findings.

---

## Key References
- @docs/handoff/2025-11-24-INVESTIGATION-REQUEST-large-json-files-skipped.md
- @haios_etl/processing.py
- @haios_etl/extraction.py
