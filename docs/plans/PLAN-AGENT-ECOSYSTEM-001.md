# generated: 2025-11-30
# System Auto: last updated on: 2025-11-30
# PLAN: Agent Ecosystem Architecture (Session 17)

> **Context:** [Session 17 Checkpoint](../checkpoints/2025-11-30-SESSION-17-agent-ecosystem-vision.md) -> **Ecosystem Plan (YOU ARE HERE)**

---

## 1. Goal Description

Establish the foundational architecture for the **HAIOS Agent Ecosystem**. This involves defining the schema for "Agents" and "Skills," deciding on the "Marketplace" implementation, and specifying the first two subagents (**Interpreter** and **Ingester**) to kickstart the ecosystem.

## 2. Key Decisions (Q1-Q3)

### Q1: First Agents to Design
**Decision:** **YES**, proceed with **Interpreter** and **Ingester**.
- **Rationale:**
    - **Interpreter:** Solves the "Vision Alignment" gap. It translates Operator intent (ambiguous) into System directives (explicit).
    - **Ingester:** Solves the "Input" gap. It operationalizes the "Extraction" phase of the refinery.
    - **Synergy:** Operator speaks to Interpreter -> Interpreter configures Ingester -> Ingester feeds Memory.

### Q2: Agent Card Schema
**Decision:** Use a **YAML-based Agent Card** stored in the `agent_registry` table.
- **Schema Draft:**
    ```yaml
    id: "agent-interpreter-v1"
    name: "Interpreter"
    version: "1.0.0"
    description: "Translates operator intent into system directives."
    type: "subagent"
    capabilities:
      - "vision-alignment"
      - "concept-translation"
    tools:
      - "memory_search_with_experience"
    input_schema:
      type: "object"
      properties:
        intent: {type: "string"}
    output_schema:
      type: "object"
      properties:
        directive: {type: "string"}
    ```

### Q3: Marketplace Architecture
**Decision:** **Hybrid Approach (Database + MCP)**.
- **Storage:** `agent_registry` and `skill_registry` tables in `memory.db`.
- **Access:** `haios-marketplace` MCP server exposing `marketplace_browse`, `marketplace_search`, `marketplace_get_agent`.
- **Rationale:** Agents need a standard tool interface (MCP) to "shop" for capabilities, while the system needs robust storage (SQL) for the registry.

---

## 3. Proposed Architecture Changes

### Database Schema (`memory_db_schema_v3.sql`)
#### [NEW] `agent_registry`
- `id` (PK, TEXT)
- `name` (TEXT)
- `description` (TEXT)
- `version` (TEXT)
- `card_json` (JSON) - Full schema
- `status` (TEXT) - active, deprecated

#### [NEW] `skill_registry`
- `id` (PK, TEXT)
- `name` (TEXT)
- `description` (TEXT)
- `provider_agent_id` (FK)

### MCP Server (`haios_marketplace`)
- **Tools:**
    - `marketplace_list_agents(filter_capability: str)`
    - `marketplace_get_agent(agent_id: str)`
    - `marketplace_register_agent(card: str)` (Admin only)

---

## 4. Subagent Specifications (High-Level)

### Agent 1: Interpreter
- **Role:** The "Front Desk" of HAIOS.
- **Responsibility:** Disambiguate user requests, map them to known skills/agents, and formulate a plan.
- **Key Skill:** `vision-alignment` (Checking request against `VISION-INTERPRETATION-SESSION.md`).

### Agent 2: Ingester
- **Role:** The "Mouth" of HAIOS.
- **Responsibility:** Read files/URLs, classify content (Episteme/Techne/Doxa), chunk, and store in Memory.
- **Key Skill:** `knowledge-classification` (Using `refinement.py` logic).

---

## 5. Implementation Steps

1.  **Schema Update:** Add `agent_registry` and `skill_registry` to `memory_db_schema_v3.sql`.
2.  **Marketplace MCP:** Create `haios_marketplace` server (or add to existing `mcp_server.py` for MVP).
3.  **Agent Cards:** Create initial YAML cards for Interpreter and Ingester.
4.  **Registration:** Register the initial agents into the database.

---

## 6. Verification Plan

### Automated Tests
- **Registry Test:** Register a dummy agent, retrieve it via SQL.
- **MCP Test:** Call `marketplace_list_agents` via MCP and verify output.

### Manual Verification
- **Browser:** Inspect `memory.db` to see registered agents.
- **Simulation:** Pretend to be an Orchestrator agent and "discover" the Interpreter agent using the Marketplace tool.

---

## 7. Implementation Status

**Status:** PHASE 1 COMPLETE (Session 17) | PHASE 2 APPROVED (2025-12-01)

### Phase 1: Infrastructure (COMPLETE - Session 17)
- [x] Schema Update: `agent_registry` and `skill_registry` added
- [x] Marketplace MCP: `marketplace_list_agents`, `marketplace_get_agent` tools
- [x] Agent Cards: Interpreter and Ingester registered
- [x] Tests: 88 passing (including registry and MCP tests)

### Phase 2: Agent Logic (APPROVED - Ready for Implementation)
See: [Validation Handoff](../handoff/2025-12-01-VALIDATION-interpreter-ingester-implementation.md)

**Design Decisions (DD-012 to DD-020):**
| ID | Decision | Rationale |
|----|----------|-----------|
| DD-012 | LLM-based translation with rule fallback | Handles ambiguity |
| DD-013 | No confidence threshold; return score | Caller decides |
| DD-014 | Proceed when no context (flag grounded=false) | Fail-open for MVP |
| DD-015 | Single-item ingestion (no batching) | Simplicity |
| DD-016 | 3 retries, exponential backoff (2s,4s,8s) | Existing pattern |
| DD-017 | Include agent ID in provenance | Audit trail |
| DD-018 | Synchronous collaboration | MVP simplicity |
| DD-019 | 30 second timeout | Industry standard |
| DD-020 | Hybrid architecture (module + MCP) | Testable + accessible |

---

## 8. References

| Document | Relationship |
|----------|--------------|
| [Session 17 Checkpoint](../checkpoints/2025-11-30-SESSION-17-agent-ecosystem-vision.md) | Vision context |
| [Validation Handoff](../handoff/2025-12-01-VALIDATION-interpreter-ingester-implementation.md) | Implementation spec |
| [Gap Closer Handoff](../handoff/2025-12-01-GAP-CLOSER-remaining-system-gaps.md) | Remaining gaps |
| [PLAN-AGENT-ECOSYSTEM-002](PLAN-AGENT-ECOSYSTEM-002.md) | Hardening plan (COMPLETE) |
| [Epistemic State](../epistemic_state.md) | System state tracking |
