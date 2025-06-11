# Schema: `Agent Card` (e.g., `persona_coding_assistant.txt`)

*   **ADR Reference:** ADR-OS-012: Dynamic Agent Management
*   **Location:** `os_root/agents/persona_<id>.txt`
*   **Purpose:** To provide a single, detailed, and dynamic source of truth for a specific agent persona available to the OS. It defines the agent's role, capabilities, current configuration (including the specific AI model), operational status, and a log of its key activities.

---

## 1. Schema Structure

The `Agent Card` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "str", // e.g., "persona_coding_assistant"
    "entity_type": "AGENT_CARD",
    "schema_definition_id_ref": "HybridAI_OS_AgentCard_Payload_v1.0",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "persona_id": "str",
    "_persona_id_locked": true,
    "description": "str",
    "status": "ACTIVE|DISABLED|IN_MAINTENANCE",

    "capabilities": {
      "_locked_object_definition": false,
      "maps_to_plan_types": ["str"],
      "supported_processing_actions": ["str"],
      "specializations": ["str"]
    },

    "model_configuration": {
      "current_agent_model_id": "str",
      "model_parameters": {
        "temperature": "float",
        "max_tokens": "int",
        "top_p": "float",
        "system_prompt_base_id_ref": "str|null" // Optional: ID of a base system prompt artifact
      },
      "supported_models": [
        { "model_id": "str", "notes": "str" }
      ]
    },

    "operational_history": [
      {
        "_locked_entry": true,
        "g_event": "int",
        "event_type": "TASK_STARTED|TASK_COMPLETED|MODEL_SWAPPED|STATUS_CHANGED|SESSION_CREATED",
        "summary": "str",
        "linked_exec_plan_id": "str|null",
        "linked_task_id": "str|null"
      }
    ],

    "notes": "str"
  }
}