# Schema: `global_issues_summary.txt`

*   **ADR References:** ADR-009, ADR-025, ADR-027, ADR-029
*   **Location:** `os_root/global_issues_summary.txt`
*   **Purpose:** To serve as the single, global index of all `Issue` artifacts across all initiatives.

---
## 1. Schema Structure
```json
{
  "os_file_header": {
    "file_id": "global_issues_summary",
    "entity_type": "GLOBAL_ISSUES_SUMMARY",
    "schema_definition_id_ref": "HybridAI_OS_GlobalIssuesSummary_Payload_v1.0",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "issues_map": {
      "[issue_id]": {
        "status": "str",
        "title": "str",
        "severity": "str",
        "initiative_id_ref": "str",
        "last_updated_g": "int",
        "last_updated_by_archetype": "str",
        "trace_id": "str|null"
      }
    }
  }
}
```

---

## 2. Field Descriptions

- `issues_map` (object): A map where the key is the `issue_id` and the value is a summary of the issue.
  - `status` (string): The current status of the issue (e.g., `OPEN`, `IN_PROGRESS`, `RESOLVED`).
  - `title` (string): The title of the issue.
  - `severity` (string): The severity of the issue (e.g., `CRITICAL`, `HIGH`).
  - `initiative_id_ref` (string): The ID of the initiative this issue belongs to.
  - `last_updated_g` (integer): The `g` event counter value when this issue was last updated. **(ADR-027)**
  - `last_updated_by_archetype` (string, optional): The archetype of the agent that performed the last update. **(ADR-025)**
  - `trace_id` (string, optional): The distributed trace ID associated with the last update. **(ADR-029)**