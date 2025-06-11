# Schema: `exec_plan_<g>.txt` (v5.4 - Immutable Spec)

*   **Status:** Ratified
*   **Date:** 2025-06-09
*   **ADR References:** ADR-002, ADR-010, ADR-016
*   **Supersedes:** v5.3

*   **Purpose:** The **immutable**, tactical "work order" that details the specific tasks required to complete an initiative stage. Once `APPROVED`, its definitional content is locked. All live progress is tracked in its companion `exec_status_<g_plan>.txt` file.

---

## 1. Schema Structure & Example

```json
{
  "os_file_header": {
    "file_id": "exec_plan_125",
    "entity_type": "EXECUTION_PLAN",
    "schema_definition_id_ref": "HybridAI_OS_ExecutionPlan_Payload_v5.4",
    "g_file_created": 125,
    "g_file_last_modified": 155,
    "v_file_instance": 4
  },
  "payload": {
    "execution_plan_id": "exec_plan_125",
    "plan_type": "DEVELOPMENT",
    "_plan_type_locked": true,
    "final_execution_status": "DONE",
    "final_validation_status": "VALIDATED_SUCCESS",
    "origin_and_context": {
      "parent_initiative_plan_id_ref": "init_plan_101",
      "_parent_initiative_plan_id_ref_locked": true,
      "parent_initiative_stage_id_ref": "stage_g101_02_develop_view",
      "_parent_initiative_stage_id_ref_locked": true,
      "preceding_execution_plan_id_ref": "exec_plan_115_scaffold",
      "_preceding_execution_plan_id_ref_locked": true,
      "linked_issues_summary_id_ref": "initiative_issues_summary_101"
    },
    "plan_definition": {
      "goal": "Implement the core user profile view component.",
      "_goal_locked": true,
      "scope_summary": ["Display user avatar, name, bio.", "Fetch data from user service."],
      "_scope_summary_list_immutable": true,
      "exclusions_summary": ["Editing functionality is out of scope."],
      "_exclusions_summary_list_immutable": true
    },
    "test_execution_metadata": null,
    "tasks": [
      {
        "_locked_entry_definition": true,
        "task_id": "task_g125_001_dev_view",
        "title": "Develop ProfileView Component",
        "description": "Create the React component for ProfileView using shadcn/ui components.",
        "intent": "To provide a reusable UI component for displaying user profile information.",
        "assigned_agent_persona": "CODING_ASSISTANT",
        "max_retries": 3,
        "context_loading_instructions": [],
        "inputs": [],
        "outputs": [],
        "execution_checklist": [],
        "dependencies": [],
        "criticality": "HIGH",
        "notes": ["Ensure component is responsive."]
      }
    ],
    "_tasks_list_immutable": true
  }
}

2. Task Definition Object Sub-Schema (payload.tasks[])
This object now only contains the immutable specification for a task. All dynamic/log fields have been removed.
_locked_entry_definition (boolean): Set to true when the plan is approved.
task_id: string
title: string
description: string
intent: string
assigned_agent_persona: string
max_retries (int): The configured retry limit for this task.
context_loading_instructions (object[]): The immutable list of context items to load.
inputs (object[]): The immutable list of primary input artifacts.
outputs (object[]): The immutable list of expected output artifacts.
execution_checklist (object[]): The immutable list of checklist items. The mutable status of these items would be tracked in the exec_status file if that level of granularity is needed, or just managed in the agent's short-term memory for the task.
dependencies (string[]): The immutable set of task_ids this task depends on.
criticality: string
notes (string[]): Initial notes from the blueprinting phase. Running notes move to the exec_status file or task-specific logs.
