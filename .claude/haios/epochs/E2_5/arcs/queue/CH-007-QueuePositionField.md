# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:29:16
# Chapter: Queue Position Field

## Definition

**Chapter ID:** CH-007
**Arc:** queue
**Status:** Planned
**Implementation Type:** REFACTOR
**Depends:** None
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/haios/modules/work_engine.py` (lines 90-112)

WorkState dataclass exists with these fields:
```python
@dataclass
class WorkState:
    id: str
    title: str
    status: str           # active, blocked, complete, archived
    current_node: str     # DAG node
    type: str             # feature, investigation, bug, chore, spike
    blocked_by: List[str]
    node_history: List[Dict]
    memory_refs: List[int]
    requirement_refs: List[str]  # traces_to
    source_files: List[str]
    acceptance_criteria: List[str]
    artifacts: List[str]
    extensions: Dict[str, Any]
    path: Optional[Path]
    priority: str         # For queue ordering
```

**Source:** `.claude/haios/config/work_queues.yaml`

Queue config exists separately from WorkState:
```yaml
queues:
  workitem-evolution:
    type: fifo
    items: [WORK-001, E2-179]
    allowed_cycles: [implementation-cycle, work-creation-cycle]
```

**What exists:**
- `priority` field in WorkState (E2-290)
- Separate work_queues.yaml config with queue types (fifo, priority, batch, chapter_aligned)
- WorkEngine methods: `load_queues()`, `get_queue()`, `get_next()`, `is_cycle_allowed()`

**What doesn't exist:**
- `queue_position` field in WorkState
- Per-item queue position tracking (queues.yaml lists items, doesn't track position)

---

## Problem

Queue position is tracked externally (work_queues.yaml) not in WorkState. The WORK-065 finding about conflation was addressed differently - queues are orthogonal config, not WorkState fields.

**Design decision needed:** Add queue_position to WorkState, or keep external tracking via work_queues.yaml?

---

## Agent Need

> "I need queue position tracked separately from lifecycle phase so I can have an item in 'active' queue while it's in any lifecycle phase, not just specific nodes."

---

## Requirements

### R1: Separate Queue Field (REQ-QUEUE-001)

WorkState gets dedicated `queue_position` field:

```yaml
# WORK.md frontmatter
status: active
queue_position: active    # NEW: separate field
cycle_phase: SPECIFY      # Within design lifecycle
activity_state: DESIGN    # Governed activity
```

### R2: Four-Dimension Tracking

Per WORK-065 finding, WorkState tracks four orthogonal dimensions:

| Dimension | Field | Values | Purpose |
|-----------|-------|--------|---------|
| Lifecycle | status | active/blocked/complete/archived | ADR-041 authoritative |
| Queue | queue_position | backlog/ready/**working**/done | Selection pipeline |
| Cycle | cycle_phase | per-lifecycle phases | Current phase |
| Activity | activity_state | EXPLORE/DESIGN/etc | Governed state |

**TERMINOLOGY FIX:** Rename `queue_position: active` to `queue_position: working` to avoid collision with `status: active`.

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

### R4: Independent State Machines

Queue and lifecycle are parallel state machines:

```
Queue:     backlog ──→ ready ──→ active ──→ done
                         │
Work:                    └──→ [lifecycle phases] ──→ complete
```

---

## Interface

### WorkState Schema Changes

```python
@dataclass
class WorkState:
    id: str
    status: str           # active, blocked, complete, archived
    queue_position: str   # NEW: backlog, ready, active, done
    cycle_phase: str      # PLAN, DO, CHECK, DONE, etc.
    activity_state: str   # EXPLORE, DESIGN, IMPLEMENT, etc.
    # ... other fields
```

### WORK.md Template Update

```yaml
---
id: WORK-XXX
status: active
queue_position: backlog   # NEW FIELD
lifecycle: implementation
cycle_phase: PLAN
activity_state: IMPLEMENT
---
```

### WorkEngine Changes

```python
def get_queue_position(work_id: str) -> str:
    """Get queue position independently of lifecycle."""

def set_queue_position(work_id: str, position: str) -> None:
    """Update queue position without affecting lifecycle."""
```

---

## Success Criteria

- [ ] WorkState has queue_position field
- [ ] WORK.md template includes queue_position
- [ ] WorkEngine parses and writes queue_position
- [ ] queue_position changes don't affect cycle_phase
- [ ] cycle_phase changes don't affect queue_position
- [ ] Unit tests for four-dimension independence
- [ ] Migration: existing WORK.md files get queue_position added

---

## Non-Goals

- Queue ceremonies (see CH-010)
- Queue lifecycle definition (see CH-009)
- Validation of queue transitions (that's governance)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-001)
- @docs/work/archive/WORK-065/ (conflation finding)
