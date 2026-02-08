# generated: 2026-02-03
# System Auto: last updated on: 2026-02-07T15:30:54
# Chapter: Queue Position Field

## Definition

**Chapter ID:** CH-007
**Arc:** queue
**Status:** Partially Implemented
**Implementation Type:** REFACTOR
**Depends:** None
**Work Items:** WORK-066 (complete, MVP), WORK-105 (blocked by WORK-106)

---

## Current State (Verified — Session 320)

**Source:** `.claude/haios/modules/work_engine.py` (lines 90-115)

WORK-066 (complete, Session 307) implemented an MVP with 3 values:
```python
@dataclass
class WorkState:
    # ... other fields ...
    queue_position: str = "backlog"  # WORK-066: backlog|in_progress|done
    cycle_phase: str = "backlog"     # WORK-066: renamed from current_node
```

**WorkEngine methods (implemented by WORK-066):**
- `set_queue_position(id, position)` — validates against `{backlog, in_progress, done}`
- `get_in_progress()` — returns items with `queue_position == "in_progress"`
- `_parse_work_file()` reads `queue_position` with `backlog` default
- `_write_work_file()` persists `queue_position`
- 6 tests in `test_work_engine.py` (lines 1142-1296)

**What exists (WORK-066 MVP):**
- `queue_position` field in WorkState (3 values: backlog/in_progress/done)
- Parse/write roundtrip for queue_position
- `set_queue_position()` with validation
- `get_in_progress()` query method
- Template updated with queue_position field

**What doesn't exist (gap to L4 target):**
- `ready` value (Prioritize ceremony output)
- `parked` value (REQ-QUEUE-005, scope exclusion)
- `in_progress` → `working` rename (terminology fix)
- Forbidden state combination enforcement
- Parked exclusion from `get_queue()` / `just ready`
- Independence tests (queue changes vs cycle changes)

---

## Problem

WORK-066 implemented an MVP with 3 queue_position values. L4 REQ-QUEUE-003 (updated Session 314) defines 5 values. The gap: `ready` and `parked` are missing, and `in_progress` should be renamed to `working` per terminology fix.

---

## Agent Need

> "I need queue position tracked separately from lifecycle phase so I can have an item in 'working' queue while it's in any lifecycle phase, not just specific nodes. And I need parked items invisible to survey-cycle."

---

## Requirements

### R1: Separate Queue Field (REQ-QUEUE-001)

WorkState has dedicated `queue_position` field with 5 values:

```yaml
# WORK.md frontmatter
status: active
queue_position: working    # 5 values: parked/backlog/ready/working/done
cycle_phase: SPECIFY       # Within design lifecycle
activity_state: DESIGN     # Governed activity
```

### R2: Four-Dimension Tracking

Per WORK-065 finding, WorkState tracks four orthogonal dimensions:

| Dimension | Field | Values | Purpose |
|-----------|-------|--------|---------|
| Lifecycle | status | active/blocked/complete/archived | ADR-041 authoritative |
| Queue | queue_position | **parked**/backlog/ready/**working**/done | Selection pipeline |
| Cycle | cycle_phase | per-lifecycle phases | Current phase |
| Activity | activity_state | EXPLORE/DESIGN/etc | Governed state |

**TERMINOLOGY FIX:** Use `working` (not `active`, not `in_progress`) to avoid collision with `status: active`.

| Term | Meaning | Context |
|------|---------|---------|
| `status: active` | Work not blocked | Lifecycle dimension |
| `queue_position: working` | Currently being worked | Queue dimension |

### R3: Forbidden State Combinations

Some combinations are invalid:

| Combination | Reason |
|-------------|--------|
| `status: complete` + `queue_position: working` | Complete work can't be actively worked |
| `status: blocked` + `queue_position: working` | Blocked work can't be actively worked |
| `status: archived` + `queue_position: !done` | Archived implies queue done |
| `queue_position: parked` + `queue_position: working` | N/A (single field) |

### R4: Independent State Machines

Queue and lifecycle are parallel state machines:

```
Queue:     parked ──→ backlog ──→ ready ──→ working ──→ done
                                    │
Work:                               └──→ [lifecycle phases] ──→ complete
```

### R5: Parked Items Excluded from Scope (REQ-QUEUE-005)

Parked items are excluded from current epoch scope:
- `get_queue()` excludes parked items
- `just ready` never shows parked items
- `survey-cycle` never presents parked items
- Parked != blocked (parked = scope decision, blocked = dependency)

| | Parked | Blocked |
|---|---|---|
| Meaning | Out of scope (future epoch) | Has unresolved dependency |
| Field | `queue_position: parked` | `status: blocked` + `blocked_by: [...]` |
| Visibility | Excluded from all queues | Visible but not selectable |
| Resolution | Operator decision (Unpark ceremony) | Dependency completion |

---

## Interface

### WorkState Schema Changes

```python
@dataclass
class WorkState:
    id: str
    status: str           # active, blocked, complete, archived
    queue_position: str   # parked, backlog, ready, working, done
    cycle_phase: str      # PLAN, DO, CHECK, DONE, etc.
    # ... other fields
```

### WORK.md Template Update

```yaml
---
id: WORK-XXX
status: active
queue_position: backlog   # parked|backlog|ready|working|done
cycle_phase: PLAN
---
```

### WorkEngine Changes

```python
VALID_QUEUE_POSITIONS = {"parked", "backlog", "ready", "working", "done"}

def set_queue_position(work_id: str, position: str) -> None:
    """Update queue position without affecting lifecycle."""

def get_by_queue_position(position: str) -> List[WorkState]:
    """Get all items at given queue position."""

def get_working() -> List[WorkState]:
    """Get items with queue_position: working. Replaces get_in_progress()."""
```

---

## Success Criteria

- [ ] WorkState has queue_position field with 5 valid values
- [ ] WORK.md template includes queue_position
- [ ] WorkEngine parses and writes queue_position
- [ ] queue_position changes don't affect cycle_phase (independence)
- [ ] cycle_phase changes don't affect queue_position (independence)
- [ ] Forbidden state combinations enforced
- [ ] Parked items excluded from get_queue() and get_ready()
- [ ] Unit tests for five-value validation
- [ ] Unit tests for four-dimension independence
- [ ] Unit tests for forbidden state combinations
- [ ] Unit tests for parked exclusion
- [ ] Migration: `in_progress` → `working` rename in existing files

---

## Non-Goals

- Queue ceremonies (see CH-010)
- Queue lifecycle transition rules (see CH-009)
- Transition validation via governance (see CH-009)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-001, REQ-QUEUE-005)
- @docs/work/active/WORK-065/WORK.md (conflation finding)
- @docs/work/active/WORK-066/WORK.md (MVP implementation, complete)
- @docs/work/active/WORK-105/WORK.md (full implementation, blocked by WORK-106)
- @docs/work/active/WORK-106/WORK.md (this alignment review)
