---
template: implementation_plan
status: complete
date: 2026-01-03
backlog_id: E2-240
title: Implement GovernanceLayer Module
author: Hephaestus
lifecycle_phase: plan
session: 160
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-03T15:31:02'
---
# Implementation Plan: Implement GovernanceLayer Module

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

Create a stateless GovernanceLayer module that provides gate checking, transition validation, handler loading, and event routing as the central policy enforcement point for HAIOS.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `cycles.yaml` (add cycle defs), `components.yaml` (add handler registry) |
| Lines of code affected | ~60 | Existing config files (cycles.yaml: 57, components.yaml: 10) |
| New files to create | 2 | `.claude/haios/modules/governance_layer.py`, `tests/test_governance_layer.py` |
| Tests to write | 8 | 4 L4 functions + 4 edge cases |
| Dependencies | 3 | `node_cycle.py`, `governance_events.py`, `config.py` (consume this module) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | Replaces logic in node_cycle.py, hooks consume via config |
| Risk of regression | Low | New module, strangler fig pattern, existing code unchanged initially |
| External dependencies | Low | Pure Python, reads from config files only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests (TDD) | 45 min | High |
| Implement GovernanceLayer class | 60 min | Med |
| Add cycle definitions to config | 30 min | High |
| Integration + verification | 30 min | Med |
| **Total** | ~3 hours | Med |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/node_cycle.py:210-230 - Exit criteria checking is inline
def check_exit_criteria(node: str, work_id: str, base_path: Path = Path(".")) -> list:
    """Check all exit criteria for a node."""
    criteria = get_exit_criteria(node)  # From config
    failures = []
    for criterion in criteria:
        result = _check_single_criterion(criterion, work_id, base_path)
        if result:
            failures.append(result)
    return failures

# .claude/lib/governance_events.py:57-86 - Validation logging is standalone
def log_validation_outcome(gate: str, work_id: str, result: str, reason: str) -> dict:
    """Log validation outcome and check thresholds."""
    event = {"type": "ValidationOutcome", "gate": gate, ...}
    _append_event(event)
    return event
```

**Behavior:** Governance logic scattered across `node_cycle.py` (exit criteria), `governance_events.py` (logging), and hooks (policy checks). No unified interface.

**Result:** Adding new gates requires modifying multiple files. No single point for policy enforcement. Hard to swap compliance regimes.

### Desired State

```python
# .claude/haios/modules/governance_layer.py - Unified governance interface
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class GateResult:
    allowed: bool
    reason: str

class GovernanceLayer:
    """Stateless policy enforcement module."""

    def check_gate(self, gate_id: str, context: Dict[str, Any]) -> GateResult:
        """Check if gate allows transition."""
        ...

    def validate_transition(self, from_node: str, to_node: str) -> bool:
        """Validate DAG transition is valid."""
        ...

    def load_handlers(self, config_path: str) -> Dict[str, Any]:
        """Load handler registry from config."""
        ...

    def on_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Route event to registered handlers."""
        ...
```

**Behavior:** Single module owns all governance. Consumers call `GovernanceLayer.check_gate()` instead of inline logic.

**Result:** Clean swap point for compliance regimes. All gate decisions logged. Easy to add new gates without touching consumers.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: check_gate Returns GateResult
```python
def test_check_gate_returns_gate_result():
    """L4: check_gate(gate_id, context) returns GateResult(allowed, reason)."""
    layer = GovernanceLayer()
    context = {"work_id": "E2-240", "dod_complete": False}

    result = layer.check_gate("dod", context)

    assert isinstance(result, GateResult)
    assert result.allowed is False
    assert "DoD" in result.reason
```

### Test 2: check_gate Denies Incomplete DoD
```python
def test_check_gate_denies_incomplete_dod():
    """L4 Acceptance: Returns deny for incomplete DoD."""
    layer = GovernanceLayer()
    context = {"work_id": "E2-240", "tests_pass": False}

    result = layer.check_gate("dod", context)

    assert result.allowed is False
    assert "incomplete" in result.reason.lower()
```

### Test 3: validate_transition Blocks Invalid
```python
def test_validate_transition_blocks_invalid():
    """L4: Blocks invalid transitions (e.g., backlog→complete)."""
    layer = GovernanceLayer()

    # Valid transition
    assert layer.validate_transition("backlog", "discovery") is True

    # Invalid transition (skip implement)
    assert layer.validate_transition("backlog", "complete") is False
```

### Test 4: load_handlers Returns Registry
```python
def test_load_handlers_returns_registry():
    """L4: load_handlers(config_path) returns Handler registry."""
    layer = GovernanceLayer()

    handlers = layer.load_handlers(".claude/haios/config/components.yaml")

    assert isinstance(handlers, dict)
    assert "hooks" in handlers or handlers == {}  # May be empty initially
```

### Test 5: on_event Routes to Handlers
```python
def test_on_event_routes_to_handler(mocker):
    """L4: on_event(event_type, payload) routes to correct handlers."""
    layer = GovernanceLayer()
    mock_handler = mocker.Mock()
    layer._handlers = {"work_transition": [mock_handler]}

    layer.on_event("work_transition", {"work_id": "E2-240", "to_node": "plan"})

    mock_handler.assert_called_once()
```

### Test 6: Stateless (No Internal State)
```python
def test_governance_layer_is_stateless():
    """L4 Invariant: MUST be stateless (no internal state between calls)."""
    layer1 = GovernanceLayer()
    layer2 = GovernanceLayer()

    # Different instances should produce same results
    result1 = layer1.check_gate("dod", {"tests_pass": True})
    result2 = layer2.check_gate("dod", {"tests_pass": True})

    assert result1.allowed == result2.allowed
```

### Test 7: Logs All Gate Decisions
```python
def test_logs_all_gate_decisions(mocker):
    """L4 Invariant: MUST log all gate decisions for audit."""
    mock_log = mocker.patch('governance_layer.log_validation_outcome')
    layer = GovernanceLayer()

    layer.check_gate("dod", {"work_id": "E2-240"})

    mock_log.assert_called_once()
```

### Test 8: Does Not Modify Work Files
```python
def test_does_not_modify_work_files(tmp_path):
    """L4 Invariant: MUST NOT modify work files directly."""
    layer = GovernanceLayer()
    work_file = tmp_path / "WORK.md"
    work_file.write_text("status: active")
    original_content = work_file.read_text()

    layer.check_gate("dod", {"work_id": "E2-240", "work_path": str(work_file)})

    assert work_file.read_text() == original_content
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
     4. Input/output examples with REAL data from the system -->

### New File: governance_layer.py

**File:** `.claude/haios/modules/governance_layer.py` (NEW)

```python
"""
GovernanceLayer Module (E2-240)

Stateless policy enforcement for HAIOS. Provides:
- Gate checks (DoD, preflight, observation)
- Transition validation (DAG node constraints)
- Handler loading (from config)
- Event routing (to registered handlers)

L4 Invariants:
- MUST NOT modify work files directly
- MUST log all gate decisions for audit
- MUST be stateless (no internal state between calls)
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import yaml

# Import existing governance_events for logging
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))
from governance_events import log_validation_outcome


@dataclass
class GateResult:
    """Result of a gate check."""
    allowed: bool
    reason: str


# Valid DAG transitions (from -> allowed_to_nodes)
VALID_TRANSITIONS = {
    "backlog": ["discovery", "plan"],
    "discovery": ["backlog", "plan"],
    "plan": ["backlog", "implement"],
    "implement": ["plan", "close"],
    "close": ["complete"],
    "complete": [],  # Terminal node
}


class GovernanceLayer:
    """Stateless policy enforcement module."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def check_gate(self, gate_id: str, context: Dict[str, Any]) -> GateResult:
        """
        Check if gate allows operation.

        Args:
            gate_id: Gate identifier (e.g., "dod", "preflight", "observation")
            context: Context dict with work_id and relevant state

        Returns:
            GateResult with allowed flag and reason
        """
        work_id = context.get("work_id", "unknown")

        # Dispatch to specific gate check
        if gate_id == "dod":
            result = self._check_dod_gate(context)
        elif gate_id == "preflight":
            result = self._check_preflight_gate(context)
        elif gate_id == "observation":
            result = self._check_observation_gate(context)
        else:
            result = GateResult(allowed=True, reason=f"Unknown gate '{gate_id}', allowing")

        # Log decision for audit (L4 invariant)
        log_validation_outcome(
            gate=gate_id,
            work_id=work_id,
            result="pass" if result.allowed else "block",
            reason=result.reason
        )

        return result

    def _check_dod_gate(self, context: Dict[str, Any]) -> GateResult:
        """Check Definition of Done criteria."""
        tests_pass = context.get("tests_pass", False)
        why_captured = context.get("why_captured", False)
        docs_current = context.get("docs_current", False)

        if not tests_pass:
            return GateResult(allowed=False, reason="DoD incomplete: tests not passing")
        if not why_captured:
            return GateResult(allowed=False, reason="DoD incomplete: WHY not captured")
        if not docs_current:
            return GateResult(allowed=False, reason="DoD incomplete: docs not current")

        return GateResult(allowed=True, reason="DoD complete")

    def _check_preflight_gate(self, context: Dict[str, Any]) -> GateResult:
        """Check preflight criteria (plan readiness)."""
        plan_approved = context.get("plan_approved", False)
        file_count = context.get("file_count", 0)

        if not plan_approved:
            return GateResult(allowed=False, reason="Preflight: plan not approved")
        if file_count > 3:
            return GateResult(allowed=False, reason=f"Preflight: {file_count} files exceeds 3-file threshold")

        return GateResult(allowed=True, reason="Preflight passed")

    def _check_observation_gate(self, context: Dict[str, Any]) -> GateResult:
        """Check observation pending threshold."""
        pending_count = context.get("pending_observations", 0)
        max_count = context.get("max_observations", 10)

        if pending_count > max_count:
            return GateResult(
                allowed=False,
                reason=f"Observation gate: {pending_count} pending > {max_count} threshold"
            )

        return GateResult(allowed=True, reason="Observation threshold OK")

    def validate_transition(self, from_node: str, to_node: str) -> bool:
        """
        Validate DAG transition is allowed.

        Args:
            from_node: Current node (e.g., "backlog")
            to_node: Target node (e.g., "discovery")

        Returns:
            True if transition is valid, False otherwise
        """
        allowed = VALID_TRANSITIONS.get(from_node, [])
        return to_node in allowed

    def load_handlers(self, config_path: str) -> Dict[str, Any]:
        """
        Load handler registry from config file.

        Args:
            config_path: Path to components.yaml

        Returns:
            Dict with handler registries (hooks, skills, agents)
        """
        path = Path(config_path)
        if not path.exists():
            return {}

        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            self._handlers = self._parse_handlers(config)
            return config
        except Exception:
            return {}

    def _parse_handlers(self, config: Dict[str, Any]) -> Dict[str, List[Callable]]:
        """Parse handler config into callable registry."""
        # For MVP, just store the config structure
        # Future: resolve handler paths to callables
        return {}

    def on_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Route event to registered handlers.

        Args:
            event_type: Event type (e.g., "work_transition", "gate_decision")
            payload: Event payload dict
        """
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception:
                # Log but don't fail on handler errors
                pass
```

### Call Chain Context

```
implementation-cycle PLAN phase
    |
    +-> plan-validation-cycle
    |       |
    |       +-> GovernanceLayer.check_gate("preflight", context)
    |                Returns: GateResult(allowed=True/False, reason)
    |
close-work-cycle VALIDATE phase
    |
    +-> dod-validation-cycle
            |
            +-> GovernanceLayer.check_gate("dod", context)
                     Returns: GateResult(allowed=True/False, reason)

node_cycle.py (future integration)
    |
    +-> GovernanceLayer.validate_transition(from_node, to_node)
            Returns: bool
```

### Function/Component Signatures

```python
@dataclass
class GateResult:
    """Result of a gate check."""
    allowed: bool  # Whether operation is allowed
    reason: str    # Human-readable explanation

class GovernanceLayer:
    def check_gate(self, gate_id: str, context: Dict[str, Any]) -> GateResult:
        """
        Check if gate allows operation.

        Args:
            gate_id: Gate identifier ("dod", "preflight", "observation")
            context: Dict with work_id and gate-specific state

        Returns:
            GateResult with allowed flag and reason

        Side Effects:
            Logs decision via governance_events.log_validation_outcome()
        """

    def validate_transition(self, from_node: str, to_node: str) -> bool:
        """
        Validate DAG transition.

        Args:
            from_node: Current node name
            to_node: Target node name

        Returns:
            True if transition allowed by DAG, False otherwise
        """

    def load_handlers(self, config_path: str) -> Dict[str, Any]:
        """
        Load handler registry from config.

        Args:
            config_path: Path to components.yaml

        Returns:
            Parsed config dict (may be empty)
        """

    def on_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Route event to handlers.

        Args:
            event_type: Event type string
            payload: Event data dict

        Side Effects:
            Calls registered handlers (may fail silently)
        """
```

### Behavior Logic

**Gate Check Flow:**
```
check_gate(gate_id, context)
    │
    ├─ gate_id == "dod"?
    │       └─ Check tests_pass, why_captured, docs_current
    │               ├─ Any missing → GateResult(False, reason)
    │               └─ All present → GateResult(True, "DoD complete")
    │
    ├─ gate_id == "preflight"?
    │       └─ Check plan_approved, file_count <= 3
    │               ├─ Failed → GateResult(False, reason)
    │               └─ Passed → GateResult(True, "Preflight passed")
    │
    └─ Unknown gate → GateResult(True, "allowing")

    Finally: log_validation_outcome() for all decisions
```

**Transition Validation Flow:**
```
validate_transition(from_node, to_node)
    │
    └─ VALID_TRANSITIONS[from_node] contains to_node?
            ├─ YES → True
            └─ NO  → False
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dataclass for GateResult | `@dataclass` | Simple, typed, immutable result |
| Static VALID_TRANSITIONS | Dict constant | Easy to read and modify; no config parsing needed |
| Logging via governance_events | Reuse existing | L4 invariant: log all decisions. Don't reinvent. |
| Handlers as callables | `List[Callable]` | Flexible; can be functions, methods, or lambdas |
| Silent handler failures | try/except pass | One bad handler shouldn't block the event system |
| Strangler fig pattern | New module, no migration yet | Consumers can adopt incrementally; existing code unchanged |

### Input/Output Examples

**DoD Gate Check:**
```python
# Input
layer.check_gate("dod", {
    "work_id": "E2-240",
    "tests_pass": True,
    "why_captured": True,
    "docs_current": False
})

# Output
GateResult(allowed=False, reason="DoD incomplete: docs not current")

# Side effect: governance_events.log_validation_outcome called
```

**Transition Validation:**
```python
# Valid transition
layer.validate_transition("backlog", "discovery")  # True

# Invalid transition (skipping implement)
layer.validate_transition("backlog", "complete")  # False

# From terminal node
layer.validate_transition("complete", "backlog")  # False
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Unknown gate_id | Allow with warning reason | Implicit (fallback case) |
| Missing context keys | Default to False/0 | Test 1, 2 |
| Empty handlers list | on_event does nothing | Test 5 |
| Config file missing | load_handlers returns {} | Test 4 |
| Handler throws exception | Silently caught, continue | Test 5 variant |
| Terminal node transition | Always returns False | Test 3 |

### Open Questions

**Q: Should we add gate definitions to cycles.yaml?**

Deferred. For MVP, gates are hardcoded in the module. Future: add gate definitions to cycles.yaml so gates are configurable.

**Q: How to handle async handlers?**

Deferred. For MVP, handlers are synchronous. Future: add async support with `asyncio.create_task`.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests (RED)
- [ ] Create `tests/test_governance_layer.py`
- [ ] Add 8 tests from Tests First section
- [ ] Verify all tests fail (module doesn't exist yet)

### Step 2: Create Module Directory
- [ ] Create `.claude/haios/modules/` directory
- [ ] Create `.claude/haios/modules/__init__.py`

### Step 3: Implement GateResult and GovernanceLayer (GREEN)
- [ ] Create `.claude/haios/modules/governance_layer.py`
- [ ] Implement `GateResult` dataclass
- [ ] Implement `VALID_TRANSITIONS` constant
- [ ] Implement `GovernanceLayer` class with 4 L4 functions
- [ ] Tests 1-5 pass (core functionality)

### Step 4: Implement Invariants
- [ ] Add logging via `governance_events.log_validation_outcome`
- [ ] Verify stateless behavior
- [ ] Tests 6-8 pass (invariants)

### Step 5: Integration Verification
- [ ] All 8 tests pass
- [ ] Run full test suite: `just test`
- [ ] No regressions

### Step 6: README Sync (MUST)
- [ ] **MUST:** Create `.claude/haios/modules/README.md`
- [ ] **MUST:** Update `.claude/haios/README.md` to include modules directory
- [ ] **MUST:** Verify README content matches actual file state

### Step 7: Consumer Preparation (No Migration Yet)
<!-- Strangler fig pattern: new module exists but consumers not migrated yet -->
- [ ] Document integration points for future work (node_cycle.py, dod-validation-cycle)
- [ ] No consumer migration in this work item (that's future E2-24x)

**Integration Points (for future):**
```python
# node_cycle.py - replace check_exit_criteria with GovernanceLayer.check_gate
# dod-validation-cycle - use GovernanceLayer.check_gate("dod", context)
# implementation-cycle - use GovernanceLayer.check_gate("preflight", context)
```

> **Pattern:** Strangler fig - new module exists alongside old code. Migration happens incrementally.

---

## Verification

- [ ] Tests pass: `pytest tests/test_governance_layer.py -v` (8 tests)
- [ ] **MUST:** `.claude/haios/modules/README.md` created
- [ ] **MUST:** `.claude/haios/README.md` updated
- [ ] L4 functions implemented: check_gate, validate_transition, load_handlers, on_event

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import path issues | Med | Use sys.path manipulation for cross-module imports |
| Breaking existing governance_events | Low | Only import, don't modify existing module |
| Incomplete gate coverage | Med | Start with 3 gates (dod, preflight, observation); add more later |
| Handler registration complexity | Low | MVP uses empty registry; populate in future work |

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
| `.claude/haios/modules/governance_layer.py` | GateResult, GovernanceLayer class, 4 L4 functions | [ ] | |
| `tests/test_governance_layer.py` | 8 tests, all passing | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Documents module purpose and functions | [ ] | |
| `.claude/haios/README.md` | **MUST:** Lists modules directory | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_governance_layer.py -v
# Expected: 8 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (8 tests for GovernanceLayer)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated (.claude/haios/modules/README.md, .claude/haios/README.md)
- [ ] **MUST:** No consumer migration (strangler fig pattern)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- L4-implementation.md: GovernanceLayer functional requirements (lines 161-175)
- INV-052: HAIOS Architecture Reference (module design)
- INV-053: HAIOS Modular Architecture Review (consolidation decision)
- E2-246: Config Consolidation MVP (prerequisite - provides ConfigLoader)

---
