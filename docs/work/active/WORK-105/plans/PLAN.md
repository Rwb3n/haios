---
template: implementation_plan
status: approved
date: 2026-02-08
backlog_id: WORK-105
title: Queue Position Field (CH-007) - Expand to 5 Values
author: Hephaestus
lifecycle_phase: plan
session: 321
version: '1.5'
generated: 2026-02-08
last_updated: '2026-02-08T21:36:44'
---
# Implementation Plan: Queue Position Field (CH-007) - Expand to 5 Values

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory refs 84026-84035 queried (S320 decisions) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Expand `queue_position` from 3 MVP values (backlog/in_progress/done) to 5 canonical values (parked/backlog/ready/working/done), rename `in_progress` to `working`, add forbidden state combination enforcement, and exclude parked items from query methods.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | work_engine.py, test_work_engine.py, work_item.md template |
| Lines of code affected | ~120 | work_engine.py:103,628-682; tests:1141-1296 |
| New files to create | 0 | All changes in existing files |
| Tests to write | 10 | See Tests First section (T1-T10) |
| Dependencies | 2 | get_ready() and get_queue() need parked exclusion |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | WorkEngine internal + template |
| Risk of regression | Med | Renaming in_progress breaks existing tests |
| External dependencies | Low | No APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| Migration + verification | 10 min | High |
| **Total** | 45 min | |

---

## Current State vs Desired State

### Current State

```python
# work_engine.py:103
queue_position: str = "backlog"  # WORK-066: backlog|in_progress|done

# work_engine.py:644 (inside set_queue_position)
VALID_POSITIONS = {"backlog", "in_progress", "done"}

# work_engine.py:662-682
def get_in_progress(self) -> List[WorkState]:
    # Returns items with queue_position == "in_progress"
```

**Behavior:** 3 queue positions, `in_progress` naming, no parked/ready values, no forbidden state enforcement.

**Result:** Cannot park items out of scope, cannot distinguish "ready for work" from "backlog", naming collision risk with `status: active`.

### Desired State

```python
# work_engine.py:103
queue_position: str = "backlog"  # WORK-105: parked|backlog|ready|working|done

# work_engine.py - module level constant
VALID_QUEUE_POSITIONS = {"parked", "backlog", "ready", "working", "done"}

# work_engine.py - renamed method
def get_working(self) -> List[WorkState]:
    # Returns items with queue_position == "working"

# work_engine.py - new method
def validate_state_combination(self, work: WorkState) -> None:
    # Enforces forbidden combinations
```

**Behavior:** 5 queue positions, `working` naming, parked excluded from queries, forbidden states enforced.

**Result:** Full four-dimensional work tracking per REQ-QUEUE-001.

---

## Tests First (TDD)

### Test 1: Five-Value Validation Accepts All Valid Positions
```python
def test_set_queue_position_five_values(tmp_path, governance):
    """WORK-105 T1: set_queue_position accepts all 5 canonical values."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-5V", "Five Value Test")
    for pos in ["parked", "backlog", "ready", "working", "done"]:
        result = engine.set_queue_position("WORK-5V", pos)
        assert result is not None
        assert result.queue_position == pos
```

### Test 2: in_progress Rejected (Renamed to working)
```python
def test_in_progress_rejected(tmp_path, governance):
    """WORK-105 T2: 'in_progress' is no longer valid after rename to 'working'."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-RENAMED", "Rename Test")
    with pytest.raises(ValueError):
        engine.set_queue_position("WORK-RENAMED", "in_progress")
```

### Test 3: get_working Replaces get_in_progress
```python
def test_get_working(tmp_path, governance):
    """WORK-105 T3: get_working() returns items with queue_position: working."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-W1", "Item 1")
    engine.create_work("WORK-W2", "Item 2")
    engine.set_queue_position("WORK-W1", "working")
    working = engine.get_working()
    assert len(working) == 1
    assert working[0].id == "WORK-W1"
```

### Test 4: Parked Items Excluded from get_ready
```python
def test_parked_excluded_from_get_ready(tmp_path, governance):
    """WORK-105 T4: Parked items don't appear in get_ready()."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-PARKED", "Parked Item")
    engine.create_work("WORK-ACTIVE", "Active Item")
    engine.set_queue_position("WORK-PARKED", "parked")
    ready = engine.get_ready()
    ids = [w.id for w in ready]
    assert "WORK-PARKED" not in ids
    assert "WORK-ACTIVE" in ids
```

### Test 5: Parked Items Excluded from get_queue
```python
def test_parked_excluded_from_get_queue(tmp_path, governance):
    """WORK-105 T5: Parked items excluded from get_queue()."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-P1", "Parked")
    engine.create_work("WORK-B1", "Backlog")
    engine.set_queue_position("WORK-P1", "parked")
    queue = engine.get_queue()
    ids = [w.id for w in queue]
    assert "WORK-P1" not in ids
```

### Test 6: Queue Independence - queue_position Change Doesn't Affect cycle_phase
```python
def test_queue_position_independent_of_cycle_phase(tmp_path, governance):
    """WORK-105 T6: Changing queue_position doesn't change cycle_phase."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-IND", "Independence Test")
    # Set cycle_phase manually
    work = engine.get_work("WORK-IND")
    work.cycle_phase = "DO"
    engine._write_work_file(work)
    # Change queue_position
    engine.set_queue_position("WORK-IND", "working")
    # Verify cycle_phase unchanged
    reread = engine.get_work("WORK-IND")
    assert reread.queue_position == "working"
    assert reread.cycle_phase == "DO"
```

### Test 7: Forbidden State - Complete + Working
```python
def test_forbidden_complete_working(tmp_path, governance):
    """WORK-105 T7: Cannot set queue_position=working when status=complete."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-FORB", "Forbidden Test")
    work = engine.get_work("WORK-FORB")
    work.status = "complete"
    engine._write_work_file(work)
    with pytest.raises(ValueError, match="forbidden"):
        engine.set_queue_position("WORK-FORB", "working")
```

### Test 8: Forbidden State - Archived + Non-Done
```python
def test_forbidden_archived_not_done(tmp_path, governance):
    """WORK-105 T8: Cannot set queue_position != done when status=archived."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-ARCH", "Archived Test")
    work = engine.get_work("WORK-ARCH")
    work.status = "archived"
    engine._write_work_file(work)
    with pytest.raises(ValueError, match="forbidden"):
        engine.set_queue_position("WORK-ARCH", "backlog")
```

### Test 9: Reverse Independence - cycle_phase Change Doesn't Affect queue_position (A12)
```python
def test_cycle_phase_independent_of_queue_position(tmp_path, governance):
    """WORK-105 T9: Changing cycle_phase doesn't change queue_position."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-REV", "Reverse Independence Test")
    engine.set_queue_position("WORK-REV", "working")
    # Change cycle_phase directly
    work = engine.get_work("WORK-REV")
    work.cycle_phase = "CHECK"
    engine._write_work_file(work)
    # Verify queue_position unchanged
    reread = engine.get_work("WORK-REV")
    assert reread.cycle_phase == "CHECK"
    assert reread.queue_position == "working"
```

### Test 10: Forbidden State via _write_work_file Catch-All (A6)
```python
def test_forbidden_state_caught_on_write(tmp_path, governance):
    """WORK-105 T10: _write_work_file catches forbidden state (complete+working)."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-CATCH", "Catch-All Test")
    engine.set_queue_position("WORK-CATCH", "working")
    work = engine.get_work("WORK-CATCH")
    work.status = "complete"
    with pytest.raises(ValueError, match="forbidden"):
        engine._write_work_file(work)
```

---

## Detailed Design

### Critique Mitigations (A6, A9, A12)

**A6 (Forbidden state at write time):** Move `_validate_state_combination` call into `_write_work_file()` as catch-all. This ensures forbidden states are caught regardless of which method changes status or queue_position.

**A9 (Deprecated alias):** Follow-up work item to remove `get_in_progress()` alias. Not blocking for WORK-105.

**A12 (Reverse independence):** Added T9 to verify cycle_phase changes don't affect queue_position.

### Exact Code Changes

**File:** `.claude/haios/modules/work_engine.py`

**Change 1: Module-level constant (add near line 88)**

```python
# WORK-105: Canonical queue positions (5 values per REQ-QUEUE-003)
VALID_QUEUE_POSITIONS = {"parked", "backlog", "ready", "working", "done"}

# WORK-105: Forbidden state combinations per CH-007 R3
FORBIDDEN_STATE_COMBINATIONS = [
    # (status, queue_position, reason)
    ("complete", "working", "Complete work cannot be actively worked"),
    ("blocked", "working", "Blocked work cannot be actively worked"),
    # archived must be done - checked separately
]
```

**Change 2: WorkState comment (line 103)**

```diff
-    queue_position: str = "backlog"  # WORK-066: backlog|in_progress|done
+    queue_position: str = "backlog"  # WORK-105: parked|backlog|ready|working|done
```

**Change 3: set_queue_position (lines 628-660)**

```python
def set_queue_position(self, id: str, position: str) -> Optional[WorkState]:
    """
    Set queue_position for work item (WORK-105: 5 canonical values).

    Uses unified write path via _write_work_file() per critique A1.
    Validates forbidden state combinations per CH-007 R3.

    Args:
        id: Work item ID
        position: New position (parked, backlog, ready, working, done)

    Returns:
        Updated WorkState, or None if not found

    Raises:
        ValueError: If position is not valid or state combination is forbidden
    """
    if position not in VALID_QUEUE_POSITIONS:
        raise ValueError(
            f"Invalid queue_position: {position}. Must be one of {VALID_QUEUE_POSITIONS}"
        )

    work = self.get_work(id)
    if work is None:
        return None

    # WORK-105: Validate forbidden state combinations
    self._validate_state_combination(work.status, position)

    # Update in-memory state
    work.queue_position = position

    # Persist via unified write path (A1 mitigation)
    self._write_work_file(work)

    return work
```

**Change 4: Rename get_in_progress → get_working (lines 662-682)**

```python
def get_working(self) -> List[WorkState]:
    """
    Get all work items with queue_position: working (WORK-105).

    Replaces get_in_progress() per in_progress→working terminology fix.
    Used by survey-cycle to enforce single working constraint.

    Returns:
        List of WorkState with queue_position == "working"
    """
    result = []
    if not self.active_dir.exists():
        return result

    for subdir in self.active_dir.iterdir():
        if subdir.is_dir():
            work_md = subdir / "WORK.md"
            if work_md.exists():
                work = self._parse_work_file(work_md)
                if work and work.queue_position == "working":
                    result.append(work)
    return result

# WORK-105: Backward compat alias (deprecated)
def get_in_progress(self) -> List[WorkState]:
    """Deprecated: Use get_working() instead."""
    return self.get_working()
```

**Change 5: New _validate_state_combination method**

```python
def _validate_state_combination(self, status: str, queue_position: str) -> None:
    """
    Validate status + queue_position combination (WORK-105, CH-007 R3).

    Raises:
        ValueError: If combination is forbidden
    """
    for forbidden_status, forbidden_qp, reason in FORBIDDEN_STATE_COMBINATIONS:
        if status == forbidden_status and queue_position == forbidden_qp:
            raise ValueError(
                f"Forbidden state combination: status={status} + "
                f"queue_position={queue_position}. {reason}"
            )
    # archived must have queue_position: done
    if status == "archived" and queue_position != "done":
        raise ValueError(
            f"Forbidden state combination: status=archived + "
            f"queue_position={queue_position}. Archived items must be queue done"
        )
```

**Change 6: Parked exclusion in get_ready() (line 366)**

```diff
-                    if work and not work.blocked_by and work.status not in terminal_statuses:
+                    if work and not work.blocked_by and work.status not in terminal_statuses and work.queue_position != "parked":
```

**Change 7: Parked exclusion in get_queue() (lines 460-469)**

Add parked filter after items are collected but before sorting:

```python
# WORK-105: Exclude parked items from queue
items = [item for item in items if item.queue_position != "parked"]
```

**Change 8: Catch-all validation in _write_work_file (A6 mitigation)**

Add forbidden state validation to `_write_work_file()` so any code path that changes status or queue_position is covered:

```python
def _write_work_file(self, work: WorkState) -> None:
    """..."""
    if work.path is None:
        return

    # WORK-105: Catch-all forbidden state validation (A6 mitigation)
    self._validate_state_combination(work.status, work.queue_position)

    content = work.path.read_text(encoding="utf-8")
    # ... rest unchanged
```

### Call Chain Context

```
survey-cycle → WorkEngine.get_ready() / get_queue()   ← parked exclusion
                   |
                   +→ WorkEngine.get_working()          ← renamed from get_in_progress
                   |
                   +→ WorkEngine.set_queue_position()   ← 5 values + forbidden combos
                           |
                           +→ _validate_state_combination()  ← early check
                           |
                           +→ _write_work_file()
                                   |
                                   +→ _validate_state_combination()  ← catch-all (A6)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module-level constant vs method-local | Module-level `VALID_QUEUE_POSITIONS` | Reusable by other methods, visible to tests, single source of truth |
| Keep get_in_progress as alias | Deprecated alias calling get_working | Backward compat for any callers; explore found no runtime callers but tests reference it |
| Forbidden combos as list-of-tuples | Simple data structure | Easy to extend, readable, no over-engineering |
| Parked filter in get_ready/get_queue | Filter at query time | No schema change needed, just exclude at read |
| Migration of existing files | Script in test, manual for active items | Only 0 items currently have `in_progress`; 2 have `parked` (already valid after change) |
| Catch-all validation in _write_work_file | Validate on every write | A6 mitigation: prevents forbidden states regardless of which method changes status/queue_position |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Legacy items without queue_position | Default to "backlog" (existing behavior) | Existing WORK-066 T2 |
| `in_progress` in old files | Rejected by validation; migration renames to `working` | T2 |
| Parked item set back to backlog | Allowed (Unpark ceremony use case) | Implicit in T1 |
| Complete + done | Allowed (valid terminal state) | Not forbidden |
| Blocked + backlog | Allowed (waiting for dependency) | Not forbidden |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | All decisions resolved via CH-007 spec and S320 memory |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 8 tests to `tests/test_work_engine.py` (T1-T8)
- [ ] Verify all new tests fail (red)

### Step 2: Add Constants and Validation Method
- [ ] Add `VALID_QUEUE_POSITIONS` module-level constant
- [ ] Add `FORBIDDEN_STATE_COMBINATIONS` constant
- [ ] Add `_validate_state_combination()` method
- [ ] T7, T8 pass (forbidden combos)

### Step 3: Update set_queue_position
- [ ] Replace local `VALID_POSITIONS` with module-level `VALID_QUEUE_POSITIONS`
- [ ] Add forbidden state validation call
- [ ] Update docstring
- [ ] T1, T2 pass (5 values, in_progress rejected)

### Step 4: Rename get_in_progress to get_working
- [ ] Add `get_working()` method
- [ ] Convert `get_in_progress()` to deprecated alias
- [ ] Update WorkState comment
- [ ] T3 pass (get_working)

### Step 5: Add Parked Exclusion
- [ ] Filter parked in `get_ready()` (line 366)
- [ ] Filter parked in `get_queue()` (after item collection)
- [ ] T4, T5 pass (parked exclusion)

### Step 6: Update Existing Tests
- [ ] Update WORK-066 tests to use `working` instead of `in_progress`
- [ ] Update sample data constants
- [ ] T6 pass (independence)
- [ ] All tests pass

### Step 7: Update Template and Migration
- [ ] Update `.claude/templates/work_item.md` comment to 5 values
- [ ] Update modules README

### Step 8: Consumer Verification (MUST)
- [ ] Grep for `in_progress` references in py files
- [ ] Grep for `get_in_progress` references
- [ ] Verify no stale references remain

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing WORK-066 tests | Medium | Update test data to use `working` before running |
| Consumers calling get_in_progress | Low | Deprecated alias maintained |
| Existing `in_progress` in WORK.md files | Low | Grep found 0 active items with `in_progress`; 2 have `parked` which becomes valid |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 321 | 2026-02-08 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-105/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| WorkState queue_position expanded to 5 values | [ ] | VALID_QUEUE_POSITIONS constant |
| WORK.md template updated with 5-value comment | [ ] | work_item.md line 22 |
| in_progress renamed to working in WorkEngine | [ ] | set_queue_position, get_working |
| ready value added and validated | [ ] | T1 passes |
| parked value added and validated | [ ] | T1 passes |
| Parked items excluded from get_ready/get_queue | [ ] | T4, T5 pass |
| queue_position changes don't affect cycle_phase | [ ] | T6 passes |
| cycle_phase changes don't affect queue_position | [ ] | Implicit - no coupling in code |
| Forbidden state combinations enforced | [ ] | T7, T8 pass |
| Migration: in_progress renamed to working | [ ] | Grep shows 0 stale references |
| Unit tests for all above | [ ] | 8 new tests pass |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | VALID_QUEUE_POSITIONS, get_working(), _validate_state_combination() | [ ] | |
| `tests/test_work_engine.py` | 8 new tests (T1-T8) + updated WORK-066 tests | [ ] | |
| `.claude/templates/work_item.md` | Comment shows 5 values | [ ] | |
| `.claude/haios/modules/README.md` | get_working documented | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_engine.py -v -k "WORK_105 or queue_position"
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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (get_ready/get_queue use parked exclusion; set_queue_position called by survey-cycle)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] **MUST:** Consumer verification complete (zero stale `in_progress` references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-007-QueuePositionField.md (chapter spec)
- @.claude/haios/epochs/E2_5/arcs/queue/ARC.md (parent arc)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-001)
- Memory 84026-84035 (S320 terminology decisions)

---
