---
name: queue-intake
type: ceremony
description: Create new work item at backlog queue position with ceremony logging.
  Use when capturing a new idea or requirement as a tracked work item. Wraps work-creation-cycle
  with queue ceremony event.
category: queue
input_contract:
  - field: description
    type: string
    required: true
    description: "What is the idea/work?"
  - field: traces_to
    type: string
    required: false
    description: "Which requirement does this trace to?"
  - field: rationale
    type: string
    required: false
    description: "Why is this being created now?"
output_contract:
  - field: work_id
    type: string
    guaranteed: on_success
    description: "Created WORK-XXX ID"
  - field: queue_position
    type: string
    guaranteed: on_success
    description: "Always backlog"
  - field: event_logged
    type: boolean
    guaranteed: on_success
    description: "Whether ceremony event was captured"
side_effects:
  - "Create work item"
  - "Log Intake ceremony event via log_queue_ceremony()"
generated: 2026-02-09
last_updated: '2026-02-09'
---
# Queue Intake Ceremony

Governs the creation of new work items at the `backlog` queue position. This ceremony logs the intake event for audit trail purposes.

## When to Use

- Capturing a new idea, bug, or requirement as a work item
- Creating work that enters the queue at `backlog` position

**Note:** This ceremony wraps work-creation-cycle. It does NOT replace it — it adds ceremony logging on top.

**Invocation:** `Skill(skill="queue-intake")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `description` | MUST | What is the idea/work? |
| `traces_to` | SHOULD | Which requirement does this trace to? |
| `rationale` | SHOULD | Why is this being created now? |

---

## Ceremony Steps

1. Invoke `work-creation-cycle` to create the work item
2. Work item created at `queue_position: backlog` (default)
3. Log Intake ceremony event via `log_queue_ceremony()`
4. Report created work item ID to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `work_id` | On success | Created WORK-XXX ID |
| `queue_position` | On success | Always `backlog` |
| `event_logged` | On success | Boolean confirming ceremony event captured |

---

## Implementation

```python
from queue_ceremonies import log_queue_ceremony

# After work-creation-cycle completes:
log_queue_ceremony(
    ceremony="Intake",
    items=[work_id],
    from_position="new",
    to_position="backlog",
    rationale="New work item created",
    agent="Hephaestus"
)
```

---

## Validation

- Work item must be successfully created before logging
- `queue_position` defaults to `backlog` on creation (WorkEngine.create_work)
- Intake is a logging-only ceremony (no state transition needed — create_work sets backlog)

---

## References

- CH-010: Queue Ceremonies specification
- REQ-QUEUE-004: Queue ceremonies govern transitions
- REQ-CEREMONY-002: Each ceremony has input/output contract
- work-creation-cycle: Creates the actual work item
