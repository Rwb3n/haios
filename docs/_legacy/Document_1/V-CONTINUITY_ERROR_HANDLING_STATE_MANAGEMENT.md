# V. CONTINUITY, ERROR HANDLING, & STATE MANAGEMENT

A robust autonomous system must be resilient. This section outlines the principles and procedures for handling task failures, ensuring data integrity, and managing the OS's state over time.

### A. Task Failure & Remediation (ADR-OS-011)

The OS adopts a **"Log, Isolate, and Remediate"** strategy for task failures, as defined in **ADR-OS-011**.

1.  **Log:** On failure, the agent immediately logs the error context to the `exec_status_<g>.txt` file.
2.  **Isolate:** The task is marked as `FAILED`. A detailed `Issue` of type `BLOCKER` is created and linked. The plan is halted.
3.  **Remediate:** A human or supervisor agent must approve a new, explicit `REMEDIATION`-type `Execution Plan` to fix the issue.

This process is now enhanced by the following policies:
*   **Idempotency (ADR-023):** Initial retries (before the `FAILED` state) and the remediation actions themselves must be idempotent to prevent cascading failures.
*   **Failure Propagation (ADR-026):** Failures are escalated up the agent hierarchy (e.g., Builder to Supervisor) according to a defined policy. The `human_attention_queue` is the ultimate escalation point.
*   **Observability (ADR-029):** The entire failure lifecycle, from initial retry to final remediation, must be captured within a single, continuous distributed trace via its `trace_id`.

### B. Constraint Violation Handling (ADR-OS-010)

When an agent encounters a locked constraint (`_locked*` flag) that prevents it from completing a task, it follows the "Isolate and Escalate" procedure:
1.  The task `status` is set to `BLOCKED`.
2.  A `BLOCKER` `Issue` is logged, detailing the conflict.
3.  An item is added to the `human_attention_queue.txt` with `reason_code: "USER_OVERRIDE_REQUESTED"`.
4.  Resolution requires an explicit `Request` from a supervisor to authorize the override.

### C. State Integrity & Optimistic Locking (ADR-OS-004)

To prevent data corruption from stale writes, the OS uses an optimistic locking mechanism for all mutable OS Control Files.
1.  **Version Counter (`v`):** Every OS Control File contains a `v_file_instance` in its `os_file_header`.
2.  **Read-Check-Write Cycle:** Before writing changes, the OS must verify that the `v` value of the file on disk has not changed since it was read. If it has not, the write proceeds, and `v` is incremented. If it has, the operation is aborted and retried after re-reading the newer data.

### D. Snapshot Strategy

To provide immutable restore points and support historical auditing, the OS can generate snapshots.
1.  **`snapshot_<g>.json` Artifact:** A snapshot is a single JSON file conforming to its own schema, containing a deep copy of key OS Control Files at a specific moment. For auditing, snapshots should also copy key governance metadata (e.g., `license`, `data_sensitivity_level`) from the included artifacts. An optional checksum for each embedded file can be included for tamper detection.
2.  **Read-Only Audit Artifacts:** Snapshots are strictly read-only audit artifacts; they are **never** automatically replayed or used for state rollback by the OS.
3.  **Triggering:** Snapshots are generated upon significant events, such as the successful validation of a major initiative stage, the generation of a `Progress Review`, or an explicit `Request`.

## B. State Management, Snapshots, and Partition Tolerance

State is managed through a combination of the central `state.txt` file and the distributed network of OS Control Files.

*   **Optimistic Locking:** All mutable control files (`state.txt`, `exec_status_*.txt`, etc.) use a `v_file_instance` counter for optimistic locking to prevent stale writes.
*   **Snapshots:** The OS can generate immutable, point-in-time `snapshot_<g>.json` artifacts at key milestones, providing a verifiable baseline for audits and manual recovery (**ADR-OS-011**).
*   **Partition Tolerance (ADR-028):** In a distributed environment, the system is designed to favor consistency and partition tolerance (CP). During a network partition, agents may lose access to central state. The protocol requires them to halt operations that require consistent state, log their partitioned status, and await reconnection and reconciliation. Key schemas contain a `partition_status` field to make this state explicit.