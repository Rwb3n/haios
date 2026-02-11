---
name: memory-commit-ceremony
type: ceremony
description: "Store learnings to memory with provenance tracking."
category: memory
stub: true
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
generated: 2026-02-09
last_updated: "2026-02-09"
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

1. Validate content is non-empty
2. Call ingester_ingest with content and source_path
3. Log MemoryCommit ceremony event
4. Report concept IDs to operator

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
