{
  "os_file_header": {
    "file_id": "str", // e.g., "initiative_issues_summary_101"
    "entity_type": "INITIATIVE_ISSUES_SUMMARY",
    "schema_definition_id_ref": "HybridAI_OS_InitiativeIssuesSummary_Payload_v5.1",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "init_plan_id": "str",
    "issues_map": {
      "[issue_id]": {
        "status": "str",
        "title": "str",
        "last_updated_g": "int",
        "trace_id": "str|null"
      }
    }
  }
}

## Field Descriptions

- `init_plan_id` (string): The ID of the `Initiative Plan` this issue summary belongs to.
- `issues_map` (object): A map where the key is the `issue_id` and the value is a summary of the issue.
  - `status` (string): The current status of the issue (e.g., `OPEN`, `IN_PROGRESS`, `RESOLVED`).
  - `title` (string): The title of the issue.
  - `last_updated_g` (integer): The `g` event counter value when this issue was last updated. **(ADR-027)**
  - `trace_id` (string, optional): The distributed trace ID associated with the last update. **(ADR-029)**