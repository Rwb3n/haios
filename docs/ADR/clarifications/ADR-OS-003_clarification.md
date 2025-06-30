# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Question

Q1: What recovery process is defined if an EmbeddedAnnotationBlock becomes corrupted or partially deleted?
Q2: How will concurrent annotation updates be orchestrated to avoid race conditions across distributed agents?
Q3: What strategy will be employed for non-text artifacts (e.g., binaries) that cannot embed JSON blocks?
Q4: How will schema version migrations be automated to guarantee backward compatibility?
Q5: What audit trail fields (e.g., trace_id, vector_clock) are mandatory within each annotation update event?

