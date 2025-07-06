# ADR-OS-011: Task Failure Handling & Remediation

* **Status**: Proposed
* **Date**: 2025-06-09
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

---

## Context

Tasks will inevitably fail. A robust autonomous system must have a predictable, safe, and traceable process for handling these failures without corrupting state or halting progress indefinitely. A simple "crash and stop" approach is insufficient.

## Assumptions

* [ ] Automated, stateful rollback of file system changes is too complex and risky to be reliable.
* [ ] Failures, once they exceed a simple retry threshold, require formal tracking as `Issues`.
* [ ] Human or supervisor-level intelligence is necessary to diagnose and plan remediation for non-trivial failures.
* [ ] The retry policy and escalation thresholds are clearly defined and versioned.
* [ ] The system can distinguish between task failure and unreachable dependencies in distributed environments.
* [ ] The human_attention_queue and remediation process are auditable and tamper-evident.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-028, ADR-OS-029) are up-to-date and enforced.

_This section was expanded in response to [issue_assumptions.txt](../../issues/issue_assumptions.txt) to surface implicit assumptions and improve framework compliance._

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Fail-Safe Design v1.0
- **Compliance Proof:** "Log, Isolate, and Remediate" strategy ensures system fails safely without corrupting state or halting indefinitely.
- **Self-Critique:** Approach is intentionally heavyweight; simple task failures require creating new issue and plan.

### Distributed Systems Principles v1.0
- **Compliance Proof:** Addresses idempotency, partition tolerance, and observability for failure handling in distributed environments.
- **Self-Critique:** Distinguishing between task failure and unreachable dependency needs clearer implementation guidelines.

### Escalation Management v1.0
- **Compliance Proof:** Formal escalation to human_attention_queue when failures exceed retry thresholds.
- **Self-Critique:** Human attention queue presentation mechanism needs definition.

### Traceability v1.0
- **Compliance Proof:** Every failure creates Issue with complete context and trace_id linkage for debugging.
- **Self-Critique:** Relies on quality of initial failure report; poor failure_details make diagnosis difficult.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about rollback complexity, formal tracking needs, and human intelligence requirements.
- **Self-Critique:** Only three assumptions listed; failure handling likely has more implicit assumptions about retry policies and state management.

## Decision

**Decision:**

> We will adopt a **"Log, Isolate, and Remediate"** strategy. On task failure beyond retries, the agent MUST: 1) Update the task status to `FAILED` with details. 2) Log a new `Issue` containing all failure context. 3) Halt the current plan and escalate to the `human_attention_queue`. Remediation will occur via a new, explicit `REMEDIATION`-type `Execution Plan`.
>
> ### Distributed Systems Implications
>
> The failure handling process must be robust against the challenges of a distributed environment.
>
> *   **Idempotency & Retries (ADR-OS-023):** The initial, pre-`FAILED` state retry attempts mentioned in "Alternatives Considered" MUST adhere to the universal retry policy, using exponential backoff and circuit breakers to avoid retry storms. The task execution itself must be idempotent to ensure retries are safe.
> *   **Partition Tolerance (ADR-OS-028):** In a network partition, an agent must be able to distinguish between task failure and an unreachable dependency. If a required service is in a separate, unreachable partition, the task should be marked `BLOCKED`, not `FAILED`, to await partition healing.
> *   **Observability (ADR-OS-029):** Every task failure, retry attempt, and state change (`PENDING` -> `ACTIVE` -> `FAILED`) MUST be captured as events within a distributed trace. The resulting `Issue` must be linked to the `trace_id` of the failure for end-to-end debugging.

**Confidence:** High

## Rationale

1. **Avoids Complex State Management**
   * Self-critique: This approach is intentionally heavyweight. The failure of even a simple task requires creating a new issue and plan, which could slow down development for trivial errors.
   * Confidence: High
2. **Traceability of Remediation**
   * Self-critique: It relies on the quality of the initial failure report. If the agent's `failure_details` are poor, the resulting `Issue` may be difficult to diagnose.
   * Confidence: High
3. **Leverages Existing Mechanisms**
   * Self-critique: This could lead to a proliferation of small, single-task `REMEDIATION` plans, cluttering the project history.
   * Confidence: High

## Alternatives Considered

1. **Automated Artifact Rollback**: Rejected due to the high complexity of managing which files to revert and ensuring a consistent state across all related artifacts and OS Control Files.
   * Confidence: High
2. **Conversational Debugging Loop**: This is used *within* a task's retry attempts. The "Log, Isolate, Remediate" process is for when that inner loop fails, ensuring formal tracking.
   * Confidence: High

## Consequences

* **Positive:** Highly robust and safe. Creates a complete, auditable history of all failures and their resolutions. Simple to implement as it builds on existing OS primitives.
* **Negative:** Slower recovery for simple failures. A typo that fails a task might require a new plan to fix, which can feel heavyweight.

## Clarifying Questions

* What is the standard retry and escalation policy before a task is officially marked as `FAILED`, and how is this policy versioned and enforced?
* How does the `human_attention_queue` get presented to the supervisor, and what is the audit trail for human interventions?
* Can a `REMEDIATION` plan itself fail, and if so, does it trigger a new, nested remediation? How is remediation recursion managed?
* How does the system distinguish between task failure and unreachable dependencies in distributed or partitioned environments?
* What mechanisms are in place to audit, validate, and roll back failure and remediation events, especially in the presence of partial or conflicting updates?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*