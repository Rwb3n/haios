# Schema: `request_summary.txt`

- **ADR References:** ADR-OS-002, ADR-OS-009 (by analogy)
- **Location:** `os_root/request_summary.txt`
- **Purpose:** To serve as the global index and status summary for all `request_<g>.txt` files. It provides a single, centralized place to quickly view all directives given to the OS and their current processing state. This is essential for supervisor oversight and UI dashboarding.

---

## 1. Schema Structure

The `request_summary.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "request_summary",
    "entity_type": "REQUEST_SUMMARY",
    "schema_definition_id_ref": "HybridAI_OS_RequestSummary_Payload_v1.0",
    "g_file_created": 1,
    "g_file_last_modified": 286,
    "v_file_instance": 52
  },
  "payload": {
    "requests_map": {
      "request_281": {
        "status": "ANALYZED",
        "request_summary": "Refactor the authentication module to use new security guidelines.",
        "g_created": 281,
        "linked_initiative_plan_id": "init_plan_284"
      },
      "request_286": {
        "status": "PENDING_ANALYSIS",
        "request_summary": "Generate Q2 Progress Review for stakeholder meeting.",
        "g_created": 286,
        "linked_initiative_plan_id": null
      }
    }
  }
}
```

---

## 2. Field Descriptions

### 2.1. `os_file_header`

A standard modular header block for OS Control Files.

- `file_id`: Constant string `"request_summary"`.
- `entity_type`: Constant string `"REQUEST_SUMMARY"`.

### 2.2. `payload`

- `requests_map` (object):  
  A map where each key is a unique `request_id` string (e.g., `"request_281"`).  
  The value for each `request_id` is an object containing key information mirrored from the full `request_<g>.txt` file for quick access. This summary is updated by the OS whenever a Request is created or its status changes.

#### `requests_map.[request_id]` (object)

- `status` (string): The current processing status of the Request. Mirrored from `request_*.txt.payload.status`.  
  Enum: `PENDING_ANALYSIS`, `ANALYSIS_IN_PROGRESS`, `ANALYZED`, `PLAN_GENERATED`, `REJECTED`, `FAILED_TO_PROCESS`.
- `request_summary` (string): A mirrored copy of the concise summary from the Request file.
- `g_created` (int): The `g` value when the Request was created.
- `linked_initiative_plan_id` (string, nullable): The id of the `init_plan` that was created or updated to address this request. Mirrored from `request_*.txt.payload.linked_initiative_plan_id`.