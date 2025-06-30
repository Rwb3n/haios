# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Question

Q1: Should idempotency keys be namespaced per endpoint or global?
Q2: How will key storage migrate from SQLite to a distributed store in Phase-2?
Q3: Can read-modify-write operations use the same key for GET and subsequent POST?
Q4: What metrics monitor retry attempts and circuit breaker trips?
Q5: How are long-running saga steps made idempotent across partial failures?

