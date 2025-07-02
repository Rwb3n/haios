# Schema: `request_<g>.txt`

*   **ADR References:** ADR-OS-002, ADR-OS-005, ADR-023, ADR-029
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
    "idempotency_key": "user_cli_session_xyz_timestamp_123",
    "trace_id": "trace_abc_123",
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
```

---

## 2. Field Descriptions

- `idempotency_key` (string, optional): **(ADR-023)** A unique key provided by the client to prevent duplicate processing of the same request.
- `trace_id` (string, optional): **(ADR-029)** The distributed trace ID that this request is a part of. If this is the start of a new causal chain, the OS will generate a new trace_id.
- `source` (string): The origin of the request (e.g., `USER_DIRECT_COMMAND`, `AGENT_API_CALL`).
- `_source_locked` (boolean): Should be true.
- `request_summary` (string): A brief description of the request.
- `_request_summary_locked` (boolean): Should be true.
- `full_request_payload` (string): The full text of the request.
- `_full_request_payload_locked` (boolean): Should be true.
- `status` (string): The current status of the request.
- `linked_initiative_plan_id` (string): The ID of the initiative plan linked to the request.
- `linked_project_summary_id_ref` (string): The ID of the project summary linked to the request.
- `_linked_project_summary_id_ref_locked` (boolean): Should be true.
- `linked_originating_artifact_ids` (array of strings): The IDs of the originating artifacts linked to the request.
- `_linked_originating_artifact_ids_list_immutable` (boolean): Should be true.
- `linked_issue_ids_as_context` (array of strings): The IDs of the issues as context linked to the request.
- `_linked_issue_ids_as_context_list_immutable` (boolean): Should be true.
- `analysis_summary` (string): A summary of the analysis performed on the request.
