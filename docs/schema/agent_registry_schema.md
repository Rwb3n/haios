# Schema: `agent_registry.txt`

*   **ADR Reference:** ADR-OS-012: Dynamic Agent Management
*   **Location:** `os_root/agent_registry.txt`
*   **Purpose:** Serves as the central index of all available agent personas within the Hybrid_AI_OS instance. It provides a quick, queryable list mapping `persona_id`s to their detailed `Agent Card` files and key operational statuses. This file is dynamic and managed by OS-level actions.

---

## 1. Schema Structure

The `agent_registry.txt` file is a JSON object with a modular header and a payload.

```json
{
  "os_file_header": {
    "file_id": "agent_registry",
    "entity_type": "AGENT_REGISTRY",
    "schema_definition_id_ref": "HybridAI_OS_AgentRegistry_Payload_v1.0",
    "g_file_created": "int",
    "g_file_last_modified": "int",
    "v_file_instance": "int"
  },
  "payload": {
    "agent_cards_index": {
      "[persona_id]": {
        "agent_card_path": "str",
        "status": "ACTIVE|DISABLED|IN_MAINTENANCE",
        "current_agent_model_id": "str"
      }
    }
  }
}