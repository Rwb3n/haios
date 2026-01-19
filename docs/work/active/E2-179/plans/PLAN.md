---
template: implementation_plan
status: complete
date: 2026-01-19
backlog_id: E2-179
title: Scaffold Recipe Optional Frontmatter Args
author: Hephaestus
lifecycle_phase: plan
session: 213
version: '1.6'
generated: 2025-12-21
last_updated: '2026-01-19T22:04:04'
---
# Implementation Plan: Scaffold Recipe Optional Frontmatter Args

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

Justfile scaffold recipes (`just work`, `just inv`, `just plan`) will accept optional arguments like `--spawned-by`, `--priority`, and `--milestone` that populate frontmatter fields during scaffolding, eliminating manual post-creation editing.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/lib/scaffold.py` (482 lines), `justfile` (362 lines) |
| Lines of code affected | ~20 | Justfile recipes only; scaffold.py already supports `variables` dict |
| New files to create | 0 | No new files |
| Tests to write | 3 | Backward compat + spawned_by + multiple kwargs |
| Dependencies | 2 | `governance_layer.py`, `migrate_backlog.py` import scaffold |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only justfile recipes call scaffold.py; scaffold.py already has `variables` param |
| Risk of regression | Low | 629-line test suite exists; adding backward-compat test |
| External dependencies | Low | No external services; pure file operations |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Justfile recipe updates | 20 min | High |
| README update | 5 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

**scaffold.py (lines 355-361):** Already supports `variables` dict parameter:
```python
# .claude/lib/scaffold.py:355-361
def scaffold_template(
    template: str,
    output_path: Optional[str] = None,
    backlog_id: Optional[str] = None,
    title: Optional[str] = None,
    variables: Optional[dict] = None,  # <-- KEY: Already exists!
) -> str:
```

**justfile (lines 40-41):** Recipes don't pass optional args to variables:
```bash
# justfile:40-41
work id title:
    just scaffold work_item {{id}} "{{title}}"
```

**Behavior:** `just work E2-179 "My Title"` creates work item, but `spawned_by` field must be manually edited afterward.

**Result:** Friction when spawning work from investigations; manual editing required.

### Desired State

**justfile:** Recipes accept optional `spawned_by` arg:
```bash
# justfile - desired
work id title spawned_by="":
    python .claude/haios/modules/cli.py scaffold work_item {{id}} "{{title}}" --spawned-by="{{spawned_by}}"
```

**Behavior:** `just work E2-180 "My Title" INV-033` creates work item with `spawned_by: INV-033` pre-populated.

**Result:** Zero manual editing for spawned work items.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Backward Compatibility - Default Behavior Unchanged
```python
def test_scaffold_work_item_without_spawned_by(self, tmp_path):
    """Scaffolding work item without spawned_by should produce same output as before."""
    # Setup: Create tmp work directory, template
    # Action: scaffold_template(template="work_item", backlog_id="E2-999", title="Test")
    # Assert: File created, spawned_by field is null/missing (not required)
    content = Path(result).read_text()
    assert "spawned_by:" not in content or "spawned_by: null" in content
```

### Test 2: Variables Dict Passes spawned_by to Template
```python
def test_scaffold_work_item_with_spawned_by(self, tmp_path):
    """Scaffolding with variables dict should populate spawned_by in frontmatter."""
    # Setup: Create tmp work directory, template with {{SPAWNED_BY}} placeholder
    # Action: scaffold_template(
    #     template="work_item",
    #     backlog_id="E2-999",
    #     title="Test",
    #     variables={"SPAWNED_BY": "INV-033"}
    # )
    content = Path(result).read_text()
    assert "spawned_by: INV-033" in content
```

### Test 3: Multiple Optional Variables
```python
def test_scaffold_with_multiple_optional_variables(self, tmp_path):
    """Multiple optional variables should all be substituted."""
    # Action: scaffold_template with variables={"SPAWNED_BY": "INV-033", "PRIORITY": "high"}
    content = Path(result).read_text()
    assert "spawned_by: INV-033" in content
    assert "priority: high" in content
```

---

## Detailed Design

### Architecture Discovery (Session 212)

**Key Finding:** `scaffold_template()` already supports `variables` dict parameter (lines 355-361). No changes needed to Python code. The work reduces to:
1. Update templates with placeholders (e.g., `{{SPAWNED_BY}}`)
2. Update cli.py to accept `--spawned-by` arg and pass to `variables`
3. Update justfile recipes to accept and pass optional args

### Exact Code Change 1: CLI Scaffold Command

**File:** `.claude/haios/modules/cli.py`
**Location:** Lines 252-266, cmd_scaffold function

**Current Code:**
```python
# cli.py:252-266
def cmd_scaffold(template: str, backlog_id: str, title: str, output_path: str = None) -> int:
    """Scaffold a new document from template."""
    layer = GovernanceLayer()
    try:
        path = layer.scaffold_template(
            template=template,
            backlog_id=backlog_id,
            title=title,
            output_path=output_path,
        )
```

**Changed Code:**
```python
# cli.py - add variables parameter
def cmd_scaffold(template: str, backlog_id: str, title: str, output_path: str = None, variables: dict = None) -> int:
    """Scaffold a new document from template."""
    layer = GovernanceLayer()
    try:
        path = layer.scaffold_template(
            template=template,
            backlog_id=backlog_id,
            title=title,
            output_path=output_path,
            variables=variables,  # <-- ADD
        )
```

**Diff:**
```diff
- def cmd_scaffold(template: str, backlog_id: str, title: str, output_path: str = None) -> int:
+ def cmd_scaffold(template: str, backlog_id: str, title: str, output_path: str = None, variables: dict = None) -> int:
          path = layer.scaffold_template(
              template=template,
              backlog_id=backlog_id,
              title=title,
              output_path=output_path,
+             variables=variables,
          )
```

### Exact Code Change 2: CLI Argument Parsing

**File:** `.claude/haios/modules/cli.py`
**Location:** Lines 362-379, scaffold command parsing

**Current Code:**
```python
# cli.py:362-379
    elif cmd == "scaffold":
        # Handle --output option
        output_path = None
        if "--output" in sys.argv:
            # ... existing output handling ...
        if len(args) < 5:
            print("Usage: cli.py scaffold <template> <backlog_id> <title> [--output <path>]")
            return 1
        return cmd_scaffold(template, backlog_id, title, output_path)
```

**Changed Code:**
```python
    elif cmd == "scaffold":
        # Handle optional flags
        output_path = None
        variables = {}

        if "--output" in sys.argv:
            idx = sys.argv.index("--output")
            output_path = sys.argv[idx + 1]
            sys.argv = [a for i, a in enumerate(sys.argv) if i not in (idx, idx + 1)]

        if "--spawned-by" in sys.argv:
            idx = sys.argv.index("--spawned-by")
            variables["SPAWNED_BY"] = sys.argv[idx + 1]
            sys.argv = [a for i, a in enumerate(sys.argv) if i not in (idx, idx + 1)]

        if len(sys.argv) < 5:
            print("Usage: cli.py scaffold <template> <backlog_id> <title> [--output <path>] [--spawned-by <id>]")
            return 1
        return cmd_scaffold(template, backlog_id, title, output_path, variables)
```

### Exact Code Change 3: Template Placeholder

**File:** `.claude/templates/work_item.md`
**Location:** Line 10, add spawned_by field

**Current Code:**
```yaml
# work_item.md - no spawned_by field
priority: medium
effort: medium
```

**Changed Code:**
```yaml
# work_item.md - add spawned_by placeholder
spawned_by: {{SPAWNED_BY}}
priority: medium
effort: medium
```

**Note:** `substitute_variables()` leaves unmatched placeholders as-is, so if `SPAWNED_BY` is not provided, the field will show `{{SPAWNED_BY}}`. We need to either:
1. Default `SPAWNED_BY` to empty string in scaffold.py
2. Or handle it in the variables dict construction

**Decision:** Default to `null` in scaffold.py if not provided (see Key Design Decisions).

### Call Chain Context

```
justfile recipe (e.g., `just work E2-180 "Title" INV-033`)
    |
    +-> cli.py main() -> cmd_scaffold()
    |       Parses --spawned-by arg, builds variables dict
    |
    +-> GovernanceLayer.scaffold_template(variables={"SPAWNED_BY": "INV-033"})
    |       Passes through to scaffold.py
    |
    +-> scaffold.scaffold_template(variables=...)
            Calls substitute_variables() which replaces {{SPAWNED_BY}}
```

### Function/Component Signatures

No signature changes needed - `variables` parameter already exists:

```python
# .claude/lib/scaffold.py:355-361 (EXISTING - no change)
def scaffold_template(
    template: str,
    output_path: Optional[str] = None,
    backlog_id: Optional[str] = None,
    title: Optional[str] = None,
    variables: Optional[dict] = None,  # Already exists!
) -> str:
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to add spawned_by handling | CLI arg parsing (cli.py) | Template already supports variables; cli.py is the gap |
| How to handle missing spawned_by | Default to "null" string in scaffold.py | Keeps template field present but null; consistent with existing fields |
| Which templates to update | work_item.md, investigation.md | These are the only templates with spawned_by semantics |
| Justfile recipe pattern | Optional arg with default | `work id title spawned_by=""` - empty default means backward compatible |

### Input/Output Examples

**Before Fix (current behavior):**
```bash
just work E2-180 "My New Work"
# Creates work item with no spawned_by field
# User must manually edit WORK.md to add: spawned_by: INV-033
```

**After Fix (expected):**
```bash
just work E2-180 "My New Work" --spawned-by=INV-033
# Creates work item with:
#   spawned_by: INV-033
# No manual editing required
```

**Alternative (positional for common case):**
```bash
just work E2-180 "My New Work" INV-033
# Same result, positional arg for convenience
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No spawned_by provided | Field defaults to null | Test 1: Backward compat |
| Empty spawned_by string | Treat as null | Implicit in default handling |
| Invalid spawned_by ID | No validation (user responsibility) | N/A - not in scope |
| Multiple optional args | Each handled independently | Test 3: Multiple variables |

### Open Questions

**Q: Should we validate that spawned_by references an existing work item?**

Answer: No. This would add complexity and external validation is out of scope. The field is informational linkage, not a hard dependency. Consistent with existing behavior where `blocked_by` is not validated either.

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
| N/A | - | - | No operator_decisions in work item; all design decisions documented in Key Design Decisions above |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 3 tests to `tests/test_lib_scaffold.py`:
  - `test_scaffold_work_item_without_spawned_by` (backward compat)
  - `test_scaffold_work_item_with_spawned_by` (new behavior)
  - `test_scaffold_with_multiple_optional_variables`
- [ ] Verify tests fail (red) - spawned_by not yet in template

### Step 2: Update Template with Placeholder
- [ ] Edit `.claude/templates/work_item.md` - add `spawned_by: {{SPAWNED_BY}}`
- [ ] Edit `.claude/lib/scaffold.py` - default `SPAWNED_BY` to "null" if not in variables
- [ ] Test 1 passes (backward compat - defaults to null)

### Step 3: Update CLI to Accept --spawned-by Arg
- [ ] Edit `.claude/haios/modules/cli.py`:
  - Add `variables` param to `cmd_scaffold()`
  - Add `--spawned-by` arg parsing in main()
  - Pass variables dict to `layer.scaffold_template()`
- [ ] Tests 2-3 pass (spawned_by populated when provided)

### Step 4: Update Justfile Recipes (Optional - Convenience Layer)
- [ ] Edit `justfile` - update `work` recipe to accept optional arg:
  ```bash
  work id title spawned_by="":
      python .claude/haios/modules/cli.py scaffold work_item {{id}} "{{title}}" {{if spawned_by != ""}}--spawned-by={{spawned_by}}{{end}}
  ```
- [ ] Manual test: `just work TEST-001 "Test" INV-033` creates item with spawned_by

### Step 5: Integration Verification
- [ ] Run `pytest tests/test_lib_scaffold.py -v` - all tests pass
- [ ] Run `pytest` - full suite passes (no regressions)

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` with new --spawned-by parameter docs
- [ ] **MUST:** Verify justfile help shows new optional arg (via `just --list`)

### Step 7: Consumer Verification
**Not applicable:** This is an additive change; no migrations or renames.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Template placeholder `{{SPAWNED_BY}}` appears in output if not substituted | Low | Default SPAWNED_BY to "null" in scaffold.py (Step 2) |
| Justfile conditional syntax may be shell-dependent | Low | Test on Windows (current platform); fall back to cli.py args only if needed |
| Existing tests may break if template changes | Medium | Add backward-compat test first (Step 1); ensure default behavior unchanged |
| Other templates (investigation.md) may need spawned_by too | Low | Out of scope for this work item; investigation already has `spawned_by: null` field |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 212 | 2026-01-19 | 2026-01-19-05-SESSION-212 | AUTHOR started | Goal populated. Discovered scaffold_template() already supports variables dict. |
| 213 | 2026-01-19 | (pending) | AUTHOR complete | Full plan authored; ready for validation. |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/E2-179/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Update `scaffold_template()` in `.claude/lib/scaffold.py` to accept optional kwargs | [ ] | Already supports `variables` dict - no change needed |
| Update `just work` recipe to accept optional `--spawned-by` arg | [ ] | Read justfile, verify arg exists |
| Update `just inv` recipe to accept optional `--spawned-by` arg | [ ] | Read justfile, verify arg exists |
| Update `just plan` recipe to accept optional `--spawned-by` arg | [ ] | Read justfile, verify arg exists |
| Consider other optional args: `--milestone`, `--priority`, `--related` | [ ] | Documented: Out of scope for v1; spawned_by is the critical friction point |
| Update `.claude/lib/README.md` with new parameter documentation | [ ] | Read README, verify --spawned-by documented |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/work_item.md` | Has `spawned_by: {{SPAWNED_BY}}` field | [ ] | |
| `.claude/lib/scaffold.py` | Defaults SPAWNED_BY to "null" if not provided | [ ] | |
| `.claude/haios/modules/cli.py` | cmd_scaffold accepts variables, main parses --spawned-by | [ ] | |
| `justfile` | work/inv/plan recipes accept optional spawned_by arg | [ ] | |
| `tests/test_lib_scaffold.py` | 3 new tests exist and pass | [ ] | |
| `.claude/lib/README.md` | Documents --spawned-by parameter | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_lib_scaffold.py -v
# Expected: All tests pass including 3 new spawned_by tests
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

- @docs/work/active/E2-179/WORK.md - Work item definition
- @.claude/lib/scaffold.py - Scaffolding implementation (already supports variables)
- @.claude/haios/modules/cli.py - CLI entry point (needs --spawned-by arg)
- @.claude/templates/work_item.md - Template to update
- INV-033 - Spawned this work item (observation about manual spawned_by editing)

---
