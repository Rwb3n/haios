# generated: 2026-02-03
# System Auto: last updated on: 2026-02-07T15:31:29
# Chapter: Queue Lifecycle

## Definition

**Chapter ID:** CH-009
**Arc:** queue
**Status:** Planned
**Implementation Type:** REFACTOR (queue types exist, transitions don't)
**Depends:** CH-007
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/haios/config/work_queues.yaml`

Queue types defined:
```yaml
queue_types:
  fifo:
    ordering: "creation_date ASC"
  priority:
    ordering: "priority DESC, creation_date ASC"
  batch:
    phases: [plan_all, review, implement_all, validate_all]
  chapter_aligned:
    ordering: "chapter_priority DESC, priority DESC"
```

**Source:** `.claude/haios/modules/work_engine.py` (lines 114-122)

QueueConfig dataclass exists:
```python
@dataclass
class QueueConfig:
    name: str
    type: str  # fifo, priority, batch, chapter_aligned
    items: Any  # Work IDs list or "auto"
    allowed_cycles: List[str]
    phases: Optional[List[str]]  # For batch type
```

**What exists:**
- Queue types with ordering rules
- Queue configs with allowed_cycles enforcement
- WorkEngine methods: `load_queues()`, `get_queue()`, `get_next()`, `is_cycle_allowed()`
- Strict cycle enforcement policy

**What doesn't exist:**
- QUEUE_TRANSITIONS state machine
- `is_valid_queue_transition()` function
- `validate_queue_transition()` in governance
- Queue position as tracked field (items are in queues, but don't track their position)

---

## Problem

Queue types and ordering exist, but no position lifecycle (backlog→ready→working→done). Items are in named queues, but their position within the selection pipeline isn't tracked.

---

## Agent Need

> "I need the queue to have its own lifecycle with defined phases and transitions so I can understand where items are in the selection pipeline."

---

## Requirements

### R1: Queue Lifecycle Definition (REQ-QUEUE-003, REQ-QUEUE-005)

Queue has five phases (using "working" per CH-007 terminology fix):

```
parked ──→ backlog ──→ ready ──→ working ──→ done
```

| Phase | Meaning | Entry Condition |
|-------|---------|-----------------|
| parked | Out of scope for current epoch | Created/moved by operator |
| backlog | Captured, not prioritized | Created via Intake or Unpark |
| ready | Prioritized, dependencies clear | Prioritize ceremony |
| working | Currently being worked | Commit ceremony |
| done | Work complete | Release ceremony |

### R2: Transition Rules

Valid transitions only:

```
parked → backlog   (Unpark - operator decision)
backlog → ready    (Prioritize)
backlog → parked   (Park - scope deferral)
ready → working    (Commit)
ready → backlog    (Deprioritize - valid rollback)
working → done     (Release)
```

Invalid transitions:
- parked → ready (must go through backlog first)
- parked → working (must go through backlog → ready)
- backlog → working (skip ready)
- done → working (reopen)
- working → backlog (abandon without release)

### R3: Queue Query Methods

WorkEngine provides queue-aware queries:

```python
def get_backlog() -> List[WorkState]:
    """Items captured but not prioritized."""

def get_ready() -> List[WorkState]:
    """Items prioritized, available for work."""

def get_active() -> List[WorkState]:
    """Items currently being worked."""
```

---

## Interface

### Queue State Machine

```python
QUEUE_TRANSITIONS = {
    "parked": ["backlog"],           # Unpark
    "backlog": ["ready", "parked"],  # Prioritize or Park
    "ready": ["working", "backlog"], # Commit or Deprioritize
    "working": ["done"],             # Release
    "done": []                       # Terminal
}

def is_valid_queue_transition(from_pos: str, to_pos: str) -> bool:
    return to_pos in QUEUE_TRANSITIONS.get(from_pos, [])
```

### WorkEngine Query Methods

```python
def get_by_queue_position(position: str) -> List[WorkState]:
    """Get all work items at given queue position."""

def get_parked(self) -> List[WorkState]:
    return self.get_by_queue_position("parked")

def get_backlog(self) -> List[WorkState]:
    return self.get_by_queue_position("backlog")

def get_ready(self) -> List[WorkState]:
    return self.get_by_queue_position("ready")

def get_working(self) -> List[WorkState]:
    return self.get_by_queue_position("working")
```

### Governance Integration

```python
def validate_queue_transition(work_id: str, to_position: str) -> GateResult:
    work = work_engine.get_work(work_id)
    if not is_valid_queue_transition(work.queue_position, to_position):
        return GateResult(
            blocked=True,
            reason=f"Invalid: {work.queue_position} → {to_position}"
        )
    return GateResult(allowed=True)
```

---

## Success Criteria

- [ ] Queue lifecycle defined with 5 phases (parked/backlog/ready/working/done)
- [ ] Transition rules enforced by governance (including parked transitions)
- [ ] WorkEngine.get_parked/get_backlog/get_ready/get_working methods work
- [ ] Invalid transitions blocked (parked→ready, parked→working, done→working)
- [ ] Valid rollback (ready → backlog) works
- [ ] Valid park/unpark (backlog ↔ parked) works
- [ ] Unit tests for all valid transitions
- [ ] Unit tests for blocked invalid transitions

---

## Non-Goals

- Ceremony implementation (see CH-010)
- Priority ordering within phases (future work)
- Queue capacity limits (not needed yet)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-003)
- @.claude/haios/epochs/E2_5/arcs/queue/CH-007-QueuePositionField.md (field definition)
