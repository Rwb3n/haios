# generated: 2025-10-20
# System Auto: last updated on: 2025-10-20 00:12:40
# RD-001: LLM Non-Determinism

**Status:** ACCEPTED
**Created:** 2025-10-19
**Updated:** 2025-10-20

---

## Risk Description

**Category:** Technical Limitation
**Severity:** MEDIUM
**Probability:** HIGH (100% - inherent to LLM-based extraction)

LangExtract uses Gemini LLM for extraction, which is non-deterministic. Running the same file through the pipeline multiple times may yield slightly different entity/concept extractions even with identical input.

**Impact:**
- Cannot guarantee reproducible results
- Unit tests for extraction quality are difficult
- Hard to validate "correctness" of extractions
- Schema refinement requires subjective evaluation

**Source:** TRD-ETL-v2.md Section 7 (Known Limitations)

---

## Decision

**Accept the risk with mitigation strategy.**

**Rationale:**
- LLM-based extraction is core requirement (R1)
- Benefits (semantic understanding, flexibility) outweigh reproducibility concerns
- HAIOS-RAW content is one-time migration (not ongoing production data)
- File hashing (R4) prevents re-processing unchanged files
- Quality metrics (R5) provide visibility into extraction variability

**Mitigation:**
1. **File Hashing (R4):** Once file is processed successfully, skip on re-runs (idempotency)
2. **Quality Metrics (R5):** Track extraction counts, flag anomalies (zero extractions, unusually high/low counts)
3. **Schema Iteration:** Test on small HAIOS-RAW subset first, refine schema before full run
4. **Manual Validation:** Operator spot-checks quality_report.json for sanity
5. **Acceptance Criteria:** Focus on "good enough" not "perfect" - goal is philosophy extraction, not precision NER

**Trade-offs Accepted:**
- Extractions are "best effort" not ground truth
- Schema effectiveness validated through testing, not formal metrics
- Some valuable content may be missed, some noise may be captured

---

## Status Updates

**2025-11-23:** Mitigation strategies (File Hashing, Quality Metrics, Schema Iteration) have been implemented (R4, R5) and validated during T014 dry runs. The schema coverage was confirmed against diverse real-world data. This risk remains accepted with robust mitigation in place.

---

## References

- TRD-ETL-v2.md Section 7 (Known Limitations)
- TRD-ETL-v2.md Section 4.4 (File Hashing)
- TRD-ETL-v2.md Section 4.5 (Quality Metrics)
- docs/specs/langextract_schema_v1.yml
