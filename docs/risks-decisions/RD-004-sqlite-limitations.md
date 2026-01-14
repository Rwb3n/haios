# generated: 2025-10-20
# System Auto: last updated on: 2025-10-20 00:12:54
# RD-004: SQLite Write Limitations

**Status:** ACCEPTED
**Created:** 2025-10-19
**Updated:** 2025-10-20

---

## Risk Description

**Category:** Technical Limitation
**Severity:** LOW
**Probability:** HIGH (100% - inherent to SQLite)

SQLite supports only a single concurrent writer. Cannot run multiple ETL processes in parallel to speed up processing.

**Impact:**
- Cannot parallelize ETL across multiple processes
- Processing time is serial (3-6 hours minimum)
- Cannot use multi-core CPU for parallel extraction
- Limited scalability for future large corpora

**Source:** TRD-ETL-v2.md Section 4.7, Section 7 (Known Limitations)

---

## Decision

**Accept limitation for v2, document for future consideration.**

**Rationale:**
- HAIOS-RAW is one-time migration (not ongoing production workload)
- 3-6 hour runtime is acceptable for one-time processing
- SQLite is sufficient for corpus size (<500MB database expected)
- Simplicity of SQLite (no server, no config) outweighs parallelization benefits
- LangExtract library has internal parallelization (max_workers=20) for batches

**Future Considerations (v3+):**
- If ongoing incremental updates needed, consider PostgreSQL for concurrent writes
- If corpus grows >10k files, consider parallel processing with partitioned databases
- If real-time updates required, reconsider architecture

**Current Mitigation:**
- LangExtract uses `max_workers=20` for parallel API calls within single process
- Batch processing (50 files) with commits minimizes transaction overhead
- Processing runs as background task (operator can continue other work)

**Trade-offs Accepted:**
- No parallel ETL processes
- Processing time cannot be reduced via horizontal scaling
- Single point of failure (one process crash = whole pipeline stops, but resume capability mitigates)

---

## Status Updates

**2025-11-23:** Limitation documented. Accepted for v2. Performance optimization (T012) is currently in progress, focusing on maximizing efficiency within this single-writer constraint (e.g., via `langextract.Document` batching).

---

## References

- TRD-ETL-v2.md Section 4.7 (Performance Requirements - Concurrent ETL runs)
- TRD-ETL-v2.md Section 7 (Known Limitations)
- TRD-ETL-v2.md Section 4.1 (max_workers=20 for LangExtract)
