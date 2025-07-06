# ADR-OS-016: Live Execution Status Tracking

*   **Status**: Proposed
*   **Date**: 2025-06-09
*   **Deciders**: \[List of decision-makers]
*   **Reviewed By**: \[List of reviewers]

---

## Context

As the OS executes tasks within an `exec_plan`, a significant amount of dynamic state is generated (task statuses, completion percentages, retry logs, test results). Placing this mutable, high-frequency data directly within the `exec_plan_<g>.txt` file violates the principle of plan immutability established in ADR-OS-010 (Constraint Locking). It forces agents to edit their own locked-down specifications, creating architectural tension and risking data corruption.

## Assumptions

*   [ ] The filesystem can handle the write frequency to the `exec_status_<g_plan>.txt` file without performance degradation.
*   [ ] A separate status file provides better contention management than updating a single large plan file.
*   [ ] The global `state.txt` can reliably point to the currently active status file.
*   [ ] The status file schema is robust against partial writes and concurrent updates.
*   [ ] The system can detect and recover from status/plan file desynchronization.
*   [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-027, ADR-OS-029) are up-to-date and enforced.

## Frameworks/Models Applied

This ADR applies the following canonical models and frameworks (per ADR-OS-032):

### Fail-Safe Design v1.0
- **Compliance Proof:** Retry mechanism with exponential backoff provides graceful degradation for transient failures; maximum retry limits prevent infinite loops.
- **Self-Critique:** Retry logic complexity might introduce new failure modes; incorrect retry categorization could waste resources.

### Distributed Systems Principles v1.0
- **Compliance Proof:** Exponential backoff with jitter prevents retry storms; addresses distributed system failure patterns and cascading failures.
- **Self-Critique:** Missing explicit handling of partial work completion and state consistency during retries.

### Performance Optimization v1.0
- **Compliance Proof:** Intelligent retry reduces unnecessary work repetition; exponential backoff optimizes resource usage during failure recovery.
- **Self-Critique:** Retry overhead and delay might impact overall system throughput; aggressive retries could consume more resources than immediate failure.

### Assumption Surfacing v1.0
- **Compliance Proof:** Explicit assumptions about failure categorization, backoff effectiveness, and retry limit configuration.
- **Self-Critique:** Only three assumptions listed; retry logic likely has more implicit assumptions about task idempotency and state management.

### Traceability v1.0
- **Compliance Proof:** Retry attempts and outcomes are logged with task context for pattern analysis and debugging.
- **Self-Critique:** Trace data might not capture enough context to distinguish between different types of transient failures.

### Escalation Management v1.0
- **Compliance Proof:** After maximum retries exceeded, clear escalation path to human intervention with detailed failure context.
- **Self-Critique:** Escalation effectiveness depends on quality of failure categorization and diagnostic information provided.

## Decision

**Decision:**

> We will architecturally separate the **immutable plan** from its **mutable execution status**. This will be achieved by:
>
> 1.  **Stripping all dynamic/live state fields** from the `exec_plan_<g>.txt` schema. The `Execution Plan` becomes a purely definitional, immutable "work order" after its `DRAFT` phase is complete and its definitional fields are locked.
> 2.  Introducing a new, dedicated OS Control File: **`exec_status_<g_plan>.txt`**. This file will be created alongside its corresponding `Execution Plan` and will serve as the single, mutable source of truth for all live execution progress, metrics, logs, and status updates for that plan.
>
> ### Implementation Details
>
> *   **Creation:** When an `Execution Plan` is blueprinted, a corresponding `exec_status_*.txt` file will be created in the same directory, initialized with "0% complete" status.
> *   **Updates:** During the `CONSTRUCT` phase, executing agents write *only* to this `exec_status_*.txt` file to report progress, log retries, and record test outcomes.
> *   **Security:** Status updates can be "signed" with the `persona_id` of the writing agent and protected with a simple hash chain to ensure integrity.
> *   **Lifecycle:** After the `VALIDATE` phase for a plan is complete, the `exec_status_*.txt` file is effectively frozen. Its final state can be summarized in the `Validation Report`, and the file itself is then considered `ARCHIVED`.
> *   **State Reference:** The global `state.txt` will contain a `current_exec_status_id_ref` for convenient access to the live status of the currently active plan.
>
> ### Distributed Systems Implications
>
> The `exec_status_*.txt` file acts as a shared log and is subject to the following policies:
>
> *   **Asynchronicity (ADR-OS-024):** Agents MUST update the status file asynchronously. They should emit a "status update" event and continue their work, not block while waiting for the file write to complete. A dedicated log-writing service or agent should handle the batching and writing of these events.
> *   **Event Ordering (ADR-OS-027):** Every update written to the status file is an event and MUST contain a logical timestamp (e.g., a vector clock) to ensure that a causal sequence of events can be reconstructed, even if the events are written out of order due to network latency.
> *   **Observability (ADR-OS-029):** Every status update event (e.g., "task started," "test passed") MUST be part of a distributed trace, linked to the `trace_id` of the overarching task execution. This allows for fine-grained performance analysis and debugging.

**Confidence:** High

## Rationale

1.  **Restores Plan Immutability**
    *   Self-critique: This introduces an extra file to manage for every plan, increasing the number of artifacts in the system.
    *   Confidence: High
2.  **Clear Separation of Concerns**
    *   Self-critique: An agent or human operator now needs to consult two files instead of one to get the full picture of a plan and its progress.
    *   Confidence: High
3.  **Enables Rich, Machine-Readable Telemetry**
    *   Self-critique: The structure of the status file must be carefully designed to be both easily parsable and extensible for future metrics.
    *   Confidence: High
4.  **Mitigates Write Contention**
    *   Self-critique: This assumes agents update their own distinct sections of the file. If multiple agents need to update a single global field (e.g., overall percentage complete), contention can still occur.
    *   Confidence: Medium

## Alternatives Considered

1.  **Keeping Live State in Plan**: The previous model. Rejected because it violates the locking/immutability principle and creates architectural tension.
    *   Confidence: High
2.  **In-Memory Status Tracking**: Relying on the Supervisor agent's memory for status. Rejected as it is not durable, not easily accessible to other agents, and would be lost on restart.
    *   Confidence: High

## Consequences

*   **Positive:** Achieves true immutability for approved `Execution Plans`. Provides a dedicated, structured artifact for real-time progress monitoring. Improves system scalability and reduces write conflicts. Creates a cleaner, more logical data model.
*   **Negative:** Increases the number of OS Control Files to manage. Requires a migration strategy for any existing `Execution Plan` artifacts that contain live state.

## Clarifying Questions

*   What is the migration path for old `Execution Plan` files that contain live state?
*   How does the system ensure that the `exec_plan` and its `exec_status` file do not get out of sync? This is managed via the event ordering guarantees of ADR-OS-027.
*   How are partial writes, concurrent updates, and file corruption detected and recovered in the status file?
*   What mechanisms are in place to audit, validate, and roll back erroneous or malicious status updates?
*   How is the schema for the status file versioned and evolved to support new metrics or fields without breaking compatibility?

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*