# ADR-OS-011: Task Failure Handling & Remediation

*   **Status:** Proposed
*   **Date:** 2025-06-09
*   **Context:**
    In any complex execution system, tasks will inevitably fail due to environmental issues, flawed logic, invalid inputs, or other unforeseen problems. A robust autonomous system must have a predictable, safe, and traceable process for handling these failures without corrupting state or halting progress indefinitely. A simple "crash and stop" approach is insufficient.

*   **Decision:**
    We will adopt a **"Log, Isolate, and Remediate"** strategy for task failure handling. Automated, stateful rollback of artifact content will be avoided in favor of explicit, planned remediation.

    The process is as follows:
    1.  **Detect & Log:** When a task in the `CONSTRUCT` phase fails and exceeds its configured retry attempts, the executing agent MUST record the failure state.
        *   It will update the task's `status` to `FAILED` in the `exec_plan_*.txt`.
        *   It will populate the task's `failure_details` object with the `g` of failure, a clear `reason`, and detailed technical error messages/stack traces.
        *   It will update the task's `retry_attempts_log`.
    2.  **Isolate & Report:** The agent MUST immediately log a new `Issue` of type `BUG`, `RUNTIME_ERROR`, or `BLOCKER`. This `Issue` will contain all details from the task's `failure_details` and link back to the failed plan, task, and any relevant artifacts.
    3.  **Halt & Escalate:** The OS will set the `Execution Plan`'s `status` to `BLOCKED` or `FAILED` and `state.txt.st` to `BLOCK_INPUT`. It will add an item to the `human_attention_queue.txt` referencing the new `Issue`, signaling that the automated process cannot continue without intervention.
    4.  **Remediate via New Plan:** The resolution of the `Issue` will be handled through the standard OS lifecycle. A human or Supervisor agent will analyze the `Issue` and `blueprint` a new `Execution Plan` of type `REMEDIATION`. This plan will contain tasks to fix the underlying problem (e.g., "Correct logic in `module_X.ts`," "Install missing dependency Y," "Fix configuration in `artifact_Z.json`").

*   **Rationale:**
    *   **Avoids Complex State Management:** Automated, stateful rollback of file system changes is extremely complex and fraught with edge cases. It can lead to inconsistent states. Our approach treats the failed state as a new "fact" to be addressed, which is simpler and more robust.
    *   **Traceability of Remediation:** By forcing failures to be resolved via a new `REMEDIATION` plan, the fix itself becomes a traceable, planned, and validated unit of work, just like any other feature development. This provides a clear audit trail of what went wrong and how it was fixed.
    *   **Leverages Existing Mechanisms:** This strategy reuses the existing `Issue` management and `Execution Plan` systems, requiring no new, complex rollback machinery. Failure handling becomes a standard part of the OS's operational loop.
    *   **Human-in-the-Loop for Complex Failures:** For non-trivial failures, human or high-level supervisor intelligence is often required to diagnose the root cause and determine the best corrective action. This model provides a natural escalation path for such scenarios.

*   **Consequences:**
    *   **Pros:**
        *   Highly robust and safe; prevents the OS from attempting complex, potentially destructive rollback operations.
        *   Creates a complete and auditable history of all failures and their resolutions.
        *   Simple to implement as it builds on existing OS primitives (Plans, Issues).
    *   **Cons:**
        *   Slower recovery for simple failures. A simple typo that fails a task might require a full new `REMEDIATION` plan to fix, which could feel heavyweight. (This can be mitigated by the intelligence of the Supervisor agent in creating very small, fast-tracked remediation plans).

*   **Alternatives Considered:**
    *   **Automated Artifact Rollback:** Using snapshots or VCS (like `git restore`) to automatically revert file changes on task failure. Rejected due to the high complexity of managing which files to revert, handling partially successful tasks, and ensuring a consistent state across all related artifacts and OS Control Files.
    *   **Conversational Debugging Loop:** Keeping the agent in a tight loop to try and fix the problem conversationally. While the agent can do this *within* its retry attempts for a single task, once that threshold is breached, we escalate to the more formal "Log, Isolate, Remediate" process to ensure the failure is formally tracked and resolved.