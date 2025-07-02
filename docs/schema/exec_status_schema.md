# Schema: `exec_status_<g_plan>.txt` (v1.0)

*   **Status:** Ratified
*   **Date:** 2025-06-09
*   **ADR References:** ADR-004, ADR-007, ADR-010, ADR-012, ADR-013, ADR-016, ADR-023, ADR-025, ADR-027, ADR-029
*   **Supersedes:** none

*   **Purpose:** To serve as the single, mutable source of truth for the live execution progress, metrics, and logs for its corresponding `exec_plan_<g_plan>.txt`. It separates the *observation* of work from the *specification* of work.

---

## 1. Schema Structure & Example

```json
{
  "os_file_header": {
    "file_id": "exec_status_125",
    "entity_type": "EXECUTION_STATUS",
    "schema_definition_id_ref": "HybridAI_OS_ExecutionStatus_Payload_v1.0",
    "g_file_created": 125,
    "g_file_last_modified": 145,
    "v_file_instance": 22
  },
  "payload": {
    "execution_plan_id_ref": "exec_plan_125",
    "payload_hash_previous": "sha256:abc...",
    "payload_hash_current": "sha256:def...",
    "g_last_update": 145,
    "last_mutation_trace_id": "str|null",
    "partition_status": "CONSISTENT|PARTITIONED|RECONCILING",
    "overall_status_summary": {
      "overall_completion_percentage": 50,
      "active_blockers_summary": [
        "Task task_003 blocked due to missing API key."
      ]
    },
    "key_achievements_log": [
      {
        "_locked_entry_definition": true,
        "g_event": 130,
        "achievement_summary": "Scaffolding of core UI components completed.",
        "linked_task_id": "task_001_scaffold",
        "linked_artifact_id": null,
        "trace_id": "str|null"
      }
    ],
    "tasks_status": [
      {
        "task_id_ref": "task_001_scaffold",
        "status": "DONE",
        "percent_complete": 100,
        "g_last_update": 130,
        "last_updated_by_persona_id": "CODING_ASSISTANT",
        "last_updated_by_archetype": "str",
        "signature_hash": "sha256:ghi...",
        "readiness_check": {
          "status": "PASSED",
          "g_checked": 128,
          "idempotency_key": "str|null",
          "readiness_assessment_id_ref": null
        },
        "execution_log": {
          "failure_details": null,
          "retry_attempts_log": [],
          "lock_override_log": []
        },
        "latest_test_status": null
      }
    ],
    "_tasks_status_list_immutable": false
  }
}

2. Field Descriptions (payload section)
2.1. Top-Level Fields
execution_plan_id_ref: The ID of the exec_plan this status file tracks. Used for GUID checks.
payload_hash_previous: A hash of the payload from the previous version of this file, creating a simple checksum chain to help detect out-of-order or unauthorized writes. null for the first version.
g_last_update: The global g value when this status file was last written to.
last_mutation_trace_id (string, optional): **(ADR-029)** The trace ID of the last operation that modified this file.
partition_status (string, optional): **(ADR-028)** The current partition tolerance state of this status file. Defaults to `CONSISTENT`.
2.2. overall_status_summary
An object containing plan-level roll-up metrics, typically updated by a Supervisor agent.
execution_status & validation_status: Mirrored from the exec_plan payload for convenience.
overall_completion_percentage: A calculated percentage based on completed tasks.
active_blockers_summary: A human-readable list of current high-priority blockers.
2.3. key_achievements_log
An append-only log of significant, positive milestones achieved during the plan's execution.
Each entry is an immutable record (_locked_entry_definition: true) and now includes a `trace_id` **(ADR-029)**.
2.4. tasks_status[]
The core of the status file. An array of objects, one for each task in the corresponding exec_plan.
task_id_ref: Links to the specific task definition in the exec_plan.
status: The current, mutable status of the task.
g_last_update: The g value when this task's status object was last changed.
last_updated_by_persona_id: The persona_id of the agent that performed the last update, providing a "signature."
last_updated_by_archetype (string): **(ADR-025)** The archetype of the agent that performed the last update.
readiness_check: The status of the mandatory pre-execution check for this task. Now includes an `idempotency_key` **(ADR-023)**.
execution_log: Contains the running logs for failures, retries, and lock overrides for this specific task.
latest_test_status: A structured object summarizing the results from the most recent relevant Test Results Artifact. Populated during or after test execution.
This schema provides a robust, mutable companion to the immutable Execution Plan.