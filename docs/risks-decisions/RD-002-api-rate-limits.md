# generated: 2025-10-20
# System Auto: last updated on: 2025-10-20 00:12:46
# RD-002: API Rate Limits

**Status:** MITIGATED
**Created:** 2025-10-19
**Updated:** 2025-10-20

---

## Risk Description

**Category:** External Dependency
**Severity:** HIGH
**Probability:** MEDIUM (depends on API tier, concurrent usage)

Gemini API has rate limits (requests per minute/day). Processing ~2000 files from HAIOS-RAW will make thousands of API calls. Hitting rate limits (HTTP 429 responses) will cause processing failures.

**Impact:**
- Pipeline fails mid-processing
- Manual intervention required to restart
- Extended processing time (3-6 hours → potentially much longer)
- Unpredictable completion time

**Source:** TRD-ETL-v2.md Section 4.6 (Error Handling)

---

## Decision

**Implement exponential backoff with configurable rate limiting.**

**Rationale:**
- Rate limits are external constraint we cannot eliminate
- Graceful degradation better than hard failure
- Resume capability (R3) allows recovery from interruptions
- Configurable limits allow adaptation to API tier

**Implementation (TRD-ETL-v2 Section 4.6):**
1. **Exponential Backoff:** On HTTP 429, wait `min(2^attempt, 60)` seconds before retry
2. **Max Retries:** 3 attempts per file, then mark as "error" in processing_log
3. **Rate Limiting:** Configurable RPM limit (default 60), pace requests accordingly
4. **Resume Capability:** If pipeline killed/interrupted, resume from processing_log on restart

**Configuration (CLI):**
```bash
--rate-limit 60  # Requests per minute (default)
--max-retries 3  # Retry attempts (default)
```

**Trade-offs Accepted:**
- Processing time may extend beyond 3-6 hour estimate
- Some files may fail after 3 retries (acceptable if <5%)
- Manual adjustment of --rate-limit may be needed based on API tier

---

## Status Updates

**2025-11-23:** Mitigation strategy implemented as part of T010 and validated during T014 Phase 2 (no rate limit issues encountered). This risk is now considered effectively mitigated.

---

## References

- TRD-ETL-v2.md Section 4.6 (Error Handling - LLM Errors)
- TRD-ETL-v2.md Section 6 (CLI - rate-limit argument)
- TRD-ETL-v2.md Section 4.4 (Resume Capability)
