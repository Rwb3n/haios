# V. CONTINUITY, ERROR HANDLING, & STATE MANAGEMENT

A robust autonomous system must be resilient. This section outlines the principles and procedures for handling task failures, ensuring data integrity, and managing the OS's state over time.

### A. Task Failure & Remediation (ADR-OS-011)

The OS follows a **"Log, Isolate, and Remediate"** strategy for task failure. Stateful, automated rollback of artifact content is explicitly avoided in favor of a more robust, traceable process.

1.  **Detection & Logging:**
    *   **Readiness Failure (ADR-OS-013):** If the mandatory pre-execution readiness check for a task fails, the task is immediately set to `BLOCKED`, and a `BLOCKER` `Issue` is logged. The `CONSTRUCT` phase for this task does not begin.
    *   **Runtime Failure:** If a task fails during execution and exceeds its configured retry attempts (defined in `haios.config.json` and overridable per-task), the executing agent's final action is to meticulously log the failure in the `exec_plan_*.txt`, populating the task's `execution_log.failure_details` and `retry_attempts_log`.

2.  **Isolation & Reporting:**
    *   The agent logs a new `Issue` (e.g., type `BUG`, `RUNTIME_ERROR`, `READINESS_BLOCKER`). This `Issue` contains all details from the failure and links back to the relevant plan, task, and artifacts.
    *   The OS immediately updates the corresponding `initiative_issues_summary_*.txt` and `global_issues_summary.txt` to reflect the new issue (ADR-OS-009).

3.  **Escalation:**
    *   The `Execution Plan`'s status is set to `BLOCKED` or `FAILED`.
    *   If the failure requires human action, the OS `state.txt.st` is set to `BLOCK_INPUT`, and an item is added to the `human_attention_queue.txt`, formally requesting supervisor intervention.

4.  **Planned Remediation:**
    *   The resolution of the `Issue` is handled through a new, planned unit of work.
    *   The `BLUEPRINT` phase for the new `REMEDIATION` plan consults the `agent_registry.txt` to ensure a persona with appropriate debugging or administrative capabilities is available and assigned (ADR-OS-012).

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