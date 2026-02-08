---
template: implementation_plan
status: complete
date: 2026-02-08
backlog_id: WORK-103
title: Dynamic Blocker Resolution in Queue Engine
author: Hephaestus
lifecycle_phase: plan
session: 323
version: '1.5'
generated: 2026-02-08
last_updated: '2026-02-08T22:37:31'
---
# Implementation Plan: Dynamic Blocker Resolution in Queue Engine

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

`WorkEngine.get_ready()` and `get_queue()` will dynamically resolve `blocked_by` references against actual work item status, so items whose blockers are all terminal (complete/archived) appear as unblocked without manual frontmatter edits.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `work_engine.py`, `test_work_engine.py` |
| Lines of code affected | ~5 | 1 new method (~20 lines), 1 line change in `get_ready()` |
| New files to create | 0 | |
| Tests to write | 5 | See Tests First section |
| Dependencies | 0 | No new imports; `get_queue()` auto-inherits fix via `get_ready()` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only `get_ready()` changes; `get_queue()` auto-inherits |
| Risk of regression | Low | 61 existing tests cover work_engine; change is additive |
| External dependencies | Low | No external deps; reads existing WORK.md files |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 10 min | High |
| Verification | 10 min | High |
| **Total** | 35 min | |

---

## Current State vs Desired State

### Current State

```python
# work_engine.py:378 - get_ready() static blocked_by check
if work and not work.blocked_by and work.status not in terminal_statuses and work.queue_position != "parked":
    ready.append(work)
```

**Behavior:** `not work.blocked_by` treats any non-empty list as blocked, regardless of blocker status.

**Result:** Items with completed blockers remain phantom-blocked. Manual frontmatter edit required to clear.

### Desired State

```python
# work_engine.py:378 - get_ready() dynamic blocked_by resolution
if work and not self._is_actually_blocked(work) and work.status not in terminal_statuses and work.queue_position != "parked":
    ready.append(work)
```

**Behavior:** `_is_actually_blocked()` resolves each blocker ID against actual status. Only items with at least one active blocker are filtered out.

**Result:** Items auto-unblock when their blockers complete. No manual intervention needed.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Item blocked by completed work appears in get_ready
```python
def test_get_ready_resolves_completed_blocker(tmp_path, governance):
    """WORK-103: Item blocked_by completed work should appear in get_ready()."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    # Create blocker A (status: complete) and item B (blocked_by: [A])
    # get_ready() should return B
```

### Test 2: Item blocked by active work stays blocked
```python
def test_get_ready_excludes_actively_blocked(tmp_path, governance):
    """WORK-103: Item blocked_by active work should NOT appear in get_ready()."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    # Create blocker A (status: active) and item B (blocked_by: [A])
    # get_ready() should NOT return B
```

### Test 3: Mixed blockers - one complete, one active - stays blocked
```python
def test_get_ready_partial_blocker_resolution(tmp_path, governance):
    """WORK-103: Item with mix of complete and active blockers stays blocked."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    # Create A (complete), C (active), B (blocked_by: [A, C])
    # get_ready() should NOT return B
```

### Test 4: Missing blocker treated as resolved
```python
def test_get_ready_missing_blocker_treated_as_resolved(tmp_path, governance):
    """WORK-103: Item blocked_by nonexistent work should appear in get_ready()."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    # Create B (blocked_by: [NONEXISTENT-001])
    # get_ready() should return B
```

### Test 5: Backward compatibility - empty blocked_by still works
```python
def test_get_ready_empty_blocked_by_unchanged(tmp_path, governance):
    """WORK-103: Items with empty blocked_by still appear (no regression)."""
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    # Create item with blocked_by: []
    # get_ready() should return it (same as before)
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Exact Code Change

**File:** `.claude/haios/modules/work_engine.py`

**Change 1: New method `_is_actually_blocked()`**
**Location:** After `_validate_state_combination()` (line ~828), before Helper Methods section

```python
def _is_actually_blocked(self, work: WorkState) -> bool:
    """Check if work item is actually blocked (blockers still active).

    WORK-103: Resolves blocked_by IDs against actual work item status.
    Items whose blockers are ALL terminal are treated as unblocked.

    Args:
        work: WorkState to check

    Returns:
        True if at least one blocker is still active, False otherwise
    """
    if not work.blocked_by:
        return False

    terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}

    for blocker_id in work.blocked_by:
        blocker = self.get_work(blocker_id)
        # If blocker not found (deleted/moved), treat as resolved
        if blocker is None:
            continue
        # If blocker is still active, item is actually blocked
        if blocker.status not in terminal_statuses:
            return True

    return False
```

**Change 2: Update `get_ready()` filter**
**Location:** Line 378 in `get_ready()`

**Current Code:**
```python
# work_engine.py:378
if work and not work.blocked_by and work.status not in terminal_statuses and work.queue_position != "parked":
```

**Changed Code:**
```python
# work_engine.py:378
if work and not self._is_actually_blocked(work) and work.status not in terminal_statuses and work.queue_position != "parked":
```

**Diff:**
```diff
-                    if work and not work.blocked_by and work.status not in terminal_statuses and work.queue_position != "parked":
+                    if work and not self._is_actually_blocked(work) and work.status not in terminal_statuses and work.queue_position != "parked":
```

### Call Chain Context

```
survey-cycle / just queue / just ready
    |
    +-> get_queue(queue_name)
    |       |
    |       +-> get_ready()  (for auto queues)
    |               |
    |               +-> _is_actually_blocked(work)  # <-- NEW
    |                       |
    |                       +-> get_work(blocker_id)  # resolve each blocker
    |
    +-> get_ready()  (direct callers)
            |
            +-> _is_actually_blocked(work)  # <-- NEW
```

### Function/Component Signatures

```python
def _is_actually_blocked(self, work: WorkState) -> bool:
    """Check if work item is actually blocked (blockers still active).

    WORK-103: Resolves blocked_by IDs against actual work item status.
    Items whose blockers are ALL terminal are treated as unblocked.

    Args:
        work: WorkState with blocked_by field populated

    Returns:
        True if at least one blocker is still active, False otherwise
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to resolve | New `_is_actually_blocked()` method | Single responsibility: resolution logic isolated from iteration logic in `get_ready()` |
| Missing blocker handling | Treat as resolved (not blocked) | If blocker was deleted/archived/moved, the dependency is gone. Blocking on missing data would be worse than unblocking. |
| Terminal status set | Reuse same set as `get_ready()` | Consistency: `{"complete", "archived", "dismissed", "invalid", "deferred"}` already defined in `get_ready()` |
| Performance | N+1 reads per `get_ready()` call | Acceptable for current scale (~15 active items, ~2 blockers max). If scale grows, add caching later. |

### Input/Output Examples

**Before Fix (real data from S316):**
```
WORK-091 has blocked_by: [WORK-088]
WORK-088 has status: complete (closed 2026-02-04)
get_ready() -> WORK-091 NOT in list (phantom-blocked)
```

**After Fix (expected):**
```
WORK-091 has blocked_by: [WORK-088]
WORK-088 has status: complete (closed 2026-02-04)
_is_actually_blocked(WORK-091) -> False (WORK-088 is terminal)
get_ready() -> WORK-091 IN list (correctly unblocked)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty blocked_by | Short-circuit return False | Test 5 |
| All blockers complete | Return False (unblocked) | Test 1 |
| All blockers active | Return True (blocked) | Test 2 |
| Mix of complete + active | Return True (still blocked) | Test 3 |
| Blocker not found (deleted) | Skip, treat as resolved | Test 4 |
| Blocker in archive dir | `get_work()` checks archive via `_find_work_file()` | Covered by existing `_find_work_file` logic |

### Open Questions

None. Design is straightforward with clear precedent from the existing cascade tests.

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No open decisions. Design is fully determined by acceptance criteria and existing patterns.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write 5 Failing Tests
- [ ] Add 5 tests to `tests/test_work_engine.py` under new section
- [ ] Verify all 5 tests fail (red) - `_is_actually_blocked` does not exist yet

### Step 2: Add `_is_actually_blocked()` method
- [ ] Add method to WorkEngine class after `_validate_state_combination()`
- [ ] Tests 1-5 still fail (method exists but not wired in)

### Step 3: Update `get_ready()` to use `_is_actually_blocked()`
- [ ] Replace `not work.blocked_by` with `not self._is_actually_blocked(work)` on line 378
- [ ] Tests 1-5 pass (green)

### Step 4: Integration Verification
- [ ] All 5 new tests pass
- [ ] Run full test suite: `pytest tests/test_work_engine.py -v` (no regressions)
- [ ] Run `just queue default` to verify real queue behavior

### Step 5: README Sync
**SKIPPED:** No new files created, no directory structure changes. Existing READMEs unaffected.

### Step 6: Consumer Verification
**SKIPPED:** Not a migration/refactor. `get_ready()` signature unchanged. All existing callers auto-benefit.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| N+1 reads on large workspaces | Low | Current scale is ~15 active items with ~2 blockers max. Add caching if scale grows. |
| Circular blocked_by references | Low | `get_work()` reads files, no recursion. Circular refs would just mean both items stay blocked. |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-103/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| WorkEngine.get_queue() resolves blocked_by against actual status | [ ] | Test 1 passes + `just queue` demo |
| Items with all blockers complete treated as unblocked | [ ] | Tests 1, 4 pass |
| Unit test: blocked by complete appears in queue | [ ] | Test 1 exists and passes |
| Unit test: blocked by active does NOT appear | [ ] | Test 2 exists and passes |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | `_is_actually_blocked()` exists; `get_ready()` uses it | [ ] | |
| `tests/test_work_engine.py` | 5 new WORK-103 tests exist and pass | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/WORK-103/WORK.md
- @.claude/haios/modules/work_engine.py
- @tests/test_work_engine.py

---
