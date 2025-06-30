# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Questions

Q1: What signing mechanism authenticates override REQUEST artifacts?
Q2: Will there be a namespace/schema for different lock types to avoid ambiguity?
Q3: How can read-only minority partitions continue non-mutating work without lock conflicts?
Q4: What telemetry will surface counts of active locks and recent override events?
Q5: Are composite locks (affecting multiple fields atomically) supported, and how represented?

