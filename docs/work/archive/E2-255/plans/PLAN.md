---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-255
title: CycleRunner Module - Phase Execution and Gates
author: Hephaestus
lifecycle_phase: plan
session: 167
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T15:58:55'
---
# Implementation Plan: CycleRunner Module - Phase Execution and Gates

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

A CycleRunner module will exist that validates phase transitions and gate checks for cycle skills, emitting events for observability while delegating actual phase execution to Claude's markdown skill interpretation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | `__init__.py`, `cli.py`, `README.md` in `.claude/haios/modules/` |
| Lines of code affected | ~50 | Imports/exports only |
| New files to create | 2 | `cycle_runner.py`, `tests/test_cycle_runner.py` |
| Tests to write | 8 | Based on interface methods |
| Dependencies | 3 | GovernanceLayer, WorkEngine, governance_events |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Calls GovernanceLayer.check_gate, WorkEngine.transition |
| Risk of regression | Low | New module, no existing code modified |
| External dependencies | Low | Uses existing internal modules only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests (TDD) | 30 min | High |
| Core implementation | 45 min | High |
| Integration + docs | 30 min | Medium |
| **Total** | ~2 hr | |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/__init__.py:12-16
from .governance_layer import GovernanceLayer, GateResult
from .memory_bridge import MemoryBridge, QueryResult, StoreResult
from .work_engine import WorkEngine, WorkState, InvalidTransitionError, WorkNotFoundError
from .context_loader import ContextLoader, GroundedContext
# No CycleRunner - module doesn't exist
```

**Behavior:** Phase gate checking is scattered across:
- `.claude/lib/node_cycle.py` (exit criteria checking, 300 lines)
- `.claude/lib/observations.py` (observation validation, 484 lines)
- `GovernanceLayer.check_gate()` (DoD/preflight/observation gates)

**Result:** No unified cycle orchestration. Cycle skills invoke gates directly without consistent event emission.

### Desired State

```python
# .claude/haios/modules/cycle_runner.py (NEW)
@dataclass
class CycleResult:
    cycle_id: str
    final_phase: str
    outcome: Literal["completed", "blocked", "chain"]
    gate_results: List[GateResult]
    next_cycle: Optional[str] = None

class CycleRunner:
    def __init__(self, governance: GovernanceLayer, work_engine: WorkEngine):
        ...

    def check_phase_entry(self, cycle_id: str, phase: str, work_id: str) -> GateResult:
        """Check if phase can be entered (entry conditions met)."""

    def check_phase_exit(self, cycle_id: str, phase: str, work_id: str) -> GateResult:
        """Check if phase can be exited (exit criteria met)."""

    def get_cycle_phases(self, cycle_id: str) -> List[str]:
        """Return ordered phases for a cycle."""
```

**Behavior:** Unified cycle gate validation with event emission for observability.

**Result:** Cycle skills invoke CycleRunner for gate checks, events logged via governance_events.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: CycleRunner instantiation with dependencies
```python
def test_cycle_runner_requires_governance_and_work_engine():
    governance = GovernanceLayer()
    work_engine = WorkEngine(governance=governance)
    runner = CycleRunner(governance=governance, work_engine=work_engine)
    assert runner._governance is governance
    assert runner._work_engine is work_engine
```

### Test 2: Get phases for known cycle
```python
def test_get_cycle_phases_implementation_cycle():
    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    phases = runner.get_cycle_phases("implementation-cycle")
    assert phases == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]
```

### Test 3: Get phases for unknown cycle returns empty
```python
def test_get_cycle_phases_unknown_returns_empty():
    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    phases = runner.get_cycle_phases("nonexistent-cycle")
    assert phases == []
```

### Test 4: Check phase entry allowed
```python
def test_check_phase_entry_allowed():
    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    result = runner.check_phase_entry("implementation-cycle", "PLAN", "E2-255")
    assert result.allowed is True
```

### Test 5: Check phase exit with exit criteria
```python
def test_check_phase_exit_with_criteria():
    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    # Exit from discovery node requires investigation status=complete
    result = runner.check_phase_exit("investigation-cycle", "CONCLUDE", "INV-001")
    # Returns GateResult - may be blocked or allowed based on file state
    assert isinstance(result, GateResult)
```

### Test 6: CycleResult dataclass fields
```python
def test_cycle_result_dataclass():
    result = CycleResult(
        cycle_id="implementation-cycle",
        final_phase="DONE",
        outcome="completed",
        gate_results=[],
        next_cycle=None
    )
    assert result.cycle_id == "implementation-cycle"
    assert result.outcome == "completed"
```

### Test 7: Load cycle definitions from config
```python
def test_load_cycle_definitions():
    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    # Should load from .claude/haios/config/cycles.yaml
    cycles = runner._load_cycle_definitions()
    assert "nodes" in cycles
    assert "discovery" in cycles["nodes"]
```

### Test 8: Emit phase entered event (side effect)
```python
def test_emit_phase_entered_event(mocker):
    mock_log = mocker.patch("cycle_runner.log_phase_transition")
    runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
    runner._emit_phase_entered("implementation-cycle", "DO", "E2-255")
    mock_log.assert_called_once_with("DO", "E2-255", "Hephaestus")
```

---

## Detailed Design

### New File: `.claude/haios/modules/cycle_runner.py`

```python
# generated: 2026-01-04
"""
CycleRunner Module (E2-255)

Stateless phase gate validator for HAIOS cycle skills. Provides:
- Phase entry/exit gate checking
- Cycle phase sequence lookup
- Event emission for observability

L4 Invariants (from S17.5):
- MUST NOT execute skill content (Claude interprets markdown)
- MUST delegate gate checks to GovernanceLayer
- MUST emit events for observability (PhaseEntered, GatePassed)
- MUST NOT own persistent state

Design Decision: CycleRunner validates gates, does NOT orchestrate.
Skills remain markdown files that Claude interprets.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml

# Import from sibling modules
from .governance_layer import GovernanceLayer, GateResult

# Import event logging from lib
import sys
_lib_path = Path(__file__).parent.parent.parent / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_phase_transition, log_validation_outcome


@dataclass
class CycleResult:
    """Result of a cycle validation or execution."""
    cycle_id: str
    final_phase: str
    outcome: Literal["completed", "blocked", "chain"]
    gate_results: List[GateResult] = field(default_factory=list)
    next_cycle: Optional[str] = None


# Cycle phase definitions (from S17.5 and existing skills)
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["HYPOTHESIZE", "EXPLORE", "CONCLUDE", "CHAIN"],
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}


class CycleRunner:
    """
    Stateless phase gate validator for cycle skills.

    Does NOT execute skills - validates that phases can be entered/exited.
    """

    def __init__(
        self,
        governance: GovernanceLayer,
        work_engine: Optional[Any] = None,
    ):
        self._governance = governance
        self._work_engine = work_engine
        self._cycle_config = self._load_cycle_definitions()

    def _load_cycle_definitions(self) -> Dict[str, Any]:
        """Load cycle definitions from config."""
        config_path = Path(__file__).parent.parent / "config" / "cycles.yaml"
        if not config_path.exists():
            return {}
        try:
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def get_cycle_phases(self, cycle_id: str) -> List[str]:
        """Return ordered phases for a cycle."""
        return CYCLE_PHASES.get(cycle_id, [])

    def check_phase_entry(
        self, cycle_id: str, phase: str, work_id: str
    ) -> GateResult:
        """
        Check if a phase can be entered (entry conditions met).

        Entry conditions are currently defined in skill markdown.
        This method provides a hook for programmatic checks.
        """
        # For MVP: always allow entry (conditions in skill markdown)
        # Future: read entry conditions from skill and validate
        self._emit_phase_entered(cycle_id, phase, work_id)
        return GateResult(allowed=True, reason=f"Phase {phase} entry allowed")

    def check_phase_exit(
        self, cycle_id: str, phase: str, work_id: str
    ) -> GateResult:
        """
        Check if a phase can be exited (exit criteria met).

        Delegates to node_cycle.check_exit_criteria for node-bound cycles.
        """
        from node_cycle import check_exit_criteria, get_exit_criteria

        # Map cycle to node (if node-bound)
        node = self._get_node_for_cycle(cycle_id)
        if not node:
            # Not node-bound, allow exit
            return GateResult(allowed=True, reason=f"Phase {phase} exit allowed (no node binding)")

        # Check exit criteria from config
        failures = check_exit_criteria(node, work_id)
        if failures:
            return GateResult(
                allowed=False,
                reason=f"Exit blocked: {'; '.join(failures)}"
            )

        return GateResult(allowed=True, reason=f"Phase {phase} exit criteria met")

    def _get_node_for_cycle(self, cycle_id: str) -> Optional[str]:
        """Map cycle to DAG node (if any)."""
        nodes = self._cycle_config.get("nodes", {})
        for node_name, config in nodes.items():
            if config.get("cycle") == cycle_id:
                return node_name
        return None

    def _emit_phase_entered(self, cycle_id: str, phase: str, work_id: str) -> None:
        """Emit PhaseEntered event for observability."""
        log_phase_transition(phase, work_id, "Hephaestus")
```

### Call Chain Context

```
Skill(skill="implementation-cycle")
    |
    |  (Claude interprets skill markdown)
    |
    +-> CycleRunner.check_phase_entry("implementation-cycle", "DO", "E2-255")
    |       |
    |       +-> _emit_phase_entered() -> log_phase_transition()
    |       |
    |       Returns: GateResult(allowed=True)
    |
    +-> CycleRunner.check_phase_exit("implementation-cycle", "DO", "E2-255")
            |
            +-> node_cycle.check_exit_criteria()
            |
            Returns: GateResult
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Validator not orchestrator | CycleRunner validates gates, Claude executes | Skills work as markdown. Programmatic execution adds complexity without benefit. Memory pattern 78899 confirms "skills are markdown files that Claude interprets" |
| CYCLE_PHASES hardcoded | Define phases in Python const | cycles.yaml has node bindings but not phase lists. Hardcoding is simpler than YAML schema change |
| Delegate to node_cycle | Reuse existing exit criteria | node_cycle.py already has check_exit_criteria(). No duplication needed |
| Work engine optional | Constructor allows None | Not all gate checks need work state. Enables simpler testing |
| Event emission on entry | Emit on phase entry, not exit | Entry is the point of commitment. Exit may never happen if blocked |

### Input/Output Examples

**Check phase entry for E2-255:**
```python
runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
result = runner.check_phase_entry("implementation-cycle", "DO", "E2-255")
# Returns: GateResult(allowed=True, reason="Phase DO entry allowed")
# Side effect: log_phase_transition("DO", "E2-255", "Hephaestus")
```

**Check phase exit with exit criteria:**
```python
# cycles.yaml defines exit_criteria for discovery node:
#   - file_status: investigation status=complete
#   - section_content: Findings >= 50 chars
result = runner.check_phase_exit("investigation-cycle", "CONCLUDE", "INV-055")
# If investigation not complete:
# Returns: GateResult(allowed=False, reason="Exit blocked: Investigation status not complete")
# If complete:
# Returns: GateResult(allowed=True, reason="Phase CONCLUDE exit criteria met")
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Unknown cycle_id | get_cycle_phases returns [] | Test 3 |
| Cycle with no node binding | check_phase_exit allows (no criteria) | Implicit in design |
| Missing cycles.yaml | _load_cycle_definitions returns {} | Test 7 |
| work_engine is None | Skip work state checks | Test 4 |

### Open Questions

**Q: Should CycleRunner own the CYCLE_PHASES or read from cycles.yaml?**

Answer: Hardcode in Python. The cycles.yaml currently only has node bindings (which node triggers which cycle). Adding phase definitions would require schema change. Skills already define their phases in markdown. CYCLE_PHASES const is the single source of truth for phase order.

**Q: Should observations.py migrate to CycleRunner?**

Answer: No. observations.py is observation-specific (validation, scaffolding, triage). CycleRunner is cycle-generic. Keep observations.py in `.claude/lib/` as a utility. CycleRunner can call it for observation-related gates.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_cycle_runner.py`
- [ ] Add 8 tests from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Implement CycleResult dataclass
- [ ] Create `.claude/haios/modules/cycle_runner.py`
- [ ] Add CycleResult dataclass
- [ ] Test 6 passes (green)

### Step 3: Implement CycleRunner class core
- [ ] Add CycleRunner.__init__ with governance/work_engine
- [ ] Add CYCLE_PHASES constant
- [ ] Add get_cycle_phases method
- [ ] Tests 1, 2, 3 pass (green)

### Step 4: Implement gate checking methods
- [ ] Add check_phase_entry with event emission
- [ ] Add check_phase_exit with node_cycle delegation
- [ ] Add _get_node_for_cycle helper
- [ ] Add _load_cycle_definitions
- [ ] Tests 4, 5, 7 pass (green)

### Step 5: Implement event emission
- [ ] Add _emit_phase_entered calling log_phase_transition
- [ ] Test 8 passes (green)

### Step 6: Update module exports
- [ ] Add to `__init__.py`: `from .cycle_runner import CycleRunner, CycleResult`
- [ ] Add to `__all__` list
- [ ] Verify import works: `from haios.modules import CycleRunner`

### Step 7: Integration Verification
- [ ] All 8 tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with CycleRunner docs
- [ ] **MUST:** Verify README content matches actual module

### Step 9: Runtime Consumer (E2-250 DoD)
- [ ] Add CLI command `cmd_cycle_phases` to cli.py
- [ ] Add `just cycle-phases <cycle-id>` recipe to justfile
- [ ] Verify: `just cycle-phases implementation-cycle` returns phases

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment | Medium | Designed as validator (S17.5 says "Execute phase-based workflows") but implementation validates gates, doesn't execute. Rationale: skills work as markdown, execution is implicit |
| Integration with node_cycle | Low | Delegates to existing check_exit_criteria(). If node_cycle changes, CycleRunner may break. Mitigate: test covers this path |
| CYCLE_PHASES drift | Low | Hardcoded phases may diverge from skill markdown. Mitigate: add test that compares to skill headers |
| No runtime consumer initially | Medium | Module may not be called by anything. Mitigate: Step 9 adds CLI command + justfile recipe |
| Scope creep to orchestration | Medium | Temptation to add full cycle execution. Mitigate: Documented design decision that skills remain markdown |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cycle_runner.py` | CycleRunner class with check_phase_entry/exit | [ ] | |
| `tests/test_cycle_runner.py` | 8 tests covering all interface methods | [ ] | |
| `.claude/haios/modules/__init__.py` | Exports CycleRunner, CycleResult | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Documents CycleRunner | [ ] | |
| `justfile` | **MUST:** Has `cycle-phases` recipe | [ ] | |
| `.claude/haios/modules/cli.py` | **MUST:** Has `cmd_cycle_phases` | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_cycle_runner.py -v
# Expected: 8 tests passed

just cycle-phases implementation-cycle
# Expected: ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- `docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md` (S17.5 CycleRunner spec)
- `.claude/haios/config/cycles.yaml` (node-cycle bindings)
- `.claude/lib/node_cycle.py` (exit criteria checking)
- `.claude/lib/observations.py` (observation validation)
- Memory concepts 78899, 78901, 78925, 78972 (skill gate patterns)
- ADR-033: Work Item Lifecycle Governance
- ADR-040: Modular Black Box Architecture

---
