---
template: implementation_plan
status: approved
date: 2026-02-09
backlog_id: WORK-113
title: "Ceremony Contract Validation and Governance"
author: Hephaestus
lifecycle_phase: plan
session: 334
version: "1.5"
generated: 2026-02-09
last_updated: 2026-02-09T23:55:00
---
# Implementation Plan: Ceremony Contract Validation and Governance

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | DONE | Memory: 84183 (ceremony-as-wrapper), 84188 (validation in engine), 84250 (queue ceremonies reference) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Implement Python validation functions that parse ceremony YAML frontmatter contracts and validate inputs/outputs, with configurable governance enforcement (warn/block) via haios.yaml.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `ceremony_contracts.py` (add validation), `haios.yaml` (add toggle) |
| Lines of code affected | ~247 | `ceremony_contracts.py` is 247 lines; adding ~120 new lines |
| New files to create | 1 | `tests/test_ceremony_validation.py` |
| Tests to write | ~12 | See Tests First section |
| Dependencies | 1 | `ceremony_contracts.py` already imported by `test_ceremony_contracts.py` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Validation functions are pure; governance gate is config-driven |
| Risk of regression | Low | Adding new functions to existing module, not modifying existing ones |
| External dependencies | Low | Only reads YAML frontmatter and haios.yaml |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 20 min | High |
| Validation functions | 30 min | High |
| Governance toggle | 10 min | High |
| Registry self-verification | 10 min | High |
| **Total** | ~70 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/ceremony_contracts.py:55-150
# Data model exists: ContractField, OutputField, CeremonyContract, CeremonyRegistry
# CeremonyContract.from_frontmatter() parses YAML into dataclasses
# NO validation functions exist
# NO governance enforcement exists
```

**Behavior:** Contracts are parsed and stored as dataclasses. No validation of actual inputs/outputs against these contracts. The contracts are documentation-only.

**Result:** Ceremonies can be invoked with missing/invalid inputs and produce unvalidated outputs. Contracts exist but are not enforced.

### Desired State

```python
# .claude/haios/lib/ceremony_contracts.py (new functions)
def validate_ceremony_input(contract: CeremonyContract, inputs: Dict[str, Any]) -> ValidationResult:
    """Validate inputs against ceremony's input contract."""

def validate_ceremony_output(contract: CeremonyContract, outputs: Dict[str, Any]) -> ValidationResult:
    """Validate outputs against ceremony's output contract."""
```

**Behavior:** Validation functions check actual values against contract definitions. Governance layer reads haios.yaml toggle to decide warn vs block behavior.

**Result:** Ceremony inputs/outputs are validated. Invalid inputs produce clear error messages. Governance enforcement is configurable.

---

## Tests First (TDD)

### Test 1: Valid Input Passes Validation
```python
def test_validate_input_valid():
    contract = CeremonyContract.from_frontmatter({
        "name": "queue-commit",
        "category": "queue",
        "input_contract": [
            {"field": "work_id", "type": "string", "required": True, "description": "Work item ID"}
        ],
        "output_contract": [],
        "side_effects": []
    })
    result = validate_ceremony_input(contract, {"work_id": "WORK-113"})
    assert result.valid is True
    assert result.errors == []
```

### Test 2: Missing Required Input Fails
```python
def test_validate_input_missing_required():
    contract = CeremonyContract.from_frontmatter({
        "name": "queue-commit",
        "category": "queue",
        "input_contract": [
            {"field": "work_id", "type": "string", "required": True, "description": "Work item ID"}
        ],
        "output_contract": [],
        "side_effects": []
    })
    result = validate_ceremony_input(contract, {})
    assert result.valid is False
    assert any("work_id" in e for e in result.errors)
```

### Test 3: Optional Input May Be Absent
```python
def test_validate_input_optional_absent():
    contract = CeremonyContract.from_frontmatter({
        "name": "queue-commit",
        "category": "queue",
        "input_contract": [
            {"field": "work_id", "type": "string", "required": True, "description": "ID"},
            {"field": "rationale", "type": "string", "required": False, "description": "Why"}
        ],
        "output_contract": [],
        "side_effects": []
    })
    result = validate_ceremony_input(contract, {"work_id": "WORK-113"})
    assert result.valid is True
```

### Test 4: Pattern Validation (regex match)
```python
def test_validate_input_pattern_match():
    contract = CeremonyContract.from_frontmatter({
        "name": "queue-commit",
        "category": "queue",
        "input_contract": [
            {"field": "work_id", "type": "string", "required": True,
             "description": "ID", "pattern": r"WORK-\d{3}"}
        ],
        "output_contract": [],
        "side_effects": []
    })
    result = validate_ceremony_input(contract, {"work_id": "WORK-113"})
    assert result.valid is True

    result_bad = validate_ceremony_input(contract, {"work_id": "invalid"})
    assert result_bad.valid is False
    assert any("pattern" in e for e in result_bad.errors)
```

### Test 5: Valid Output Passes Validation
```python
def test_validate_output_valid():
    contract = CeremonyContract.from_frontmatter({
        "name": "queue-commit",
        "category": "queue",
        "input_contract": [],
        "output_contract": [
            {"field": "success", "type": "boolean", "guaranteed": "always", "description": "Result"}
        ],
        "side_effects": []
    })
    result = validate_ceremony_output(contract, {"success": True})
    assert result.valid is True
```

### Test 6: Missing Guaranteed=always Output Fails
```python
def test_validate_output_missing_always():
    contract = CeremonyContract.from_frontmatter({
        "name": "queue-commit",
        "category": "queue",
        "input_contract": [],
        "output_contract": [
            {"field": "success", "type": "boolean", "guaranteed": "always", "description": "Result"}
        ],
        "side_effects": []
    })
    result = validate_ceremony_output(contract, {})
    assert result.valid is False
    assert any("success" in e for e in result.errors)
```

### Test 7: OutputField.guaranteed Vocabulary Validation (A5)
```python
def test_output_field_guaranteed_vocabulary():
    """guaranteed must be one of: always, on_success, on_failure"""
    valid_values = ["always", "on_success", "on_failure"]
    for val in valid_values:
        field = OutputField(field="x", type="string", guaranteed=val, description="test")
        assert field.guaranteed == val

    with pytest.raises(ValueError, match="Invalid guaranteed"):
        OutputField(field="x", type="string", guaranteed="sometimes", description="test")
```

### Test 8: ContractField.type Vocabulary Validation (A6)
```python
def test_contract_field_type_vocabulary():
    """type must be one of: string, boolean, list, path, integer"""
    valid_types = ["string", "boolean", "list", "path", "integer"]
    for t in valid_types:
        field = ContractField(field="x", type=t, required=True, description="test")
        assert field.type == t

    with pytest.raises(ValueError, match="Invalid type"):
        ContractField(field="x", type="float", required=True, description="test")
```

### Test 9: Registry Self-Verification (A10)
```python
def test_registry_ceremony_count_matches_actual():
    """ceremony_count in registry must equal actual ceremony list length."""
    registry = load_ceremony_registry()
    assert registry.ceremony_count == len(registry.ceremonies), (
        f"Registry declares {registry.ceremony_count} but has {len(registry.ceremonies)}"
    )
```

### Test 10: Empty Contract Validation
```python
def test_validate_input_empty_contract():
    """Ceremony with no input contract accepts any input."""
    contract = CeremonyContract(
        name="session-start", category="session",
        input_contract=[], output_contract=[], side_effects=[]
    )
    result = validate_ceremony_input(contract, {"anything": "goes"})
    assert result.valid is True
```

### Test 11: Conditional Output (on_success/on_failure)
```python
def test_validate_output_conditional_fields():
    """on_success fields only required when success=True."""
    contract = CeremonyContract.from_frontmatter({
        "name": "test", "category": "queue",
        "input_contract": [],
        "output_contract": [
            {"field": "success", "type": "boolean", "guaranteed": "always", "description": "Result"},
            {"field": "data", "type": "string", "guaranteed": "on_success", "description": "Payload"},
            {"field": "error", "type": "string", "guaranteed": "on_failure", "description": "Error msg"}
        ],
        "side_effects": []
    })
    # Success case: data required, error not
    result = validate_ceremony_output(contract, {"success": True, "data": "ok"})
    assert result.valid is True

    # Failure case: error required, data not
    result = validate_ceremony_output(contract, {"success": False, "error": "failed"})
    assert result.valid is True
```

### Test 12: Backward Compatibility
```python
def test_existing_contract_parsing_unchanged():
    """WORK-111/112 contract parsing still works."""
    sample = {
        "name": "queue-commit", "category": "queue",
        "input_contract": [
            {"field": "work_id", "type": "string", "required": True, "description": "ID"}
        ],
        "output_contract": [
            {"field": "success", "type": "boolean", "guaranteed": "always", "description": "Result"}
        ],
        "side_effects": ["Logs event"]
    }
    contract = CeremonyContract.from_frontmatter(sample)
    assert contract.name == "queue-commit"
    assert len(contract.input_contract) == 1
    assert len(contract.output_contract) == 1
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/lib/ceremony_contracts.py`
**Location:** After line 150 (after `CeremonyContract.from_frontmatter()`)

**New Code (appended to existing module):**

```python
# --- Vocabulary constants (WORK-112 critique A5, A6) ---

VALID_TYPES = frozenset(["string", "boolean", "list", "path", "integer"])
VALID_GUARANTEED = frozenset(["always", "on_success", "on_failure"])


@dataclass
class ValidationResult:
    """Result of validating inputs/outputs against a contract."""
    valid: bool
    errors: List[str] = field(default_factory=list)


def validate_ceremony_input(
    contract: CeremonyContract, inputs: Dict[str, Any]
) -> ValidationResult:
    """Validate inputs against ceremony's input contract.

    Args:
        contract: Parsed ceremony contract
        inputs: Dict of actual input values

    Returns:
        ValidationResult with valid=True if all required fields present
        and patterns match, else valid=False with error descriptions.
    """
    errors = []
    for field_def in contract.input_contract:
        value = inputs.get(field_def.field)
        if field_def.required and value is None:
            errors.append(f"Required field '{field_def.field}' is missing")
            continue
        if value is not None and field_def.pattern:
            import re
            if not re.fullmatch(field_def.pattern, str(value)):
                errors.append(
                    f"Field '{field_def.field}' value '{value}' "
                    f"does not match pattern '{field_def.pattern}'"
                )
    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_ceremony_output(
    contract: CeremonyContract, outputs: Dict[str, Any]
) -> ValidationResult:
    """Validate outputs against ceremony's output contract.

    Args:
        contract: Parsed ceremony contract
        outputs: Dict of actual output values

    Returns:
        ValidationResult with valid=True if all guaranteed fields present
        per their condition (always/on_success/on_failure).
    """
    errors = []
    success_value = outputs.get("success")

    for field_def in contract.output_contract:
        value = outputs.get(field_def.field)
        if field_def.guaranteed == "always" and value is None:
            errors.append(f"Guaranteed field '{field_def.field}' is missing (guaranteed=always)")
        elif field_def.guaranteed == "on_success" and success_value is True and value is None:
            errors.append(f"Field '{field_def.field}' is missing (guaranteed=on_success, success=True)")
        elif field_def.guaranteed == "on_failure" and success_value is False and value is None:
            errors.append(f"Field '{field_def.field}' is missing (guaranteed=on_failure, success=False)")
    return ValidationResult(valid=len(errors) == 0, errors=errors)
```

**File:** `.claude/haios/lib/ceremony_contracts.py`
**Location:** `ContractField.__post_init__` and `OutputField.__post_init__` (new)

Add `__post_init__` validators to existing dataclasses:

```python
@dataclass
class ContractField:
    # ... existing fields ...
    def __post_init__(self):
        if self.type not in VALID_TYPES:
            raise ValueError(
                f"Invalid type '{self.type}'. Must be one of: {sorted(VALID_TYPES)}"
            )

@dataclass
class OutputField:
    # ... existing fields ...
    def __post_init__(self):
        if self.guaranteed not in VALID_GUARANTEED:
            raise ValueError(
                f"Invalid guaranteed '{self.guaranteed}'. Must be one of: {sorted(VALID_GUARANTEED)}"
            )
```

**File:** `.claude/haios/config/haios.yaml`
**Location:** In `toggles:` section

```yaml
toggles:
  block_powershell: true
  ceremony_contract_enforcement: warn  # warn|block (WORK-113)
```

### Call Chain Context

```
Ceremony Skill invoked (e.g., queue-commit)
    |
    +-> [Governance Gate] validate_ceremony_input(contract, inputs)
    |       Returns: ValidationResult
    |       If enforcement=block and !valid -> STOP
    |       If enforcement=warn and !valid -> log warning, continue
    |
    +-> Ceremony executes (existing behavior)
    |
    +-> [Governance Gate] validate_ceremony_output(contract, outputs)
            Returns: ValidationResult
            Logged for audit (no blocking on output)
```

### Function/Component Signatures

```python
@dataclass
class ValidationResult:
    """Result of contract validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)

def validate_ceremony_input(
    contract: CeremonyContract, inputs: Dict[str, Any]
) -> ValidationResult:
    """Check inputs satisfy ceremony's input contract.

    Args:
        contract: Parsed CeremonyContract from skill frontmatter
        inputs: Dict of actual input key-value pairs

    Returns:
        ValidationResult with valid=True if all checks pass

    Raises:
        No exceptions - returns ValidationResult with errors list
    """

def validate_ceremony_output(
    contract: CeremonyContract, outputs: Dict[str, Any]
) -> ValidationResult:
    """Check outputs satisfy ceremony's output contract.

    Args:
        contract: Parsed CeremonyContract from skill frontmatter
        outputs: Dict of actual output key-value pairs

    Returns:
        ValidationResult with valid=True if all checks pass
    """
```

### Behavior Logic

```
validate_ceremony_input(contract, inputs):
    For each field in contract.input_contract:
        ├─ required=True AND field missing → ERROR
        ├─ pattern defined AND value doesn't match → ERROR
        └─ Otherwise → OK
    Return ValidationResult(valid=no_errors, errors=[...])

validate_ceremony_output(contract, outputs):
    For each field in contract.output_contract:
        ├─ guaranteed="always" AND field missing → ERROR
        ├─ guaranteed="on_success" AND success=True AND field missing → ERROR
        ├─ guaranteed="on_failure" AND success=False AND field missing → ERROR
        └─ Otherwise → OK
    Return ValidationResult(valid=no_errors, errors=[...])
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add to existing module | Extend `ceremony_contracts.py` | Functions operate on `CeremonyContract` - same module, same concern. No new module needed. |
| Vocabulary validation via `__post_init__` | Dataclass self-validation | Catches invalid values at construction time, not just at validation time. Fail-fast principle. |
| `re.fullmatch` for patterns | Full string match, not partial | Pattern `WORK-\d{3}` should match entire value, not substring. Prevents "WORK-113-extra" matching. |
| Conditional output validation | Check `outputs["success"]` for on_success/on_failure | Matches the contract semantics - `on_success` fields only required when ceremony succeeded. |
| ValidationResult as dataclass | Not exception-based | Callers need programmatic access to errors list. Exceptions lose structured error information. |
| Governance as config toggle | `haios.yaml` toggles section | Matches existing pattern (`block_powershell`). Configurable without code changes. |
| `warn` as default enforcement | Start permissive | Avoid breaking existing ceremony invocations. Operator can tighten to `block` when ready. |

### Input/Output Examples

**Real Example - queue-commit ceremony (from `.claude/skills/queue-commit/SKILL.md`):**

```
Input contract from frontmatter:
  - field: work_id, type: string, required: true, pattern: "WORK-\\d{3}"
  - field: rationale, type: string, required: false

validate_ceremony_input(contract, {"work_id": "WORK-113"})
  Returns: ValidationResult(valid=True, errors=[])

validate_ceremony_input(contract, {})
  Returns: ValidationResult(valid=False, errors=["Required field 'work_id' is missing"])

validate_ceremony_input(contract, {"work_id": "bad-id"})
  Returns: ValidationResult(valid=False, errors=["Field 'work_id' value 'bad-id' does not match pattern 'WORK-\\d{3}'"])
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty input_contract | All inputs accepted | Test 10 |
| Empty output_contract | All outputs accepted | Implicit in Test 5 structure |
| Pattern on optional absent field | Skip pattern check if value is None | Test 3 + pattern logic |
| Dual-category ceremony | Validation works same regardless of category | Inherits from CeremonyContract |
| `success` field absent in outputs | on_success/on_failure fields not checked | Defensive: only check when success is explicitly True/False |

### Open Questions

**Q: Should type validation check Python types (e.g., `type: boolean` requires `isinstance(value, bool)`)?**

No. Type validation at the contract level is schema documentation. Runtime type checking would require parsing skill markdown at ceremony execution time, which is outside scope (CH-011 non-goal: "Not implementing runtime type checking"). The `type` field in ContractField validates against the vocabulary (string/boolean/list/path/integer) but does not type-check actual values.

---

## Open Decisions (MUST resolve before implementation)

No unresolved operator decisions. All acceptance criteria from WORK-113 are addressed in this design.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No open decisions | N/A | N/A | All 7 acceptance criteria mapped to test/design |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_ceremony_validation.py` with all 12 tests
- [ ] Verify all new tests fail (red) - validation functions don't exist yet

### Step 2: Vocabulary Validation (A5, A6)
- [ ] Add `VALID_TYPES` and `VALID_GUARANTEED` constants to `ceremony_contracts.py`
- [ ] Add `__post_init__` to `ContractField` (type vocabulary check)
- [ ] Add `__post_init__` to `OutputField` (guaranteed vocabulary check)
- [ ] Tests 7, 8 pass (green)
- [ ] Verify existing 122 tests still pass (no regression from `__post_init__`)

### Step 3: ValidationResult + validate_ceremony_input
- [ ] Add `ValidationResult` dataclass
- [ ] Add `validate_ceremony_input()` function
- [ ] Tests 1, 2, 3, 4, 10 pass (green)

### Step 4: validate_ceremony_output
- [ ] Add `validate_ceremony_output()` function
- [ ] Tests 5, 6, 11 pass (green)

### Step 5: Registry Self-Verification (A10)
- [ ] Test 9 should already pass (registry has ceremony_count=19, list has 19 entries)
- [ ] Verify test 9 is green

### Step 6: Governance Toggle
- [ ] Add `ceremony_contract_enforcement: warn` to `haios.yaml` toggles section
- [ ] Test 12 (backward compat) passes (green)

### Step 7: Integration Verification
- [ ] All 12 new tests pass
- [ ] All 122 existing tests pass (no regressions)
- [ ] Full test suite: `pytest tests/test_ceremony_contracts.py tests/test_ceremony_validation.py tests/test_ceremony_retrofit.py -v`

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/` README if one exists
- [ ] **MUST:** Verify test file location documented

### Step 9: Consumer Verification
- [ ] **SKIPPED:** No migration or rename. New functions added, no existing functions changed.

---

## Verification

- [ ] Tests pass (12 new + 122 existing)
- [ ] **MUST:** All WORK.md deliverables verified
- [ ] Runtime consumer: validation functions importable from `ceremony_contracts`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `__post_init__` on ContractField/OutputField breaks existing tests | High | Run existing 122 tests IMMEDIATELY after adding `__post_init__`. If any fail, existing frontmatter has invalid values that need fixing. |
| Pattern regex in YAML has escaping issues | Medium | Use `re.fullmatch` and test with real patterns from queue-commit (`WORK-\\d{3}`). Verify YAML double-backslash → Python single-backslash. |
| Governance toggle not read by any runtime consumer yet | Low | Toggle exists for future hook integration. Document that enforcement is config-only for now; actual hook integration is a separate work item. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 334 | 2026-02-09 | Plan authored | In Progress | Plan created, ready for implementation |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-113/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `validate_ceremony_input()` in lib/ | [ ] | Read ceremony_contracts.py, function exists |
| `validate_ceremony_output()` in lib/ | [ ] | Read ceremony_contracts.py, function exists |
| Governance enforcement (warn/block in haios.yaml) | [ ] | Read haios.yaml toggles section |
| Unit tests for contract validation | [ ] | pytest test_ceremony_validation.py passes |
| OutputField.guaranteed vocabulary (A5) | [ ] | `__post_init__` on OutputField validates against {always, on_success, on_failure} |
| ContractField.type vocabulary (A6) | [ ] | `__post_init__` on ContractField validates against {string, boolean, list, path, integer} |
| Registry ceremony_count self-verifying (A10) | [ ] | Test 9 asserts declared == actual |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/ceremony_contracts.py` | ValidationResult, validate_ceremony_input, validate_ceremony_output, VALID_TYPES, VALID_GUARANTEED, __post_init__ validators | [ ] | |
| `tests/test_ceremony_validation.py` | 12 tests covering all acceptance criteria | [ ] | |
| `.claude/haios/config/haios.yaml` | `ceremony_contract_enforcement: warn` in toggles | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_ceremony_validation.py tests/test_ceremony_contracts.py tests/test_ceremony_retrofit.py -v
# Expected: 134+ tests passed (12 new + 122 existing)
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
- [ ] **Runtime consumer exists** (validate functions importable from ceremony_contracts)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md (R3: Contract Validation)
- @.claude/haios/lib/ceremony_contracts.py (existing module to extend)
- @.claude/haios/lib/queue_ceremonies.py (sibling module pattern reference)
- @.claude/haios/config/ceremony_registry.yaml (registry with 19 ceremonies)
- @docs/work/active/WORK-112/WORK.md (predecessor: retrofit)
- @docs/work/active/WORK-111/WORK.md (predecessor: schema)
- Memory: 84183 (validation in engine layer), 84188 (ceremony-as-wrapper), 84288 (stub:true pattern)

---
