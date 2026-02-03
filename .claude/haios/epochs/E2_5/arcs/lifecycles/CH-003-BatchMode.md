# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T19:44:20
# Chapter: Batch Mode

## Definition

**Chapter ID:** CH-003
**Arc:** lifecycles
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-001
**Work Items:** WORK-086

---

## Current State (Verified)

**Source:** `.claude/haios/config/activity_matrix.yaml`

activity_matrix.yaml exists (E2.4 CH-004) with state-based governance. Checked for single-item constraints:

```yaml
# No explicit single-item constraints found in activity_matrix.yaml
# Governance is per-primitive (file-read, shell-execute, etc.), not per-work-item count
```

**Source:** `.claude/haios/modules/work_engine.py`

WorkEngine has no batch methods:
- `get_work(id)` - single item
- `get_ready()` - returns list but no batch processing
- No `get_in_lifecycle()` or `run_batch()` methods

**What exists:**
- Multiple work items can have `status: active` simultaneously (no enforcement)
- work_queues.yaml has `batch` queue type (for queue grouping, not lifecycle batching)

**What doesn't exist:**
- `CycleRunner.run_batch()` method
- `WorkEngine.get_in_lifecycle()` method
- `WorkEngine.count_active_in_lifecycle()` method

---

## Problem

No explicit single-item constraint exists, but also no support for intentional batch operations. Batch design (design A, B, C before implementing) requires new methods.

---

## Agent Need

> "I need to work on multiple items in the same lifecycle phase simultaneously so I can batch related designs or investigations before committing to implementation."

---

## Requirements

### R1: Multiple Active Items (REQ-LIFECYCLE-003)

WorkEngine must support multiple items in same lifecycle phase:

```python
# Valid state
WORK-001: lifecycle=design, phase=SPECIFY
WORK-002: lifecycle=design, phase=CRITIQUE
WORK-003: lifecycle=design, phase=EXPLORE
```

All three can be "active" in design lifecycle simultaneously.

### R2: No Single-Focus Constraint

Remove any governance that enforces single active item. Activity state should track per-item, not globally.

### R3: Batch Operations

CycleRunner should support batch invocation:

```python
# Batch design
results = cycle_runner.run_batch(
    work_ids=["WORK-001", "WORK-002", "WORK-003"],
    lifecycle="design"
)
```

---

## Interface

### WorkEngine Changes

```python
# Get all items in specific lifecycle/phase
def get_in_lifecycle(lifecycle: str, phase: str = None) -> List[WorkState]:
    """Get all work items in given lifecycle, optionally filtered by phase."""

# Count in batch
def count_active_in_lifecycle(lifecycle: str) -> int:
    """Count items currently in this lifecycle."""
```

### CycleRunner Changes

```python
def run_batch(
    work_ids: List[str],
    lifecycle: str,
    until_phase: str = None
) -> Dict[str, LifecycleOutput]:
    """Run lifecycle on multiple items, return outputs keyed by work_id."""
```

### Governance Changes

**Verified:** No single-item constraints exist in activity_matrix.yaml to remove.

Add batch-aware governance (optional):
- `max_batch_size: 10` - optional limit on batch size
- `batch_lifecycle_lock: true` - all items in batch must be same lifecycle

---

## Success Criteria

- [ ] Multiple items can be in design lifecycle simultaneously
- [ ] WorkEngine.get_in_lifecycle() returns multiple items
- [ ] CycleRunner.run_batch() processes multiple items
- [ ] No governance errors for batch design
- [ ] Unit tests: 3 items in design phase concurrently
- [ ] Integration test: Batch design 3 features → all complete with specs → then batch implement

---

## Non-Goals

- Parallel execution (batch is sequential internally, just multiple items in same phase)
- Cross-lifecycle batch (can't do design(A) + implement(B) in same batch)
- Automatic batch grouping (caller chooses batch membership)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-003)
- @.claude/haios/config/activity_matrix.yaml (governance constraints to modify)
