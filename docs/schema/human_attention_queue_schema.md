# Schema: `human_attention_queue.txt`

*   **ADR Reference:** ADR-026, ADR-029
*   **Location:** `os_root/human_attention_queue.txt`
*   **Purpose:** To serve as a single, explicit queue of items that require human attention, review, or intervention. When the OS enters a `BLOCK_INPUT` state, it MUST add a corresponding item to this queue. This file allows a user or a "cockpit" UI to quickly see what is blocking the system's progress without parsing other complex state files.

---

## 1. Schema Structure

The `human_attention_queue.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "human_attention_queue",
    "entity_type": "HUMAN_ATTENTION_QUEUE",
    "schema_definition_id_ref": "HybridAI_OS_HumanAttentionQueue_Payload_v1.0",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "queue_items": [
      {
        "queue_item_id": "str",
        "g_queued": "int",
        "priority": "CRITICAL|HIGH|NORMAL",
        "reason_code": "APPROVAL_REQUIRED|CLARIFICATION_NEEDED|CRITICAL_FAILURE_HALT|USER_OVERRIDE_REQUESTED|AGENT_ESCALATION",
        "summary_of_request": "str",
        "requesting_agent_persona_id": "str|null",
        "linked_artifact_ids_for_review": ["str"],
        "linked_issue_id": "str|null",
        "status": "AWAITING_RESPONSE|RESPONSE_RECEIVED",
        "trace_id": "str|null",
        "escalation_policy": {
          "on_timeout_escalate_to_persona_id": "str|null",
          "timeout_seconds": "int"
        }
      }
    ]
  }
}
```

---

## 2. Field Descriptions

- `queue_items` (object[]): An array of items requiring attention.
  - `queue_item_id` (string): A unique ID for this queue item.
  - `g_queued` (integer): The `g` event counter value when the item was added.
  - `priority` (string): The priority level.
  - `reason_code` (string): A machine-readable code for why this item was queued.
  - `summary_of_request` (string): A human-readable summary.
  - `requesting_agent_persona_id` (string): The persona ID of the agent that raised this item.
  - `linked_artifact_ids_for_review` (string[]): A list of artifact IDs relevant to this request.
  - `linked_issue_id` (string): The ID of a formal `Issue` artifact, if one was created.
  - `status` (string): The current status of the queue item.
  - `trace_id` (string, optional): **(ADR-029)** The distributed trace ID associated with the event that triggered this queue item.
  - `escalation_policy` (object, optional): **(ADR-026)** Defines behavior if the item is not addressed in a timely manner.
    - `on_timeout_escalate_to_persona_id` (string, optional): The persona to re-assign this to on timeout.
    - `timeout_seconds` (integer, optional): The timeout duration in seconds.
