# Schema: `human_attention_queue.txt`

*   **ADR Reference:** (Implicitly supports ADR-OS-001 by managing a key state transition, directly addresses principles from our "The Goal" analysis).
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
        "status": "AWAITING_RESPONSE|RESPONSE_RECEIVED"
      }
    ]
  }
}