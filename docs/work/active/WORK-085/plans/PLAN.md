---
template: implementation_plan
status: approved
date: 2026-02-03
backlog_id: WORK-085
title: Implement Pause Semantics
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-03T22:12:48'
---
# Implementation Plan: Implement Pause Semantics

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

WorkEngine will programmatically recognize pause points per lifecycle (S27 Breath Model), enabling close-work-cycle to accept work closure at pause without warnings or implicit "incomplete" status.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `cycle_runner.py`, `work_engine.py` |
| Lines of code affected | ~50 | New constant + 1 method + integration |
| New files to create | 0 | Adding to existing modules |
| Tests to write | 6 | 5 lifecycle pause tests + 1 integration |
| Dependencies | 2 | close-work-cycle skill, tests/test_cycle_runner.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | WorkEngine + CycleRunner only |
| Risk of regression | Low | Existing 16 tests in test_cycle_runner.py |
| External dependencies | Low | No external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement PAUSE_PHASES | 10 min | High |
| Implement is_at_pause_point | 15 min | High |
| Integration verification | 10 min | High |
| **Total** | ~50 min | High |

---

## Current State vs Desired State

### Current State

```python
# cycle_runner.py:132-141 - CYCLE_PHASES defines phases but no pause mapping
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"],
    # ... other cycles
}
# No PAUSE_PHASES constant exists
# No is_at_pause_point() method exists
```

**Behavior:** close-work-cycle has no programmatic way to know if work is at a valid pause point. It allows `await_operator` but doesn't recognize pause phases.

**Result:** Agent cannot confidently close work at pause points per S27 Breath Model. Pause points are implicit, not explicit.

### Desired State

```python
# cycle_runner.py - New constant mapping lifecycles to pause phases
PAUSE_PHASES: Dict[str, List[str]] = {
    "investigation": ["CONCLUDE"],
    "design": ["COMPLETE"],
    "implementation": ["DONE"],
    "validation": ["REPORT"],
    "triage": ["COMMIT"],
}

# work_engine.py - New method
def is_at_pause_point(self, work_id: str) -> bool:
    """Check if work item is at valid pause point per S27."""
    work = self.get_work(work_id)
    if work is None:
        return False
    lifecycle = self._get_lifecycle_for_work(work)
    pause_phases = PAUSE_PHASES.get(lifecycle, [])
    return work.current_node in pause_phases
```

**Behavior:** WorkEngine can programmatically check if work is at a valid pause point. close-work-cycle can query this before accepting closure.

**Result:** Pause points are recognized as valid completion states (REQ-LIFECYCLE-002). "Complete without spawn" is accepted at pause points.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: PAUSE_PHASES Constant Exists
```python
def test_pause_phases_constant_exists():
    """PAUSE_PHASES constant defines pause phases for all 5 lifecycles."""
    from cycle_runner import PAUSE_PHASES

    assert "investigation" in PAUSE_PHASES
    assert "design" in PAUSE_PHASES
    assert "implementation" in PAUSE_PHASES
    assert "validation" in PAUSE_PHASES
    assert "triage" in PAUSE_PHASES
```

### Test 2: PAUSE_PHASES Maps to Correct Phases
```python
def test_pause_phases_maps_to_exhale_phases():
    """Pause phases match S27 exhale phases (CONCLUDE, COMPLETE, DONE, REPORT, COMMIT)."""
    from cycle_runner import PAUSE_PHASES

    assert "CONCLUDE" in PAUSE_PHASES["investigation"]
    assert "COMPLETE" in PAUSE_PHASES["design"]
    assert "DONE" in PAUSE_PHASES["implementation"]
    assert "REPORT" in PAUSE_PHASES["validation"]
    assert "COMMIT" in PAUSE_PHASES["triage"]
```

### Test 3: WorkEngine is_at_pause_point Returns True at Pause
```python
def test_is_at_pause_point_true_at_conclude(tmp_path):
    """is_at_pause_point returns True when work is at CONCLUDE phase."""
    from work_engine import WorkEngine
    from governance_layer import GovernanceLayer

    # Setup: Create work item at CONCLUDE phase
    engine = WorkEngine(governance=GovernanceLayer(), base_path=tmp_path)
    # ... create work with current_node="CONCLUDE" and type="investigation"

    result = engine.is_at_pause_point("INV-001")
    assert result is True
```

### Test 4: WorkEngine is_at_pause_point Returns False Not at Pause
```python
def test_is_at_pause_point_false_at_explore(tmp_path):
    """is_at_pause_point returns False when work is at EXPLORE phase (inhale, not pause)."""
    from work_engine import WorkEngine
    from governance_layer import GovernanceLayer

    engine = WorkEngine(governance=GovernanceLayer(), base_path=tmp_path)
    # ... create work with current_node="EXPLORE" and type="investigation"

    result = engine.is_at_pause_point("INV-001")
    assert result is False
```

### Test 5: WorkEngine is_at_pause_point Returns False for Unknown Work
```python
def test_is_at_pause_point_false_for_unknown_work(tmp_path):
    """is_at_pause_point returns False when work item doesn't exist."""
    from work_engine import WorkEngine
    from governance_layer import GovernanceLayer

    engine = WorkEngine(governance=GovernanceLayer(), base_path=tmp_path)
    result = engine.is_at_pause_point("NONEXISTENT-001")
    assert result is False
```

### Test 6: Integration - All Lifecycles Have Pause Points
```python
def test_all_lifecycles_have_defined_pause_points():
    """Every lifecycle in PAUSE_PHASES has at least one pause phase defined."""
    from cycle_runner import PAUSE_PHASES

    for lifecycle, phases in PAUSE_PHASES.items():
        assert len(phases) > 0, f"Lifecycle {lifecycle} has no pause phases"
```

### Test 7: Backward Compatibility
```python
def test_existing_cycle_phases_unchanged():
    """CYCLE_PHASES constant unchanged after adding PAUSE_PHASES."""
    from cycle_runner import CYCLE_PHASES

    # Verify existing cycles still have same phases
    assert CYCLE_PHASES["implementation-cycle"] == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]
    assert CYCLE_PHASES["investigation-cycle"] == ["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"]
```

---

## Detailed Design

### Exact Code Change 1: PAUSE_PHASES Constant

**File:** `.claude/haios/modules/cycle_runner.py`
**Location:** After line 141 (after CYCLE_PHASES definition)

**Current Code:**
```python
# cycle_runner.py:132-141
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"],
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}
```

**Changed Code (ADD after CYCLE_PHASES):**
```python
# WORK-085: Pause phases per lifecycle (REQ-LIFECYCLE-002, S27 Breath Model)
# Pause = exhale complete, valid completion state
PAUSE_PHASES: Dict[str, List[str]] = {
    "investigation": ["CONCLUDE"],      # After exhale: findings committed
    "design": ["COMPLETE"],             # After exhale: spec committed
    "implementation": ["DONE"],         # After exhale: artifact committed
    "validation": ["REPORT"],           # After exhale: verdict committed
    "triage": ["COMMIT"],               # After exhale: priorities committed
}
```

### Exact Code Change 2: is_at_pause_point Method

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After line 352 (after get_ready method)

**New Method:**
```python
def is_at_pause_point(self, work_id: str) -> bool:
    """
    Check if work item is at valid pause point per S27 Breath Model.

    Pause points are the exhale-complete phases where work can safely stop
    without being considered incomplete. Per REQ-LIFECYCLE-002.

    Args:
        work_id: Work item ID (e.g., "INV-001", "WORK-085")

    Returns:
        True if work is at pause phase, False otherwise
    """
    work = self.get_work(work_id)
    if work is None:
        return False

    # Import PAUSE_PHASES from cycle_runner
    try:
        from .cycle_runner import PAUSE_PHASES
    except ImportError:
        from cycle_runner import PAUSE_PHASES

    # Map work type to lifecycle
    type_to_lifecycle = {
        "investigation": "investigation",
        "design": "design",
        "feature": "implementation",
        "implementation": "implementation",
        "bug": "implementation",
        "chore": "implementation",
        "spike": "investigation",
        "validation": "validation",
        "triage": "triage",
    }
    lifecycle = type_to_lifecycle.get(work.type, "implementation")

    # Check if current_node is a pause phase for this lifecycle
    pause_phases = PAUSE_PHASES.get(lifecycle, [])
    return work.current_node in pause_phases
```

### Call Chain Context

```
close-work-cycle VALIDATE phase
    |
    +-> WorkEngine.is_at_pause_point(work_id)  # <-- NEW
    |       Imports: PAUSE_PHASES from cycle_runner
    |       Returns: bool
    |
    +-> WorkEngine.get_work(work_id)
            Returns: WorkState
```

### Function/Component Signatures

```python
def is_at_pause_point(self, work_id: str) -> bool:
    """
    Check if work item is at valid pause point per S27 Breath Model.

    Args:
        work_id: Work item ID (e.g., "INV-001", "WORK-085")

    Returns:
        True if work is at pause phase, False otherwise.
        Returns False if work item doesn't exist.

    Raises:
        None - returns False on error for safety
    """
```

### Behavior Logic

**Current Flow:**
```
close-work-cycle VALIDATE → [no pause awareness] → always prompts for spawn
```

**New Flow:**
```
close-work-cycle VALIDATE → is_at_pause_point(work_id)?
                              ├─ True  → "At pause point, closure valid"
                              └─ False → "Not at pause, may need more work"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Location of PAUSE_PHASES | cycle_runner.py | Alongside CYCLE_PHASES for consistency; both are phase constants |
| Location of is_at_pause_point | work_engine.py | WorkEngine owns work state queries; follows get_work, get_ready pattern |
| Return False for unknown work | Defensive | Safe default; unknown work is not at pause |
| Map work.type to lifecycle | type_to_lifecycle dict | Work items use `type` field, lifecycles use different names |
| Fallback lifecycle | "implementation" | Most common case; safe default |
| Import pattern | try/except conditional | Same pattern as existing WorkEngine imports (E2-255) |

### Input/Output Examples

**Example 1: Investigation at CONCLUDE**
```python
# Work item INV-001 with:
#   type: investigation
#   current_node: CONCLUDE

engine.is_at_pause_point("INV-001")
# Returns: True
# Reason: CONCLUDE is in PAUSE_PHASES["investigation"]
```

**Example 2: Feature at DO**
```python
# Work item WORK-085 with:
#   type: feature
#   current_node: DO

engine.is_at_pause_point("WORK-085")
# Returns: False
# Reason: DO is not in PAUSE_PHASES["implementation"] (which has ["DONE"])
```

**Example 3: Nonexistent work**
```python
engine.is_at_pause_point("NONEXISTENT-999")
# Returns: False
# Reason: get_work returns None, defensive return
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Unknown work_id | Return False | Test 5 |
| Unknown work type | Default to "implementation" lifecycle | Implicit in type_to_lifecycle |
| Empty current_node | Not in any pause_phases list → False | Handled by `in` check |
| Lifecycle not in PAUSE_PHASES | Empty list → False | Handled by .get(lifecycle, []) |

### Open Questions

**Q: Should CHAIN phases be considered pause points?**

No. Per S27 Breath Model, CHAIN is transition to next breath, not pause. Pause is the moment after exhale before next inhale. CHAIN is already inhaling.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item frontmatter - none to resolve -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| *None* | - | - | No operator decisions required for this work item |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_cycle_runner.py` in new `TestPauseSemantics` class
- [ ] Add tests to `tests/test_work_engine.py` for `is_at_pause_point`
- [ ] Verify all 7 new tests fail (red)

### Step 2: Add PAUSE_PHASES Constant
- [ ] Add `PAUSE_PHASES` constant to `cycle_runner.py` after `CYCLE_PHASES`
- [ ] Tests 1, 2, 6, 7 pass (green)

### Step 3: Add is_at_pause_point Method
- [ ] Add `is_at_pause_point` method to `WorkEngine` class
- [ ] Import `PAUSE_PHASES` from `cycle_runner`
- [ ] Implement type_to_lifecycle mapping
- [ ] Tests 3, 4, 5 pass (green)

### Step 4: Integration Verification
- [ ] All 7 new tests pass
- [ ] Run full test suite: `pytest tests/test_cycle_runner.py tests/test_work_engine.py -v`
- [ ] Verify existing 16 tests in test_cycle_runner.py still pass (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` - document `is_at_pause_point` method
- [ ] **MUST:** Verify module docstrings reflect new functionality

### Step 6: Consumer Verification
- [ ] Verify close-work-cycle skill documentation references pause semantics
- [ ] Verify CH-002 chapter status reflects implementation complete

**Note:** This is an additive change (new constant + new method). No migrations or renames.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment: S27 phase names vs actual lifecycle phases | Medium | Verified mapping in CH-002 chapter: CONCLUDE/COMPLETE/DONE/REPORT/COMMIT are correct |
| Circular import: work_engine imports cycle_runner | Low | Use same try/except conditional pattern as existing imports |
| Type mapping incomplete | Low | Default to "implementation" lifecycle; covers most cases |
| Regression in existing tests | Low | Run full test suite before/after; 16 existing tests verify no breaks |

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

**MUST** read `docs/work/active/WORK-085/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Define PAUSE_PHASES constant | [ ] | Grep for PAUSE_PHASES in cycle_runner.py |
| Implement WorkEngine.is_at_pause_point() | [ ] | Grep for is_at_pause_point in work_engine.py |
| Update close-work-cycle to accept pause closure | [ ] | Skill uses is_at_pause_point (doc update) |
| Unit tests for pause recognition | [ ] | test_pause_phases_* tests pass |
| Integration test: Investigation CONCLUDE → close | [ ] | test_is_at_pause_point_true_at_conclude passes |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cycle_runner.py` | PAUSE_PHASES constant exists | [ ] | |
| `.claude/haios/modules/work_engine.py` | is_at_pause_point method exists | [ ] | |
| `tests/test_cycle_runner.py` | TestPauseSemantics class with tests | [ ] | |
| `.claude/haios/modules/README.md` | Documents is_at_pause_point | [ ] | |

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

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-002-PauseSemantics.md (chapter specification)
- @.claude/haios/epochs/E2_4/architecture/S27-breath-model.md (breath model source)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-002)
- @docs/work/active/WORK-085/WORK.md (work item)
- Memory: 83289 - "S27 Breath Model applies: each lifecycle is inhale→exhale→pause, pause is valid completion"

---
