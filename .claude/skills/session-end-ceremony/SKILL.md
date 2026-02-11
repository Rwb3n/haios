---
name: session-end-ceremony
type: ceremony
description: "Finalize session with orphan check and event logging."
category: session
stub: true
input_contract:
  - field: session_number
    type: integer
    required: false
    description: "Session number to end (auto-detected from context)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether session ended successfully"
  - field: orphan_count
    type: integer
    guaranteed: on_success
    description: "Number of orphan items detected"
  - field: event_logged
    type: boolean
    guaranteed: on_success
    description: "Whether SessionEnded event was logged"
side_effects:
  - "Log event, orphan check"
generated: 2026-02-09
last_updated: "2026-02-09"
---
# Session End Ceremony

Finalize a HAIOS session by checking for orphan work items and logging the session end event.

## When to Use

- At the end of every session
- Before closing the CLI

**Invocation:** `Skill(skill="session-end-ceremony")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `session_number` | SHOULD | Session number to end (auto-detected from context) |

---

## Ceremony Steps

1. Check for orphan work items (active but not in any chapter)
2. Check for uncommitted changes
3. Log SessionEnded ceremony event
4. Report session summary to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether session ended successfully |
| `orphan_count` | On success | Number of orphan items detected |
| `event_logged` | On success | Whether SessionEnded event was logged |

---

## Side Effects

- Log SessionEnded event to governance-events.jsonl
- Orphan check (warn if items found)

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- checkpoint-cycle: Should be invoked before session-end
- CH-011: CeremonyContracts
