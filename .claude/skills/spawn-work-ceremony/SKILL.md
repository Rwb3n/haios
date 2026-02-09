---
name: spawn-work-ceremony
description: "Create a linked work item from an existing work item."
category: spawn
stub: true
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
  - "Create linked work item"
generated: 2026-02-09
last_updated: "2026-02-09"
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

1. Validate parent work item exists
2. Create new work item via work-creation-cycle
3. Set spawned_by field to parent_work_id
4. Log SpawnWork ceremony event
5. Report new work item ID to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether spawn succeeded |
| `new_work_id` | On success | Created WORK-XXX ID |
| `parent_work_id` | Always | Source work item ID |

---

## Side Effects

- Create linked work item with spawned_by provenance

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- REQ-LIFECYCLE-004: Chaining is caller choice
- close-work-cycle: CHAIN phase may invoke spawn
- CH-011: CeremonyContracts
