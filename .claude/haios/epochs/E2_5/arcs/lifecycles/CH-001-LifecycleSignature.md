# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T19:44:16
# Chapter: Lifecycle Signature

## Definition

**Chapter ID:** CH-001
**Arc:** lifecycles
**Status:** Planned
**Implementation Type:** REFACTOR
**Depends:** None
**Work Items:** WORK-084

---

## Current State (Verified)

**Source:** `.claude/haios/modules/cycle_runner.py`

CycleRunner exists as a stateless phase gate validator (E2-255). Current API:

```python
# Actual current methods (cycle_runner.py:113-148)
def get_cycle_phases(cycle_id: str) -> List[str]
def check_phase_entry(cycle_id: str, phase: str, work_id: str) -> GateResult
def check_phase_exit(cycle_id: str, phase: str, work_id: str) -> GateResult
```

**Key design decision (docstring lines 17-18):**
> "CycleRunner validates gates, does NOT orchestrate. Skills remain markdown files that Claude interprets."

**What exists:**
- CycleResult dataclass with `outcome: Literal["completed", "blocked", "chain"]`
- CYCLE_PHASES dict with 7 cycle definitions
- Phase entry/exit gate checking
- No `run()` method - Claude interprets skill markdown directly

**What doesn't exist:**
- Typed lifecycle output objects
- Output schema definitions
- `run()` or `chain()` methods

---

## Problem

CycleRunner validates gates but doesn't return typed outputs. Skills complete via markdown interpretation with implicit chaining in CHAIN phases.

Gap to address:
- No typed return objects (Findings, Specification, etc.)
- CHAIN phases in skills prompt for next lifecycle (soft auto-chain)
- No explicit pure function signature

---

## Agent Need

> "I need lifecycles to be pure functions with explicit Input → Output signatures so I can reason about what each lifecycle produces without implicit side effects."

---

## Requirements

### R1: Pure Function Signatures (REQ-LIFECYCLE-001)

Each lifecycle must have explicit signature:

```
Investigation: Question → Findings
Design:        Requirements → Specification
Implementation: Specification → Artifact
Validation:    Artifact × Spec → Verdict
Triage:        [Items] → [PrioritizedItems]
```

CycleRunner.run() returns the typed output, does not trigger next lifecycle.

### R2: Independent Completion

Lifecycles are independently completable. Design can complete without spawning implementation. Investigation can complete with just findings, no action required.

---

## Interface

### CycleRunner API Changes

```python
# Before (implicit chaining)
cycle_runner.run(work_id, lifecycle="design")  # auto-chains to implementation

# After (pure function)
output = cycle_runner.run(work_id, lifecycle="design")  # returns Specification
# Caller decides: store output, pipe to next, or do nothing
```

### Output Types

| Lifecycle | Output Type | Schema |
|-----------|-------------|--------|
| Investigation | Findings | findings_schema |
| Design | Specification | spec_schema |
| Implementation | Artifact | artifact_schema |
| Validation | Verdict | verdict_schema |
| Triage | PriorityList | queue_schema |

### Output Type Definitions (Prerequisite)

**NOTE:** These types must be defined before implementation. See CH-023 (Assets Arc) for full type definitions.

```python
@dataclass
class LifecycleOutput:
    """Base class for all lifecycle outputs."""
    lifecycle: str
    work_id: str
    timestamp: datetime
    status: Literal["success", "failure", "partial"]

@dataclass
class Findings(LifecycleOutput):
    question: str
    conclusions: List[str]
    evidence: List[str]
    open_questions: List[str]

@dataclass
class Specification(LifecycleOutput):
    requirements: List[str]
    design_decisions: List[str]
    interfaces: Dict[str, Any]

# ... remaining types defined in CH-023
```

### Failure Handling

Lifecycle can return with `status: failure` or `status: partial`:

```python
output = cycle_runner.run(work_id, lifecycle="design")
if output.status == "failure":
    # Caller handles - may retry, escalate, or abandon
    pass
elif output.status == "partial":
    # Lifecycle produced some output but didn't fully complete
    # Caller decides whether to accept partial output
    pass
```

**No implicit retry.** Failure returns to caller for decision.

---

## Success Criteria

- [ ] CycleRunner.run() returns typed output object
- [ ] No auto-chaining to next lifecycle
- [ ] Each lifecycle has documented Input → Output signature
- [ ] Unit tests verify pure function behavior (no side effects)
- [ ] Integration test: Design completes, returns Specification, no implementation spawned

---

## Non-Goals

- Implementing all lifecycle phase templates (see CH-005, CH-006)
- Queue integration (see Arc 2: Queue)
- Ceremony triggers (see Arc 3: Ceremonies)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-001)
- @.claude/haios/epochs/E2_4/architecture/S27-breath-model.md (breath model)
