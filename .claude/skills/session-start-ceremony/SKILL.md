---
name: session-start-ceremony
type: ceremony
description: "Initialize a new session with context loading and event logging."
category: session
stub: true
input_contract:
  - field: config_path
    type: path
    required: false
    description: "Path to haios.yaml config (auto-detected if not provided)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether session started successfully"
  - field: session_number
    type: integer
    guaranteed: on_success
    description: "Assigned session number"
  - field: context_loaded
    type: list
    guaranteed: on_success
    description: "List of context files loaded"
side_effects:
  - "Log event, load context"
generated: 2026-02-09
last_updated: "2026-02-09"
---
# Session Start Ceremony

Initialize a new HAIOS session by loading configuration, context files, and logging the session start event.

## When to Use

- At the beginning of every new session
- After coldstart orchestrator completes

**Invocation:** `Skill(skill="session-start-ceremony")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `config_path` | SHOULD | Path to haios.yaml config (auto-detected if not provided) |

---

## Ceremony Steps

1. Load haios.yaml configuration
2. Load epoch context and active arcs
3. Query memory refs from prior checkpoint
4. Log SessionStarted ceremony event
5. Report session number to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether session started successfully |
| `session_number` | On success | Assigned session number |
| `context_loaded` | On success | List of context files loaded |

---

## Side Effects

- Log SessionStarted event to governance-events.jsonl
- Load context files into agent working memory

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- coldstart command: Current session initialization mechanism
- CH-011: CeremonyContracts
