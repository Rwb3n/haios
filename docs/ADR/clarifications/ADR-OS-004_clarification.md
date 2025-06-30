# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Questions

Q1: What consensus or locking mechanism ensures atomic g increments across multiple OS instances?
Q2: What automated rollback or repair process exists if a gap (skipped g) or duplicate is detected in production?
Q3: How will high-frequency event generation avoid write contention on state.txt without sacrificing strict ordering?
Q4: Under what conditions can minority partitions safely continue read-write operations, or must they remain read-only until reconciliation?
Q5: Which log/trace fields are mandatory to correlate g, v, and trace_id for complete observability?
