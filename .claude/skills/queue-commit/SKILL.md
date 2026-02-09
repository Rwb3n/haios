---
name: queue-commit
description: Move work item from ready to working queue position, signaling active
  work session. Use when starting implementation of a ready item. Typically invoked
  by survey-cycle after work selection.
category: queue
input_contract:
  - field: work_id
    type: string
    required: true
    description: "Work item ID to commit (e.g., WORK-110)"
    pattern: "WORK-\\d{3}"
  - field: rationale
    type: string
    required: false
    description: "Why starting now (optional — commit is mechanical)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether transition succeeded"
  - field: work_id
    type: string
    guaranteed: always
    description: "The work item ID"
  - field: queue_position
    type: string
    guaranteed: on_success
    description: "working"
  - field: error
    type: string
    guaranteed: on_failure
    description: "Error description"
side_effects:
  - "Start work, log event"
  - "Log QueueCeremony event to governance-events.jsonl"
generated: 2026-02-09
last_updated: '2026-02-09'
---
# Queue Commit Ceremony

Governs the transition from `ready` to `working` queue position. This ceremony signals that active work has begun on an item.

## When to Use

- Starting implementation of a selected work item
- Signaling that a `ready` item is now being actively worked on
- Typically invoked after survey-cycle selects an item

**Invocation:** `Skill(skill="queue-commit")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `work_id` | MUST | Work item ID to commit (e.g., WORK-110) |
| `rationale` | SHOULD | Why starting now (optional — commit is mechanical, not a scope decision) |

---

## Ceremony Steps

1. Read work item via `WorkEngine.get_work(work_id)`
2. Verify current `queue_position == "ready"`
3. (Optional) Check `get_working()` for single-tasking policy
4. Execute transition via `execute_queue_transition()`
5. QueueCeremony event logged to governance-events.jsonl
6. Report result to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Boolean indicating transition success |
| `work_id` | Always | The work item ID |
| `queue_position` | On success | `working` |
| `error` | On failure | Error description |

---

## Implementation

```python
from queue_ceremonies import execute_queue_transition

result = execute_queue_transition(
    engine, work_id, "working", "Commit",
    rationale="Starting work on queue ceremonies",
    agent="Hephaestus"
)
```

---

## Policy Notes

- **Single-tasking:** The skill layer MAY enforce a single-working-item policy by checking `WorkEngine.get_working()` before committing. This is a policy decision, not enforced by the ceremony module.
- **Release:** The transition from `working` to `done` is handled by `close-work-cycle` (CH-008 decision). There is no separate `queue-release` skill.

---

## Validation

- Work item must currently be at `ready` position
- Transition validated by `QUEUE_TRANSITIONS` state machine (CH-009)
- Rationale is optional (commit is a mechanical action, unlike Park/Prioritize which are decisions)

---

## References

- CH-010: Queue Ceremonies specification
- CH-008: Release IS close-work-cycle (no separate Release skill)
- REQ-QUEUE-004: Queue ceremonies govern transitions
- REQ-CEREMONY-002: Each ceremony has input/output contract
- survey-cycle: Selects work item, may invoke Commit
