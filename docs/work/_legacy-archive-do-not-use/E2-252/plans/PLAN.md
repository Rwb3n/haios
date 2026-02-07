---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-252
title: GovernanceLayer Scaffold Validate Migration
author: Hephaestus
lifecycle_phase: plan
session: 164
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T00:35:43'
---
# Implementation Plan: GovernanceLayer Scaffold Validate Migration

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

Migrate `validate_template()` and `scaffold_template()` functions from `.claude/lib/` to the GovernanceLayer module, maintaining the E2-251 pattern: tests first, cli.py commands, justfile recipes as runtime consumers.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | governance_layer.py, cli.py, justfile, test files |
| Lines of code affected | ~100 | Method wrappers + CLI commands |
| New files to create | 0 | Adding to existing files |
| Tests to write | 7 | 5 unit + 2 integration |
| Dependencies | 2 | validate.py, scaffold.py (delegation) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Delegation pattern, no deep integration |
| Risk of regression | Low | Existing tests remain, new tests added |
| External dependencies | Low | No external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 30 min | High |
| Implementation | 30 min | High |
| **Total** | 1 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/validate.py - 748 lines, standalone module
def validate_template(file_path: str) -> dict[str, Any]:
    """Main validation function - works but accessed directly"""

# .claude/lib/scaffold.py - 443 lines, standalone module
def scaffold_template(template, output_path, backlog_id, title, variables) -> str:
    """Main scaffold function - works but accessed directly"""

# justfile - calls lib directly
validate file:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from validate import validate_template; ..."
```

**Behavior:** Functions work, but not exposed through GovernanceLayer module

**Result:** Inconsistent architecture - some operations use modules (WorkEngine), some use lib directly

### Desired State

```python
# .claude/haios/modules/governance_layer.py - adds delegation methods
class GovernanceLayer:
    def validate_template(self, file_path: str) -> dict:
        """Delegates to lib/validate.py"""
        return _validate_template(file_path)

    def scaffold_template(self, template, output_path, backlog_id, title, variables) -> str:
        """Delegates to lib/scaffold.py"""
        return _scaffold_template(template, output_path, backlog_id, title, variables)

# justfile - routes through cli.py
validate file:
    python .claude/haios/modules/cli.py validate {{file}}
```

**Behavior:** Template operations route through GovernanceLayer via cli.py

**Result:** Consistent architecture - all governance operations go through modules

---

## Tests First (TDD)

### Unit Tests (tests/test_governance_layer.py)

### Test 1: validate_template method exists
```python
def test_governance_layer_has_validate_template():
    """GovernanceLayer should have validate_template method."""
    layer = GovernanceLayer()
    assert hasattr(layer, 'validate_template')
    assert callable(layer.validate_template)
```

### Test 2: validate_template returns valid for good file
```python
def test_validate_template_valid_file(tmp_path):
    """Valid template should return is_valid=True."""
    # Create minimal valid checkpoint
    checkpoint = tmp_path / "test.md"
    checkpoint.write_text("""---
template: checkpoint
status: active
date: 2026-01-04
version: '1.0'
author: Test
project_phase: test
---
# Test

@docs/README.md
@docs/epistemic_state.md
""")
    layer = GovernanceLayer()
    result = layer.validate_template(str(checkpoint))
    assert result["is_valid"] is True
```

### Test 3: validate_template returns invalid for missing field
```python
def test_validate_template_missing_field(tmp_path):
    """Missing required field should return is_valid=False."""
    checkpoint = tmp_path / "test.md"
    checkpoint.write_text("""---
template: checkpoint
status: active
---
# Test
""")
    layer = GovernanceLayer()
    result = layer.validate_template(str(checkpoint))
    assert result["is_valid"] is False
    assert any("Missing" in e for e in result["errors"])
```

### Test 4: scaffold_template method exists
```python
def test_governance_layer_has_scaffold_template():
    """GovernanceLayer should have scaffold_template method."""
    layer = GovernanceLayer()
    assert hasattr(layer, 'scaffold_template')
    assert callable(layer.scaffold_template)
```

### Test 5: scaffold_template creates file
```python
def test_scaffold_template_creates_file(tmp_path, monkeypatch):
    """scaffold_template should create file in output_path."""
    # Monkeypatch PROJECT_ROOT for test isolation
    monkeypatch.setattr('scaffold.PROJECT_ROOT', tmp_path)

    layer = GovernanceLayer()
    output = tmp_path / "test_output.md"
    result = layer.scaffold_template(
        template="checkpoint",
        output_path=str(output),
        backlog_id="999",
        title="Test",
    )
    assert output.exists()
```

### Integration Tests (tests/test_modules_cli.py)

### Test 6: CLI validate command
```python
def test_cli_validate_command(tmp_path):
    """cli.py validate <file> should work."""
    # Create valid checkpoint
    checkpoint = tmp_path / "valid.md"
    checkpoint.write_text(VALID_CHECKPOINT_CONTENT)

    result = subprocess.run(
        ["python", ".claude/haios/modules/cli.py", "validate", str(checkpoint)],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Passed" in result.stdout
```

### Test 7: CLI scaffold command
```python
def test_cli_scaffold_command():
    """cli.py scaffold <type> <id> <title> should work."""
    result = subprocess.run(
        ["python", ".claude/haios/modules/cli.py", "scaffold", "checkpoint", "999", "Test"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Created" in result.stdout
```

---

## Detailed Design

### Approach: Delegation Pattern

Following E2-251 pattern, GovernanceLayer will **delegate** to existing lib functions rather than copy/absorb all 1200+ lines. This:
- Minimizes code duplication
- Reduces merge conflicts
- Keeps working code intact
- Allows gradual migration

### Exact Code Change - GovernanceLayer

**File:** `.claude/haios/modules/governance_layer.py`
**Location:** Add after line 214 (end of class)

**Added Code:**
```python
    def validate_template(self, file_path: str) -> dict:
        """Validate a template file against its schema.

        Delegates to .claude/lib/validate.validate_template().

        Args:
            file_path: Path to template file

        Returns:
            Validation result dict with is_valid, errors, warnings, etc.
        """
        from validate import validate_template as _validate_template
        return _validate_template(file_path)

    def scaffold_template(
        self,
        template: str,
        output_path: str = None,
        backlog_id: str = None,
        title: str = None,
        variables: dict = None,
    ) -> str:
        """Scaffold a new document from template.

        Delegates to .claude/lib/scaffold.scaffold_template().

        Args:
            template: Template type (checkpoint, implementation_plan, etc.)
            output_path: Optional explicit output path
            backlog_id: Backlog item ID
            title: Document title
            variables: Additional template variables

        Returns:
            Path to created file.
        """
        from scaffold import scaffold_template as _scaffold_template
        return _scaffold_template(
            template=template,
            output_path=output_path,
            backlog_id=backlog_id,
            title=title,
            variables=variables,
        )
```

### Exact Code Change - CLI

**File:** `.claude/haios/modules/cli.py`
**Location:** Add after line 155 (before main())

**Added Code:**
```python
# =============================================================================
# E2-252: Validate and Scaffold Commands
# =============================================================================


def cmd_validate(file_path: str) -> int:
    """Validate a template file."""
    layer = GovernanceLayer()
    result = layer.validate_template(file_path)
    if result["is_valid"]:
        print(f"Passed | Type: {result['template_type']} | Refs: {result['reference_count']}")
    else:
        print(f"Failed | {'; '.join(result['errors'])}")
    return 0 if result["is_valid"] else 1


def cmd_scaffold(template: str, backlog_id: str, title: str) -> int:
    """Scaffold a new document from template."""
    layer = GovernanceLayer()
    try:
        path = layer.scaffold_template(template, backlog_id=backlog_id, title=title)
        print(f"Created: {path}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
```

### Exact Code Change - Justfile

**File:** `justfile`
**Location:** Lines 16-22 (validate and scaffold recipes)

**Current Code:**
```just
validate file:
    python -c "import sys; sys.path.insert(0, '.claude\lib'); from validate import validate_template; r = validate_template('{{file}}'); print('Passed' if r['is_valid'] else 'Failed: ' + '; '.join(r['errors'])); sys.exit(0 if r['is_valid'] else 1)"

scaffold type id title:
    python -c "import sys; sys.path.insert(0, '.claude\lib'); from scaffold import scaffold_template; r = scaffold_template('{{type}}', backlog_id='{{id}}', title='{{title}}'); print(f'Created: {r}')"
```

**Changed Code:**
```just
# Validate a markdown file (E2-252: via cli.py)
validate file:
    python .claude/haios/modules/cli.py validate {{file}}

# Scaffold a new document (E2-252: via cli.py)
scaffold type id title:
    python .claude/haios/modules/cli.py scaffold {{type}} {{id}} {{title}}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delegation vs Absorption | Delegation | 1200+ lines is too much to copy; delegation keeps working code intact |
| Import location | Inside method | Avoids import cycle issues; lazy loading |
| CLI integration | Add to existing cli.py | Follows E2-251 pattern; single entry point |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| File not found | validate_template returns is_valid=False with error | Test 3 |
| Invalid template type | scaffold_template raises ValueError | Existing scaffold tests |
| Missing @ references | validate_template returns is_valid=False | Test 3 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 5 unit tests to tests/test_governance_layer.py
- [ ] Add 2 integration tests to tests/test_modules_cli.py
- [ ] Verify tests fail (RED)

### Step 2: Implement GovernanceLayer Methods
- [ ] Add validate_template() method
- [ ] Add scaffold_template() method
- [ ] Tests 1-5 pass (GREEN)

### Step 3: Add CLI Commands
- [ ] Add cmd_validate() function
- [ ] Add cmd_scaffold() function
- [ ] Add command dispatch in main()
- [ ] Tests 6-7 pass (GREEN)

### Step 4: Update Justfile Recipes
- [ ] Update validate recipe to use cli.py
- [ ] Update scaffold recipe to use cli.py
- [ ] Verify `just validate <file>` works
- [ ] Verify `just scaffold <type> <id> <title>` works

### Step 5: Mark Legacy Files Deprecated
- [ ] Add DEPRECATED header to .claude/lib/validate.py
- [ ] Add DEPRECATED header to .claude/lib/scaffold.py

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update .claude/haios/modules/README.md with new methods

### Step 7: Full Test Suite
- [ ] Run `pytest` - all tests pass
- [ ] No regressions

---

## Verification

- [ ] Tests pass (`pytest tests/test_governance_layer.py tests/test_modules_cli.py -v`)
- [ ] Demo: `just validate docs/checkpoints/<latest>.md` returns Passed
- [ ] Demo: `just scaffold checkpoint 999 "Test"` creates file

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import cycle | High | Lazy import inside methods |
| Path resolution | Medium | Use existing _lib_path pattern |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/governance_layer.py` | Has validate_template() and scaffold_template() | [ ] | |
| `.claude/haios/modules/cli.py` | Has validate and scaffold commands | [ ] | |
| `justfile` | validate/scaffold use cli.py | [ ] | |
| `tests/test_governance_layer.py` | 5 new tests pass | [ ] | |
| `tests/test_modules_cli.py` | 2 new tests pass | [ ] | |
| `.claude/lib/validate.py` | DEPRECATED header | [ ] | |
| `.claude/lib/scaffold.py` | DEPRECATED header | [ ] | |
| `.claude/haios/modules/README.md` | Documents new methods | [ ] | |
| `just validate <file>` | Works via cli.py | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_governance_layer.py tests/test_modules_cli.py -v
# Expected: 7+ new tests passed
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
- [ ] **Runtime consumer exists** (justfile recipes use cli.py)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** README updated (.claude/haios/modules/README.md)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- E2-251: WorkEngine migration pattern
- INV-052 Section 17: Modular Architecture
- ADR-033: Work Item Lifecycle

---
