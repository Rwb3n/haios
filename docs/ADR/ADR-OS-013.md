# ADR-OS-013: Pre-Execution Readiness Checks

*   **Status:** Proposed
*   **Date:** 2024-05-31 (g value of this session)
*   **Context:**
    Executing a task within an `Execution Plan` can be computationally expensive and may have side effects. Attempting to execute a task when its environmental prerequisites (e.g., required tools, configuration files, dependencies, input artifacts) are missing or invalid leads to guaranteed failure, wasted resources, and potentially corrupted state. A proactive mechanism is needed to verify that a task is ready to be executed *before* its primary work commences.

*   **Decision:**
    We will mandate that a **"Readiness Check"** is the first step in the execution of any task within the `CONSTRUCT` phase.

    This check is a formal, non-negotiable procedure where the executing agent verifies the existence, accessibility, and basic validity of all environmental prerequisites for the task. The prerequisites are determined by analyzing the task's `inputs` and, crucially, its `context_loading_instructions`.

    If the Readiness Check fails:
    1.  The agent **MUST NOT** proceed with the main execution of the task.
    2.  The agent **MUST** set the task's `status` to `BLOCKED`.
    3.  The agent **MUST** log a new `Issue` of type `BLOCKER`, detailing precisely which prerequisites are missing or invalid.
    4.  The agent's work on the task ceases, and the OS waits for a `REMEDIATION` plan to fix the environment before the original task can be retried.

    The output of a successful Readiness Check can be a simple internal "pass" or, for complex tasks like test execution, it can be a formal **`Readiness Assessment`** artifact (.md) detailing the status of all components.

*   **Rationale:**
    *   **Fail-Fast Principle:** This approach identifies environmental and dependency issues at the earliest possible moment, preventing the system from wasting time and compute on tasks that are destined to fail.
    *   **Reduces "Context Overwhelm":** By separating the "Is the environment ready?" check from the "Do the actual work" logic, we create focused agent actions. A "builder" agent isn't distracted by setup issues; it receives a task only when the environment is confirmed ready.
    *   **Explicit Error Reporting:** Instead of cryptic failures deep inside a task's execution (e.g., "cannot find file"), the system generates a clear, actionable `Issue` (e.g., "Prerequisite `.env.local` file is missing for task X").
    *   **Improved System Stability:** Prevents tasks from leaving the system in a partially-completed or inconsistent state due to environmental failures.

*   **Implementation within the `CONSTRUCT` Phase:**

    The `AI_Execute_Next_Viable_Task_...` core action will be updated to include this logic:

    ```
    1. Select viable task.
    2. Update state.ct_id to this task.
    3. --> **PERFORM READINESS CHECK for the task:**
           a. Parse task.inputs and task.context_loading_instructions.
           b. Verify existence of all referenced artifact IDs in `global_registry_map.txt`.
           c. Verify existence of required files/tools on the file system (e.g., `.env.local`, `k6` binary if needed).
           d. Verify project dependencies are installed (e.g., `node_modules` exists if `package.json` is a context).
           e. **IF CHECK FAILS:**
              i.   Update task status to `BLOCKED`.
              ii.  Create a `BLOCKER` issue with details.
              iii. Update state.st to `BLOCK_INPUT` (awaiting remediation plan).
              iv.  Cease processing this task.
           f. **IF CHECK PASSES (and is complex enough to warrant it):**
              i.   Optionally generate a `readiness_assessment_gX.md` artifact.
    4. --> **EXECUTE PRIMARY TASK WORK (only if Readiness Check passed).**
    5. ... (Continue with normal task completion logic).
    ```

*   **Consequences:**
    *   **Pros:**
        *   Dramatically increases the reliability and robustness of task execution.
        *   Makes debugging environmental setup issues straightforward via the generated `BLOCKER` issues.
        *   Fits perfectly with the "separation of concerns" principle for agent actions.
    *   **Cons:**
        *   Adds a small amount of overhead at the beginning of every task for the verification step. This is a highly worthwhile trade-off for the increased reliability.

*   **Alternatives Considered:**
    *   **No Explicit Check (Reactive Failure):** Letting tasks fail mid-execution and then trying to parse the error logs. Rejected as messy, unreliable, and provides poor-quality error reporting.
    *   **A Single Validation Phase for Environment:** Having one big check at the beginning of an `Execution Plan`. Rejected because different tasks within the same plan may have different environmental needs, making a single upfront check insufficient or overly broad. A per-task check is more precise.