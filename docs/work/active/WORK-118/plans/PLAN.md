---
template: implementation_plan
status: complete
date: 2026-02-11
backlog_id: WORK-118
title: "Implement CeremonyLifecycleDistinction (CH-013)"
author: Hephaestus
lifecycle_phase: plan
session: 342
version: "1.5"
generated: 2026-02-11
last_updated: 2026-02-11T18:55:59
---
# Implementation Plan: Implement CeremonyLifecycleDistinction (CH-013)

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

Establish code-level distinction between lifecycles (artifact production) and ceremonies (state changes) via a CeremonyRunner thin wrapper, `type:` field in skill frontmatter, and CEREMONY_PHASES split from CYCLE_PHASES — without renaming existing skill directories (deferred due to blast radius).

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 5 | cycle_runner.py, governance_layer.py, ~15 skill SKILL.md files, 1 test file |
| Lines of code affected | ~200 | New CeremonyRunner (~80 LOC), CEREMONY_PHASES extraction (~20), skill frontmatter additions (~15 files × 1 line) |
| New files to create | 2 | `ceremony_runner.py`, `tests/test_ceremony_runner.py` |
| Tests to write | 8 | CeremonyRunner unit tests + CYCLE_PHASES/CEREMONY_PHASES split tests |
| Dependencies | 3 | governance_layer.py (ceremony_context), cycle_runner.py (CYCLE_PHASES), CycleRunner consumers |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | CeremonyRunner wraps existing ceremony_context; CYCLE_PHASES consumers |
| Risk of regression | Low | Additive changes; existing CycleRunner untouched except phase extraction |
| External dependencies | Low | No external APIs; all internal modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 20 min | High |
| CeremonyRunner + CEREMONY_PHASES | 30 min | High |
| Skill frontmatter `type:` field | 20 min | High |
| Consumer verification | 15 min | Med |
| **Total** | ~85 min | |

---

## Current State vs Desired State

### Current State

```python
# cycle_runner.py:134-142 — single dict holds ALL phases (lifecycles + ceremonies)
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"],
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],       # ceremony
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],                  # ceremony
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"], # ceremony
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],      # lifecycle
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],               # ceremony
}
```

**Behavior:** CycleRunner.get_cycle_phases() returns phases for both lifecycles and ceremonies. No code-level distinction exists. No `type:` field in skill frontmatter.

**Result:** Agent cannot programmatically determine whether a skill is a lifecycle (produces artifacts) or ceremony (produces state changes). REQ-CEREMONY-003 not satisfied.

### Desired State

```python
# cycle_runner.py — only lifecycle phases
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
}

# ceremony_runner.py — ceremony phases + thin wrapper around ceremony_context
CEREMONY_PHASES: Dict[str, List[str]] = {
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}

class CeremonyRunner:
    """Thin wrapper: validates ceremony phases + delegates to ceremony_context."""
    def get_ceremony_phases(self, ceremony_id: str) -> List[str]: ...
    def invoke(self, ceremony: str, work_id: str, **inputs) -> CeremonyResult: ...
```

**Behavior:** Lifecycles and ceremonies have separate phase registries and separate runner classes. Each skill declares `type: lifecycle` or `type: ceremony` in frontmatter.

**Result:** REQ-CEREMONY-003 satisfied. Agent can distinguish ceremonies from lifecycles programmatically.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: CeremonyRunner returns ceremony phases
```python
def test_ceremony_runner_get_phases():
    runner = CeremonyRunner(governance=MockGovernance())
    phases = runner.get_ceremony_phases("close-work-cycle")
    assert phases == ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]
```

### Test 2: CeremonyRunner returns empty for unknown ceremony
```python
def test_ceremony_runner_unknown_returns_empty():
    runner = CeremonyRunner(governance=MockGovernance())
    assert runner.get_ceremony_phases("nonexistent") == []
```

### Test 3: CeremonyRunner does NOT contain lifecycle phases
```python
def test_ceremony_phases_exclude_lifecycles():
    from ceremony_runner import CEREMONY_PHASES
    lifecycle_names = ["implementation-cycle", "investigation-cycle", "plan-authoring-cycle"]
    for name in lifecycle_names:
        assert name not in CEREMONY_PHASES
```

### Test 4: CycleRunner still returns lifecycle phases (backward compat)
```python
def test_cycle_runner_still_has_lifecycle_phases():
    runner = CycleRunner(governance=MockGovernance())
    assert runner.get_cycle_phases("implementation-cycle") == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]
```

### Test 5: CycleRunner no longer has ceremony phases
```python
def test_cycle_phases_exclude_ceremonies():
    from cycle_runner import CYCLE_PHASES
    ceremony_names = ["close-work-cycle", "checkpoint-cycle", "work-creation-cycle", "observation-triage-cycle"]
    for name in ceremony_names:
        assert name not in CYCLE_PHASES
```

### Test 6: CeremonyResult has state-change semantics
```python
def test_ceremony_result_dataclass():
    result = CeremonyResult(ceremony_id="close-work", work_id="WORK-118", side_effects=["status_change"])
    assert result.ceremony_id == "close-work"
    assert len(result.side_effects) == 1
```

### Test 7: CeremonyRunner.invoke wraps ceremony_context
```python
def test_ceremony_runner_invoke_uses_context(monkeypatch):
    contexts_entered = []
    @contextmanager
    def mock_ceremony_context(name):
        contexts_entered.append(name)
        yield CeremonyContext(ceremony_name=name)
    monkeypatch.setattr("ceremony_runner.ceremony_context", mock_ceremony_context)
    runner = CeremonyRunner(governance=MockGovernance())
    runner.invoke("close-work", work_id="WORK-118")
    assert "close-work" in contexts_entered
```

### Test 8: Backward compatibility — get_cycle_phases falls back to CEREMONY_PHASES
```python
def test_cycle_runner_fallback_to_ceremony_phases():
    """CycleRunner.get_cycle_phases still resolves ceremony IDs via fallback."""
    runner = CycleRunner(governance=MockGovernance())
    # Should still work via fallback (backward compat)
    phases = runner.get_cycle_phases("close-work-cycle")
    assert len(phases) > 0  # Resolved via CEREMONY_PHASES fallback
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

### Change 1: New file `ceremony_runner.py`

**File:** `.claude/haios/modules/ceremony_runner.py` (NEW)

```python
"""
CeremonyRunner Module (WORK-118, CH-013)

Thin wrapper for ceremony phase validation and invocation.
Delegates state-change enforcement to ceremony_context() from governance_layer.

Ceremonies produce state changes (WHEN). Lifecycles produce artifacts (WHAT).
Per REQ-CEREMONY-003: these are distinct concepts.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

# Sibling import pattern (matches cycle_runner.py)
try:
    from .governance_layer import GovernanceLayer, GateResult, ceremony_context, CeremonyContext
except ImportError:
    from governance_layer import GovernanceLayer, GateResult, ceremony_context, CeremonyContext

import sys
from pathlib import Path
_lib_path = Path(__file__).parent.parent / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from governance_events import log_phase_transition


@dataclass
class CeremonyResult:
    """Result of a ceremony invocation."""
    ceremony_id: str
    work_id: str
    side_effects: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: Literal["success", "failure"] = "success"


# Ceremony phase definitions — extracted from CYCLE_PHASES
CEREMONY_PHASES: Dict[str, List[str]] = {
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}


class CeremonyRunner:
    """Ceremony phase validator and invoker.

    Thin wrapper around ceremony_context(). Does NOT replace CycleRunner —
    CycleRunner handles lifecycles, CeremonyRunner handles ceremonies.
    """

    def __init__(self, governance: GovernanceLayer):
        self._governance = governance

    def get_ceremony_phases(self, ceremony_id: str) -> List[str]:
        """Return ordered phases for a ceremony."""
        return CEREMONY_PHASES.get(ceremony_id, [])

    def invoke(self, ceremony: str, work_id: str, **inputs) -> CeremonyResult:
        """Invoke ceremony within ceremony_context boundary.

        Args:
            ceremony: Ceremony name (e.g., "close-work")
            work_id: Work item ID
            **inputs: Ceremony-specific inputs

        Returns:
            CeremonyResult with side effects logged
        """
        with ceremony_context(ceremony) as ctx:
            ctx.log_side_effect("ceremony_invoked", {
                "work_id": work_id, **inputs
            })
            log_phase_transition(ceremony, work_id, "Hephaestus")
            return CeremonyResult(
                ceremony_id=ceremony,
                work_id=work_id,
                side_effects=[str(se) for se in ctx.side_effects],
            )
```

### Change 2: Extract ceremony phases from CYCLE_PHASES

**File:** `.claude/haios/modules/cycle_runner.py`
**Location:** Lines 134-142 (`CYCLE_PHASES` dict)

**Current Code:**
```python
# cycle_runner.py:134-142
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"],
    "close-work-cycle": ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"],
    "work-creation-cycle": ["VERIFY", "POPULATE", "READY"],
    "checkpoint-cycle": ["SCAFFOLD", "FILL", "VERIFY", "CAPTURE", "COMMIT"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
    "observation-triage-cycle": ["SCAN", "TRIAGE", "PROMOTE"],
}
```

**Changed Code:**
```python
# cycle_runner.py — lifecycle phases only
CYCLE_PHASES: Dict[str, List[str]] = {
    "implementation-cycle": ["PLAN", "DO", "CHECK", "DONE", "CHAIN"],
    "investigation-cycle": ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"],
    "plan-authoring-cycle": ["ANALYZE", "AUTHOR", "VALIDATE", "CHAIN"],
}
```

**Backward compat in get_cycle_phases():**
```python
def get_cycle_phases(self, cycle_id: str) -> List[str]:
    """Return ordered phases for a cycle. Falls back to CEREMONY_PHASES."""
    from ceremony_runner import CEREMONY_PHASES
    return CYCLE_PHASES.get(cycle_id, CEREMONY_PHASES.get(cycle_id, []))
```

### Change 3: Add `type:` field to skill frontmatter

Each skill SKILL.md gets a `type:` field in its YAML frontmatter (if it has one) or as a comment header.

**Lifecycle skills** (type: lifecycle):
- implementation-cycle, investigation-cycle, plan-authoring-cycle, survey-cycle, ground-cycle, design-review-validation, dod-validation-cycle, plan-validation-cycle

**Ceremony skills** (type: ceremony):
- close-work-cycle, checkpoint-cycle, work-creation-cycle, observation-capture-cycle, observation-triage-cycle, close-chapter-ceremony, close-arc-ceremony, close-epoch-ceremony, session-start-ceremony, session-end-ceremony, memory-commit-ceremony, spawn-work-ceremony, queue-intake, queue-commit, queue-prioritize, queue-unpark

**Pattern (add at top of SKILL.md):**
```markdown
<!-- type: ceremony -->
# Close Work Cycle
```

### Call Chain Context

```
Skill invocation (Claude interprets SKILL.md)
    |
    +-> just set-cycle {skill} {phase} {work_id}    # existing
    |       |
    |       +-> CycleRunner.check_phase_entry()      # for lifecycles
    |       +-> CeremonyRunner.get_ceremony_phases()  # for ceremonies (NEW)
    |
    +-> ceremony_context(name)                        # for ceremonies (existing from CH-012)
    |       |
    |       +-> CeremonyRunner.invoke()               # NEW thin wrapper
    |
    +-> CycleRunner.run()                             # for lifecycles (existing)
```

### Function/Component Signatures

```python
class CeremonyRunner:
    def __init__(self, governance: GovernanceLayer): ...

    def get_ceremony_phases(self, ceremony_id: str) -> List[str]:
        """Return ordered phases for a ceremony.
        Returns empty list if ceremony_id not found."""

    def invoke(self, ceremony: str, work_id: str, **inputs) -> CeremonyResult:
        """Invoke ceremony within ceremony_context boundary.
        Raises CeremonyNestingError if already inside ceremony."""

@dataclass
class CeremonyResult:
    ceremony_id: str
    work_id: str
    side_effects: List[str]
    timestamp: datetime
    status: Literal["success", "failure"]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| CeremonyRunner as thin wrapper | Wraps ceremony_context(), not parallel to CycleRunner | CH-012 proved ceremony_context() works (memory 84320, 84790). CeremonyRunner adds phase validation on top, not a competing runtime. |
| Defer skill directory renames | Keep `-cycle` suffix on existing ceremony skill dirs | 391 refs across 107 files. Rename is CH-013 R2 but blast radius too high for single work item. Queue as WORK-119. |
| Backward compat fallback in get_cycle_phases | CycleRunner falls back to CEREMONY_PHASES | Consumers calling get_cycle_phases("close-work-cycle") must not break. Fallback import keeps them working. |
| `type:` as YAML frontmatter field | `type: ceremony` inside `---` block | HTML comment before `---` broke frontmatter parsing in test_ceremony_retrofit.py. YAML field is machine-parseable and consistent with existing frontmatter pattern. |
| Memory query results | Found ceremony-as-wrapper pattern (84182, 84188), PreToolUse interception (84320), ceremony_context adoption (84790) | All confirm: wrap existing ceremony_context, don't build parallel system. |

### Input/Output Examples

**Before (current):**
```python
runner = CycleRunner(governance=gov)
runner.get_cycle_phases("close-work-cycle")
# Returns: ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]
# Problem: No way to know this is a ceremony, not a lifecycle
```

**After (target):**
```python
cycle_runner = CycleRunner(governance=gov)
ceremony_runner = CeremonyRunner(governance=gov)

cycle_runner.get_cycle_phases("implementation-cycle")
# Returns: ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]  — lifecycle

ceremony_runner.get_ceremony_phases("close-work-cycle")
# Returns: ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]  — ceremony

# Backward compat still works:
cycle_runner.get_cycle_phases("close-work-cycle")
# Returns: ["VALIDATE", "OBSERVE", "ARCHIVE", "MEMORY"]  — via fallback
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Unknown ceremony_id | get_ceremony_phases returns [] | Test 2 |
| CeremonyRunner.invoke inside existing ceremony | CeremonyNestingError from ceremony_context | Inherits from governance_layer tests |
| Lifecycle ID passed to CeremonyRunner | Returns [] (not an error) | Test 2 (same behavior) |
| Ceremony ID passed to CycleRunner after split | Backward compat fallback returns phases | Test 8 |
| Skill with no type comment | Treated as unknown; no runtime effect (type is advisory) | N/A (documentation-only) |

### Open Questions

**Q: Should `just set-cycle` differentiate between lifecycle and ceremony?**

No — `just set-cycle` is a thin shell command that writes state. CeremonyRunner/CycleRunner are the code-level distinction. The justfile recipe remains unified. TBD if future work adds `just set-ceremony`.

**Q: Should dod-validation-cycle and plan-validation-cycle be lifecycle or ceremony?**

They are validation lifecycles (produce verdicts), not ceremonies (no state changes). Classified as `type: lifecycle`.

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
| CeremonyRunner architecture | [Follow CH-013 as-is, Evolve CH-013, Scope down to naming+typing] | Evolve CH-013 | CH-012 proved ceremony_context() works at hook level (memory 84320, 84790). CeremonyRunner becomes thin wrapper, not parallel class. Operator decided S342. |
| Defer skill renames | [Rename now, Defer to separate WORK item] | Defer | 391 refs across 107 files. Blast radius too high. Queue as WORK-119 (companion item per MEMORY pattern). |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_ceremony_runner.py`
- [ ] Write Tests 1-8 from Tests First section
- [ ] Verify all tests fail (red) — CeremonyRunner doesn't exist yet

### Step 2: Create CeremonyRunner module
- [ ] Create `.claude/haios/modules/ceremony_runner.py` with CeremonyResult + CEREMONY_PHASES + CeremonyRunner class
- [ ] Follow sibling import pattern from cycle_runner.py (try/except conditional imports)
- [ ] Tests 1, 2, 3, 6, 7 pass (green)

### Step 3: Extract ceremony phases from CYCLE_PHASES
- [ ] Remove ceremony entries from CYCLE_PHASES in cycle_runner.py
- [ ] Add backward-compat fallback in CycleRunner.get_cycle_phases()
- [ ] Tests 4, 5, 8 pass (green)

### Step 4: Add `type:` comment to skill frontmatter
- [ ] Add `<!-- type: lifecycle -->` to: implementation-cycle, investigation-cycle, plan-authoring-cycle, survey-cycle, ground-cycle, design-review-validation, dod-validation-cycle, plan-validation-cycle
- [ ] Add `<!-- type: ceremony -->` to: close-work-cycle, checkpoint-cycle, work-creation-cycle, observation-capture-cycle, observation-triage-cycle, close-chapter-ceremony, close-arc-ceremony, close-epoch-ceremony, session-start-ceremony, session-end-ceremony, memory-commit-ceremony, spawn-work-ceremony, queue-intake, queue-commit, queue-prioritize, queue-unpark

### Step 5: Integration Verification
- [ ] All 8 new tests pass
- [ ] Run full test suite — no regressions
- [ ] Verify CycleRunner backward compat: `get_cycle_phases("close-work-cycle")` still works

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with ceremony_runner.py
- [ ] **MUST:** Verify README content matches actual file state

### Step 7: Queue companion work item for skill renames
- [ ] Create WORK-119 for `-cycle` → `-ceremony` skill directory renames (deferred blast radius)
- [ ] Link WORK-119 as `enables` from WORK-118

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backward compat break in get_cycle_phases | High | Fallback import from CEREMONY_PHASES ensures existing callers still work |
| Circular import: ceremony_runner ↔ cycle_runner | Med | ceremony_runner imports from governance_layer only, not from cycle_runner. No circular dependency. |
| `just set-cycle` breaks for ceremony skills | Med | `just set-cycle` writes raw state and doesn't validate against CYCLE_PHASES — unaffected |
| Skill type comment not machine-parseable | Low | HTML comments are greppable; formal parsing deferred to assets arc (CH-023) |
| Spec misalignment: CH-013 says rename skills | Low | Operator decided to defer renames (S342). Update CH-013 scope notes. |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 342 | 2026-02-11 | TBD | Plan authored | WORK-118 created, plan authored, operator decided evolve CH-013 + defer renames |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-118/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| CeremonyRunner class in ceremony_runner.py | [ ] | Read file, verify class exists |
| CeremonyResult dataclass | [ ] | Read file, verify dataclass |
| `type: lifecycle\|ceremony` in skill frontmatter | [ ] | Grep for `<!-- type:` across skills |
| CYCLE_PHASES split | [ ] | Read cycle_runner.py, verify no ceremony entries |
| Rename ceremony skills (DEFERRED) | N/A | Deferred to WORK-119 per operator decision |
| Update all consumers of renamed skills (DEFERRED) | N/A | Deferred to WORK-119 |
| Unit tests for CeremonyRunner | [ ] | pytest test_ceremony_runner.py passes |
| Unit tests verifying CycleRunner no longer has ceremony phases | [ ] | Test 5 in test_ceremony_runner.py |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/ceremony_runner.py` | CeremonyRunner class + CEREMONY_PHASES + CeremonyResult | [ ] | |
| `.claude/haios/modules/cycle_runner.py` | CYCLE_PHASES has only lifecycle entries; get_cycle_phases has fallback | [ ] | |
| `tests/test_ceremony_runner.py` | 8 tests, all passing | [ ] | |
| `.claude/haios/modules/README.md` | Lists ceremony_runner.py | [ ] | |
| Grep: `<!-- type:` in `.claude/skills/` | Present in all skill SKILL.md files | [ ] | |

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

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-013-CeremonyLifecycleDistinction.md (chapter spec)
- @.claude/haios/modules/cycle_runner.py (existing CycleRunner + CYCLE_PHASES)
- @.claude/haios/modules/governance_layer.py (ceremony_context, CeremonyContext)
- @.claude/haios/lib/queue_ceremonies.py (_ceremony_context_safe pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-003)
- Memory: 84320 (PreToolUse interception decision), 84790 (ceremony_context adoption)

---
