---
template: implementation_plan
status: complete
date: 2026-01-17
backlog_id: E2-298
title: Consumer Migration to WorkEngine
author: Hephaestus
lifecycle_phase: plan
session: 201
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-17T16:01:27'
---
# Implementation Plan: Consumer Migration to WorkEngine

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

Migrate test files from the deprecated `work_item.py` module to use `WorkEngine`, completing the strangler fig pattern and enabling safe deprecation of the old module.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | `tests/test_work_item.py`, `tests/test_close_work_item.py`, `.claude/lib/work_item.py` |
| Lines of code affected | ~421 | `wc -l`: test_work_item.py (294) + test_close_work_item.py (127) |
| New files to create | 0 | Migration only - no new files |
| Tests to write | 0 | Existing tests migrate, not new tests |
| Dependencies | 0 | No other modules import work_item.py at runtime |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Test files only, no runtime code |
| Risk of regression | Low | Tests already covered in test_work_engine.py (723 lines) |
| External dependencies | Low | No external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Analyze test coverage overlap | 15 min | High |
| Migrate test_work_item.py | 30 min | High |
| Migrate test_close_work_item.py | 20 min | High |
| Add deprecation notice | 5 min | High |
| Verify and run tests | 10 min | High |
| **Total** | 80 min | High |

---

## Current State vs Desired State

### Current State

```python
# tests/test_work_item.py:135 - Imports from deprecated work_item.py
from work_item import find_work_file, ACTIVE_DIR

# tests/test_close_work_item.py:27 - Same deprecated imports
from work_item import find_work_file, ACTIVE_DIR
```

**Behavior:** Test files import functions from `.claude/lib/work_item.py` which duplicates functionality now in `WorkEngine`.

**Result:** Two parallel implementations exist. Deprecating work_item.py is blocked because tests still import it. WorkEngine is the canonical implementation but can't be sole owner.

### Desired State

```python
# tests/test_work_item.py - Uses WorkEngine directly
from work_engine import WorkEngine
from governance_layer import GovernanceLayer

engine = WorkEngine(governance=GovernanceLayer(), base_path=tmp_path)
result = engine.get_work("E2-TEST")  # Replaces find_work_file()
```

**Behavior:** Test files import from `WorkEngine` module in `.claude/haios/modules/`. Tests validate WorkEngine functionality directly, not the deprecated module.

**Result:** `work_item.py` can be marked deprecated with clear notice. WorkEngine is sole owner of work file operations. Clean architecture with single source of truth.

---

## Tests First (TDD)

<!-- This is a migration task. Existing tests in test_work_engine.py already cover WorkEngine.
     The goal is to verify the migration doesn't break existing coverage. -->

### Test 1: Verify WorkEngine Tests Pass
```python
# tests/test_work_engine.py already has comprehensive coverage (723 lines)
# Run: pytest tests/test_work_engine.py -v
# Expected: All 20+ tests pass
```

### Test 2: Verify Migrated Tests Pass
```python
# After migration, run full test suite
# Run: pytest tests/ -v
# Expected: All tests pass, no import errors from work_item.py
```

### Test 3: Verify Deprecation Warning (Manual)
```python
# After adding deprecation notice, importing work_item.py should show warning
# This is a documentation notice, not runtime warning (avoid breaking hooks)
```

**Note:** This is a migration task, not new feature. The tests already exist in `test_work_engine.py`. The migration verifies coverage is maintained, not added.

---

## Detailed Design

### Migration Strategy: Analyze and Merge

The test files have overlapping coverage with `test_work_engine.py`. Strategy:
1. **Keep unique tests** - Tests for infrastructure (validate.py, scaffold.py, status.py) stay
2. **Remove duplicates** - Tests duplicated in test_work_engine.py are removed
3. **Redirect imports** - Tests that test work_item.py functions use WorkEngine equivalents

### Analysis: test_work_item.py Coverage

| Test Class | Tests | Verdict |
|------------|-------|---------|
| `TestWorkItemValidation` | 2 tests | **KEEP** - Tests validate.py registry, not work_item.py |
| `TestWorkItemScaffold` | 2 tests | **KEEP** - Tests scaffold.py paths, not work_item.py |
| `TestWorkItemStatus` | 2 tests | **KEEP** - Tests status.py scanning, not work_item.py |
| `TestWorkDirectoryStructure` | 5 tests | **MIGRATE** - Tests directory patterns using work_item.py imports |
| `TestNodeTransitions` | 4 tests | **DUPLICATE** - Already in test_work_engine.py (transition tests) |

### Analysis: test_close_work_item.py Coverage

| Test Class | Tests | Verdict |
|------------|-------|---------|
| `TestFindWorkFile` | 2 tests | **DUPLICATE** - test_work_engine.py has `test_get_work_*` |
| `TestUpdateWorkFileStatus` | 1 test | **DUPLICATE** - test_work_engine.py has transition/close tests |
| `TestMoveWorkFileToArchive` | 1 test | **DUPLICATE** - test_work_engine.py has `test_archive_*` |

### Exact Code Changes

**File 1:** `tests/test_work_item.py`

**Lines 133-171:** Remove tests that import `work_item.find_work_file`

```diff
- class TestWorkDirectoryStructure:
-     """Tests for E2-212: Work directory structure migration."""
-
-     def test_find_work_file_resolves_directory(self, tmp_path):
-         """find_work_file finds WORK.md in directory structure."""
-         from work_item import find_work_file, ACTIVE_DIR
-         # ... test body removed - covered by test_work_engine.py
```

**Lines 219-294:** Remove `TestNodeTransitions` class - all tests covered in test_work_engine.py

```diff
- class TestNodeTransitions:
-     """Tests for E2-162: Node transition functions."""
-     # ... all tests removed - covered by test_work_engine.py
```

**File 2:** `tests/test_close_work_item.py`

**Entire file:** Remove - all functionality covered by test_work_engine.py

```diff
- # tests/test_close_work_item.py - REMOVE ENTIRE FILE
- # All tests duplicated in test_work_engine.py:
- # - TestFindWorkFile -> test_get_work_*
- # - TestUpdateWorkFileStatus -> test_transition_*
- # - TestMoveWorkFileToArchive -> test_archive_*
```

**File 3:** `.claude/lib/work_item.py`

**Lines 1-10:** Add deprecation notice

```python
# generated: 2025-12-23
# System Auto: last updated on: 2026-01-17
"""
DEPRECATED: This module is deprecated as of E2-298 (Session 201).
Use WorkEngine from .claude/haios/modules/work_engine.py instead.

Migration guide:
- find_work_file(id) -> engine.get_work(id).path
- update_work_file_status(path, status) -> engine.transition(id, node)
- update_node(path, node) -> engine.transition(id, node)
- add_document_link(path, type, path) -> engine.add_document_link(id, type, path)

This module remains for backward compatibility with hooks that import it.
"""
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delete vs deprecate test files | Delete `test_close_work_item.py`, modify `test_work_item.py` | test_close_work_item.py is 100% duplicate; test_work_item.py has non-duplicate tests |
| Keep work_item.py | Add deprecation notice, don't delete | Hooks (post_tool_use.py, pre_tool_use.py) still import node_cycle.py which may reference work_item.py patterns |
| Deprecation type | Documentation notice, not runtime warning | Runtime warnings would spam hooks; documentation guides future migration |

### Function Mapping (work_item.py → WorkEngine)

| work_item.py | WorkEngine | Notes |
|--------------|------------|-------|
| `find_work_file(id)` | `engine.get_work(id).path` | Returns WorkState with .path attribute |
| `update_work_file_status(path, status)` | `engine.close(id)` or `engine.transition()` | WorkEngine owns status changes |
| `update_work_file_closed_date(path, date)` | Handled by `engine.close(id)` | Bundled in close() |
| `move_work_file_to_archive(path)` | `engine.archive(id)` | Preserves directory structure |
| `update_node(path, node)` | `engine.transition(id, node)` | Validates via GovernanceLayer |
| `add_document_link(path, type, path)` | `engine.add_document_link(id, type, path)` | Identical API |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Hooks still using work_item.py | Keep module, add deprecation notice | Manual verification |
| node_cycle.py imports | Unaffected - different module | N/A |
| Archive directory patterns | WorkEngine handles both flat and directory | test_work_engine.py |

### Open Questions

**Q: Should we add a DeprecationWarning at import time?**

No - hooks import this module on every tool use. Runtime warnings would create noise. Documentation notice is sufficient.

---

## Open Decisions (MUST resolve before implementation)

No open decisions. Work item `operator_decisions` field is empty.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | N/A | N/A | No decisions required |

---

## Implementation Steps

### Step 1: Verify Baseline
- [ ] Run `pytest tests/test_work_engine.py -v` - all tests pass
- [ ] Note test count for comparison

### Step 2: Delete test_close_work_item.py
- [ ] Delete `tests/test_close_work_item.py` (100% duplicate coverage)
- [ ] Run `pytest tests/` - no import errors

### Step 3: Modify test_work_item.py
- [ ] Remove `TestWorkDirectoryStructure.test_find_work_file_resolves_directory` (lines 133-153)
- [ ] Remove `TestWorkDirectoryStructure.test_find_work_file_falls_back_to_flat` (lines 155-172)
- [ ] Remove `TestNodeTransitions` class entirely (lines 219-294)
- [ ] Keep `TestWorkItemValidation`, `TestWorkItemScaffold`, `TestWorkItemStatus` - these test other modules

### Step 4: Add Deprecation Notice to work_item.py
- [ ] Add deprecation docstring at top of `.claude/lib/work_item.py`
- [ ] Include migration guide in docstring

### Step 5: Verify Migration Complete
- [ ] Run `pytest tests/` - all tests pass
- [ ] Run `Grep(pattern="from work_item import", path="tests/")` - no results
- [ ] Run `Grep(pattern="from work_item import", path=".claude/", glob="**/*.py")` - only hooks allowed

### Step 6: README Sync
- [ ] **MUST:** Update `.claude/lib/README.md` to note work_item.py deprecation
- [ ] **MUST:** Verify tests/README.md (if exists) reflects test file changes

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hooks break after work_item.py changes | Low | Only adding deprecation docstring, not modifying functionality |
| Lost test coverage | Low | Analysis shows all removed tests are duplicates in test_work_engine.py |
| Import errors in test files | Low | Verify imports after each modification; rollback if needed |
| Spec misalignment | Low | This is cleanup work following E2-242 implementation, not new spec work |

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

**MUST** read `docs/work/active/E2-298/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Migrate test_work_item.py to test WorkEngine methods | [ ] | Removed work_item imports, kept non-duplicate tests |
| Migrate test_close_work_item.py to test WorkEngine methods | [ ] | File deleted - 100% coverage in test_work_engine.py |
| Add deprecation notice to work_item.py header | [ ] | Docstring added with migration guide |
| Verify no runtime (non-test) imports from work_item.py | [ ] | Grep shows only test files imported (now removed) |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `tests/test_work_item.py` | Duplicate tests removed, ~180 lines remain | [ ] | |
| `tests/test_close_work_item.py` | File deleted | [ ] | |
| `.claude/lib/work_item.py` | Deprecation notice in docstring | [ ] | |
| `.claude/lib/README.md` | **MUST:** Notes work_item.py deprecation | [ ] | |
| `Grep: from work_item import` in tests/ | **MUST:** Zero results | [ ] | |

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

- @docs/work/archive/E2-242/WORK.md (WorkEngine implementation)
- @docs/work/archive/E2-242/observations.md (source of migration observation)
- @.claude/haios/modules/work_engine.py (canonical implementation)
- @.claude/lib/work_item.py (deprecated module)
- @tests/test_work_engine.py (target test file with full coverage)

---
