---
name: memory-commit-ceremony
type: ceremony
description: "Store learnings to memory with provenance tracking."
category: memory
input_contract:
  - field: content
    type: string
    required: true
    description: "Learning content to store"
  - field: source_path
    type: string
    required: true
    description: "Provenance source path (e.g., closure:WORK-110)"
  - field: content_type_hint
    type: string
    required: false
    description: "Classification hint: episteme, techne, doxa, or unknown"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether memory commit succeeded"
  - field: concept_ids
    type: list
    guaranteed: on_success
    description: "Stored concept IDs from ingester"
  - field: classification
    type: string
    guaranteed: on_success
    description: "Final classification (episteme/techne/doxa)"
side_effects:
  - "Store to memory via ingester_ingest"
  - "Log MemoryCommitted event to governance-events.jsonl"
  - "Update work item memory_refs field"
generated: 2026-02-09
last_updated: "2026-02-12"
---
# Memory Commit Ceremony

Store learnings and insights to the HAIOS memory system with provenance tracking and classification.

## When to Use

- During close-work-cycle MEMORY phase
- When capturing significant learnings or decisions
- After observation triage promotes insights

**Invocation:** `Skill(skill="memory-commit-ceremony")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `content` | MUST | Learning content to store |
| `source_path` | MUST | Provenance source path (e.g., closure:WORK-110) |
| `content_type_hint` | SHOULD | Classification hint: episteme, techne, doxa, or unknown |

---

## Ceremony Steps

### Step 1: Validate Input
- Verify `content` is non-empty string (BLOCK if empty — return `{success: false, error: "Content is empty"}`)
- Verify `source_path` is non-empty string (BLOCK if empty — return `{success: false, error: "Source path is empty"}`)
- Default `content_type_hint` to "doxa" if not provided

### Step 2: Store to Memory
- Call `ingester_ingest` MCP tool:
  - `content`: The learning content
  - `source_path`: Provenance path (e.g., "closure:WORK-133")
  - `content_type_hint`: Classification hint (episteme, techne, doxa, or unknown)
- Capture returned concept IDs
- If ingester_ingest fails: WARN — log error, return `{success: false, error: "<message>"}`

### Step 3: Log Governance Event
- Log `MemoryCommitted` event to governance-events.jsonl:
  ```json
  {
    "type": "MemoryCommitted",
    "ceremony": "memory-commit",
    "source_path": "closure:WORK-133",
    "concept_count": 2,
    "timestamp": "2026-02-12T18:00:00"
  }
  ```
- Use `_log_ceremony_event()` from governance_layer or append directly to events file

### Step 4: Report Results
- Report concept IDs to operator
- Update work item `memory_refs` field with returned IDs
- If no concept IDs returned: WARN — log warning, return `{success: true, concept_ids: []}`

---

## Error Handling

| Error | Handling |
|-------|----------|
| Empty content | BLOCK — return `{success: false, error: "Content is empty"}` |
| Empty source_path | BLOCK — return `{success: false, error: "Source path is empty"}` |
| ingester_ingest failure | WARN — log error, return `{success: false, error: "<message>"}` |
| No concept IDs returned | WARN — log warning, return `{success: true, concept_ids: []}` |

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether memory commit succeeded |
| `concept_ids` | On success | Stored concept IDs from ingester |
| `classification` | On success | Final classification (episteme/techne/doxa) |

---

## Side Effects

- Store content to memory database via ingester_ingest

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- ADR-033: Work Item Lifecycle (WHY capture)
- close-work-cycle: Invokes memory commit during MEMORY phase
- CH-011: CeremonyContracts
