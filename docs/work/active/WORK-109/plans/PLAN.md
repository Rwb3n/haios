---
template: implementation_plan
status: complete
date: 2026-02-09
backlog_id: WORK-109
title: Queue Lifecycle State Machine
author: Hephaestus
lifecycle_phase: PLAN
session: 326
version: '1.5'
generated: 2026-02-09
last_updated: '2026-02-09T19:18:49'
---
# Implementation Plan: Queue Lifecycle State Machine (CH-009)

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | CH-007 (WORK-105) added queue_position field with 5 values - this adds transition validation |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

WorkEngine enforces queue lifecycle transitions via QUEUE_TRANSITIONS state machine, blocking invalid queue position changes (parked->ready, done->working) while allowing valid transitions and rollbacks (ready->backlog).

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `work_engine.py`, `governance_layer.py` |
| Lines of code affected | ~40 | QUEUE_TRANSITIONS (9), is_valid_queue_transition (3), validate_queue_transition (15), get_parked (12), get_by_queue_position (14), integration (3) |
| New files to create | 0 | All additions to existing modules |
| Tests to write | 15 | 6 valid + 5 invalid + 2 query + 1 integration + 1 backward compat |
| Dependencies | 1 | set_queue_position() calls validate_queue_transition() |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single integration point at set_queue_position() |
| Risk of regression | Low | Existing 10 queue position tests remain (WORK-105) |
| External dependencies | None | Pure module logic |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests (15 tests) | 45 min | High |
| Implement state machine constants | 10 min | High |
| Implement validation functions | 30 min | High |
| Implement query methods | 20 min | High |
| Integration + verification | 15 min | High |
| **Total** | ~2 hours | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/haios/modules/work_engine.py`
**Lines:** 131-132, 645-680

```python
# Lines 131-132: Valid positions defined, but no transition rules
VALID_QUEUE_POSITIONS = {"parked", "backlog", "ready", "working", "done"}

# Lines 645-680: set_queue_position validates position value, not transition
def set_queue_position(self, id: str, position: str) -> Optional[WorkState]:
    if position not in VALID_QUEUE_POSITIONS:
        raise ValueError(...)
    work = self.get_work(id)
    if work is None:
        return None
    self._validate_state_combination(work.status, position)
    work.queue_position = position
    self._write_work_file(work)
    return work
```

**Behavior:** Any item can jump from any queue position to any other as long as the position string is valid.

**Result:** No lifecycle enforcement. Items can skip phases (parked->ready), reopen (done->working), or abandon (working->backlog).

### Desired State

```python
# NEW: Queue lifecycle state machine (CH-009)
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

**Behavior:** set_queue_position() calls validate_queue_transition() BEFORE persisting. Invalid transitions raise ValueError with governance-logged reason.

**Result:** Queue lifecycle enforced per REQ-QUEUE-003. Items follow valid paths, can roll back (ready->backlog), but cannot skip phases or reopen from done.

---

## Tests First (TDD)

### T1: Valid Transition - Parked to Backlog (Unpark)
```python
def test_queue_transition_parked_to_backlog(tmp_path, governance):
    """CH-009 T1: parked -> backlog (Unpark) is allowed."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T1", "Unpark Test")
    engine.set_queue_position("WORK-T1", "parked")
    result = engine.set_queue_position("WORK-T1", "backlog")
    assert result is not None
    assert result.queue_position == "backlog"
```

### T2: Valid Transition - Backlog to Ready (Prioritize)
```python
def test_queue_transition_backlog_to_ready(tmp_path, governance):
    """CH-009 T2: backlog -> ready (Prioritize) is allowed."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T2", "Prioritize Test")
    result = engine.set_queue_position("WORK-T2", "ready")
    assert result is not None
    assert result.queue_position == "ready"
```

### T3: Valid Transition - Backlog to Parked (Park)
```python
def test_queue_transition_backlog_to_parked(tmp_path, governance):
    """CH-009 T3: backlog -> parked (Park) is allowed."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T3", "Park Test")
    result = engine.set_queue_position("WORK-T3", "parked")
    assert result is not None
    assert result.queue_position == "parked"
```

### T4: Valid Transition - Ready to Working (Commit)
```python
def test_queue_transition_ready_to_working(tmp_path, governance):
    """CH-009 T4: ready -> working (Commit) is allowed."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T4", "Commit Test")
    engine.set_queue_position("WORK-T4", "ready")
    result = engine.set_queue_position("WORK-T4", "working")
    assert result is not None
    assert result.queue_position == "working"
```

### T5: Valid Transition - Ready to Backlog (Deprioritize)
```python
def test_queue_transition_ready_to_backlog(tmp_path, governance):
    """CH-009 T5: ready -> backlog (Deprioritize/rollback) is allowed."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T5", "Deprioritize Test")
    engine.set_queue_position("WORK-T5", "ready")
    result = engine.set_queue_position("WORK-T5", "backlog")
    assert result is not None
    assert result.queue_position == "backlog"
```

### T6: Valid Transition - Working to Done (Release)
```python
def test_queue_transition_working_to_done(tmp_path, governance):
    """CH-009 T6: working -> done (Release) is allowed."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T6", "Release Test")
    engine.set_queue_position("WORK-T6", "ready")
    engine.set_queue_position("WORK-T6", "working")
    result = engine.set_queue_position("WORK-T6", "done")
    assert result is not None
    assert result.queue_position == "done"
```

### T7: Invalid - Parked to Ready (Skip Backlog)
```python
def test_queue_transition_parked_to_ready_blocked(tmp_path, governance):
    """CH-009 T7: parked -> ready (skip backlog) is blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T7", "Skip Backlog Test")
    engine.set_queue_position("WORK-T7", "parked")
    with pytest.raises(ValueError, match="[Ii]nvalid.*transition|[Bb]locked"):
        engine.set_queue_position("WORK-T7", "ready")
```

### T8: Invalid - Parked to Working (Skip Two)
```python
def test_queue_transition_parked_to_working_blocked(tmp_path, governance):
    """CH-009 T8: parked -> working (skip backlog+ready) is blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T8", "Skip Two Test")
    engine.set_queue_position("WORK-T8", "parked")
    with pytest.raises(ValueError, match="[Ii]nvalid.*transition|[Bb]locked"):
        engine.set_queue_position("WORK-T8", "working")
```

### T9: Invalid - Backlog to Working (Skip Ready)
```python
def test_queue_transition_backlog_to_working_blocked(tmp_path, governance):
    """CH-009 T9: backlog -> working (skip ready) is blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T9", "Skip Ready Test")
    with pytest.raises(ValueError, match="[Ii]nvalid.*transition|[Bb]locked"):
        engine.set_queue_position("WORK-T9", "working")
```

### T10: Invalid - Done to Working (Reopen)
```python
def test_queue_transition_done_to_working_blocked(tmp_path, governance):
    """CH-009 T10: done -> working (reopen) is blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T10", "Reopen Test")
    engine.set_queue_position("WORK-T10", "ready")
    engine.set_queue_position("WORK-T10", "working")
    engine.set_queue_position("WORK-T10", "done")
    with pytest.raises(ValueError, match="[Ii]nvalid.*transition|[Bb]locked"):
        engine.set_queue_position("WORK-T10", "working")
```

### T11: Invalid - Working to Backlog (Abandon)
```python
def test_queue_transition_working_to_backlog_blocked(tmp_path, governance):
    """CH-009 T11: working -> backlog (abandon without release) is blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-T11", "Abandon Test")
    engine.set_queue_position("WORK-T11", "ready")
    engine.set_queue_position("WORK-T11", "working")
    with pytest.raises(ValueError, match="[Ii]nvalid.*transition|[Bb]locked"):
        engine.set_queue_position("WORK-T11", "backlog")
```

### T12: Get Parked Returns Only Parked Items
```python
def test_get_parked_returns_only_parked(tmp_path, governance):
    """CH-009 T12: get_parked() returns only parked items."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-P1", "Parked 1")
    engine.create_work("WORK-P2", "Parked 2")
    engine.create_work("WORK-B1", "Backlog")
    engine.set_queue_position("WORK-P1", "parked")
    engine.set_queue_position("WORK-P2", "parked")
    parked = engine.get_parked()
    assert len(parked) == 2
    ids = {w.id for w in parked}
    assert ids == {"WORK-P1", "WORK-P2"}
```

### T13: Get By Queue Position Generic Query
```python
def test_get_by_queue_position_generic(tmp_path, governance):
    """CH-009 T13: get_by_queue_position() returns items at specified position."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-R1", "Ready 1")
    engine.create_work("WORK-R2", "Ready 2")
    engine.create_work("WORK-W1", "Working")
    engine.set_queue_position("WORK-R1", "ready")
    engine.set_queue_position("WORK-R2", "ready")
    engine.set_queue_position("WORK-W1", "ready")
    engine.set_queue_position("WORK-W1", "working")
    ready = engine.get_by_queue_position("ready")
    assert len(ready) == 2
    ids = {w.id for w in ready}
    assert ids == {"WORK-R1", "WORK-R2"}
```

### T14: Integration - set_queue_position Validates Transitions
```python
def test_set_queue_position_validates_transition(tmp_path, governance):
    """CH-009 T14: set_queue_position() integrates with validation."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-INT", "Integration Test")
    engine.set_queue_position("WORK-INT", "parked")
    result = engine.set_queue_position("WORK-INT", "backlog")
    assert result.queue_position == "backlog"
    with pytest.raises(ValueError, match="[Ii]nvalid.*transition|[Bb]locked"):
        engine.set_queue_position("WORK-INT", "working")
```

### T15: Backward Compatibility - Initial Assignment
```python
def test_initial_queue_assignment_allowed(tmp_path, governance):
    """CH-009 T15: create_work() sets backlog by default (initial assignment)."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-INIT", "Initial Test")
    work = engine.get_work("WORK-INIT")
    assert work.queue_position == "backlog"
    # Subsequent invalid transition should be blocked
    with pytest.raises(ValueError):
        engine.set_queue_position("WORK-INIT", "working")
```

---

## Detailed Design

### Change 1: QUEUE_TRANSITIONS Constant and Validation Function

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After line 132 (VALID_QUEUE_POSITIONS), before FORBIDDEN_STATE_COMBINATIONS

```diff
 VALID_QUEUE_POSITIONS = {"parked", "backlog", "ready", "working", "done"}

+# CH-009: Queue lifecycle state machine (REQ-QUEUE-003, REQ-QUEUE-005)
+QUEUE_TRANSITIONS = {
+    "parked": ["backlog"],           # Unpark
+    "backlog": ["ready", "parked"],  # Prioritize or Park
+    "ready": ["working", "backlog"], # Commit or Deprioritize
+    "working": ["done"],             # Release
+    "done": []                       # Terminal
+}
+
+
+def is_valid_queue_transition(from_pos: str, to_pos: str) -> bool:
+    """Check if queue position transition is valid (CH-009)."""
+    return to_pos in QUEUE_TRANSITIONS.get(from_pos, [])
+
+
 # WORK-105: Forbidden state combinations per CH-007 R3
```

### Change 2: validate_queue_transition() on GovernanceLayer

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** After validate_transition() (line 174), before load_handlers()

```diff
         allowed = VALID_TRANSITIONS.get(from_node, [])
         return to_node in allowed

+    def validate_queue_transition(
+        self, work_id: str, to_position: str, work_engine: Any = None
+    ) -> "GateResult":
+        """
+        Validate queue position transition is allowed (CH-009).
+
+        Args:
+            work_id: Work item ID
+            to_position: Target queue position
+            work_engine: WorkEngine instance (to read current position)
+
+        Returns:
+            GateResult with allowed flag and reason
+        """
+        from work_engine import is_valid_queue_transition
+
+        work = work_engine.get_work(work_id) if work_engine else None
+        if work is None:
+            result = GateResult(
+                allowed=False, reason=f"Work item {work_id} not found"
+            )
+        else:
+            from_pos = work.queue_position
+
+            if from_pos == to_position:
+                # No-op: already at target position
+                result = GateResult(
+                    allowed=True, reason=f"No-op: already at {to_position}"
+                )
+            elif is_valid_queue_transition(from_pos, to_position):
+                result = GateResult(
+                    allowed=True,
+                    reason=f"Valid transition: {from_pos} -> {to_position}",
+                )
+            else:
+                result = GateResult(
+                    allowed=False,
+                    reason=f"Invalid queue transition: {from_pos} -> {to_position}",
+                )
+
+        log_validation_outcome(
+            gate="queue_transition",
+            work_id=work_id,
+            result="pass" if result.allowed else "block",
+            reason=result.reason,
+        )
+
+        return result
+
     def load_handlers(self, config_path: str) -> Dict[str, Any]:
```

### Change 3: get_parked() and get_by_queue_position() Methods

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After get_in_progress() (line 708), before Lifecycle Query Methods

```diff
     def get_in_progress(self) -> List[WorkState]:
         """Deprecated: Use get_working() instead."""
         return self.get_working()

+    def get_parked(self) -> List[WorkState]:
+        """Get all work items with queue_position: parked (CH-009)."""
+        return self.get_by_queue_position("parked")
+
+    def get_by_queue_position(self, position: str) -> List[WorkState]:
+        """
+        Get all work items at given queue position (CH-009).
+
+        Args:
+            position: Queue position to filter by
+
+        Returns:
+            List of WorkState with matching queue_position
+        """
+        result = []
+        if not self.active_dir.exists():
+            return result
+
+        for subdir in self.active_dir.iterdir():
+            if subdir.is_dir():
+                work_md = subdir / "WORK.md"
+                if work_md.exists():
+                    work = self._parse_work_file(work_md)
+                    if work and work.queue_position == position:
+                        result.append(work)
+        return result
+
     # ========== Lifecycle Query Methods (WORK-086: Batch Mode) ==========
```

### Change 4: Integrate Validation in set_queue_position()

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 645-680 (existing method)

```diff
         work = self.get_work(id)
         if work is None:
             return None

+        # CH-009: Validate queue transition before write (fail fast)
+        gate_result = self._governance.validate_queue_transition(
+            id, position, work_engine=self
+        )
+        if not gate_result.allowed:
+            raise ValueError(f"Queue transition blocked: {gate_result.reason}")
+
         # WORK-105: Validate forbidden state combinations
         self._validate_state_combination(work.status, position)
```

### Call Chain

```
Caller (survey-cycle, ceremony)
    |
    +-> WorkEngine.set_queue_position(id, position)
            |
            +-> GovernanceLayer.validate_queue_transition(id, position, work_engine)
            |       -> is_valid_queue_transition(from_pos, to_pos)
            |       -> log_validation_outcome()
            |       -> Returns: GateResult
            |
            +-> WorkEngine._validate_state_combination() [existing]
            |
            +-> WorkEngine._write_work_file() [existing]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State machine location | Module-level `QUEUE_TRANSITIONS` in work_engine.py | Co-located with `VALID_QUEUE_POSITIONS`. Matches `VALID_TRANSITIONS` pattern in governance_layer.py |
| Validation function | Module-level `is_valid_queue_transition()` | Pure function, no side effects. Matches governance pattern. |
| Governance method | `validate_queue_transition(work_id, to_position, work_engine)` | Returns GateResult for consistency. Passes work_engine to avoid circular dependency. |
| Integration point | set_queue_position() before _validate_state_combination() | Fail fast - transition check before state combo check |
| Idempotent transitions | Allow X->X as no-op | Standard state machine pattern. Reduces caller complexity. |
| Query methods | get_parked() delegates to get_by_queue_position() | Follows get_working() pattern. Generic method enables future queries. |
| Error handling | ValueError on blocked transition | Matches existing set_queue_position() error pattern |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Idempotent (X->X) | Allow as no-op in validate_queue_transition | Implicit via existing tests |
| Work item not found | GateResult(allowed=False) | Existing set_queue_position returns None |
| Empty active_dir | get_parked/get_by_queue_position return [] | Follows get_working() pattern |
| Invalid position string to get_by_queue_position | Returns [] (no matches) | Caller responsibility |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Idempotent X->X | A) Block, B) Allow as no-op | **B) Allow** | Standard state machine pattern |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 15 test functions to `tests/test_work_engine.py` (CH-009 section)
- [ ] Tests T1-T6: Valid transitions
- [ ] Tests T7-T11: Invalid transitions
- [ ] Tests T12-T13: Query methods
- [ ] Tests T14-T15: Integration + backward compat
- [ ] Verify all 15 tests fail (red)

### Step 2: Implement State Machine Constants
- [ ] Add QUEUE_TRANSITIONS dict after VALID_QUEUE_POSITIONS
- [ ] Add is_valid_queue_transition() function

### Step 3: Implement Query Methods
- [ ] Add get_by_queue_position() method after get_in_progress()
- [ ] Add get_parked() delegating to get_by_queue_position()
- [ ] Tests T12-T13 pass (green)

### Step 4: Implement Governance Validation
- [ ] Add validate_queue_transition() to GovernanceLayer after validate_transition()
- [ ] Include idempotent transition logic and initial assignment logic

### Step 5: Integrate in set_queue_position()
- [ ] Add validate_queue_transition() call before _validate_state_combination()
- [ ] Raise ValueError if gate_result.allowed is False
- [ ] Tests T1-T15 all pass (green)

### Step 6: Integration Verification
- [ ] Run `pytest tests/test_work_engine.py -v` - all pass
- [ ] Verify WORK-105 tests still pass (backward compat)
- [ ] Run full suite - no regressions

### Step 7: Consumer Verification
- [ ] Grep for set_queue_position() callers
- [ ] Grep for direct queue_position assignments (anti-pattern)
- [ ] Verify callers handle ValueError

---

## Verification

- [ ] 15 CH-009 tests pass
- [ ] 10 WORK-105 tests pass (backward compat)
- [ ] Full test suite passes
- [ ] governance_events.jsonl logs queue_transition attempts

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular import (work_engine <-> governance_layer) | High | Import is_valid_queue_transition inside method, not at module level. Pass work_engine as param. |
| Breaking existing queue position usage | High | T15 backward compat test. Existing WORK-105 tests. |
| Idempotent transitions blocked | Medium | Resolved: Allow X->X as no-op. |
| Direct queue_position assignment bypasses validation | Low | Document as anti-pattern. set_queue_position is primary entry point. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| QUEUE_TRANSITIONS dict (6 valid paths) | [ ] | Read work_engine.py, verify dict |
| is_valid_queue_transition() function | [ ] | Read work_engine.py, verify function |
| validate_queue_transition() in governance | [ ] | Read governance_layer.py, verify method |
| get_parked() query method | [ ] | Read work_engine.py, verify method |
| get_by_queue_position() generic query | [ ] | Read work_engine.py, verify method |
| Unit tests for 6 valid transitions | [ ] | Read test_work_engine.py, verify T1-T6 |
| Unit tests for invalid transitions | [ ] | Read test_work_engine.py, verify T7-T11 |
| Integration with set_queue_position() | [ ] | Read work_engine.py, verify call at line ~671 |

### File Verification

| File | Expected State | Verified |
|------|---------------|----------|
| `.claude/haios/modules/work_engine.py` | QUEUE_TRANSITIONS, is_valid_queue_transition, get_parked, get_by_queue_position, set_queue_position integration | [ ] |
| `.claude/haios/modules/governance_layer.py` | validate_queue_transition method | [ ] |
| `tests/test_work_engine.py` | 15 new CH-009 tests, all passing | [ ] |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (15 CH-009 + 10 WORK-105)
- [ ] All WORK.md deliverables verified
- [ ] Runtime consumer exists (set_queue_position called by survey-cycle)
- [ ] WHY captured (memory_refs)
- [ ] Consumer verification complete

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-009-QueueLifecycle.md
- @.claude/haios/epochs/E2_5/arcs/queue/CH-007-QueuePositionField.md
- @docs/work/active/WORK-105/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-003, REQ-QUEUE-005)
