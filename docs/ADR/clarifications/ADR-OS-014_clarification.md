# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Question

Q1: What configurable timeout caps readiness check duration per task?
Q2: Will there be centralized readiness check modules reusable across tasks?
Q3: How are dynamic external dependencies (APIs) probed without causing side effects?
Q4: Does a passed readiness check cache results for short window to avoid duplicate work?
Q5: How are readiness assessments stored and linked to tasks for future audits?

