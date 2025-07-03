# Schema: `snapshot_<g>.json`

- **ADR References:** ADR-OS-011, ADR-027, ADR-029
- **Location:** `os_root/snapshots/snapshot_<g_creation>.json`
- **Purpose:** To create a comprehensive, immutable, point-in-time record of the OS's most critical operational state. Snapshots are read-only audit artifacts, generated at major project milestones (e.g., after a successful `VALIDATE` phase or the creation of a `Progress Review`). They are **not** used for automated state rollback but serve as a verifiable baseline for auditing, debugging complex historical states, or manual recovery operations.

---

## 1. Schema Structure

The `snapshot_<g>.json` file is a JSON object. As a data artifact rather than a frequently modified OS Control File, it has a slightly different header structure, focused on metadata about the snapshot itself.

```json
{
  "snapshot_header": {
    "snapshot_id": "snapshot_295",
    "g_created": 295,
    "triggering_event_type": "VALIDATION_COMPLETED",
    "triggering_event_summary": "Validation of exec_plan_288 completed successfully.",
    "triggering_artifact_id_ref": "validation_report_exec_plan_288_g294",
    "triggering_trace_id": "str|null",
    "schema_definition_id_ref": "HybridAI_OS_StateSnapshot_Payload_v1.0"
  },
  "payload": {
    "captured_state": {
      "file_id": "state",
      "g_captured": 295,
      "vector_clock_at_capture": "str|null",
      "content_hash": "sha256:...",
      "content": {
        // Full JSON content of state.txt at g=295
      }
    },
    "captured_project_summary": {
      "file_id": "global_project_summary",
      "g_captured": 295,
      "content_hash": "sha256:...",
      "content": {
        // Full JSON content of global_project_summary.txt at g=295
      }
    },
    "captured_plans": [
      {
        "file_id": "init_plan_284",
        "g_captured": 295,
        "content_hash": "sha256:...",
        "content": {
          // Full JSON content of init_plan_284.txt at g=295
        }
      },
      {
        "file_id": "exec_plan_288",
        "g_captured": 295,
        "content_hash": "sha256:...",
        "content": {
          // Full JSON content of exec_plan_288.txt at g=295
        }
      }
    ],
    "captured_execution_statuses": [
      {
        "file_id": "exec_status_288",
        "g_captured": 295,
        "content_hash": "sha256:...",
        "content": {
          // Full JSON content of exec_status_288.txt at g=295
        }
      }
    ],
    "governance_metadata": {
      "data_sensitivity_level": "INTERNAL",
      "license_of_captured_content": "PROPRIETARY"
    }
  }
}
```

---

## 2. Field Descriptions

### 2.1. `snapshot_header`

Metadata about the snapshot itself.

- `snapshot_id` (string): The unique ID for this snapshot, matching its filename (e.g., `"snapshot_295"`).
- `g_created` (int): The `g` value when the snapshot was created.
- `triggering_event_type` (string): The OS event that triggered this snapshot's creation (e.g., `VALIDATION_COMPLETED`, `PROGRESS_REVIEW_GENERATED`, `USER_REQUESTED`).
- `triggering_event_summary` (string): A human-readable summary of the trigger.
- `triggering_artifact_id_ref` (string, nullable): The ID of the artifact (like a Validation Report) whose creation triggered this snapshot.
- `triggering_trace_id` (string, optional): **(ADR-029)** The distributed trace ID of the operation that triggered the snapshot.
- `schema_definition_id_ref` (string): The version of the snapshot payload schema.

### 2.2. `payload`

Contains the captured data.

- `captured_state` / `captured_project_summary` (object): Objects containing a full copy of the `state.txt` and `global_project_summary.txt` content at the moment the snapshot was taken.
- `captured_plans` (object[]): An array containing full copies of all active `init_plan` and `exec_plan` files at the time of the snapshot.
- `captured_execution_statuses` (object[]): An array containing full copies of the `exec_status` files for the captured active `exec_plans`.

#### Common Captured Object Structure

- `file_id` (string): The ID of the captured file (e.g., `"state"`, `"init_plan_284"`).
- `g_captured` (int): The `g` value when this specific file was read for the snapshot.
- `vector_clock_at_capture` (string, optional): **(ADR-027)** The vector clock of the captured artifact, if available, for precise causal ordering.
- `content_hash` (string): A hash (e.g., SHA256) of the captured content object for integrity verification.
- `content` (object): A deep copy of the full JSON content (header and payload) of the original OS Control File.

- `governance_metadata` (object): Captures key governance metadata about the snapshot's contents for auditing.
  - `data_sensitivity_level` (string): The highest data sensitivity level of any captured content.
  - `license_of_captured_content` (string): The license governing the project content at this time.