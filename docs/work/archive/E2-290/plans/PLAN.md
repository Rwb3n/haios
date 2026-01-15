---
template: implementation_plan
status: complete
date: 2026-01-15
backlog_id: E2-290
title: Work Queue Architecture Implementation
author: Hephaestus
lifecycle_phase: plan
session: 191
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-15T20:48:11'
---
# Implementation Plan: Work Queue Architecture Implementation

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Work items can be organized into typed queues (FIFO, Priority, Batch, Chapter-Aligned) with cycle-locking enforcement, replacing the flat unordered list from `get_ready()`.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `work_engine.py`, `justfile` |
| Lines of code affected | ~50 | New methods in WorkEngine |
| New files to create | 2 | `work_queues.yaml`, `tests/test_work_queues.py` |
| Tests to write | 5 | Load, FIFO, Priority, Batch, Cycle-lock |
| Dependencies | 1 | WorkEngine (self-contained addition) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only WorkEngine touched |
| Risk of regression | Low | New feature, existing get_ready() unchanged |
| External dependencies | None | Pure YAML + Python |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Config file + loader | 20 min | High |
| Queue methods | 30 min | High |
| Just recipes | 10 min | High |
| Tests | 20 min | High |
| **Total** | ~80 min | |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/work_engine.py:263-281
def get_ready(self) -> List[WorkState]:
    """Get all unblocked work items from active directory."""
    ready = []
    if not self.active_dir.exists():
        return ready
    for subdir in self.active_dir.iterdir():
        if subdir.is_dir():
            work_md = subdir / "WORK.md"
            if work_md.exists():
                work = self._parse_work_file(work_md)
                if work and not work.blocked_by:
                    ready.append(work)
    return ready
```

**Behavior:** Returns flat unordered list of all unblocked work items.

**Result:** No priority, no batching, no cycle-locking. Survey-cycle picks arbitrarily.

### Desired State

```python
# .claude/haios/modules/work_engine.py - New methods
def load_queues(self) -> Dict[str, QueueConfig]:
    """Load work_queues.yaml configuration."""

def get_queue(self, queue_name: str = "default") -> List[WorkState]:
    """Get ordered work items from a specific queue."""

def get_next(self, queue_name: str = "default") -> Optional[WorkState]:
    """Get next item from queue head."""

def is_cycle_allowed(self, queue_name: str, cycle_name: str) -> bool:
    """Check if cycle is allowed for this queue (cycle-locking)."""
```

**Behavior:** Queues provide typed ordering (FIFO, Priority, Batch) with cycle restrictions.

**Result:** Work selection is structured, batching enabled, cycle-locking prevents wrong cycles.

---

## Tests First (TDD)

### Test 1: Load Queue Config
```python
def test_load_queues_from_yaml():
    """Verify work_queues.yaml loads correctly."""
    engine = WorkEngine()
    queues = engine.load_queues()
    assert "default" in queues
    assert queues["default"]["type"] == "priority"
```

### Test 2: Priority Queue Ordering
```python
def test_priority_queue_ordering():
    """High priority items come first."""
    engine = WorkEngine()
    items = engine.get_queue("default")
    # Items should be sorted by priority DESC
    priorities = [item.priority for item in items]
    assert priorities == sorted(priorities, reverse=True)
```

### Test 3: Cycle Locking Enforcement
```python
def test_cycle_locking_blocks_wrong_cycle():
    """Queue with allowed_cycles blocks other cycles."""
    engine = WorkEngine()
    # planning-queue only allows plan-authoring-cycle
    assert engine.is_cycle_allowed("planning-queue", "plan-authoring-cycle") == True
    assert engine.is_cycle_allowed("planning-queue", "implementation-cycle") == False
```

### Test 4: Get Next Returns Head
```python
def test_get_next_returns_queue_head():
    """get_next() returns first item from queue."""
    engine = WorkEngine()
    next_item = engine.get_next("default")
    queue = engine.get_queue("default")
    assert next_item == queue[0] if queue else next_item is None
```

### Test 5: Backward Compatibility
```python
def test_get_ready_unchanged():
    """Existing get_ready() still works."""
    engine = WorkEngine()
    ready = engine.get_ready()
    # Should return list of WorkState (existing behavior)
    assert isinstance(ready, list)
```

---

## Detailed Design

### New Config File

**File:** `.claude/haios/config/work_queues.yaml`

```yaml
# Work Queue Configuration (INV-064 design)
version: "1.0"

queue_types:
  fifo:
    ordering: "creation_date ASC"
  priority:
    ordering: "priority DESC, creation_date ASC"
  batch:
    phases: [plan_all, review, implement_all, validate_all]
  chapter_aligned:
    ordering: "chapter_priority DESC, priority DESC"

queues:
  default:
    type: priority
    items: auto  # From get_ready()
    allowed_cycles: [implementation-cycle, investigation-cycle, work-creation-cycle]
```

### New Methods in WorkEngine

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After line 281 (after get_ready())

```python
QUEUE_CONFIG_PATH = Path(".claude/haios/config/work_queues.yaml")

@dataclass
class QueueConfig:
    """Queue configuration from work_queues.yaml."""
    name: str
    type: str  # fifo, priority, batch, chapter_aligned
    items: List[str]  # Work IDs or "auto"
    allowed_cycles: List[str]
    phases: Optional[List[str]] = None  # For batch type

def load_queues(self) -> Dict[str, QueueConfig]:
    """Load queue configuration from work_queues.yaml."""
    if not QUEUE_CONFIG_PATH.exists():
        return {"default": QueueConfig("default", "priority", ["auto"], [])}
    with open(QUEUE_CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    return {name: QueueConfig(name, **q) for name, q in config.get("queues", {}).items()}

def get_queue(self, queue_name: str = "default") -> List[WorkState]:
    """Get ordered work items from a specific queue."""
    queues = self.load_queues()
    if queue_name not in queues:
        return self.get_ready()  # Fallback to flat list

    q = queues[queue_name]
    if q.items == ["auto"] or q.items == "auto":
        items = self.get_ready()
    else:
        items = [self.get_work(id) for id in q.items if self._work_exists(id)]

    # Sort by queue type
    if q.type == "priority":
        items.sort(key=lambda x: (getattr(x, 'priority', 'medium') != 'high', x.id))
    elif q.type == "fifo":
        items.sort(key=lambda x: x.node_history[0]['entered'] if x.node_history else '')
    return items

def get_next(self, queue_name: str = "default") -> Optional[WorkState]:
    """Get next item from queue head."""
    queue = self.get_queue(queue_name)
    return queue[0] if queue else None

def is_cycle_allowed(self, queue_name: str, cycle_name: str) -> bool:
    """Check if cycle is allowed for this queue (cycle-locking)."""
    queues = self.load_queues()
    if queue_name not in queues:
        return True  # No queue = no restrictions
    q = queues[queue_name]
    if not q.allowed_cycles:
        return True  # Empty list = all allowed
    return cycle_name in q.allowed_cycles
```

### Call Chain Context

```
survey-cycle / routing-gate
    |
    +-> WorkEngine.get_next()     # <-- New method
    |       Returns: WorkState
    |
    +-> is_cycle_allowed()        # <-- Cycle-locking check
    |       Returns: bool
    |
    +-> implementation-cycle (if allowed)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep get_ready() | Unchanged | Backward compatibility; queues are additive |
| items: auto | Populate from get_ready() | Default queue doesn't require manual item lists |
| Cycle-locking | allowed_cycles field | Enables planning-only queues, research-only queues |
| QueueConfig dataclass | New dataclass | Type safety, matches WorkState pattern |
| Fallback to get_ready() | If queue not found | Graceful degradation |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Queue config missing | Return default queue with priority type | Test 1 |
| Unknown queue name | Fallback to get_ready() | Test 5 |
| Empty allowed_cycles | All cycles allowed | Test 3 |
| Work item not found | Skip in get_queue() | Implicit |

### Open Questions

**Q: Should batch queue phases be enforced?**

Deferred. Batch queue phases (PLAN_ALL, REVIEW, etc.) require state tracking across sessions. For MVP, batch type exists but phase enforcement is future work.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No operator decisions required (INV-064 provided complete design) |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_work_queues.py`
- [ ] Add 5 test functions (from Tests First section)
- [ ] Verify all tests fail (red) - methods don't exist yet

### Step 2: Create Config File
- [ ] Create `.claude/haios/config/work_queues.yaml` with schema from INV-064
- [ ] Include default queue with priority type
- [ ] Test 1 passes (green)

### Step 3: Add QueueConfig Dataclass
- [ ] Add QueueConfig dataclass to work_engine.py
- [ ] Add QUEUE_CONFIG_PATH constant
- [ ] Add load_queues() method
- [ ] Test 1 passes (green)

### Step 4: Add Queue Methods
- [ ] Add get_queue() method with sorting logic
- [ ] Add get_next() method
- [ ] Add is_cycle_allowed() method
- [ ] Tests 2, 3, 4 pass (green)

### Step 5: Add Just Recipes
- [ ] Add `queue` recipe to justfile
- [ ] Add `queue-next` recipe
- [ ] Manual verification

### Step 6: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Test 5 (backward compatibility) passes

### Step 7: README Sync
- [ ] Update `.claude/haios/config/README.md` with work_queues.yaml
- [ ] Update `.claude/haios/modules/README.md` if needed

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Queue config invalid YAML | Low | Fallback to default queue |
| Priority field missing on work items | Low | Default to 'medium' priority |
| Batch phase enforcement complexity | Medium | Defer to future work; MVP has type but no enforcement |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/work_queues.yaml` | Queue config with default queue | [ ] | |
| `.claude/haios/modules/work_engine.py` | load_queues, get_queue, get_next, is_cycle_allowed exist | [ ] | |
| `tests/test_work_queues.py` | 5 tests exist and pass | [ ] | |
| `.claude/haios/config/README.md` | Documents work_queues.yaml | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_queues.py -v
# Expected: 5 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- @docs/work/active/INV-064/investigations/001-work-hierarchy-rename-and-queue-architecture.md
- Memory 81368-81369 (queue design from INV-064)

---
