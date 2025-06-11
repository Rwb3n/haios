# Schema: `init_plan_<g>.txt`

*   **ADR References:** ADR-002, ADR-005, ADR-009, ADR-010, ADR-014
*   **Location:** `os_root/initiatives/<g_creation>/init_plan_<g_creation>.txt`
*   **Purpose:** The high-level, strategic OS Control File for a major project objective. It defines the "why" and "what" for a significant body of work, serving as the charter that guides the creation of all tactical `Execution Plans` within its scope.

---

## 1. Schema Structure

The `init_plan_<g>.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "str",
    "entity_type": "INITIATIVE_PLAN",
    "schema_definition_id_ref": "HybridAI_OS_InitiativePlan_Payload_v5.2",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "initiative_id": "str", // Redundant for robustness, e.g., "init_plan_101"
    "status": "DRAFT|APPROVED|ACTIVE|COMPLETED_SUCCESS|COMPLETED_PARTIAL|FAILED|ARCHIVED|ON_HOLD",
    "origin_and_context": { /* ... */ },
    "strategic_definition": { /* ... */ },
    "scaffolding_directives": { /* ... */ }|null,
    "lifecycle_roadmap": { /* ... */ },
    "governance": { /* ... */ },
    "notes_and_context": ["str"]
    },

    "strategic_definition": {
      "overall_goal": "str",
      "_overall_goal_locked": false,
      "quality_acceptance_criteria": [
        {
          "criterion_id": "str",
          "description": "str",
          "metric_or_verification_method": "str",
          "_locked_entry_definition": false
        }
      ],
      "_quality_acceptance_criteria_list_immutable": false
    },
    
    "scaffolding_directives": {
      "_locked_object_definition": false,
      "master_scaffold_definition_id_ref": "str",
      "customization_parameters": [
        {
          "_locked_entry_definition": false,
          "parameter_name": "str",
          "value": "any"
        }
      ],
      "_customization_parameters_list_immutable": false
    }|null,

    "lifecycle_roadmap": {
      "_stages_list_is_immutable": false,
      "stages": [
        {
          "_locked_entry_definition": false,
          "stage_id": "str",
          "title": "str",
          "description": "str",
          "stage_order": "int",
          "expected_execution_plan_types": ["str"],
          "entry_criteria": [
            { "criterion_id": "str", "description": "str", "_locked_entry_definition": false }
          ],
          "_entry_criteria_list_immutable": false,
          "exit_criteria": [
            { "criterion_id": "str", "description": "str", "_locked_entry_definition": false }
          ],
          "_exit_criteria_list_immutable": false,
          "status": "PENDING|IN_PROGRESS|COMPLETED_SUCCESS|COMPLETED_PARTIAL|FAILED|BLOCKED|ON_HOLD",
          "linked_execution_plan_ids": ["str"],
          "g_status_updated": "int",
          "follow_on_initiative_plan_ids_from_stage": ["str"]|null
        }
      ],
      "follow_on_initiative_plan_ids_from_initiative": ["str"]|null
    },

    "governance": {
      "_decision_log_list_is_immutable": true, // A log is append-only, so the list of existing items is immutable.
      "decision_log": [
        {
          "_locked_entry_definition": true, // Each entry is immutable once written.
          "g_decision": "int",
          "decision_id": "str",
          "decision_point": "str",
          "decision_made": "str",
          "rationale": "str",
          "alternatives_considered_and_rejected": [ { "alternative": "str", "rejection_reason": "str" } ],
          "linked_supporting_artifact_ids": ["str"]
        }
      ]
    },

    "notes_and_context": ["str"]
  }
}

```
2. Field Descriptions (payload section)
2.1. initiative_id & status
initiative_id (string): The unique ID for this initiative, matching the file_id. Stored here for redundancy and easier querying.
status (string): The current high-level status of the entire initiative.
2.2. origin_and_context
Links the initiative to its origins. These fields are typically locked after the ANALYZE phase.
originating_request_id_ref (string, nullable): The ID of the Request that started this initiative.
_originating_request_id_ref_locked (boolean)
originating_analysis_report_id_refs (string[]): artifact_ids of Analysis Reports that justify this plan.
_originating_analysis_report_id_refs_list_immutable (boolean)
originating_artifact_ids_context (string[]): Key existing artifacts used as context.
_originating_artifact_ids_context_list_immutable (boolean)
linked_project_summary_id_ref (string, nullable): Link to global_project_summary.txt.
_linked_project_summary_id_ref_locked (boolean)
linked_issues_summary_id_ref (string, nullable): Link to this initiative's initiative_issues_summary_*.txt.
_linked_issues_summary_id_ref_locked (boolean)
2.3. strategic_definition
Defines what success looks like. Typically locked after approval.
overall_goal (string): A comprehensive, narrative objective.
_overall_goal_locked (boolean)
quality_acceptance_criteria (object[]): A list of verifiable success conditions.
_quality_acceptance_criteria_list_immutable (boolean)
Each entry: { "criterion_id": "str", "description": "str", "metric_or_verification_method": "str", "_locked_entry_definition": boolean }
2.4. scaffolding_directives (object, nullable)
Instructions for an initial SCAFFOLDING plan.
_locked_object_definition (boolean)
master_scaffold_definition_id_ref (string): ID of a schema in os_root/scaffold_definitions/.
customization_parameters (object[]): High-level key-value pairs to adapt the scaffold.
_customization_parameters_list_immutable (boolean)
Each entry: { "parameter_name": "str", "value": "any", "_locked_entry_definition": boolean }
2.5. lifecycle_roadmap
The ordered set of major work phases. The array index serves as the stage_order.
_stages_list_immutable (boolean): Locks the number and order of stages.
stages (object[]):
Each entry: { "stage_id": "str", "title": "str", ..., "_locked_entry_definition": boolean }
entry_criteria & exit_criteria: Now structured arrays: [{ "criterion_id": "str", "description": "str", "_locked_entry_definition": boolean }].
2.6. governance
Tracks key decisions and mandatory guidelines.
governing_guideline_artifact_ids (string[]): A list of mandatory guideline artifacts (from /docs/guidelines/) that apply to all work in this initiative.
_governing_guideline_artifact_ids_list_immutable (boolean)
decision_log (object[]): An append-only log of strategic decisions.
_decision_log_list_immutable (boolean): Should be true after plan approval, making it append-only.
Each entry is an object with _locked_entry_definition: true.