---
name: queue-prioritize
type: ceremony
description: Move work items from backlog to ready queue position with rationale.
  Use when selecting items for upcoming work. Batch capable. Rationale required for
  audit trail.
category: queue
input_contract:
  - field: items
    type: list
    required: true
    description: "List of work item IDs to prioritize (e.g., ['WORK-067', 'WORK-093'])"
  - field: rationale
    type: string
    required: true
    description: "Why these items, in this order"
output_contract:
  - field: prioritized
    type: list
    guaranteed: always
    description: "List of work IDs successfully moved to ready"
  - field: failed
    type: list
    guaranteed: always
    description: "List of work IDs that failed (with reasons)"
  - field: rationale
    type: string
    guaranteed: always
    description: "Captured rationale for all transitions"
  - field: event_count
    type: integer
    guaranteed: always
    description: "Number of QueueCeremony events logged"
side_effects:
  - "Update queue_position from backlog to ready"
  - "Log QueueCeremony event per item"
generated: 2026-02-09
last_updated: '2026-02-09'
---
# Queue Prioritize Ceremony

Governs the transition from `backlog` to `ready` queue position. This ceremony requires rationale explaining why items were selected and supports batch operations.

## When to Use

- Selecting backlog items for upcoming work
- Triaging backlog to identify next priorities
- Moving items to `ready` status after assessment

**Invocation:** `Skill(skill="queue-prioritize")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `items` | MUST | List of work item IDs to prioritize (e.g., ["WORK-067", "WORK-093"]) |
| `rationale` | MUST | Why these items, in this order (e.g., "Critical dependency for CH-010") |

---

## Ceremony Steps

1. For each item in `items`:
   a. Read work item via `WorkEngine.get_work(work_id)`
   b. Verify current `queue_position == "backlog"`
   c. Execute transition via `execute_queue_transition()`
   d. QueueCeremony event logged per item
2. Report results (successes and any failures)

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `prioritized` | Always | List of work IDs successfully moved to `ready` |
| `failed` | Always | List of work IDs that failed (with reasons) |
| `rationale` | Always | Captured rationale for all transitions |
| `event_count` | Always | Number of QueueCeremony events logged |

---

## Implementation

```python
from queue_ceremonies import execute_queue_transition

results = []
for work_id in items:
    result = execute_queue_transition(
        engine, work_id, "ready", "Prioritize",
        rationale="Critical dependency for CH-010",
        agent="Hephaestus"
    )
    results.append(result)
```

---

## Validation

- All items must currently be at `backlog` position
- Rationale is required (operator must explain selection decision)
- Each item gets its own QueueCeremony event for individual traceability
- Batch failures are non-fatal (partial success allowed)

---

## References

- CH-010: Queue Ceremonies specification
- REQ-QUEUE-004: Queue ceremonies govern transitions
- REQ-CEREMONY-002: Each ceremony has input/output contract
- REQ-LIFECYCLE-003: Batch mode (multiple items in same phase)
