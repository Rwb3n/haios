---
template: implementation_plan
status: approved
date: 2026-01-29
backlog_id: WORK-033
title: Pipeline Orchestrator Module
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-29T22:48:47'
---
# Implementation Plan: Pipeline Orchestrator Module

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

A `PipelineOrchestrator` module that wires CorpusLoader → RequirementExtractor → PlannerAgent into a functional INGEST→PLAN pipeline with state machine, CLI integration, and tests.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `cli.py`, `justfile` |
| Lines of code affected | ~50 | CLI dispatch additions |
| New files to create | 2 | `modules/pipeline_orchestrator.py`, `tests/test_pipeline_orchestrator.py` |
| Tests to write | 10 | State transitions, stage execution, error handling |
| Dependencies | 3 | CorpusLoader, RequirementExtractor, PlannerAgent |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | 3 existing modules to wire together |
| Risk of regression | Low | New module, no existing code changed |
| External dependencies | Low | All dependencies are internal modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests (TDD) | 30 min | High |
| Implementation | 45 min | High |
| CLI/Justfile | 15 min | High |
| **Total** | ~90 min | High |

---

## Current State vs Desired State

### Current State

```python
# Three separate modules exist with no orchestration:

# corpus_loader.py
loader = CorpusLoader(config_path)
files = loader.discover()

# requirement_extractor.py
extractor = RequirementExtractor(loader)
req_set = extractor.extract()

# planner_agent.py
planner = PlannerAgent(req_set)
work_plan = planner.plan()
```

**Behavior:** Each module works independently. No unified pipeline execution.

**Result:** User must manually chain calls. No state tracking. No CLI access.

### Desired State

```python
# pipeline_orchestrator.py - Unified pipeline execution
orchestrator = PipelineOrchestrator(corpus_config)
orchestrator.run()  # IDLE -> INGESTING -> PLANNING -> COMPLETE

# Or step-by-step with state visibility
orchestrator.ingest()  # Returns RequirementSet, state = PLANNING
orchestrator.plan()    # Returns WorkPlan, state = COMPLETE
```

**Behavior:** Single entry point orchestrates full pipeline with state machine.

**Result:** `just pipeline-run <config>` executes INGEST→PLAN in one command.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: State Machine Initial State
```python
def test_orchestrator_starts_in_idle_state(tmp_path):
    """Orchestrator initializes in IDLE state."""
    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    assert orchestrator.state == PipelineState.IDLE
```

### Test 2: Ingest Stage Transitions State
```python
def test_ingest_transitions_to_planning(tmp_path):
    """ingest() moves state from IDLE to PLANNING."""
    # Setup: Create test corpus
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    req_set = orchestrator.ingest()

    assert orchestrator.state == PipelineState.PLANNING
    assert len(req_set.requirements) >= 1
```

### Test 3: Plan Stage Transitions State
```python
def test_plan_transitions_to_complete(tmp_path):
    """plan() moves state from PLANNING to COMPLETE."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.ingest()  # Move to PLANNING

    work_plan = orchestrator.plan()

    assert orchestrator.state == PipelineState.COMPLETE
    assert work_plan is not None
```

### Test 4: Invalid State Transition Raises
```python
def test_plan_before_ingest_raises(tmp_path):
    """plan() raises if called before ingest()."""
    config = {"corpus": {"sources": []}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    with pytest.raises(InvalidStateError):
        orchestrator.plan()  # Can't plan from IDLE
```

### Test 5: Run Executes Full Pipeline
```python
def test_run_executes_full_pipeline(tmp_path):
    """run() executes INGEST -> PLAN and returns WorkPlan."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    result = orchestrator.run()

    assert orchestrator.state == PipelineState.COMPLETE
    assert result.work_plan is not None
    assert result.requirement_set is not None
```

### Test 6: Empty Corpus Handled Gracefully
```python
def test_empty_corpus_returns_empty_results(tmp_path):
    """Empty corpus produces empty RequirementSet and WorkPlan."""
    (tmp_path / "docs").mkdir()  # Empty directory

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    result = orchestrator.run()

    assert len(result.requirement_set.requirements) == 0
    assert len(result.work_plan.work_items) == 0
```

### Test 7: Config From YAML File
```python
def test_orchestrator_accepts_yaml_path(tmp_path):
    """Orchestrator accepts path to YAML config file."""
    (tmp_path / "docs").mkdir()
    config_file = tmp_path / "corpus.yaml"
    config_file.write_text("corpus:\\n  sources:\\n    - path: docs")

    orchestrator = PipelineOrchestrator(config_file, base_path=tmp_path)

    assert orchestrator.state == PipelineState.IDLE
```

### Test 8: State History Tracked
```python
def test_state_history_recorded(tmp_path):
    """State transitions are recorded in history."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.run()

    assert PipelineState.IDLE in orchestrator.state_history
    assert PipelineState.INGESTING in orchestrator.state_history
    assert PipelineState.PLANNING in orchestrator.state_history
    assert PipelineState.COMPLETE in orchestrator.state_history
```

### Test 9: Requirements Stored After Ingest
```python
def test_requirements_accessible_after_ingest(tmp_path):
    """RequirementSet is accessible via property after ingest."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.ingest()

    assert orchestrator.requirement_set is not None
    assert len(orchestrator.requirement_set.requirements) >= 1
```

### Test 10: WorkPlan Stored After Plan
```python
def test_work_plan_accessible_after_plan(tmp_path):
    """WorkPlan is accessible via property after plan."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.run()

    assert orchestrator.work_plan is not None
```

---

## Detailed Design

### New File: `modules/pipeline_orchestrator.py`

```python
"""
PipelineOrchestrator Module (WORK-033, CH-006)

Pipeline state machine that wires INGEST and PLAN stages together.
Drives the doc-to-product pipeline per S26 architecture.

Interface:
    orchestrator = PipelineOrchestrator(corpus_config, base_path)
    result = orchestrator.run()  # Full pipeline
    # Or step-by-step:
    req_set = orchestrator.ingest()
    work_plan = orchestrator.plan()

State Machine (per S26):
    IDLE → INGESTING → PLANNING → COMPLETE
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Import sibling modules (follow existing pattern from planner_agent.py)
try:
    from .corpus_loader import CorpusLoader
    from .requirement_extractor import RequirementExtractor, RequirementSet
    from .planner_agent import PlannerAgent, WorkPlan
except ImportError:
    from corpus_loader import CorpusLoader
    from requirement_extractor import RequirementExtractor, RequirementSet
    from planner_agent import PlannerAgent, WorkPlan

logger = logging.getLogger(__name__)


class PipelineState(Enum):
    """Pipeline execution states per S26."""
    IDLE = auto()
    INGESTING = auto()
    PLANNING = auto()
    BUILDING = auto()   # Future: CH-004
    VALIDATING = auto() # Future: CH-005
    COMPLETE = auto()
    ERROR = auto()


class InvalidStateError(Exception):
    """Raised when operation called in invalid state."""
    pass


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    requirement_set: RequirementSet
    work_plan: WorkPlan
    state_history: List[PipelineState]
    completed_at: datetime


class PipelineOrchestrator:
    """Pipeline state machine per S26.

    Responsibilities:
    1. Initialize pipeline with corpus config
    2. Call stages in sequence (INGEST → PLAN)
    3. Track state transitions
    4. Store intermediate results
    """

    VERSION = "1.0.0"

    # Valid state transitions
    TRANSITIONS = {
        PipelineState.IDLE: [PipelineState.INGESTING],
        PipelineState.INGESTING: [PipelineState.PLANNING, PipelineState.ERROR],
        PipelineState.PLANNING: [PipelineState.COMPLETE, PipelineState.ERROR],
        PipelineState.COMPLETE: [],
        PipelineState.ERROR: [PipelineState.IDLE],  # Allow reset
    }

    def __init__(
        self,
        corpus_config: Union[Path, Dict],
        base_path: Optional[Path] = None
    ):
        """Initialize orchestrator with corpus configuration.

        Args:
            corpus_config: Path to YAML file or dict with corpus definition.
            base_path: Base directory for resolving paths.
        """
        self.corpus_config = corpus_config
        self.base_path = Path(base_path) if base_path else Path.cwd()

        # State machine
        self._state = PipelineState.IDLE
        self._state_history: List[PipelineState] = [PipelineState.IDLE]

        # Stage results (populated during execution)
        self._requirement_set: Optional[RequirementSet] = None
        self._work_plan: Optional[WorkPlan] = None

    @property
    def state(self) -> PipelineState:
        """Current pipeline state."""
        return self._state

    @property
    def state_history(self) -> List[PipelineState]:
        """History of state transitions."""
        return self._state_history.copy()

    @property
    def requirement_set(self) -> Optional[RequirementSet]:
        """RequirementSet from INGEST stage (None if not run)."""
        return self._requirement_set

    @property
    def work_plan(self) -> Optional[WorkPlan]:
        """WorkPlan from PLAN stage (None if not run)."""
        return self._work_plan

    def _transition(self, new_state: PipelineState) -> None:
        """Transition to new state if valid."""
        if new_state not in self.TRANSITIONS.get(self._state, []):
            raise InvalidStateError(
                f"Cannot transition from {self._state.name} to {new_state.name}"
            )
        self._state = new_state
        self._state_history.append(new_state)
        logger.info(f"Pipeline state: {new_state.name}")

    def ingest(self) -> RequirementSet:
        """Execute INGEST stage: Corpus → Requirements.

        Returns:
            RequirementSet with extracted requirements.

        Raises:
            InvalidStateError: If not in IDLE state.
        """
        self._transition(PipelineState.INGESTING)

        try:
            # Load corpus
            loader = CorpusLoader(self.corpus_config, base_path=self.base_path)

            # Extract requirements
            extractor = RequirementExtractor(loader)
            self._requirement_set = extractor.extract()

            logger.info(f"INGEST complete: {len(self._requirement_set.requirements)} requirements")
            self._transition(PipelineState.PLANNING)
            return self._requirement_set

        except Exception as e:
            logger.error(f"INGEST failed: {e}")
            self._transition(PipelineState.ERROR)
            raise

    def plan(self) -> WorkPlan:
        """Execute PLAN stage: Requirements → WorkPlan.

        Returns:
            WorkPlan with suggested work items.

        Raises:
            InvalidStateError: If not in PLANNING state.
        """
        if self._state != PipelineState.PLANNING:
            raise InvalidStateError(
                f"plan() requires PLANNING state, current: {self._state.name}"
            )

        try:
            planner = PlannerAgent(self._requirement_set)
            self._work_plan = planner.plan()

            logger.info(f"PLAN complete: {len(self._work_plan.work_items)} work items")
            self._transition(PipelineState.COMPLETE)
            return self._work_plan

        except Exception as e:
            logger.error(f"PLAN failed: {e}")
            self._transition(PipelineState.ERROR)
            raise

    def run(self) -> PipelineResult:
        """Execute full pipeline: INGEST → PLAN.

        Returns:
            PipelineResult with all outputs.
        """
        self.ingest()
        self.plan()

        return PipelineResult(
            requirement_set=self._requirement_set,
            work_plan=self._work_plan,
            state_history=self._state_history.copy(),
            completed_at=datetime.now(),
        )
```

### Call Chain Context

```
CLI (just pipeline-run)
    |
    +-> cmd_pipeline_run(corpus_config)
    |       |
    |       +-> PipelineOrchestrator(config)
    |       |       |
    |       |       +-> run()
    |       |           |
    |       |           +-> ingest()
    |       |           |       |
    |       |           |       +-> CorpusLoader.discover()
    |       |           |       +-> RequirementExtractor.extract()
    |       |           |
    |       |           +-> plan()
    |       |                   |
    |       |                   +-> PlannerAgent.plan()
    |       |
    |       +-> Print results / return exit code
```

### CLI Integration

**File:** `.claude/haios/modules/cli.py`
**Add after existing commands (~line 600):**

```python
def cmd_pipeline_run(
    corpus_config: str,
    project_root: Optional[Path] = None
) -> int:
    """Run the doc-to-product pipeline.

    Args:
        corpus_config: Path to corpus YAML config file.
        project_root: Base path for resolving paths.

    Returns:
        0 on success, 1 on failure.
    """
    from pipeline_orchestrator import PipelineOrchestrator

    root = project_root or Path.cwd()
    config_path = root / corpus_config

    if not config_path.exists():
        print(f"Error: Corpus config not found: {config_path}")
        return 1

    try:
        orchestrator = PipelineOrchestrator(config_path, base_path=root)
        result = orchestrator.run()

        print(f"Pipeline complete!")
        print(f"  Requirements: {len(result.requirement_set.requirements)}")
        print(f"  Work items: {len(result.work_plan.work_items)}")
        print(f"  Execution order: {result.work_plan.execution_order}")
        return 0

    except Exception as e:
        print(f"Pipeline failed: {e}")
        return 1
```

### Justfile Recipe

**File:** `justfile`
**Add recipe:**

```make
# Run doc-to-product pipeline
pipeline-run config:
    python .claude/haios/modules/cli.py pipeline-run {{config}}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State machine pattern | Explicit state enum + transitions dict | S26 specifies state machine; explicit states prevent invalid operations |
| State history tracking | List of all states visited | Aids debugging and allows audit trail |
| Separate ingest/plan methods | Allow step-by-step execution | Operator may want to review after INGEST before PLAN |
| Store intermediate results | Properties for requirement_set, work_plan | Allows access to stage outputs without re-running |
| Follow sibling import pattern | try/except conditional imports | Consistency with planner_agent.py, corpus_loader.py |
| BUILD/VALIDATE as future states | Defined in enum but not implemented | Extensibility for CH-004, CH-005 without breaking changes |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty corpus | Returns empty RequirementSet/WorkPlan | Test 6 |
| Invalid state transition | Raises InvalidStateError | Test 4 |
| Stage failure | Transitions to ERROR state, re-raises exception | Implicit in implementation |
| YAML config file | CorpusLoader handles Path vs Dict | Test 7 |

### Open Questions

**Q: Should BUILD/VALIDATE stages be stubbed or omitted?**

Answer: Defined in PipelineState enum for forward compatibility, but not implemented. CH-004/CH-005 will add these stages. Current implementation only wires INGEST→PLAN per deliverables.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No unresolved operator decisions in work item |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_pipeline_orchestrator.py`
- [ ] Add all 10 tests from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create PipelineOrchestrator Module
- [ ] Create `modules/pipeline_orchestrator.py`
- [ ] Implement PipelineState enum
- [ ] Implement InvalidStateError exception
- [ ] Implement PipelineResult dataclass
- [ ] Implement PipelineOrchestrator class with state machine
- [ ] Tests 1, 4, 7, 8 pass (state machine basics)

### Step 3: Implement INGEST Stage
- [ ] Implement `ingest()` method
- [ ] Wire CorpusLoader → RequirementExtractor
- [ ] Tests 2, 6, 9 pass (ingest functionality)

### Step 4: Implement PLAN Stage
- [ ] Implement `plan()` method
- [ ] Wire to PlannerAgent
- [ ] Tests 3, 10 pass (plan functionality)

### Step 5: Implement Full Pipeline Run
- [ ] Implement `run()` method
- [ ] Test 5 passes (full pipeline)

### Step 6: CLI Integration
- [ ] Add `cmd_pipeline_run()` to cli.py
- [ ] Add dispatch in CLI main
- [ ] Add `pipeline-run` recipe to justfile
- [ ] Verify: `just pipeline-run .claude/haios/config/corpus/haios-requirements.yaml`

### Step 7: Update Pipeline ARC.md
- [ ] Mark CH-006 as Complete in ARC.md
- [ ] Update exit criteria checkboxes

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import path issues between modules | Medium | Follow existing try/except pattern from planner_agent.py |
| Empty corpus edge case | Low | Explicit test (Test 6), graceful empty results |
| State machine complexity | Low | Explicit TRANSITIONS dict prevents invalid states |
| Sibling module changes | Low | Depend only on public interfaces (discover, extract, plan) |

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

**MUST** read `docs/work/active/WORK-033/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `PipelineOrchestrator` class in `modules/pipeline_orchestrator.py` | [ ] | File exists, class defined |
| State machine with INGEST → PLAN transitions | [ ] | PipelineState enum, TRANSITIONS dict |
| INGEST stage: CorpusLoader → RequirementExtractor | [ ] | ingest() method works |
| PLAN stage: PlannerAgent integration | [ ] | plan() method works |
| CLI command: `just pipeline-run <config>` | [ ] | Recipe exists, runs |
| Tests: 8+ covering state transitions | [ ] | pytest tests/test_pipeline_orchestrator.py passes |
| Pipeline ARC.md updated with CH-006 complete | [ ] | ARC.md shows CH-006 Complete |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `modules/pipeline_orchestrator.py` | PipelineOrchestrator class with ingest(), plan(), run() | [ ] | |
| `tests/test_pipeline_orchestrator.py` | 10 tests covering state machine | [ ] | |
| `modules/cli.py` | cmd_pipeline_run() added | [ ] | |
| `justfile` | pipeline-run recipe added | [ ] | |
| `.claude/haios/epochs/E2_3/arcs/pipeline/ARC.md` | CH-006 marked Complete | [ ] | |

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

- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (Pipeline spec)
- @.claude/haios/epochs/E2_3/arcs/pipeline/ARC.md (Arc definition)
- @.claude/haios/modules/corpus_loader.py (INGEST dependency)
- @.claude/haios/modules/requirement_extractor.py (INGEST dependency)
- @.claude/haios/modules/planner_agent.py (PLAN dependency)
- Memory: 8210 (File-based state machine pattern), 25794 (Stage-based pipeline)

---
