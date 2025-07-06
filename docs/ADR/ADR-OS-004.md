# ADR-OS-004: Global Event Tracking & Versioning (`g` and `v`)

* **Status**: Proposed
* **Date**: 2025-06-06
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

In an event-driven, asynchronous system where multiple actions can occur over time, a reliable mechanism is needed to sequence events, establish causality, ensure data integrity, and provide a comprehensive audit trail. Simple timestamps are prone to clock skew and don't provide a clear, causal sequence of OS-level events. Furthermore, when multiple agents could potentially interact with OS Control Files, a mechanism to prevent race conditions and stale data writes is required.

## Assumptions

* [ ] The global event counter (`g`) is always incremented atomically and never skipped.
* [ ] The version counter (`v`) is checked and incremented on every write to a mutable OS Control File.
* [ ] All agents interacting with OS Control Files implement the read-check-increment-write cycle for `v`.
* [ ] The system can detect and recover from failed or partial increments of `g` or `v`.
* [ ] Logical clocks (e.g., vector clocks) are used where causal ordering is required across distributed agents.
* [ ] The audit trail is only as reliable as the consistent use of `g` and `v` by all agents.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-027, ADR-OS-028, ADR-OS-029) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Distributed Systems Principles v1.0
- **Compliance Proof:** The "Distributed Systems Implications" section explicitly addresses logical clocks, partition tolerance, and observability for event tracking.
- **Self-Critique:** CP system behavior during partitions may halt operations; needs careful consideration of availability trade-offs.

### CAP Theorem v1.0
- **Compliance Proof:** Explicitly chooses Consistency and Partition tolerance (CP system) for state.txt, acknowledging availability trade-offs.
- **Self-Critique:** High contention on state.txt could impact system availability even without network partitions.

### Event Ordering v1.0
- **Compliance Proof:** Global event counter `g` provides total ordering of events; integration with vector clocks for causal ordering in distributed scenarios.
- **Self-Critique:** Simple integer counter may not scale to distributed, multi-node deployments without additional coordination mechanisms.

### Optimistic Locking v1.0
- **Compliance Proof:** Version counter `v` implements optimistic locking pattern to prevent stale writes and race conditions.
- **Self-Critique:** All agents must implement read-check-increment-write cycle; missing this pattern could lead to data corruption.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions section with checkboxes for validation about atomic increments and version checking.
- **Self-Critique:** Only three assumptions listed; event tracking system likely has more implicit assumptions about concurrency and failure modes.

### Audit Trail v1.0
- **Compliance Proof:** Global event counter provides comprehensive audit trail with unique, time-ordered IDs for all significant OS events.
- **Self-Critique:** Audit trail quality depends on consistent use of `g` increment; missing or incorrect usage could break traceability.

## Decision

**Decision:**

> We will adopt a dual-mechanism approach for system-wide event tracking and versioning:
> 1. **Global Event Counter (`g`)**: A single, monotonically increasing integer, stored in `state.txt`, incremented for every significant OS action. Used for sequencing, timestamping, and unique ID generation.
> 2. **Instance Version Counter (`v`)**: A per-file, integer-based version counter, present in the schema of all mutable OS Control Files. Used for optimistic locking to prevent stale writes.
>
> ### Distributed Systems Implications
>
> While `g` provides a simple total ordering, it is insufficient for complex distributed workflows. This system MUST be augmented by the following policies:
>
> *   **Logical Clocks (ADR-OS-027):** The `g` counter serves as the baseline for event ordering. However, for workflows requiring strict causal history across multiple agents or services, vector clocks MUST be used in addition to `g`.
> *   **Partition Tolerance (ADR-OS-028):** The `state.txt` file, which holds `g`, is a CP system. During a network partition, the inability to reliably increment `g` will halt operations in the minority partition that require a new global event ID.
> *   **Observability (ADR-OS-029):** The value of `g` at the time of an operation must be included in all structured logs and traces. This, combined with a `trace_id`, allows events to be correlated both by their absolute sequence and their causal flow.

**Confidence:** High

## Rationale

1. **Causal Ordering (`g`)**
   * Self-critique: If `g` is not updated atomically, event order could be ambiguous.
   * Confidence: High
2. **Data Integrity (`v`)**
   * Self-critique: If agents do not check `v` before writing, stale data could overwrite newer changes.
   * Confidence: High
3. **Simplicity & Durability**
   * Self-critique: The simplicity of integer counters may not scale to distributed, multi-node deployments without additional coordination. This is explicitly addressed by ADR-OS-027 and ADR-OS-028, which introduce logical clocks and partition tolerance protocols for more complex scenarios.
   * Confidence: High

## Alternatives Considered

1. **Timestamp-based Versioning**: Relies on synchronized clocks, which can be unreliable. Rejected in favor of a monotonic counter for sequencing.
   * Confidence: High
2. **Pessimistic Locking (File Locks)**: More complex and can reduce concurrency. Rejected in favor of optimistic locking for this use case.
   * Confidence: High

## Consequences

* **Positive:** Provides a robust, system-wide, ordered log of all significant events. Prevents data corruption from stale writes. Creates unique, time-ordered, and human-readable IDs for core entities. Simple to implement and maintain.
* **Negative:** `state.txt` becomes a point of high contention. All agents must implement the read-check-increment-write cycle for the `v` field.

## Clarifying Questions

* How will the system handle concurrent attempts to increment `g` and ensure atomicity across distributed agents?
* What is the recovery process if `v` or `g` is accidentally skipped, duplicated, or corrupted?
* How are audit trail gaps or inconsistencies detected and remediated?
* What mechanisms are in place to coordinate event and version counters in multi-node or partitioned deployments?
* How is the integrity and completeness of the event log validated, and what is the escalation process for detected anomalies?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
