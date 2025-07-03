# Schema: `state.txt` (v1.0)

- **ADR References:** ADR-001, ADR-004, ADR-027, ADR-028, ADR-029
- **Location:** `os_root/state.txt`
- **Purpose:** The central, ephemeral state file for the Hybrid_AI_OS instance. It is the single source of truth for the OS's current operational status, active workloads, and the global event counter (`g`). It is read and updated frequently by the OS orchestrator.

---

## 1. Schema Structure

The `state.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "state",
    "entity_type": "STATE",
    "schema_definition_id_ref": "HybridAI_OS_State_Payload_v1.0",
    "g_file_created": 0,
    "g_file_last_modified": 280,
    "v_file_instance": 150
  },
  "payload": {
    "g": 280,
    "vector_clock": "str|null",
    "last_mutation_trace_id": "str|null",
    "ph": "IDLE",
    "st": "READY",
    "partition_status": "CONSISTENT|PARTITIONED|RECONCILING",
    "cp_id": null,
    "ct_id": null,
    "current_exec_status_id_ref": null,
    "rt": {},
    "active_issue_ids": [],
    "last_error": null
  }
}
```

---

## 2. Field Descriptions

### 2.1. `os_file_header`

A standard modular header block for OS Control Files.

- `file_id`: Constant string `"state"`.
- `entity_type`: Constant string `"STATE"`.
- `g_file_last_modified`: This field serves as the authoritative Global Event Counter (`g`). It is incremented upon every significant OS action.
- `v_file_instance`: The optimistic locking version number for this file. It is incremented on every write to prevent race conditions.

### 2.2. `payload`

Contains the dynamic operational state of the OS.

- `g` (integer): A mirror of the `g_file_last_modified` value from the header. This is included for convenience and backward compatibility of logic that expects a top-level `g`.
- `vector_clock` (string, optional): **(ADR-027)** The vector clock representing the current state of the distributed system.
- `last_mutation_trace_id` (string, optional): **(ADR-029)** The trace ID of the last operation that modified this state file.
- `ph` (string): The current Phase of the OS.  
  Enum: `ANALYZE`, `BLUEPRINT`, `CONSTRUCT`, `VALIDATE`, `IDLE`.
- `st` (string): The current Status of the OS.  
  Enum: `READY` (awaiting work), `BUSY` (actively processing), `BLOCK_INPUT` (awaiting human/supervisor intervention).
- `partition_status` (string, optional): **(ADR-028)** The current partition tolerance state of the OS. Defaults to `CONSISTENT`.
- `cp_id` (string, nullable): The ID of the Current Plan being focused on. This can be an `init_plan_id` or an `exec_plan_id` depending on the phase.
- `ct_id` (string, nullable): The ID of the Current Task being executed within the current `exec_plan`.
- `current_exec_status_id_ref` (string, nullable): A direct reference to the `file_id` of the `exec_status_*.txt` file corresponding to the active `exec_plan`. This provides a one-hop lookup for live progress.
- `rt` (object): A map for tracking Retry Counts for failing tasks.  
  Keys are task IDs (e.g., `task_g125_001_dev_view`), values are integers representing the number of retries.
- `active_issue_ids` (string[]): A cached list of issue IDs with a status of `OPEN` or `IN_PROGRESS`, for quick access by the OS.
- `last_error` (string, nullable): A summary of the last critical error message if the OS enters an error state.