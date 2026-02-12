---
name: spawn-work-ceremony
type: ceremony
description: "Create a linked work item from an existing work item."
category: spawn
input_contract:
  - field: parent_work_id
    type: string
    required: true
    description: "Source work item ID that spawns the new item"
    pattern: "WORK-\\d{3}"
  - field: title
    type: string
    required: true
    description: "Title for the new work item"
  - field: type
    type: string
    required: false
    description: "Work type (implementation, investigation, etc.)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether spawn succeeded"
  - field: new_work_id
    type: string
    guaranteed: on_success
    description: "Created WORK-XXX ID"
  - field: parent_work_id
    type: string
    guaranteed: always
    description: "Source work item ID"
  - field: error
    type: string
    guaranteed: on_failure
    description: "Error description"
side_effects:
  - "Create linked work item with spawned_by provenance"
  - "Update parent's spawned_children field"
  - "Create REFS.md portal for child item"
  - "Log SpawnWork event to governance-events.jsonl"
generated: 2026-02-09
last_updated: "2026-02-12"
---
# Spawn Work Ceremony

Create a new work item linked to an existing parent work item. Used when work completion reveals follow-on tasks.

## When to Use

- During close-work-cycle CHAIN phase
- When observation triage spawns new work
- When investigation reveals implementation tasks

**Invocation:** `Skill(skill="spawn-work-ceremony")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `parent_work_id` | MUST | Source work item ID that spawns the new item |
| `title` | MUST | Title for the new work item |
| `type` | SHOULD | Work type (implementation, investigation, etc.) |

---

## Ceremony Steps

Implemented by `spawn_ceremonies.execute_spawn()` in `.claude/haios/lib/spawn_ceremonies.py`:

1. Validate parent work item exists via `work_engine.get_work()`
2. Get next sequential WORK-XXX ID
3. Scaffold child work item with `spawned_by` set to parent_work_id
4. Create REFS.md portal for child (structural parity with WorkEngine.create_work)
5. Update parent's `spawned_children` field with new child ID
6. Log SpawnWork ceremony event to governance-events.jsonl
7. Report new work item ID to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether spawn succeeded |
| `new_work_id` | On success | Created WORK-XXX ID |
| `parent_work_id` | Always | Source work item ID |

---

## Side Effects

- Create linked work item with `spawned_by` set to parent work item ID
- Update parent work item's `spawned_children` field with new child ID
- Create `references/REFS.md` portal for child item
- Append `SpawnWork` event to `governance-events.jsonl`

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- REQ-LIFECYCLE-004: Chaining is caller choice
- close-work-cycle: CHAIN phase may invoke spawn
- CH-011: CeremonyContracts
