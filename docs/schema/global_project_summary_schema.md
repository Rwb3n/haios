# Schema: `global_project_summary.txt`

- **ADR References:** ADR-002, ADR-008, ADR-009, ADR-025, ADR-027, ADR-029
- **Location:** `os_root/global_project_summary.txt`
- **Purpose:** To provide a single, high-level, mutable summary of the overall project's status across all initiatives. It is designed to be quickly parsed by a supervisor (human or AI) or a "cockpit" UI to get an immediate sense of the project's health, focus, and recent activity without needing to read multiple other files.

---

## 1. Schema Structure

The `global_project_summary.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "global_project_summary",
    "entity_type": "PROJECT_SUMMARY",
    "schema_definition_id_ref": "HybridAI_OS_ProjectSummary_Payload_v1.0",
    "g_file_created": 1,
    "g_file_last_modified": 290,
    "v_file_instance": 45
  },
  "payload": {
    "project_name": "Agent Browse SDK",
    "overall_project_status_summary": "Actively executing 'Phase 2: Enhanced Developer Experience'. Key initiative 'init_plan_185' is in progress with 75% completion. Currently focused on resolving 19 failing tests in the observability module.",
    "active_initiative_plan_ids": [
      "init_plan_185"
    ],
    "active_execution_plan_ids": [
      "exec_plan_288"
    ],
    "key_metrics": {
      "open_critical_issue_count": 2,
      "open_high_priority_issue_count": 8,
      "total_active_initiatives": 1,
      "total_active_execution_plans": 1
    },
    "recent_key_events_log": [
      {
        "_locked_entry_definition": true,
        "g_event": 289,
        "vector_clock": "str|null",
        "type": "VALIDATION_COMPLETED",
        "summary": "Validation for 'exec_plan_280' completed with partial success.",
        "linked_artifact_id": "validation_report_exec_plan_280_g288",
        "agent_archetype": "VALIDATOR",
        "trace_id": "str|null"
      },
      {
        "_locked_entry_definition": true,
        "g_event": 285,
        "vector_clock": "str|null",
        "type": "INITIATIVE_APPROVED",
        "summary": "New initiative 'init_plan_284' for auth refactor was approved.",
        "linked_artifact_id": "init_plan_284",
        "agent_archetype": "SUPERVISOR",
        "trace_id": "str|null"
      }
    ],
    "next_expected_milestone": "Complete 'Phase 2: Enhanced DX' by achieving >95% test pass rate and finalizing plugin framework enhancements."
  }
}
```

---

## 2. Field Descriptions (payload section)

- `project_name` (string): The human-readable name of the project, sourced from `haios.config.json` for consistency.
- `overall_project_status_summary` (string): A concise, narrative summary of the current project state. This is intended to be generated/updated by a Supervisor agent after major events (like the creation of a Progress Review).
- `active_initiative_plan_ids` (string[]): A list of `init_plan_ids` for all initiatives with a status of ACTIVE.
- `active_execution_plan_ids` (string[]): A list of `exec_plan_ids` for all execution plans with a status of ACTIVE.
- `key_metrics` (object): A collection of important, high-level counts for quick dashboarding.
  - `open_critical_issue_count` (integer): Count of open issues with CRITICAL severity.
  - `open_high_priority_issue_count` (integer): Count of open issues with HIGH severity.
  - ... (other key counts as needed).
- `recent_key_events_log` (object[]): A short, rolling log of the last ~5-10 major project-level events. This is not a complete audit trail but a "what's new" list.
  - `_locked_entry_definition` (boolean): Should be true as log entries are facts.
  - `g_event` (int): The `g` value when the event occurred.
  - `vector_clock` (string, optional): **(ADR-027)** The vector clock at the time of the event for precise causal ordering.
  - `type` (string): An enum for the event type (e.g., INITIATIVE_APPROVED, PLAN_COMPLETED, MILESTONE_REACHED, CRITICAL_ISSUE_LOGGED).
  - `summary` (string): A human-readable summary of the event.
  - `linked_artifact_id` (string, nullable): A link to a relevant plan, report, or issue.
  - `agent_archetype` (string, optional): **(ADR-025)** The archetype of the agent that reported the event.
  - `trace_id` (string, optional): **(ADR-029)** The distributed trace ID associated with the event.
- `next_expected_milestone` (string): A human-readable description of the next major strategic goal or milestone the project is working towards, likely derived from the active Initiative Plan.