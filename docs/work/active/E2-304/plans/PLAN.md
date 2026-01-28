---
template: implementation_plan
status: complete
date: 2026-01-28
backlog_id: E2-304
title: Add Status-Aware ID Validation to Work Creation
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-28T21:30:19'
---
# Implementation Plan: Add Status-Aware ID Validation to Work Creation

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

Work item creation (`create_work()` and `scaffold_template()`) will reject IDs that already exist with terminal status (complete/archived), preventing accidental overwrite of completed work items.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/haios/modules/work_engine.py`, `.claude/haios/lib/scaffold.py` |
| Lines of code affected | ~30 | Add validation function + calls |
| New files to create | 0 | Tests added to existing test files |
| Tests to write | 4 | 2 positive, 2 negative cases |
| Dependencies | 2 | `justfile` (work recipe), `cli.py` (scaffold command) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Just 2 files, both already have tests |
| Risk of regression | Low | Adding validation, not changing existing paths |
| External dependencies | Low | No external APIs, pure file system checks |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement validation in work_engine.py | 15 min | High |
| Implement validation in scaffold.py | 10 min | High |
| Integration verification | 10 min | High |
| **Total** | ~50 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/work_engine.py:189-211
def create_work(
    self,
    id: str,
    title: str,
    milestone: Optional[str] = None,
    priority: str = "medium",
    category: str = "implementation",
) -> Path:
    work_dir = self.active_dir / id
    work_dir.mkdir(parents=True, exist_ok=True)  # <- NO VALIDATION
    # ... creates WORK.md
```

**Behavior:** `create_work()` creates directory with `exist_ok=True`, silently succeeding if directory exists regardless of status.

**Result:** Completed work items can be overwritten by new work items with same ID, causing data loss (INV-072).

### Desired State

```python
# .claude/haios/modules/work_engine.py:189-211
def create_work(
    self,
    id: str,
    title: str,
    ...
) -> Path:
    # NEW: Validate ID is available
    self._validate_id_available(id)  # Raises if terminal status

    work_dir = self.active_dir / id
    work_dir.mkdir(parents=True, exist_ok=True)
    # ... creates WORK.md
```

**Behavior:** `create_work()` validates ID availability before creating. Rejects IDs with terminal status (complete/archived).

**Result:** Completed work items are protected from accidental overwrite.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Create Work with Complete Status Raises Error
```python
def test_create_work_rejects_complete_status(engine, setup_work_item):
    """create_work should reject IDs with status=complete."""
    # Setup: Create work item with status=complete
    setup_work_item("E2-COMPLETE", status="complete")

    # Action + Assert: Should raise WorkIDUnavailableError
    with pytest.raises(WorkIDUnavailableError) as exc:
        engine.create_work("E2-COMPLETE", "New Title")
    assert "already exists with status 'complete'" in str(exc.value)
```

### Test 2: Create Work with Archived Status Raises Error
```python
def test_create_work_rejects_archived_status(engine, setup_work_item):
    """create_work should reject IDs with status=archived."""
    setup_work_item("E2-ARCHIVED", status="archived")

    with pytest.raises(WorkIDUnavailableError) as exc:
        engine.create_work("E2-ARCHIVED", "New Title")
    assert "already exists with status 'archived'" in str(exc.value)
```

### Test 3: Create Work with Active Status Succeeds (Backward Compat)
```python
def test_create_work_allows_active_status(engine, setup_work_item):
    """create_work should allow overwriting active items (backward compat)."""
    setup_work_item("E2-ACTIVE", status="active")

    # Should succeed - overwriting active items is intentional
    result = engine.create_work("E2-ACTIVE", "Updated Title")
    assert result.exists()
```

### Test 4: Create Work with New ID Succeeds
```python
def test_create_work_new_id_succeeds(engine):
    """create_work should succeed for new IDs."""
    result = engine.create_work("E2-NEW", "New Work Item")
    assert result.exists()
    assert "WORK.md" in str(result)
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

<!-- REQUIRED: Show the actual code, not pseudocode -->

#### Change 1: Add Exception Class to work_engine.py

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After line 77 (after WorkNotFoundError)

**Added Code:**
```python
class WorkIDUnavailableError(Exception):
    """Raised when work item ID exists with terminal status."""
    pass
```

#### Change 2: Add Validation Method to WorkEngine

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After line 188 (before create_work)

**Added Code:**
```python
def _validate_id_available(self, id: str) -> None:
    """
    Validate that work ID is available for creation.

    Raises WorkIDUnavailableError if ID exists with terminal status.
    Allows overwriting active/draft items for backward compatibility.

    Args:
        id: Work item ID to validate

    Raises:
        WorkIDUnavailableError: If ID exists with status complete/archived
    """
    TERMINAL_STATUSES = {"complete", "archived"}

    work = self.get_work(id)
    if work is None:
        return  # ID available

    if work.status in TERMINAL_STATUSES:
        raise WorkIDUnavailableError(
            f"Work item {id} already exists with status '{work.status}'. "
            "Use a different ID."
        )
    # Allow overwriting active items (backward compat)
```

#### Change 3: Call Validation in create_work

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Line 210 (first line of create_work body)

**Current Code:**
```python
def create_work(
    self,
    id: str,
    ...
) -> Path:
    work_dir = self.active_dir / id
```

**Changed Code:**
```python
def create_work(
    self,
    id: str,
    ...
) -> Path:
    # REQ-VALID-001: Validate ID availability against terminal statuses
    self._validate_id_available(id)

    work_dir = self.active_dir / id
```

#### Change 4: Add Validation to scaffold.py

**File:** `.claude/haios/lib/scaffold.py`
**Location:** Line 444 (inside scaffold_template, after work_file_required check)

**Current Code:**
```python
# Check work file prerequisite for gated templates (E2-160)
if template in WORK_FILE_REQUIRED_TEMPLATES and backlog_id:
    if not _work_file_exists(backlog_id):
        raise ValueError(
            f"Work file required. Run '/new-work {backlog_id} \"{title}\"' first."
        )
```

**Added Code (after):**
```python
# REQ-VALID-001: Block scaffold for work_item if ID has terminal status
if template == "work_item" and backlog_id:
    existing_status = _get_work_status(backlog_id)
    if existing_status in ("complete", "archived"):
        raise ValueError(
            f"Work item {backlog_id} already exists with status '{existing_status}'. "
            "Use a different ID."
        )
```

**Also add helper function:**
```python
def _get_work_status(backlog_id: str) -> Optional[str]:
    """Get status of existing work item, or None if doesn't exist."""
    import yaml
    work_path = PROJECT_ROOT / "docs" / "work" / "active" / backlog_id / "WORK.md"
    if not work_path.exists():
        return None
    try:
        content = work_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            return fm.get("status")
    except Exception:
        pass
    return None
```

### Call Chain Context

<!-- Show where this code fits in the larger system -->

```
User: just work E2-294 "New Work"
    |
    +-> justfile: scaffold work_item ...
        |
        +-> cli.py: scaffold(...)
            |
            +-> scaffold.py: scaffold_template(...)
                    |
                    +-> _get_work_status(id)  # <-- NEW CHECK
                    |       Returns: Optional[str] status
                    |
                    +-> Creates WORK.md (only if validation passes)

User: python (programmatic)
    |
    +-> WorkEngine.create_work(id, title)
            |
            +-> _validate_id_available(id)  # <-- NEW CHECK
            |       Raises: WorkIDUnavailableError
            |
            +-> Creates directory + WORK.md (only if validation passes)
```

### Function/Component Signatures

```python
# work_engine.py - NEW
def _validate_id_available(self, id: str) -> None:
    """
    Validate that work ID is available for creation.

    Args:
        id: Work item ID to validate

    Raises:
        WorkIDUnavailableError: If ID exists with status complete/archived
    """

# scaffold.py - NEW
def _get_work_status(backlog_id: str) -> Optional[str]:
    """
    Get status of existing work item.

    Args:
        backlog_id: Work item ID to check

    Returns:
        Status string if exists, None otherwise
    """
```

### Behavior Logic

<!-- Use flowchart showing CURRENT (buggy) vs FIXED behavior -->

**Current Flow (buggy):**
```
create_work(id="E2-294") → mkdir(exist_ok=True) → Write WORK.md → OVERWRITES COMPLETED WORK
```

**Fixed Flow:**
```
create_work(id="E2-294") → _validate_id_available(id)
                                   |
                                   +-> get_work(id) returns WorkState
                                   |
                                   +-> status == "complete"?
                                         ├─ YES → RAISE WorkIDUnavailableError
                                         └─ NO  → Continue creation
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Validation vs location change | Add validation, keep ADR-041 | Moving files breaks references; validation is non-breaking |
| Block for terminal, allow for active | Different handling by status | Complete items should never be overwritten; active items might be intentional edits |
| Check in both work_engine and scaffold | Defense in depth | Multiple entry points to work creation (programmatic vs CLI) |
| New exception class | WorkIDUnavailableError | Clear error type, distinct from WorkNotFoundError |

### Input/Output Examples

<!-- REQUIRED: Use REAL data from the system, not hypothetical examples -->

**Before Fix (with real data):**
```
Run 1: create_work(id="E2-294", title="New Work")
  E2-294 exists with status="complete" (Session 196 work)
  Returns: Path to WORK.md (silently overwrites!)
  Problem: Completed work item E2-294 is lost
```

**After Fix (expected):**
```
Run 1: create_work(id="E2-294", title="New Work")
  E2-294 exists with status="complete"
  Raises: WorkIDUnavailableError("Work item E2-294 already exists with status 'complete'. Use a different ID.")
  Improvement: Agent must choose different ID, completed work protected
```

**Real Example with Current Data:**
```
Current system state:
  - E2-294: status=complete (Session 196)
  - E2-305: status=complete (Session 252)

After fix:
  - create_work("E2-294", ...) → BLOCKED
  - create_work("E2-305", ...) → BLOCKED
  - create_work("E2-306", ...) → ALLOWED (new ID)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| ID doesn't exist | Allow creation | Test 4 |
| ID exists with status=active | Allow (backward compat) | Test 3 |
| ID exists with status=complete | Block | Test 1 |
| ID exists with status=archived | Block | Test 2 |
| ID in archive directory | get_work finds it, status checked | Implicit in Test 1/2 |

### Open Questions

<!-- Surface any uncertainties discovered during design -->

**Q: Should we also check the archive directory?**

Answer: Yes. `get_work()` already checks both active/ and archive/ directories (work_engine.py:577-588). So archived items will be found and validated.

**Q: What about items with status=draft or status=backlog?**

Answer: Allow overwriting. Only terminal statuses (complete, archived) should block. This matches INV-072 design outputs.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No open decisions | - | - | Work item had no operator_decisions field |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add `WorkIDUnavailableError` import to test_work_engine.py
- [ ] Add test fixtures for complete/archived status
- [ ] Add 4 tests as defined in Tests First section
- [ ] Verify all 4 tests fail (red)

### Step 2: Add Exception Class and Validation Method
- [ ] Add `WorkIDUnavailableError` class after `WorkNotFoundError` in work_engine.py
- [ ] Add `_validate_id_available()` method before `create_work()`
- [ ] Tests 1, 2 now pass (complete/archived rejection)

### Step 3: Call Validation in create_work
- [ ] Add `self._validate_id_available(id)` as first line in `create_work()`
- [ ] Tests 3, 4 pass (active allowed, new allowed)

### Step 4: Add Validation to scaffold.py
- [ ] Add `_get_work_status()` helper function
- [ ] Add validation check in `scaffold_template()` for work_item template
- [ ] Manual test: `just work E2-294 "Test"` should fail

### Step 5: Integration Verification
- [ ] Run `pytest tests/test_work_engine.py -v`
- [ ] Run `pytest tests/test_lib_scaffold.py -v`
- [ ] Run full test suite `pytest tests/ -v --tb=short`

### Step 6: README Sync (MUST)
- [ ] **MUST:** modules/README.md - Document new exception class
- [ ] No other README changes needed (existing files modified, no new files)

### Step 7: Consumer Verification
- [ ] Not a migration - no stale references to check
- [ ] Verify error message is clear for agent troubleshooting

> **Anti-pattern prevented:** "Ceremonial Completion" - code migrated but consumers still reference old location (see epistemic_state.md)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment: INV-072 design says "warn for active" but we chose "allow" | Low | Design explicitly said "allow with warning" could be "just allow" for simplicity. Revisit if needed. |
| Integration: Existing scripts calling create_work() | Low | We're adding validation, not changing signature. Old code still works. |
| Regression: Tests for create_work() might expect different behavior | Low | Existing tests don't cover terminal status scenario. New tests are additive. |
| Scope creep: Should we add --force flag? | Low | Out of scope per INV-072. Can add later if needed. |

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

**MUST** read `docs/work/active/E2-304/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Add `_validate_id_available(id: str) -> None` to work_engine.py | [x] | Line 195 in work_engine.py |
| Function checks if WORK.md exists AND status is complete/archived | [x] | Lines 208-214, TERMINAL_STATUSES set |
| Raise error if ID exists with terminal status | [x] | Lines 215-218, WorkIDUnavailableError |
| Add same check to scaffold.py `scaffold_template()` for work_item template | [x] | Lines 478-485 in scaffold.py |
| Tests for validation logic (positive and negative cases) | [x] | 4 tests pass (pytest output above) |
| Runtime consumer: `create_work()` calls validation before creating | [x] | Line 246 in work_engine.py |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | WorkIDUnavailableError + _validate_id_available() + call in create_work() | [x] | Lines 80, 195, 246 |
| `.claude/haios/lib/scaffold.py` | _get_work_status() + validation check in scaffold_template() | [x] | Lines 142, 478 |
| `tests/test_work_engine.py` | 4 new tests for ID validation | [x] | Lines 943-984 |
| `.claude/haios/modules/README.md` | Documents WorkIDUnavailableError | [x] | Exception Classes section added |

**Verification Commands:**
```bash
# Actual output from Session 253:
pytest tests/test_work_engine.py -v -k "create_work_rejects or create_work_allows or create_work_new"
# 4 passed, 27 deselected in 0.28s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Grep confirmed all additions |
| Test output pasted above? | Yes | 4 passed |
| Any deviations from plan? | Minor | Return type None instead of bool (correct per INV-072) |

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

- @docs/work/active/INV-072/investigations/001-spawn-id-collision-completed-work-items-reused.md (source investigation)
- @.claude/haios/modules/work_engine.py (primary implementation target)
- @.claude/haios/lib/scaffold.py (secondary implementation target)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-VALID-001)

---
