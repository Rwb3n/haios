# ADR-OS-016: Live Execution Status Tracking

*   **Status:** Proposed
*   **Date:** 2025-06-09
*   **Context:**
    As the OS executes tasks within an `exec_plan`, a significant amount of dynamic state is generated (task statuses, completion percentages, retry logs, test results). Placing this mutable, high-frequency data directly within the `exec_plan_<g>.txt` file violates the principle of plan immutability established in ADR-OS-010 (Constraint Locking). It forces agents to edit their own locked-down specifications, creating architectural tension and risking data corruption.

*   **Decision:**
    We will architecturally separate the **immutable plan** from its **mutable execution status**. This will be achieved by:

    1.  **Stripping all dynamic/live state fields** from the `exec_plan_<g>.txt` schema. The `Execution Plan` becomes a purely definitional, immutable "work order" after its `DRAFT` phase is complete and its definitional fields are locked.
    2.  Introducing a new, dedicated OS Control File: **`exec_status_<g_plan>.txt`**. This file will be created alongside its corresponding `Execution Plan` and will serve as the single, mutable source of truth for all live execution progress, metrics, logs, and status updates for that plan.

*   **Rationale:**
    *   **Restores Plan Immutability:** This change perfectly aligns with ADR-OS-010. Agents no longer need to modify a locked `Execution Plan` during `CONSTRUCT`. They read the immutable instructions from the plan and write their mutable status updates to the separate status file.
    *   **Clear Separation of Concerns:** It creates a clean architectural boundary. `exec_plan` is the *specification*. `exec_status` is the *observation*. This mirrors other patterns in the OS, like the separation of `Scaffold Definition` (spec) from `Project Artifact` (observation/output).
    *   **Enables Rich, Machine-Readable Telemetry:** The `exec_status_*.txt` file becomes a rich source of structured telemetry for an in-progress plan, capturing pass/fail counts, completion percentages, and blockers in a machine-parsable format ideal for "cockpit" UIs and supervisor agent monitoring.
    *   **Mitigates Write Contention:** By structuring the `exec_status` file correctly (e.g., agents update their own task's sub-object), we can mitigate write contention issues that would arise from multiple agents trying to update a single monolithic plan file.

*   **Implementation Details:**
    *   **Creation:** When an `Execution Plan` is blueprinted, a corresponding `exec_status_*.txt` file will be created in the same directory, initialized with "0% complete" status.
    *   **Updates:** During the `CONSTRUCT` phase, executing agents write *only* to this `exec_status_*.txt` file to report progress, log retries, and record test outcomes.
    *   **Security:** Status updates can be "signed" with the `persona_id` of the writing agent and protected with a simple hash chain to ensure integrity.
    *   **Lifecycle:** After the `VALIDATE` phase for a plan is complete, the `exec_status_*.txt` file is effectively frozen. Its final state can be summarized in the `Validation Report`, and the file itself is then considered `ARCHIVED`.
    *   **State Reference:** The global `state.txt` will contain a `current_exec_status_id_ref` for convenient access to the live status of the currently active plan.

*   **Consequences:**
    *   **Pros:**
        *   Achieves true immutability for approved `Execution Plans`.
        *   Provides a dedicated, structured artifact for real-time progress monitoring.
        *   Improves system scalability and reduces write conflicts.
        *   Creates a cleaner, more logical data model.
    *   **Cons:**
        *   Increases the number of OS Control Files to manage.
        *   Requires a migration strategy for any existing `Execution Plan` artifacts that contain live state.

*   **Alternatives Considered:**
    *   **Keeping Live State in Plan:** The previous model. Rejected because it violates the locking/immutability principle and creates architectural tension.
    *   **In-Memory Status Tracking:** Relying on the Supervisor agent's memory for status. Rejected as it is not durable, not easily accessible to other agents, and would be lost on restart.