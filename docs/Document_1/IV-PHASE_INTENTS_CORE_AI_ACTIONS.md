# IV. PHASE INTENTS & CORE AI ACTIONS

The Hybrid_AI_OS operates through a cycle of distinct phases. The OS transitions between these phases based on the current state, artifact completion, and directives. All actions must be verbose, comprehensive, and schema-compliant.

## A. ANALYZE Phase (ADR-OS-001)

### 1. Intent
To process a `Request`, conduct a thorough investigation, produce a formal `Analysis Report`, and use that report to formulate or update a strategic `init_plan`.

### 2. Process
1.  **Entry:** Set `state.txt.ph = "ANALYZE"`.
2.  **Initiate Analysis:** Trigger the `AI_Initiate_Analysis_And_Draft_Report` action. This creates a DRAFT `Analysis Report` artifact and blueprints an `ANALYSIS_EXECUTION` plan.
3.  **Transition to CONSTRUCT:** Set `state.txt.cp_id` to the new `ANALYSIS_EXECUTION` plan ID and transition to the `CONSTRUCT` phase to execute it.
4.  **Formulate Initiative (post-analysis):** After the `ANALYSIS_EXECUTION` plan is completed and validated, trigger the `AI_Formulate_Initiative_From_Completed_Analysis` action.
5.  **Create/Update Initiative Plan:** Based on the completed `Analysis Report`, create or update the target `init_plan_<g>.txt`, setting appropriate `_locked*` flags.
6.  **Transition to BLUEPRINT:** Set `state.txt.cp_id` to the new/updated `Initiative Plan ID` and transition to the `BLUEPRINT` phase.

## B. BLUEPRINT Phase

### 1. Intent
To translate the strategic goals of an `initiative_lifecycle_stage` into one or more detailed, tactical, and typed `Execution Plans`.

### 2. Process
1.  **Entry:** Set `state.txt.ph = "BLUEPRINT"`.
2.  **Trigger Action:** Call `AI_Blueprint_Execution_Plans_For_Initiative_Stage` with the active `init_plan_id` and `stage_id`.
3.  **Generate Core & Support Tasks:** Decompose the stage goal into core tasks and inject mandatory support tasks (for testing, documentation, etc.) based on the `plan_type` (e.g., `DEVELOPMENT`, `SCAFFOLDING`).
4.  **Apply Scaffolding (ADR-OS-006):** If the plan type is `SCAFFOLDING`, use the specified `Scaffold Definition` and initiative-specific `customization_parameters` to derive tasks.
5.  **Finalize Plan:** Create the `exec_plan_<g>.txt` with all tasks, dependencies, and `context_loading_instructions`.
6.  **Transition to CONSTRUCT:** Set `state.txt.cp_id` to a new `Execution Plan ID` and transition.

## C. CONSTRUCT Phase

### 1. Intent
To execute the tasks defined in an active `exec_plan` via specialized agents, creating and modifying Project Artifacts as specified.

### 2. Process
1.  **Entry:** Set `state.txt.ph = "CONSTRUCT"`.
2.  **Trigger Action:** Repeatedly call `AI_Execute_Next_Viable_Task_From_Active_Plan`.
3.  **Perform Readiness Check (ADR-OS-013):** For the selected task, first verify all environmental prerequisites. If the check fails, update `exec_status` to `BLOCKED_READINESS`, log a `BLOCKER` `Issue`, and do not proceed with the task.
4.  **Execute Task:** The assigned agent persona loads context and performs the work.
5.  **Update Status:** The agent **MUST** update the `exec_status_<g_plan>.txt` file with its progress, logs, and status. It **MUST NOT** modify the locked `exec_plan_<g>.txt` itself.
6.  **Transition:** When all tasks in the plan are complete (`DONE` or `SKIPPED`), update the `exec_status` with a final `execution_status` of `DONE` and transition to the `VALIDATE` phase.

## D. VALIDATE Phase

### 1. Intent
To rigorously audit the outcomes of a completed `exec_plan`, verifying all work against evidence and project standards. This is performed by a dedicated `Validation Agent` persona.

### 2. Process
1.  **Entry:** Set `state.txt.ph = "VALIDATE"`.
2.  **Trigger Action:** Call `AI_Validate_Completed_Execution_Plan` with the completed `exec_plan_id`.
3.  **Verify Evidence (ADR-OS-007):** Parse the `Test Results Artifact(s)`. Verify they are "signed" (authored) by a trusted `Testing Agent`.
4.  **Update Annotations:** Based on the evidence, update the `quality_notes` in the `EmbeddedAnnotationBlock` of the artifacts that were tested.
5.  **Log Issues:** Create new `Issue` files for any discrepancies, test failures, or non-compliance. Immediately trigger an update of the relevant `initiative_issues_summary_*.txt` and `global_issues_summary.txt` (ADR-OS-009).
6.  **Generate Report (ADR-OS-008):** Generate a comprehensive `Validation Report` artifact.
7.  **Finalize Status:** Write the final `validation_status` (e.g., `VALIDATED_SUCCESS`, `VALIDATED_FAILED`) to the plan's `exec_status_<g_plan>.txt` file, then archive it.
8.  **Create Snapshot:** After a successful validation of a major plan, emit a `snapshot_<g>.json` for immutable audit.
9.  **Transition:** Transition to `IDLE`, `BLUEPRINT` (for remediation), or signal readiness for the next `initiative_lifecycle_stage`.

## E. IDLE Phase

### 1. Intent
The default resting state, awaiting new directives or the resolution of blocking conditions.

### 2. Process
1.  **Entry:** Set `state.txt.ph = "IDLE"`.
2.  **Trigger Action:** `AI_Manage_Idle_State_And_Await_Input`.
3.  **Monitor for Requests:** Scan the `user_requests/` directory for new `Request` files. If found, transition to `ANALYZE`.
4.  **Manage Blocks:** If `state.txt.st` is `BLOCK_INPUT`, monitor the `human_attention_queue.txt` for user action.
5.  **(Future Consideration) Monitor Agent Health:** The OS may also poll for overdue tasks or status-file heartbeat gaps to detect crashed or stalled agents.