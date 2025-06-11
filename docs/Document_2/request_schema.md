# Schema: `request_<g>.txt`

*   **ADR References:** ADR-OS-002, ADR-OS-005
*   **Location:** `os_root/user_requests/request_<g_creation>.txt`
*   **Purpose:** To serve as the atomic, immutable record of a single directive given to the OS. It is the formal starting point for all new work, triggering the `ANALYZE` phase. It can be issued by a human user or another authorized AI agent.

---

## 1. Schema Structure

The `request_<g>.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "request_281",
    "entity_type": "REQUEST",
    "schema_definition_id_ref": "HybridAI_OS_Request_Payload_v1.0",
    "g_file_created": 281,
    "g_file_last_modified": 285,
    "v_file_instance": 2
  },
  "payload": {
    "source": "USER_DIRECT_COMMAND",
    "_source_locked": true,
    "request_summary": "Refactor the authentication module to use new security guidelines.",
    "_request_summary_locked": true,
    "full_request_payload": "REQUEST: Refactor module @auth_module_g55 to comply with standards in @security_guidelines_v2_g270 and address findings in @issue_auth_vuln_g260.",
    "_full_request_payload_locked": true,
    "status": "ANALYZED",
    "linked_initiative_plan_id": "init_plan_284",
    "linked_project_summary_id_ref": "global_project_summary_main",
    "_linked_project_summary_id_ref_locked": true,
    "linked_originating_artifact_ids": [
      "auth_module_g55",
      "security_guidelines_v2_g270"
    ],
    "_linked_originating_artifact_ids_list_immutable": true,
    "linked_issue_ids_as_context": [
      "issue_auth_vuln_g260"
    ],
    "_linked_issue_ids_as_context_list_immutable": true,
    "analysis_summary": "Analysis complete. Proposed new initiative 'init_plan_284' to address the refactoring. See 'analysis_report_request_281_g283' for full details."
  }
}