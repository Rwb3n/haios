---
name: session-end-ceremony
type: ceremony
description: "Finalize session with orphan check and event logging."
category: session
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
last_updated: "2026-02-11"
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

All steps execute within a `ceremony_context("session-end")` boundary per REQ-CEREMONY-001.

### Step 1: Check for Orphan Work Items

- **Note:** Orphan detection is handled by `ColdstartOrchestrator` at next session start (RECOVERY phase). It detects incomplete work items and orphan sessions automatically.
- At session-end, skip programmatic orphan scan — the agent should note any work left in-progress in the session summary for operator awareness.
- This is informational, not a blocker — operator may intentionally leave work in progress.

### Step 2: Check for Uncommitted Changes

- Run `git status --porcelain` to detect uncommitted changes
- If changes exist, warn operator:
  ```
  Uncommitted changes detected:
  - {list of changed files}
  Consider creating a checkpoint before ending session.
  ```
- This is a **warning**, not a blocker

### Step 3: Log SessionEnded Event

- Execute: `just session-end {N}`
- This invokes `governance_events.log_session_end(session, "Hephaestus")`
- Event appended to `.claude/haios/governance-events.jsonl`:
  ```json
  {"type": "SessionEnded", "session": N, "agent": "Hephaestus", "timestamp": "..."}
  ```

### Step 4: Report Session Summary

Format:
```
Session {N} ended.
- Completed this session: [list work items completed, or "none"]
- Orphan items: {count} ({list IDs if any, or "none"})
- Uncommitted changes: {yes/no}
- Pending for next session: [items from checkpoint pending field, if checkpoint created]
```

---

## Pre-Conditions

- **SHOULD** invoke `checkpoint-cycle` before session-end to capture state
- **SHOULD** invoke `observation-capture-cycle` for any completed work items
- Session number auto-detected from `.claude/session` file if not provided

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
