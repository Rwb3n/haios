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
    "issues_map": { /* Keyed by issue_id, containing a subset of fields from the issue file */ }
  }
}