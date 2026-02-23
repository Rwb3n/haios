---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-23
backlog_id: WORK-207
title: "Auto-Reset Stale Status on Unpark Queue Transition"
author: Hephaestus
lifecycle_phase: plan
session: 438
generated: 2026-02-23
last_updated: 2026-02-23T20:25:38

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-207/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Auto-Reset Stale Status on Unpark Queue Transition

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add an auto-reset guard in `set_queue_position()` that detects stale `status=blocked` via `_is_actually_blocked()` and resets it to `active` before `_validate_state_combination()` fires, so that parked items with resolved or empty `blocked_by` lists can be unpacked to backlog without a manual status fix.

---

## Open Decisions

No `operator_decisions` present in WORK.md frontmatter. No rows required.

**SKIPPED:** No operator decisions exist.

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/modules/work_engine.py` | MODIFY | 2 |

### Consumer Files

<!-- Files that reference primary files and need updating.
     Use: Grep(pattern="module_name|function_name", glob="**/*.{py,md}") -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/queue_ceremonies.py` | calls `set_queue_position` via `execute_queue_transition` | 96-133 | NO CHANGE — fix is inside `set_queue_position`, transparent to callers |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_work_engine.py` | UPDATE | Add 3 new tests for stale blocked auto-reset |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | Primary Files table (CREATE rows) |
| Files to modify | 1 | `work_engine.py` (6-line insertion) |
| Tests to write | 3 | Test Files table |
| Total blast radius | 2 | `work_engine.py` + `test_work_engine.py` |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

```python
# .claude/haios/modules/work_engine.py  lines 722-730
        # CH-009: Validate queue transition before write (fail fast)
        gate_result = self._governance.validate_queue_transition(
            id, position, work_engine=self
        )
        if not gate_result.allowed:
            raise ValueError(f"Queue transition blocked: {gate_result.reason}")

        # WORK-105: Validate forbidden state combinations
        self._validate_state_combination(work.status, position)
```

**Behavior:** `_validate_state_combination()` is called with the work item's current `status` verbatim. If `status == "blocked"` and `position == "working"`, it raises `ValueError: Forbidden state combination`. It does not check whether the blockers are still active.

**Problem:** A work item parked in E2.5 may carry `status=blocked` with `blocked_by: []` (blockers resolved independently while parked). The unpark path (`parked → backlog`) does not hit `blocked+working`, so that step succeeds. But the subsequent `backlog → ready → working` path fails with the forbidden combination error because `status` was never reset. This requires a manual Edit to fix the status before the queue can proceed, as seen with WORK-102 in S435.

### Desired State

```python
# .claude/haios/modules/work_engine.py  lines 722-737 (after patch)
        # CH-009: Validate queue transition before write (fail fast)
        gate_result = self._governance.validate_queue_transition(
            id, position, work_engine=self
        )
        if not gate_result.allowed:
            raise ValueError(f"Queue transition blocked: {gate_result.reason}")

        # WORK-207: Auto-reset stale blocked status on unpark transition.
        # If status=blocked but _is_actually_blocked() returns False (empty
        # blocked_by, or all blockers are terminal), reset to 'active' BEFORE
        # _validate_state_combination() fires.  This makes the unpark path
        # self-healing for cross-epoch items whose blockers resolved independently.
        if work.status == "blocked" and not self._is_actually_blocked(work):
            work.status = "active"

        # WORK-105: Validate forbidden state combinations
        self._validate_state_combination(work.status, position)
```

**Behavior:** Before `_validate_state_combination()` runs, the guard checks whether the `blocked` status is genuine. If `_is_actually_blocked()` returns `False` (i.e., `blocked_by` is empty, or every listed blocker has a terminal status), `work.status` is silently reset to `active`. The subsequent `_validate_state_combination()` then sees `active + <any position>`, which has no forbidden pairing, and proceeds normally. `_write_work_file()` persists the corrected status.

**Result:** Cross-epoch items with stale `blocked` status can be unpacked and routed through the queue without manual intervention. The fix is entirely within `set_queue_position()` and transparent to all callers including `execute_queue_transition()`.

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 1: Stale Blocked with Empty blocked_by Resets on Unpark

- **file:** `tests/test_work_engine.py`
- **function:** `test_unpark_resets_stale_blocked_empty_blocked_by()`
- **setup:**
  1. `engine.create_work("WORK-STALE1", "Stale Blocked Empty")`
  2. Move to `parked`: `engine.set_queue_position("WORK-STALE1", "parked")`
  3. Manually write `status=blocked` + `blocked_by=[]` directly via `_write_work_file` after mutating the in-memory WorkState:
     ```python
     work = engine.get_work("WORK-STALE1")
     work.status = "blocked"
     engine._write_work_file(work)
     ```
  4. Verify stale state written: `assert engine.get_work("WORK-STALE1").status == "blocked"`
- **assertion:**
  - `result = engine.set_queue_position("WORK-STALE1", "backlog")` does NOT raise
  - `assert result.status == "active"` — status reset during transition
  - `assert result.queue_position == "backlog"`
  - Re-read from disk: `engine.get_work("WORK-STALE1").status == "active"`

#### Test 2: Stale Blocked with All-Terminal blocked_by Resets on Any Transition

- **file:** `tests/test_work_engine.py`
- **function:** `test_unpark_resets_stale_blocked_all_terminal_blocked_by()`
- **setup:**
  1. Create blocker: `engine.create_work("WORK-BLOCKER", "Blocker")`, then manually set `status=complete` via `_write_work_file`.
  2. `engine.create_work("WORK-STALE2", "Stale Blocked Terminal")`
  3. `engine.set_queue_position("WORK-STALE2", "parked")`
  4. Write stale state: get work, set `status=blocked`, `blocked_by=["WORK-BLOCKER"]`, write back via `_write_work_file`.
- **assertion:**
  - `result = engine.set_queue_position("WORK-STALE2", "backlog")` does NOT raise
  - `assert result.status == "active"`
  - `assert result.queue_position == "backlog"`

#### Test 3: Genuinely Blocked Item Still Blocked on Transition (Regression)

- **file:** `tests/test_work_engine.py`
- **function:** `test_genuinely_blocked_item_not_reset()`
- **setup:**
  1. Create active blocker: `engine.create_work("WORK-LIVE-BLOCKER", "Live Blocker")` — default status is `active`.
  2. `engine.create_work("WORK-GENUINE", "Genuinely Blocked")`
  3. `engine.set_queue_position("WORK-GENUINE", "parked")`
  4. Write: `status=blocked`, `blocked_by=["WORK-LIVE-BLOCKER"]` via `_write_work_file`.
- **assertion:**
  - `result = engine.set_queue_position("WORK-GENUINE", "backlog")` succeeds (parked→backlog does not hit blocked+working)
  - `assert result.status == "blocked"` — status NOT reset because blocker is still active
  - `assert result.queue_position == "backlog"`

### Design

#### File 1 (MODIFY): `.claude/haios/modules/work_engine.py`

**Location:** Lines 728-730 in `set_queue_position()` — insert 4 lines BEFORE the `_validate_state_combination` call.

**Current Code:**
```python
        # WORK-105: Validate forbidden state combinations
        self._validate_state_combination(work.status, position)
```

**Target Code:**
```python
        # WORK-207: Auto-reset stale blocked status on unpark transition.
        # If status=blocked but _is_actually_blocked() returns False (empty
        # blocked_by, or all blockers are terminal), reset to 'active' BEFORE
        # _validate_state_combination() fires.  This makes the unpark path
        # self-healing for cross-epoch items whose blockers resolved independently.
        if work.status == "blocked" and not self._is_actually_blocked(work):
            work.status = "active"

        # WORK-105: Validate forbidden state combinations
        self._validate_state_combination(work.status, position)
```

**Diff:**
```diff
+        # WORK-207: Auto-reset stale blocked status on unpark transition.
+        # If status=blocked but _is_actually_blocked() returns False (empty
+        # blocked_by, or all blockers are terminal), reset to 'active' BEFORE
+        # _validate_state_combination() fires.  This makes the unpark path
+        # self-healing for cross-epoch items whose blockers resolved independently.
+        if work.status == "blocked" and not self._is_actually_blocked(work):
+            work.status = "active"
+
         # WORK-105: Validate forbidden state combinations
         self._validate_state_combination(work.status, position)
```

### Call Chain

```
execute_queue_transition()          # queue_ceremonies.py:96
    |
    +-> work_engine.set_queue_position(id, position)   # work_engine.py:695
            |
            +-> _governance.validate_queue_transition()   # CH-009 gate
            |
            +-> [NEW] if status==blocked and not _is_actually_blocked():  # WORK-207
            |       work.status = "active"
            |
            +-> _validate_state_combination(work.status, position)  # WORK-105
            |       (now sees "active", not "blocked" — no forbidden match)
            |
            +-> _write_work_file(work)   # persists corrected status
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fix location: `set_queue_position()` not `queue_ceremonies.py` | `work_engine.py` | `set_queue_position` owns the queue state transition and is the single writer. Queue ceremonies is a logging wrapper. Fixing the source eliminates the bug for all call paths, not just ceremony-mediated ones. |
| Reset target status: `'active'` not `'open'` | `'active'` | `create_work()` sets default `status='active'`. Existing items were `active` before being blocked. Resetting to `active` matches the pre-blocking state and passes all existing `_validate_state_combination` checks. |
| Guard condition: only reset when `status == "blocked"` | Narrow predicate | Avoids touching items with intentional statuses. `_is_actually_blocked()` already handles the two sub-cases (empty `blocked_by` and all-terminal `blocked_by`). Reusing it avoids duplicating logic. |
| Placement: BEFORE `_validate_state_combination()` | Pre-validation reset | The fix must happen before validation so the corrected status is what validation sees. Placing it after would allow the exception to fire first. |
| No explicit log/event for the auto-reset | Silent correction | This is a data-quality heal, not a queue transition. It has no semantic meaning to operators. Logging could create noise; the status change is persisted via `_write_work_file` and is observable via the work item file. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `status=blocked`, `blocked_by=[]` | `_is_actually_blocked()` returns `False` immediately (line 935 early return) → status reset | Test 1 |
| `status=blocked`, all blockers terminal | `_is_actually_blocked()` returns `False` after iterating → status reset | Test 2 |
| `status=blocked`, at least one active blocker | `_is_actually_blocked()` returns `True` → status NOT reset | Test 3 |
| `status=active` or any non-blocked status | Guard condition `work.status == "blocked"` is `False` → no change, existing behavior preserved | Covered by all existing queue tests |
| Blocker work item not found (deleted/moved) | `_is_actually_blocked()` treats missing blockers as resolved → status reset | Covered by `_is_actually_blocked()` logic (line 942-943) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Legitimate blocked item incorrectly reset | High | Guard requires `_is_actually_blocked()` to return `False`. This method resolves each blocker ID against actual work item status. A live-status blocker keeps `is_actually_blocked=True` and prevents the reset. Test 3 validates this path. |
| `_write_work_file` catch-all fires on reset status | Low | `_validate_state_combination` only forbids `(blocked, working)` and `(complete, working)`. After reset to `active`, no forbidden combination can match. `_write_work_file`'s own catch-all (line 1029) will also see `active` and pass. |
| Regression to existing forbidden-state tests | Low | Existing tests set `status=complete` or `status=blocked` then try `working`. The guard only fires if `_is_actually_blocked()` is `False`. Tests using `status=blocked` without setting up `blocked_by` entries will be affected — addressed in Test 3 pattern and existing test audit. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)

- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Append 3 new test functions to `tests/test_work_engine.py` per Layer 1 Tests section. Run pytest to confirm they fail.
- **output:** 3 new test functions exist, all fail (functionality not yet implemented)
- **verify:** `pytest tests/test_work_engine.py -k "stale_blocked or genuinely_blocked" -v 2>&1 | grep -c "FAILED\|ERROR"` equals 3

### Step 2: Implement Auto-Reset Guard (GREEN)

- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Insert the 7-line guard block into `set_queue_position()` in `.claude/haios/modules/work_engine.py` BEFORE the `_validate_state_combination` call at line 730, exactly as specified in Layer 1 Design.
- **output:** 3 new tests pass
- **verify:** `pytest tests/test_work_engine.py -k "stale_blocked or genuinely_blocked" -v` exits 0, `3 passed` in output

### Step 3: Full Regression Check

- **spec_ref:** Layer 0 > Primary Files
- **input:** Step 2 complete (new tests green)
- **action:** Run the full test suite to confirm no regressions introduced by the guard
- **output:** All existing tests still pass
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `0 failed` relative to pre-change baseline (1571 passed, 0 failed, 8 skipped per MEMORY.md S418)

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_work_engine.py -k "stale_blocked or genuinely_blocked" -v` | 3 passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs 1571 passed baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| `set_queue_position()` auto-resets stale blocked status on parked->backlog | `grep -n "WORK-207" .claude/haios/modules/work_engine.py` | 1+ match at insertion point |
| Test for stale status=blocked with empty blocked_by | `grep -n "test_unpark_resets_stale_blocked_empty_blocked_by" tests/test_work_engine.py` | 1 match |
| Test for stale status=blocked with all-terminal blocked_by | `grep -n "test_unpark_resets_stale_blocked_all_terminal_blocked_by" tests/test_work_engine.py` | 1 match |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No old stale-blocked pattern reference | `grep -r "stale.*blocked\|blocked.*stale" .claude/haios/ --include="*.py"` | Only the new guard comment |
| `_is_actually_blocked` still present | `grep -n "_is_actually_blocked" .claude/haios/modules/work_engine.py` | 2+ matches (definition + call site) |
| `queue_ceremonies.py` unchanged | `git diff .claude/haios/lib/queue_ceremonies.py` | empty (no changes) |

### Completion Criteria (DoD)

- [ ] All 3 new tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Full suite: 0 new failures (Consumer Integrity — regression check)
- [ ] `queue_ceremonies.py` untouched (Consumer Integrity table)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- Session 435 retro extract REFACTOR-1 (memory: 87988)
- `.claude/haios/modules/work_engine.py` — `set_queue_position` (line 695), `_validate_state_combination` (line 903), `_is_actually_blocked` (line 923)
- `.claude/haios/lib/queue_ceremonies.py` — `execute_queue_transition` (line 96)
- `tests/test_work_engine.py` — existing queue position and forbidden state tests (lines 1210+, 1656+, 1873+)
- REQ-QUEUE-001, REQ-QUEUE-004
- WORK-105 (Forbidden State Combinations), WORK-103 (_is_actually_blocked origin)

---
