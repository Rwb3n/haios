---
template: implementation_plan
status: complete
date: 2026-02-03
backlog_id: WORK-084
title: Implement Lifecycle Signatures
author: Hephaestus
lifecycle_phase: plan
session: 301
version: '1.5'
generated: 2026-02-03
last_updated: '2026-02-03T21:51:23'
---
# Implementation Plan: Implement Lifecycle Signatures

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

CycleRunner will return typed LifecycleOutput objects from a new `run()` method, enabling lifecycles to be pure functions with explicit Input → Output signatures that do not auto-chain to subsequent lifecycles.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/modules/cycle_runner.py` |
| Lines of code affected | ~220 (add ~60-80) | `wc -l` on cycle_runner.py |
| New files to create | 0 | Types added to existing module |
| Tests to write | 6 | 6 new tests for LifecycleOutput types and run() |
| Dependencies | 0 | cycle_runner.py has no downstream importers currently |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | CycleRunner is currently thin validator, no runtime consumers |
| Risk of regression | Low | Existing 10 tests in test_cycle_runner.py, adding new method |
| External dependencies | Low | No external APIs, pure Python dataclasses |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 20 min | High |
| Define dataclasses | 15 min | High |
| Implement run() | 25 min | Medium |
| Integration test | 15 min | Medium |
| **Total** | ~75 min | High |

---

## Current State vs Desired State

### Current State

```python
# cycle_runner.py:56-64 - CycleResult dataclass
@dataclass
class CycleResult:
    """Result of a cycle validation or execution."""
    cycle_id: str
    final_phase: str
    outcome: Literal["completed", "blocked", "chain"]
    gate_results: List[GateResult] = field(default_factory=list)
    next_cycle: Optional[str] = None

# cycle_runner.py:113-123 - get_cycle_phases (only lookup, no run)
def get_cycle_phases(self, cycle_id: str) -> List[str]:
    """Return ordered phases for a cycle."""
    return CYCLE_PHASES.get(cycle_id, [])
```

**Behavior:** CycleRunner validates gates and returns phase sequences. No `run()` method exists. Skills are interpreted by Claude from markdown. No typed output objects for lifecycle results.

**Result:** Lifecycles have implicit chaining via CHAIN phases in skill markdown. No programmatic way to get typed outputs from lifecycle completion.

### Desired State

```python
# cycle_runner.py - New LifecycleOutput types
@dataclass
class LifecycleOutput:
    """Base class for all lifecycle outputs."""
    lifecycle: str
    work_id: str
    timestamp: datetime
    status: Literal["success", "failure", "partial"]

@dataclass
class Findings(LifecycleOutput):
    """Output from Investigation lifecycle."""
    question: str
    conclusions: List[str]
    evidence: List[str]
    open_questions: List[str]

@dataclass
class Specification(LifecycleOutput):
    """Output from Design lifecycle."""
    requirements: List[str]
    design_decisions: List[str]
    interfaces: Dict[str, Any]

# cycle_runner.py - New run() method
def run(self, work_id: str, lifecycle: str) -> LifecycleOutput:
    """
    Execute lifecycle and return typed output. Does NOT auto-chain.

    Returns:
        Typed LifecycleOutput subclass based on lifecycle type.
    """
```

**Behavior:** CycleRunner provides `run()` method that returns typed outputs. Caller decides whether to chain to next lifecycle.

**Result:** Lifecycles are pure functions with explicit Input → Output. No implicit side effects.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: LifecycleOutput Base Dataclass
```python
def test_lifecycle_output_base_dataclass():
    """LifecycleOutput has required fields."""
    from cycle_runner import LifecycleOutput
    from datetime import datetime

    output = LifecycleOutput(
        lifecycle="investigation",
        work_id="INV-001",
        timestamp=datetime.now(),
        status="success"
    )
    assert output.lifecycle == "investigation"
    assert output.work_id == "INV-001"
    assert output.status == "success"
```

### Test 2: Findings Output Type
```python
def test_findings_output_type():
    """Findings extends LifecycleOutput with investigation-specific fields."""
    from cycle_runner import Findings
    from datetime import datetime

    findings = Findings(
        lifecycle="investigation",
        work_id="INV-001",
        timestamp=datetime.now(),
        status="success",
        question="What causes the bug?",
        conclusions=["Root cause is X"],
        evidence=["Log file shows Y"],
        open_questions=[]
    )
    assert findings.question == "What causes the bug?"
    assert len(findings.conclusions) == 1
```

### Test 3: Specification Output Type
```python
def test_specification_output_type():
    """Specification extends LifecycleOutput with design-specific fields."""
    from cycle_runner import Specification
    from datetime import datetime

    spec = Specification(
        lifecycle="design",
        work_id="WORK-084",
        timestamp=datetime.now(),
        status="success",
        requirements=["REQ-LIFECYCLE-001"],
        design_decisions=["Use dataclasses"],
        interfaces={"run": "work_id, lifecycle -> LifecycleOutput"}
    )
    assert "REQ-LIFECYCLE-001" in spec.requirements
    assert "run" in spec.interfaces
```

### Test 4: Run Method Returns Typed Output
```python
def test_run_returns_lifecycle_output():
    """CycleRunner.run() returns LifecycleOutput subclass."""
    from cycle_runner import CycleRunner, LifecycleOutput
    from governance_layer import GovernanceLayer

    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    output = runner.run(work_id="WORK-084", lifecycle="design")
    assert isinstance(output, LifecycleOutput)
    assert output.work_id == "WORK-084"
    assert output.lifecycle == "design"
```

### Test 5: Run Does Not Auto-Chain (Pure Function)
```python
def test_run_does_not_auto_chain():
    """CycleRunner.run() returns output, does NOT trigger next lifecycle."""
    from cycle_runner import CycleRunner
    from governance_layer import GovernanceLayer
    from unittest.mock import patch

    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)

    # Mock any chaining mechanism
    with patch.object(runner, '_emit_phase_entered') as mock_emit:
        output = runner.run(work_id="WORK-084", lifecycle="design")
        # Should emit for current lifecycle phases only, not next lifecycle
        # Specifically, should NOT emit for "implementation" phases
        for call in mock_emit.call_args_list:
            assert "implementation" not in str(call)
```

### Test 6: Backward Compatibility
```python
def test_existing_get_cycle_phases_unchanged():
    """Existing get_cycle_phases behavior unchanged after adding run()."""
    from cycle_runner import CycleRunner
    from governance_layer import GovernanceLayer

    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    phases = runner.get_cycle_phases("implementation-cycle")
    assert phases == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/cycle_runner.py`
**Location:** After line 64 (after CycleResult dataclass), add new dataclasses

**Current Code:**
```python
# cycle_runner.py:56-64 - Only CycleResult exists
@dataclass
class CycleResult:
    """Result of a cycle validation or execution."""
    cycle_id: str
    final_phase: str
    outcome: Literal["completed", "blocked", "chain"]
    gate_results: List[GateResult] = field(default_factory=list)
    next_cycle: Optional[str] = None
```

**Changed Code (additions after CycleResult):**
```python
# cycle_runner.py:66+ - NEW LifecycleOutput types
from datetime import datetime

@dataclass
class LifecycleOutput:
    """Base class for all lifecycle outputs (REQ-LIFECYCLE-001)."""
    lifecycle: str
    work_id: str
    timestamp: datetime
    status: Literal["success", "failure", "partial"]

@dataclass
class Findings(LifecycleOutput):
    """Output from Investigation lifecycle: Question → Findings."""
    question: str
    conclusions: List[str]
    evidence: List[str]
    open_questions: List[str]

@dataclass
class Specification(LifecycleOutput):
    """Output from Design lifecycle: Requirements → Specification."""
    requirements: List[str]
    design_decisions: List[str]
    interfaces: Dict[str, Any]

@dataclass
class Artifact(LifecycleOutput):
    """Output from Implementation lifecycle: Specification → Artifact."""
    files_created: List[str]
    files_modified: List[str]
    tests_passed: bool

@dataclass
class Verdict(LifecycleOutput):
    """Output from Validation lifecycle: Artifact × Spec → Verdict."""
    passed: bool
    failures: List[str]
    warnings: List[str]

@dataclass
class PriorityList(LifecycleOutput):
    """Output from Triage lifecycle: [Items] → [PrioritizedItems]."""
    items: List[str]
    ranking_criteria: str
```

**New Method (add to CycleRunner class after line 220):**
```python
# cycle_runner.py:222+ - NEW run() method
def run(self, work_id: str, lifecycle: str) -> LifecycleOutput:
    """
    Execute lifecycle and return typed output. Does NOT auto-chain.

    This implements REQ-LIFECYCLE-001: Lifecycles are pure functions.
    Caller decides whether to chain to next lifecycle.

    Args:
        work_id: Work item ID (e.g., "WORK-084")
        lifecycle: Lifecycle name ("investigation", "design", "implementation", "validation", "triage")

    Returns:
        Typed LifecycleOutput subclass based on lifecycle type.
        - investigation → Findings
        - design → Specification
        - implementation → Artifact
        - validation → Verdict
        - triage → PriorityList

    Note:
        MVP implementation returns base LifecycleOutput with lifecycle/work_id.
        Full typed output population requires integration with skill execution.
    """
    from datetime import datetime

    # Map lifecycle to output type
    output_types = {
        "investigation": Findings,
        "design": Specification,
        "implementation": Artifact,
        "validation": Verdict,
        "triage": PriorityList,
    }

    # Get output type or default to base
    output_class = output_types.get(lifecycle, LifecycleOutput)

    # Emit phase entered for observability
    self._emit_phase_entered(lifecycle, "RUN", work_id)

    # MVP: Return output with basic fields populated
    # Full implementation: populate from skill execution results
    if output_class == LifecycleOutput:
        return LifecycleOutput(
            lifecycle=lifecycle,
            work_id=work_id,
            timestamp=datetime.now(),
            status="success"
        )

    # For typed outputs, provide default values for required fields
    if output_class == Findings:
        return Findings(
            lifecycle=lifecycle, work_id=work_id, timestamp=datetime.now(), status="success",
            question="", conclusions=[], evidence=[], open_questions=[]
        )
    elif output_class == Specification:
        return Specification(
            lifecycle=lifecycle, work_id=work_id, timestamp=datetime.now(), status="success",
            requirements=[], design_decisions=[], interfaces={}
        )
    elif output_class == Artifact:
        return Artifact(
            lifecycle=lifecycle, work_id=work_id, timestamp=datetime.now(), status="success",
            files_created=[], files_modified=[], tests_passed=False
        )
    elif output_class == Verdict:
        return Verdict(
            lifecycle=lifecycle, work_id=work_id, timestamp=datetime.now(), status="success",
            passed=False, failures=[], warnings=[]
        )
    elif output_class == PriorityList:
        return PriorityList(
            lifecycle=lifecycle, work_id=work_id, timestamp=datetime.now(), status="success",
            items=[], ranking_criteria=""
        )

    return LifecycleOutput(
        lifecycle=lifecycle, work_id=work_id, timestamp=datetime.now(), status="success"
    )
```

### Call Chain Context

```
skill markdown (interpreted by Claude)
    |
    +-> CycleRunner.check_phase_entry()    # Existing - gate validation
    |
    +-> CycleRunner.run()                  # NEW - returns typed output
    |       Returns: LifecycleOutput subclass
    |       Does NOT call: next lifecycle
    |
    +-> Caller decides next action         # Caller choice, not callee
            ├─ Store output
            ├─ Pipe to next lifecycle
            └─ Complete without spawn
```

### Function/Component Signatures

```python
def run(self, work_id: str, lifecycle: str) -> LifecycleOutput:
    """
    Execute lifecycle and return typed output. Does NOT auto-chain.

    Args:
        work_id: Work item ID (e.g., "WORK-084", "INV-001")
        lifecycle: One of "investigation", "design", "implementation", "validation", "triage"

    Returns:
        LifecycleOutput subclass with lifecycle-specific fields populated.
        status field indicates: "success", "failure", or "partial"

    Raises:
        None - returns output with status="failure" on error (fail-safe)
    """
```

### Behavior Logic

**Current Flow:**
```
Skill CHAIN phase → Prompts "invoke /new-plan?" → Implicit suggestion to chain
```

**New Flow (Pure Function):**
```
run(work_id, lifecycle)
    │
    ├─ Map lifecycle → output type
    │
    ├─ Emit "RUN" phase event
    │
    └─ Return LifecycleOutput
           │
           └─ Caller decides: chain? store? done?
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Base dataclass + subclasses | LifecycleOutput base, 5 typed subclasses | Enables polymorphism while preserving type safety. Matches CH-001 interface spec. |
| MVP returns empty typed output | Populate basic fields only, leave content empty | Full content population requires skill execution integration (future work). This establishes the interface contract. |
| No exception on unknown lifecycle | Return base LifecycleOutput | Fail-safe design (L3.6). Unknown lifecycle still gets basic output rather than crash. |
| datetime import inside method | Import at call time | Avoid import at module level to maintain existing import structure (E2-255 pattern). |
| Status enum via Literal | `Literal["success", "failure", "partial"]` | Matches existing CycleResult pattern, no new dependencies. |
| run() does NOT read work file | Caller provides work_id only | Maintains stateless design (L4 invariant). Work file reading delegated to caller or WorkEngine. |

### Input/Output Examples

**Example 1: Design Lifecycle**
```python
runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
output = runner.run(work_id="WORK-084", lifecycle="design")

# Returns:
Specification(
    lifecycle="design",
    work_id="WORK-084",
    timestamp=datetime(2026, 2, 3, 21, 30, 0),
    status="success",
    requirements=[],      # Empty - populated by caller
    design_decisions=[],  # Empty - populated by caller
    interfaces={}         # Empty - populated by caller
)
```

**Example 2: Investigation Lifecycle**
```python
output = runner.run(work_id="INV-069", lifecycle="investigation")

# Returns:
Findings(
    lifecycle="investigation",
    work_id="INV-069",
    timestamp=datetime(2026, 2, 3, 21, 30, 0),
    status="success",
    question="",          # Empty - populated by caller
    conclusions=[],       # Empty - populated by caller
    evidence=[],          # Empty - populated by caller
    open_questions=[]     # Empty - populated by caller
)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Unknown lifecycle | Return base LifecycleOutput | Test 4 - implicitly covers via isinstance check |
| Empty work_id | Accept (caller's responsibility) | Not tested - defensive coding in caller |
| None governance | CycleRunner requires governance at init | Existing test coverage |

### Open Questions

**Q: Should run() populate output fields from work file?**

No. Per L4 invariant, CycleRunner is stateless. run() returns the typed container; caller populates content from skill execution or work file. This keeps CycleRunner thin (current: 220 lines, target: ~300 lines).

**Q: How will skills integrate with run()?**

TBD in CH-005 (PhaseTemplateContracts). Skills will continue as markdown interpreted by Claude. run() provides the typed output contract; skill execution fills the fields.

---

## Open Decisions (MUST resolve before implementation)

**No unresolved operator decisions.** Work item has no `operator_decisions` field.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No operator decisions required for this work |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 6 new tests to `tests/test_cycle_runner.py`
- [ ] Run `pytest tests/test_cycle_runner.py -v` - verify new tests fail (red)
- [ ] Existing 10 tests should still pass

### Step 2: Add LifecycleOutput Dataclasses
- [ ] Add `datetime` import at top of cycle_runner.py
- [ ] Add LifecycleOutput base dataclass after CycleResult (line 65)
- [ ] Add Findings, Specification, Artifact, Verdict, PriorityList subclasses
- [ ] Tests 1, 2, 3 pass (green) - dataclass creation tests

### Step 3: Implement run() Method
- [ ] Add `run()` method to CycleRunner class (after line 220)
- [ ] Map lifecycle names to output types
- [ ] Return typed output with default values
- [ ] Tests 4, 5 pass (green) - run() returns correct type, no auto-chain

### Step 4: Integration Verification
- [ ] All 16 tests pass (10 existing + 6 new)
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new types
- [ ] Document LifecycleOutput hierarchy and run() method

### Step 6: Export Verification
- [ ] Verify new types can be imported: `from cycle_runner import LifecycleOutput, Findings, ...`
- [ ] No consumer updates needed (run() is new method, no migration)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment: run() interface differs from CH-001 spec | Medium | Verified CH-001 spec (lines 86-106) - interface matches exactly |
| Integration: Skills don't know about run() yet | Low | run() is additive. Skills continue working via markdown. Integration in CH-005. |
| Regression: Breaking existing CycleRunner behavior | Low | Existing 10 tests cover current behavior. No changes to existing methods. |
| Scope creep: Trying to populate output fields | Medium | MVP returns empty typed outputs. Content population is future work (CH-005). |
| Knowledge gap: How skills will integrate | Low | Documented as "TBD in CH-005". This work establishes interface contract only. |

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

**MUST** read `docs/work/active/WORK-084/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Define LifecycleOutput base dataclass | [ ] | Read cycle_runner.py, verify class exists |
| Define 5 output types: Findings, Specification, Artifact, Verdict, PriorityList | [ ] | Read cycle_runner.py, verify all 5 classes |
| Add CycleRunner.run(work_id, lifecycle) -> LifecycleOutput method | [ ] | Read cycle_runner.py, verify method exists |
| Document Input -> Output signatures for all 5 lifecycles | [ ] | Docstrings in run() method |
| Unit tests verifying pure function behavior | [ ] | Run pytest, verify 6 new tests pass |
| Integration test: Design completes, returns Specification, no implementation spawned | [ ] | Test 5 verifies no auto-chain |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cycle_runner.py` | LifecycleOutput + 5 subclasses + run() method | [ ] | |
| `tests/test_cycle_runner.py` | 16 tests (10 existing + 6 new) | [ ] | |
| `.claude/haios/modules/README.md` | Documents new types and run() method | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_cycle_runner.py -v
# Expected: 16 tests passed
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

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-001-LifecycleSignature.md (Chapter spec)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-001)
- @.claude/haios/modules/cycle_runner.py (Implementation target)
- @tests/test_cycle_runner.py (Test target)
- @docs/work/active/WORK-084/WORK.md (Work item)

---
