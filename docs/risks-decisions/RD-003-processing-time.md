# generated: 2025-10-20
# System Auto: last updated on: 2025-10-20 00:12:50
# RD-003: Long Processing Time

**Status:** MITIGATED
**Created:** 2025-10-19
**Updated:** 2025-10-20

---

## Risk Description

**Category:** Performance
**Severity:** MEDIUM
**Probability:** HIGH (estimate: 3-6 hours for ~2000 files)

Processing HAIOS-RAW corpus is estimated at 3-6 hours based on:
- ~2000 markdown files (estimated)
- <5 seconds per file (TRD performance target)
- API latency, rate limiting, retries

**Impact:**
- Long-running process vulnerable to interruption (power loss, network issues, crashes)
- Operator cannot use system during processing
- Single failure late in process = restart from beginning (without resume capability)
- Difficult to validate/debug without processing full corpus

**Source:** TRD-ETL-v2.md Section 4.7 (Performance Requirements)

---

## Decision

**Implement batch processing with checkpoint/resume capability.**

**Rationale:**
- Cannot eliminate processing time (inherent to corpus size + API latency)
- Checkpoint/resume makes long runs safe
- Batch processing enables progress visibility
- Allows validation on small subset before full run

**Implementation (TRD-ETL-v2 Section 4.4):**
1. **Batch Processing:** Process files in batches (default 50), commit after each batch
2. **Processing Log:** Track status (pending/success/error/skipped) per file
3. **Resume Capability:** On restart, skip "success" files, retry "error" files
4. **Progress Reporting:** Log after each batch (X of Y files processed)

**Validation Strategy:**
1. Test on 10-file subset first (T014 - Integration tests)
2. Validate schema effectiveness on small corpus
3. Refine before full HAIOS-RAW run
4. Full run only after subset validation passes

**Configuration (CLI):**
```bash
--batch-size 50   # Files per batch (default)
--resume          # Resume from last checkpoint
--reset           # Reset processing_log (start fresh)
```

**Trade-offs Accepted:**
- Still requires 3-6 hour commitment for full run
- Operator should expect multi-hour runtime
- May need to run overnight or during low-activity period

---

## Status Updates

**2025-11-23:** Mitigation strategies (Batch processing T006, Resume T007) implemented and verified. The validation strategy (T014 Phases 1 & 2) has been fully executed. While successful, T014 Phase 2 identified an average processing time of ~8-9s/file, exceeding the <5s/file target. Performance optimization (T012) is now in progress to address this.

---

## References

- TRD-ETL-v2.md Section 4.4 (Batch Processing and Resilience)
- TRD-ETL-v2.md Section 4.7 (Performance Requirements)
- TRD-ETL-v2.md Section 5.2 (Integration Tests - Small Corpus)
- docs/project/board.md (T006, T007, T014)
