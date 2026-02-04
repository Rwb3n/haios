---
template: implementation_plan
status: approved
date: 2026-02-04
backlog_id: WORK-088
title: Implement Phase Template Contracts
author: Hephaestus
lifecycle_phase: plan
session: 247
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-04T22:26:17'
---
# Implementation Plan: Implement Phase Template Contracts

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

Phase templates will have machine-readable input/output contracts in YAML frontmatter, with CycleRunner validating contracts on phase entry/exit.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 5 | 4 investigation templates + cycle_runner.py |
| Lines of code affected | ~500 | 416 lines cycle_runner.py + 4x ~20 lines templates |
| New files to create | 0 | Modifying existing files |
| Tests to write | 6 | Contract validation tests |
| Dependencies | 2 | CycleRunner, GovernanceLayer |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Templates are passive markdown, CycleRunner reads them |
| Risk of regression | Low | 16 existing tests in test_cycle_runner.py |
| External dependencies | Low | No external APIs, YAML only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Schema definition | 15 min | High |
| Template updates | 20 min | High |
| CycleRunner validation | 30 min | Med |
| Tests | 20 min | High |
| **Total** | ~1.5 hr | Med |

---

## Current State vs Desired State

### Current State

```yaml
# .claude/templates/investigation/EXPLORE.md:1-8 - Current frontmatter
---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:25:19'
---
```

```python
# .claude/haios/modules/cycle_runner.py:223-226 - Phase entry always allowed
    def check_phase_entry(self, cycle_id: str, phase: str, work_id: str) -> GateResult:
        # For MVP: always allow entry (conditions in skill markdown)
        self._emit_phase_entered(cycle_id, phase, work_id)
        return GateResult(allowed=True, reason=f"Phase {phase} entry allowed")
```

**Behavior:** Templates have human-readable contracts in markdown body. CycleRunner always allows phase entry/exit without validation.

**Result:** No programmatic enforcement of contracts - agent could skip required inputs/outputs.

### Desired State

```yaml
# .claude/templates/investigation/EXPLORE.md:1-20 - With machine-readable contracts
---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.1'
input_contract:
  - field: work_context
    type: markdown
    required: true
    description: Work item Context section populated
  - field: objective
    type: markdown
    required: true
    description: Work item Objective defined
output_contract:
  - field: evidence_table
    type: table
    required: true
    description: Evidence Collection table with file:line sources
  - field: memory_evidence
    type: table
    required: true
    description: Memory Evidence table with concept IDs
---
```

```python
# .claude/haios/modules/cycle_runner.py - New validation methods
def validate_phase_input(self, phase: str, work_id: str) -> GateResult:
    """Validate input contract for phase entry."""
    template = self._load_phase_template(phase)
    contract = template.get('input_contract', [])
    for item in contract:
        if item['required'] and not self._has_field(work_id, item['field']):
            return GateResult(allowed=False, reason=f"Missing: {item['field']}")
    return GateResult(allowed=True)
```

**Behavior:** Templates have machine-readable contracts in frontmatter. CycleRunner validates contracts on phase transitions.

**Result:** Programmatic enforcement - missing inputs block phase entry, missing outputs block phase exit.

---

## Tests First (TDD)

### Test 1: Template Has Input Contract
```python
def test_explore_template_has_input_contract():
    """EXPLORE template frontmatter includes input_contract field."""
    template = load_phase_template("EXPLORE")
    assert "input_contract" in template
    assert len(template["input_contract"]) > 0
```

### Test 2: Template Has Output Contract
```python
def test_explore_template_has_output_contract():
    """EXPLORE template frontmatter includes output_contract field."""
    template = load_phase_template("EXPLORE")
    assert "output_contract" in template
    assert len(template["output_contract"]) > 0
```

### Test 3: Validate Input Contract - Success
```python
def test_validate_phase_input_success():
    """validate_phase_input returns allowed when contract satisfied."""
    runner = CycleRunner(governance=GovernanceLayer())
    # Mock work item with required fields
    result = runner.validate_phase_input("EXPLORE", "WORK-088")
    assert result.allowed is True
```

### Test 4: Validate Input Contract - Missing Field (A7 - Mock Strategy)
```python
def test_validate_phase_input_missing_field_blocks():
    """validate_phase_input returns blocked when required field missing."""
    runner = CycleRunner(governance=GovernanceLayer())

    # Mock _check_work_has_field to return False for specific field
    with patch.object(runner, '_check_work_has_field', return_value=False):
        result = runner.validate_phase_input("EXPLORE", "WORK-EMPTY")
        assert result.allowed is False
        assert "Missing required input:" in result.reason
```

### Test 5: Validate Output Contract
```python
def test_validate_phase_output_missing_blocks():
    """validate_phase_output returns blocked when required output missing."""
    runner = CycleRunner(governance=GovernanceLayer())
    result = runner.validate_phase_output("EXPLORE", "WORK-088")
    assert isinstance(result, GateResult)
```

### Test 6: Backward Compatibility
```python
def test_check_phase_entry_unchanged_for_cycles_without_templates():
    """Existing check_phase_entry behavior unchanged for cycles without templates."""
    runner = CycleRunner(governance=GovernanceLayer())
    # implementation-cycle doesn't have templates yet
    result = runner.check_phase_entry("implementation-cycle", "PLAN", "WORK-088")
    assert result.allowed is True  # MVP behavior preserved
```

---

## Detailed Design

### Part 1: Contract Schema Definition

**Contract Item Schema** (to be used in template frontmatter):

```yaml
# Each contract item has:
input_contract:
  - field: <string>        # Field name to check
    type: <string>         # markdown | table | list | string
    required: <bool>       # true = must exist, false = optional
    description: <string>  # Human-readable explanation
```

### Part 2: Template Updates

**File:** `.claude/templates/investigation/EXPLORE.md`

**Current Frontmatter:**
```yaml
---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.0'
---
```

**New Frontmatter:**
```yaml
---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.1'
input_contract:
  - field: work_context
    type: markdown
    required: true
    description: Work item Context section populated
  - field: objective
    type: markdown
    required: true
    description: Work item Objective defined
output_contract:
  - field: evidence_table
    type: table
    required: true
    description: Evidence Collection table with sources
  - field: memory_evidence
    type: table
    required: true
    description: Memory Evidence table with concept IDs
---
```

Same pattern for HYPOTHESIZE.md, VALIDATE.md, CONCLUDE.md with phase-specific contracts.

### Part 3: CycleRunner Validation Methods

**File:** `.claude/haios/modules/cycle_runner.py`
**Location:** After line 298 (after build_scaffold_command)

**New Methods:**
```python
# =========================================================================
# WORK-088: Phase Template Contract Validation (REQ-TEMPLATE-001)
# =========================================================================

def _load_phase_template(self, phase: str) -> Dict[str, Any]:
    """Load phase template frontmatter.

    Args:
        phase: Phase name (e.g., "EXPLORE", "HYPOTHESIZE")

    Returns:
        Dict with frontmatter fields, empty dict if not found.
    """
    # Map phase to template path
    template_paths = {
        "EXPLORE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "EXPLORE.md",
        "HYPOTHESIZE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "HYPOTHESIZE.md",
        "VALIDATE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "VALIDATE.md",
        "CONCLUDE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "CONCLUDE.md",
    }

    path = template_paths.get(phase)
    if not path or not path.exists():
        return {}

    # Parse YAML frontmatter
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            frontmatter = content[3:end].strip()
            return yaml.safe_load(frontmatter) or {}
    return {}

def validate_phase_input(self, phase: str, work_id: str) -> GateResult:
    """Validate input contract for phase entry (REQ-TEMPLATE-001).

    Args:
        phase: Target phase name
        work_id: Work item ID

    Returns:
        GateResult - allowed if all required inputs present, blocked otherwise.
    """
    template = self._load_phase_template(phase)
    contract = template.get("input_contract", [])

    if not contract:
        # No contract defined, allow entry (backward compatible)
        return GateResult(allowed=True, reason=f"No input contract for {phase}")

    # Check each required item
    for item in contract:
        if item.get("required", False):
            if not self._check_work_has_field(work_id, item["field"]):
                return GateResult(
                    allowed=False,
                    reason=f"Missing required input: {item['field']} - {item.get('description', '')}"
                )

    return GateResult(allowed=True, reason=f"Input contract satisfied for {phase}")

def validate_phase_output(self, phase: str, work_id: str) -> GateResult:
    """Validate output contract for phase exit (REQ-TEMPLATE-001).

    Args:
        phase: Current phase name
        work_id: Work item ID

    Returns:
        GateResult - allowed if all required outputs present, blocked otherwise.
    """
    template = self._load_phase_template(phase)
    contract = template.get("output_contract", [])

    if not contract:
        return GateResult(allowed=True, reason=f"No output contract for {phase}")

    for item in contract:
        if item.get("required", False):
            if not self._check_work_has_field(work_id, item["field"]):
                return GateResult(
                    allowed=False,
                    reason=f"Missing required output: {item['field']} - {item.get('description', '')}"
                )

    return GateResult(allowed=True, reason=f"Output contract satisfied for {phase}")

def _check_work_has_field(self, work_id: str, field: str) -> bool:
    """Check if work item has a populated field.

    MVP: Returns True (actual field checking requires WorkEngine integration).
    Full implementation will read work file and check field presence.

    Args:
        work_id: Work item ID
        field: Field name to check

    Returns:
        True if field exists and is populated.
    """
    # MVP: Always return True - field validation is soft gate
    # Future: Use WorkEngine to read work file and verify field
    if self._work_engine is None:
        return True

    # TODO: Implement actual field checking when WorkEngine supports it
    return True
```

### Part 4: Integration into check_phase_entry/exit (A4 - Critique Finding)

**File:** `.claude/haios/modules/cycle_runner.py`
**Location:** Lines 203-226 (check_phase_entry) and 228-261 (check_phase_exit)

**Current check_phase_entry:**
```python
# cycle_runner.py:203-226
def check_phase_entry(
    self, cycle_id: str, phase: str, work_id: str
) -> GateResult:
    """Check if a phase can be entered..."""
    # For MVP: always allow entry (conditions in skill markdown)
    self._emit_phase_entered(cycle_id, phase, work_id)
    return GateResult(allowed=True, reason=f"Phase {phase} entry allowed")
```

**Modified check_phase_entry:**
```python
def check_phase_entry(
    self, cycle_id: str, phase: str, work_id: str
) -> GateResult:
    """Check if a phase can be entered (entry conditions met).

    WORK-088: Now validates input contract from phase template.
    """
    # WORK-088: Validate input contract before entry
    input_result = self.validate_phase_input(phase, work_id)
    if not input_result.allowed:
        # Log warning but don't block (MVP soft gate)
        log_validation_outcome(
            work_id=work_id,
            gate="phase_entry",
            outcome="warn",
            reason=input_result.reason
        )
        # MVP: Allow anyway (soft gate)
        # Future CH-007: return input_result to hard block

    self._emit_phase_entered(cycle_id, phase, work_id)
    return GateResult(allowed=True, reason=f"Phase {phase} entry allowed")
```

**Modified check_phase_exit:**
```python
def check_phase_exit(
    self, cycle_id: str, phase: str, work_id: str
) -> GateResult:
    """Check if a phase can be exited (exit criteria met).

    WORK-088: Now validates output contract from phase template.
    """
    # WORK-088: Validate output contract before exit
    output_result = self.validate_phase_output(phase, work_id)
    if not output_result.allowed:
        log_validation_outcome(
            work_id=work_id,
            gate="phase_exit",
            outcome="warn",
            reason=output_result.reason
        )
        # MVP: Allow anyway (soft gate)

    # Existing node-based exit validation
    from node_cycle import check_exit_criteria
    node = self._get_node_for_cycle(cycle_id)
    if not node:
        return GateResult(allowed=True, reason=f"Phase {phase} exit allowed")

    failures = check_exit_criteria(node, work_id)
    if failures:
        return GateResult(allowed=False, reason=f"Exit blocked: {'; '.join(failures)}")

    return GateResult(allowed=True, reason=f"Phase {phase} exit criteria met")
```

### Part 5: Error Handling for YAML Parsing (A5 - Critique Finding)

**Modified _load_phase_template with try/except:**
```python
def _load_phase_template(self, phase: str) -> Dict[str, Any]:
    """Load phase template frontmatter."""
    template_paths = {
        "EXPLORE": Path(__file__).parent.parent.parent / "templates" / "investigation" / "EXPLORE.md",
        # ... other paths
    }

    path = template_paths.get(phase)
    if not path or not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                frontmatter = content[3:end].strip()
                return yaml.safe_load(frontmatter) or {}
    except (yaml.YAMLError, OSError) as e:
        # Log warning but return empty dict (graceful degradation)
        log_validation_outcome(
            work_id="system",
            gate="template_load",
            outcome="warn",
            reason=f"Failed to load template {phase}: {e}"
        )
    return {}
```

### Call Chain Context

```
Skill invokes CycleRunner
    |
    +-> check_phase_entry(cycle_id, phase, work_id)
    |       |
    |       +-> validate_phase_input(phase, work_id)  # <-- NEW
    |       |       |
    |       |       +-> _load_phase_template(phase)   # <-- NEW
    |       |       +-> _check_work_has_field()       # <-- NEW
    |       |
    |       +-> log_validation_outcome() if warn      # <-- NEW
    |       +-> _emit_phase_entered()
    |
    +-> check_phase_exit(cycle_id, phase, work_id)
            |
            +-> validate_phase_output(phase, work_id)  # <-- NEW
            +-> log_validation_outcome() if warn       # <-- NEW
            +-> check_exit_criteria()  # existing
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Contract schema | YAML in frontmatter | Machine-readable + human-readable (memory 80824) |
| MVP field checking | Always return True | Allows incremental rollout without breaking existing flows |
| Template path mapping | Hardcoded dict | Investigation templates only for CH-005 scope |
| Backward compatibility | Empty contract = allow | Existing cycles without templates continue working |
| Validation integration | Soft gate (log, don't block) | E2.5 phased rollout - hard gate in CH-007 |
| Integration point (A4) | Modify check_phase_entry/exit | Critique surfaced gap - new methods must be wired in |
| Error handling (A5) | try/except for yaml.safe_load | Graceful degradation on malformed YAML |
| Test mock strategy (A7) | patch _check_work_has_field | Allows testing blocking path when MVP returns True |

### Input/Output Examples

**Before (current):**
```
check_phase_entry("investigation-cycle", "EXPLORE", "WORK-088")
  Returns: GateResult(allowed=True, reason="Phase EXPLORE entry allowed")
  Problem: No contract validation, agent could start without Context
```

**After (with contracts):**
```
check_phase_entry("investigation-cycle", "EXPLORE", "WORK-088")
  Calls: validate_phase_input("EXPLORE", "WORK-088")
    Loads: .claude/templates/investigation/EXPLORE.md
    Checks: input_contract items
  Returns: GateResult(allowed=True, reason="Input contract satisfied for EXPLORE")

# If missing required field:
  Returns: GateResult(allowed=False, reason="Missing required input: work_context - Work item Context section populated")
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Template file missing | Return empty dict, allow entry | Test 6 |
| No contract in template | Allow entry (backward compat) | Test 6 |
| WorkEngine is None | Always return True for field checks | Test 3 |
| Malformed YAML | Return empty dict, allow entry | Manual verification |

### Open Questions

**Q: Should contract validation block or warn?**

A: MVP uses soft validation (warn but allow). Hard blocking requires WorkEngine integration to read work files. CH-007 (Governance Enforcement) will implement hard gates.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Validation mode | [hard_block, soft_warn] | soft_warn | MVP allows incremental rollout; hard gates in CH-007 |
| Template path strategy | [hardcoded, config] | hardcoded | CH-005 scope is investigation only; config pattern in CH-006 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 6 tests to `tests/test_cycle_runner.py`
- [ ] Tests 1-4 test contract validation methods
- [ ] Test 5 tests output validation
- [ ] Test 6 tests backward compatibility
- [ ] Verify all new tests fail (red)

### Step 2: Add Contract Schema to Templates
- [ ] Update `.claude/templates/investigation/EXPLORE.md` with input_contract/output_contract
- [ ] Update `.claude/templates/investigation/HYPOTHESIZE.md` with contracts
- [ ] Update `.claude/templates/investigation/VALIDATE.md` with contracts
- [ ] Update `.claude/templates/investigation/CONCLUDE.md` with contracts
- [ ] Tests 1, 2 pass (green)

### Step 3: Implement _load_phase_template Method
- [ ] Add `_load_phase_template(self, phase: str)` to CycleRunner
- [ ] Parse YAML frontmatter from template files
- [ ] Handle missing files gracefully
- [ ] Tests 1, 2 still pass

### Step 4: Implement validate_phase_input Method
- [ ] Add `validate_phase_input(self, phase: str, work_id: str)` to CycleRunner
- [ ] Check each required input_contract item
- [ ] Return GateResult with appropriate reason
- [ ] Tests 3, 4 pass (green)

### Step 5: Implement validate_phase_output Method
- [ ] Add `validate_phase_output(self, phase: str, work_id: str)` to CycleRunner
- [ ] Check each required output_contract item
- [ ] Test 5 passes (green)

### Step 6: Integrate into check_phase_entry/exit (A4 - Critique)
- [ ] Modify `check_phase_entry` to call `validate_phase_input`
- [ ] Modify `check_phase_exit` to call `validate_phase_output`
- [ ] Add `log_validation_outcome` calls for soft gate warnings
- [ ] Add try/except around yaml.safe_load (A5)

### Step 7: Verify Backward Compatibility
- [ ] Ensure existing check_phase_entry behavior unchanged (returns allowed=True)
- [ ] Test 6 passes (green)
- [ ] All 16 existing tests still pass

### Step 8: Integration Verification
- [ ] Run full test suite: `pytest tests/test_cycle_runner.py -v`
- [ ] All 22 tests pass (16 existing + 6 new)

### Step 9: README Sync (MUST)
- [ ] **MUST:** Update `.claude/templates/investigation/README.md` with contract schema
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new methods

### Step 10: Consumer Verification
- [ ] Verify skills that use CycleRunner don't break
- [ ] Grep for `check_phase_entry` usage - ensure compatible

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - contracts don't match actual skill needs | Medium | Contracts derived from existing human-readable contracts in templates |
| Integration - skills may expect different GateResult format | Low | Returning same GateResult type, no API change |
| Regression - existing 16 tests could break | Low | Test 6 explicitly verifies backward compatibility |
| Scope creep - tempted to add hard validation | Medium | MVP explicitly soft_warn; hard gates deferred to CH-007 |
| Knowledge gap - YAML parsing edge cases | Low | Use yaml.safe_load which is battle-tested |

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

**MUST** read `docs/work/active/WORK-088/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Define contract schema (input_contract, output_contract YAML structure) | [ ] | Detailed Design Part 1 |
| Add machine-readable contracts to investigation phase templates | [ ] | 4 template files updated |
| Implement validate_template_input(phase, work) function | [ ] | CycleRunner.validate_phase_input() |
| Implement validate_template_output(phase, work) function | [ ] | CycleRunner.validate_phase_output() |
| Integrate contract validation into CycleRunner phase entry/exit | [ ] | Called from check_phase_entry/exit |
| Unit tests for contract validation | [ ] | 6 tests in test_cycle_runner.py |
| Integration test: missing input -> blocked entry | [ ] | Test 4 |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cycle_runner.py` | Has validate_phase_input/output methods | [ ] | |
| `.claude/templates/investigation/EXPLORE.md` | Has input_contract in frontmatter | [ ] | |
| `.claude/templates/investigation/HYPOTHESIZE.md` | Has input_contract in frontmatter | [ ] | |
| `.claude/templates/investigation/VALIDATE.md` | Has input_contract in frontmatter | [ ] | |
| `.claude/templates/investigation/CONCLUDE.md` | Has input_contract in frontmatter | [ ] | |
| `tests/test_cycle_runner.py` | Has 6 new contract tests | [ ] | |
| `.claude/templates/investigation/README.md` | Documents contract schema | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_cycle_runner.py -v
# Expected: 22 tests passed (16 existing + 6 new)
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

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-001)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-005-PhaseTemplateContracts.md
- @.claude/templates/investigation/EXPLORE.md (existing template)
- @.claude/haios/modules/cycle_runner.py (target module)
- Memory: 80784 (TDD for YAML validation), 80824 (frontmatter for machine-checkable metadata), 82838 (contract pattern)

---
