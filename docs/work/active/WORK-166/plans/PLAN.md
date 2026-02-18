---
template: implementation_plan
status: complete
date: 2026-02-18
backlog_id: WORK-166
title: "Bug Batch E2.8"
author: Hephaestus
lifecycle_phase: plan
session: 395
version: "1.5"
generated: 2026-02-18
last_updated: 2026-02-18T08:15:58
---
# Implementation Plan: Bug Batch E2.8

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

Fix three confirmed bugs: checkpoint same-session sort tie-breaking (session_loader + work_loader), queue state machine missing backlog->done admin transition, and EPOCH.md E2.6 stale work item status annotations.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | session_loader.py, work_loader.py, work_engine.py, EPOCH.md E2.6 |
| Lines of code affected | ~15 | 2x _session_number() rewrite + 1 transition table line + EPOCH table rows |
| New files to create | 0 | Tests added to existing test files |
| Tests to write | 5 | 2 tiebreak + 2 queue transition + 1 backward compat |
| Dependencies | 2 | coldstart_orchestrator imports session_loader; queue_ceremonies imports work_engine |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Each fix is isolated to one function/constant |
| Risk of regression | Low | Existing tests cover session_loader and work_engine; tuple comparison is superset of int |
| External dependencies | Low | No APIs or external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 15 min | High |
| EPOCH.md verification | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

**Bug 1: Checkpoint sort** — `session_loader.py:115-120` and `work_loader.py:135-140`:
```python
def _session_number(path: Path) -> int:
    """Extract session number from filename like '...-SESSION-348-...'."""
    match = re.search(r"SESSION-(\d+)", path.name, re.IGNORECASE)
    return int(match.group(1)) if match else 0

return max(checkpoints, key=_session_number)
```

**Behavior:** Returns int session number only. When `SESSION-94` appears in multiple filenames (`-04-SESSION-94-early.md`, `-05-SESSION-94-late.md`), `max()` picks arbitrarily among tied values.

**Bug 2: Queue transitions** — `work_engine.py:136-142`:
```python
QUEUE_TRANSITIONS = {
    "parked": ["backlog"],
    "backlog": ["ready", "parked"],
    "ready": ["working", "backlog"],
    "working": ["done"],
    "done": [],
}
```

**Behavior:** No path from backlog to done. Admin cleanup of items completed outside normal flow requires manual YAML editing.

**Bug 3: EPOCH.md E2.6** — Work items table shows items without `(COMPLETE)` annotations despite `status: complete` in WORK.md.

### Desired State

**Bug 1 fix:** `_session_number()` returns tuple for deterministic tie-breaking:
```python
def _session_number(path: Path) -> tuple:
    session_match = re.search(r"SESSION-(\d+)", path.name, re.IGNORECASE)
    session_num = int(session_match.group(1)) if session_match else 0
    date_match = re.match(r"(\d{4}-\d{2}-\d{2}-\d{2})", path.name)
    date_prefix = date_match.group(1) if date_match else ""
    return (session_num, date_prefix, path.name)
```

**Behavior:** Primary sort by session number, tie-break by date prefix, final tiebreak by filename. Fully deterministic via explicit tuple comparison.

**Bug 2 fix:** Add `"done"` to backlog transitions:
```python
"backlog": ["ready", "parked", "done"],  # Added "done" for admin cleanup
```

**Bug 3 fix:** Verify each WORK.md status, add `(COMPLETE Sxxx)` annotations to EPOCH.md table.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Session loader checkpoint sort tie-breaking
```python
def test_find_latest_checkpoint_tiebreak(tmp_path):
    """When multiple checkpoints share session number, pick latest by date prefix."""
    (tmp_path / "2025-12-21-04-SESSION-94-early.md").write_text("---\nsession: 94\n---\n")
    (tmp_path / "2025-12-21-05-SESSION-94-late.md").write_text("---\nsession: 94\n---\n")
    loader = SessionLoader(checkpoint_dir=tmp_path)
    result = loader._find_latest_checkpoint()
    assert result is not None
    assert "05-SESSION-94-late" in result.name
```

### Test 2: Work loader checkpoint sort tie-breaking
```python
def test_find_latest_checkpoint_tiebreak(tmp_path):
    """When multiple checkpoints share session number, pick latest by date prefix."""
    (tmp_path / "2025-12-21-04-SESSION-94-early.md").write_text("---\nsession: 94\n---\n")
    (tmp_path / "2025-12-21-05-SESSION-94-late.md").write_text("---\nsession: 94\n---\n")
    loader = WorkLoader(checkpoint_dir=tmp_path)
    result = loader._find_latest_checkpoint()
    assert result is not None
    assert "05-SESSION-94-late" in result.name
```

### Test 3: Queue backlog-to-done transition valid
```python
def test_queue_transition_backlog_to_done():
    """Admin cleanup: backlog -> done should be valid."""
    assert is_valid_queue_transition("backlog", "done") is True
```

### Test 4: Existing queue transitions unchanged
```python
def test_queue_transitions_backward_compat():
    """Adding backlog->done doesn't break existing transitions."""
    assert is_valid_queue_transition("backlog", "ready") is True
    assert is_valid_queue_transition("backlog", "parked") is True
    assert is_valid_queue_transition("working", "done") is True
    assert is_valid_queue_transition("done", "backlog") is False  # Still terminal
```

### Test 5: Session number without date prefix backward compat
```python
def test_find_latest_checkpoint_no_date_prefix(tmp_path):
    """Checkpoints without date prefix still sort by session number."""
    (tmp_path / "SESSION-100-foo.md").write_text("---\nsession: 100\n---\n")
    (tmp_path / "SESSION-99-bar.md").write_text("---\nsession: 99\n---\n")
    loader = SessionLoader(checkpoint_dir=tmp_path)
    result = loader._find_latest_checkpoint()
    assert result is not None
    assert "SESSION-100" in result.name
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

### Bug 1: Checkpoint Sort Tie-Breaking

**Files:** `.claude/haios/lib/session_loader.py:115-120`, `.claude/haios/lib/work_loader.py:135-140`

**Current Code (identical in both files):**
```python
def _session_number(path: Path) -> int:
    """Extract session number from filename like '...-SESSION-348-...'."""
    match = re.search(r"SESSION-(\d+)", path.name, re.IGNORECASE)
    return int(match.group(1)) if match else 0
```

**Changed Code (identical change in both files):**
```python
def _session_number(path: Path) -> tuple:
    """Extract session number and date sequence for sort ordering.

    Returns (session_number, date_prefix, filename) tuple for deterministic ordering.
    Session number is primary key, date prefix breaks ties, filename is final tiebreaker.
    Date prefix like '2025-12-21-05' is lexicographically sortable.
    """
    session_match = re.search(r"SESSION-(\d+)", path.name, re.IGNORECASE)
    session_num = int(session_match.group(1)) if session_match else 0
    date_match = re.match(r"(\d{4}-\d{2}-\d{2}-\d{2})", path.name)
    date_prefix = date_match.group(1) if date_match else ""
    return (session_num, date_prefix, path.name)
```

**Call chain:** `SessionLoader.extract()` -> `_find_latest_checkpoint()` -> `max(checkpoints, key=_session_number)`. The `max()` call is unchanged — tuple comparison handles tie-breaking.

**Real example with current data:**
```
Checkpoints with SESSION-94:
  2025-12-21-04-SESSION-94-e2-120-phase-3-complete.md
  2025-12-21-05-SESSION-94-m5-progress-e2-126-complete.md
  2025-12-21-05-SESSION-94-m5-complete-e2-125-e2-129-migration.md

Current: max() picks arbitrarily among these three (all return 94)
Fixed: max() returns (94, "2025-12-21-05") — picks one of the -05- files
       Between two -05- files, picks lexicographically later (deterministic)
```

### Bug 2: Queue State Machine Admin Transition

**File:** `.claude/haios/modules/work_engine.py:136-142`

**Diff:**
```diff
 QUEUE_TRANSITIONS = {
     "parked": ["backlog"],
-    "backlog": ["ready", "parked"],
+    "backlog": ["ready", "parked", "done"],  # Admin cleanup (caller must set status=complete)
     "ready": ["working", "backlog"],
     "working": ["done"],
     "done": [],
 }
```

**Call chain:** `WorkEngine.set_queue_position()` -> `GovernanceLayer.validate_queue_transition()` -> reads `QUEUE_TRANSITIONS`. Also used by `is_valid_queue_transition()` standalone function.

### Bug 3: EPOCH.md E2.6 Stale Status

**File:** `.claude/haios/epochs/E2_6/EPOCH.md:128-145`

Verify each WORK.md `status` field, then update table entries missing `(COMPLETE Sxxx)`.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tuple vs secondary sort | Tuple return from `_session_number()` | Python `max()` with tuple key handles tie-breaking natively — no extra sort step needed |
| Date prefix pattern | `YYYY-MM-DD-NN` (13 chars) | Matches all observed checkpoint filenames; lexicographic comparison works for date+sequence |
| Empty string fallback | `""` for files without date prefix | Files without prefix sort before dated files at same session number — safe backward compat |
| backlog->done only | Not adding ready->done or parked->done | Minimal change; ready/parked items should go through normal flow. Backlog->done is specifically for admin cleanup of items that completed outside queue |
| active+done state | Callers must set status=complete before or after backlog->done | The backlog->done transition is for items already complete (operator override, epoch cleanup). Not adding to FORBIDDEN_STATE_COMBINATIONS because the transition itself is valid — the caller is responsible for status consistency. Document this in code comment. |
| Explicit tiebreaker | Include `path.name` as third tuple element | Avoids implicit reliance on Path.__lt__ comparison. Makes sort deterministic and explicit. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No date prefix in filename | Returns `(session_num, "")` — sorts before dated files | Test 5 |
| No SESSION-N in filename | Returns `(0, date_prefix)` — lowest priority | Existing test coverage |
| Multiple files with same session AND date prefix | `max()` picks lexicographically later filename — deterministic | Inherent in tuple comparison |
| backlog->done with forbidden state combo | `_validate_state_combination()` still runs — blocks if status is incompatible | Existing validation tests |

### Open Questions

None. All design decisions are clear from code analysis.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

**SKIPPED:** Bug batch — no open operator decisions. All fixes are deterministic from code analysis.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write failing tests
- [ ] Add tiebreak tests to test_session_loader.py (Tests 1, 5)
- [ ] Add tiebreak test to test_work_loader.py (Test 2)
- [ ] Add queue transition tests to test_work_engine.py (Tests 3, 4)
- [ ] Verify all new tests fail (red)

### Step 2: Fix checkpoint sort tie-breaking
- [ ] Update `_session_number()` in session_loader.py to return tuple
- [ ] Update `_session_number()` in work_loader.py to return tuple
- [ ] Tests 1, 2, 5 pass (green)

### Step 3: Fix queue state machine
- [ ] Add `"done"` to backlog transitions in work_engine.py QUEUE_TRANSITIONS
- [ ] Tests 3, 4 pass (green)

### Step 4: Fix EPOCH.md E2.6 stale status
- [ ] Verify WORK.md status for each E2.6 work item (075, 096, 104, 135, 144, 145, 146, 147, 148, 149, 150, 151)
- [ ] Update EPOCH.md work items table with `(COMPLETE Sxxx)` annotations

### Step 5: Integration verification
- [ ] All new tests pass
- [ ] Run full test suite (no regressions)

### Step 6: Consumer verification
**SKIPPED:** No migrations or renames. All changes are in-place fixes to existing functions/constants. No consumer updates needed.

---

## Verification

- [ ] Tests pass (5 new + existing suite)
- [ ] **MUST:** No README changes needed (no new files or structural changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tuple return type breaks callers of _session_number | Low | No external callers — private helper used only by `max()` in same file |
| backlog->done bypasses ready/working flow | Low | Intentional for admin cleanup; normal items still follow backlog->ready->working->done |
| EPOCH.md annotations inaccurate | Low | Verify each WORK.md status before annotating |

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

**MUST** read `docs/work/active/WORK-166/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Checkpoint same-session sort bug fixed | [ ] | Tests 1, 2, 5 pass |
| Queue state machine backlog->done transition added | [ ] | Tests 3, 4 pass |
| All confirmed E2.7 triage bugs resolved or explicitly deferred | [ ] | Triage table in plan: 85712 resolved, 85557/85795/85132 deferred with rationale |
| Zero test regressions | [ ] | Full pytest suite output |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/session_loader.py` | `_session_number()` returns tuple | [ ] | |
| `.claude/haios/lib/work_loader.py` | `_session_number()` returns tuple | [ ] | |
| `.claude/haios/modules/work_engine.py` | `QUEUE_TRANSITIONS["backlog"]` includes `"done"` | [ ] | |
| `.claude/haios/epochs/E2_6/EPOCH.md` | Work items table has completion annotations | [ ] | |
| `tests/test_session_loader.py` | Tiebreak + backward compat tests exist | [ ] | |
| `tests/test_work_loader.py` | Tiebreak test exists | [ ] | |
| `tests/test_work_engine.py` | Queue transition tests exist | [ ] | |

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

## Memory Ref Triage

| Memory ID | Description | Verdict | Rationale |
|-----------|-------------|---------|-----------|
| 84963 | Batch bug pattern validated | N/A | Meta-observation, not a bug |
| 85712 | WorkLoader sorted bug | RESOLVED | Fixed in WORK-156 (S388), code now uses `max(key=_session_number)` |
| 85557 | `just set-cycle` no governance events | DEFER | Feature request, not bug |
| 85573 | EPOCH.md E2.6 stale work item status | IN SCOPE | Documentation bug |
| 85795 | cycle_phase programmatic updater | DEFER | Feature proposal, not bug |
| 85132 | ingester_ingest source_path pipeline | DEFER | Feature (medium), different scope |

## References

- @.claude/haios/lib/session_loader.py (Bug 1)
- @.claude/haios/lib/work_loader.py (Bug 1)
- @.claude/haios/modules/work_engine.py (Bug 2)
- @.claude/haios/epochs/E2_6/EPOCH.md (Bug 3)
- @docs/work/active/WORK-166/WORK.md
- Memory: 84963 (batch pattern), 85573 (stale EPOCH.md), 85712 (already resolved)

---
