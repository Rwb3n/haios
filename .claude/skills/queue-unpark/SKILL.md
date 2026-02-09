---
name: queue-unpark
description: Move work item between parked and backlog (scope decision). Use when
  bringing a parked item into scope (Unpark) or deferring a backlog item out of scope
  (Park). Operator decision requiring rationale.
generated: 2026-02-09
last_updated: '2026-02-09'
---
# Queue Unpark/Park Ceremony

Governs transitions between `parked` and `backlog` queue positions. These are operator scope decisions that change whether a work item is in the current epoch's active scope.

## When to Use

- **Unpark:** Bringing a previously deferred item back into active scope
- **Park:** Deferring a backlog item out of current scope (e.g., to next epoch)

**Invocation:** `Skill(skill="queue-unpark")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `work_id` | MUST | Work item ID (e.g., WORK-067) |
| `direction` | MUST | "unpark" (parked->backlog) or "park" (backlog->parked) |
| `rationale` | MUST | Reason for scope decision (e.g., "Bringing into E2.5 scope") |

---

## Ceremony Steps

1. Read work item via `WorkEngine.get_work(work_id)`
2. Verify current queue_position matches expected source:
   - Unpark: must be `parked`
   - Park: must be `backlog`
3. Execute transition via `execute_queue_transition()`
4. QueueCeremony event logged to governance-events.jsonl
5. Report result to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Boolean indicating transition success |
| `work_id` | Always | The work item ID |
| `from_position` | On success | Source queue position |
| `to_position` | On success | Target queue position |
| `rationale` | On success | Captured rationale |
| `error` | On failure | Error description |

---

## Implementation

```python
from queue_ceremonies import execute_queue_transition

# Unpark: parked -> backlog
result = execute_queue_transition(engine, work_id, "backlog", "Unpark",
                                  rationale="Bringing into E2.5 scope")

# Park: backlog -> parked
result = execute_queue_transition(engine, work_id, "parked", "Park",
                                  rationale="Deferring to E2.6")
```

---

## Validation

- Transition must be valid per `QUEUE_TRANSITIONS` state machine (CH-009)
- Rationale is required for scope decisions
- Park/Unpark are the only transitions between `parked` and `backlog`

---

## References

- CH-010: Queue Ceremonies specification
- CH-009: Queue Lifecycle State Machine (QUEUE_TRANSITIONS)
- REQ-QUEUE-004: Queue ceremonies govern transitions
- REQ-QUEUE-005: Parked items excluded from current epoch scope
