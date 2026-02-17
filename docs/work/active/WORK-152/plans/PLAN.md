---
template: implementation_plan
status: complete
date: 2026-02-16
backlog_id: WORK-152
title: "Plan Template Fracturing by Work Type"
author: Hephaestus
lifecycle_phase: plan
session: 389
version: "1.5"
generated: 2026-02-16
last_updated: 2026-02-16T22:45:00
---
# Implementation Plan: Plan Template Fracturing by Work Type

---

<!-- TEMPLATE GOVERNANCE (v1.4)
     SKIP RATIONALE REQUIREMENT: See individual sections for skip rationale where applicable.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Tests defined in "Tests First" section |
| Query prior work | SHOULD | Memory 85528-85531, 85666, 84275, 84898 queried (template skew, lighter plans) |
| Document design decisions | MUST | Key Design Decisions table populated |
| Ground truth metrics | MUST | wc -l on target files, Glob for file counts |

---

## Goal

Plan templates are fractured by work type (implementation, design, investigation, cleanup) so that each type gets only the sections relevant to its work, eliminating skip-rationale overhead.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | scaffold.py (567L), validate.py (777L), test_lib_scaffold.py (1012L) |
| Lines of code affected | ~120 | load_plan_template, type mapping, validate routing, test additions |
| New files to create | 3 | `.claude/templates/plans/design.md`, `cleanup.md`, `implementation.md` |
| Tests to write | 8 | Template routing, type mapping, validation routing, backward compat |
| Dependencies | 4 | plan-authoring-cycle, plan-validation-cycle, test_lib_validate.py, test_template_rfc2119.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | scaffold.py, validate.py, 2 skill MDs, 3 test files |
| Risk of regression | Med | 30+ existing tests reference `implementation_plan` template type |
| External dependencies | Low | Pure file/code changes, no external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Templates (create 3 new + README) | 20 min | High |
| scaffold.py (mapping, extraction, routing) | 20 min | High |
| validate.py (registry + subtype routing) | 20 min | High |
| Tests (8 new) | 25 min | High |
| Consumer verification + WORK.md update | 10 min | High |
| **Total** | **95 min** | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/scaffold.py:254-279 - load_template()
def load_template(template: str) -> str:
    template_path = PROJECT_ROOT / ".claude" / "templates" / f"{template}.md"
    if not template_path.exists():
        legacy_path = PROJECT_ROOT / ".claude" / "templates" / "_legacy" / f"{template}.md"
        if legacy_path.exists():
            template_path = legacy_path
        else:
            raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8-sig")
```

**Behavior:** `scaffold_template("implementation_plan", ...)` always loads the same monolithic template regardless of work item type.

**Result:** For `type: design` work (ADRs, specs), ~60% of sections require SKIPPED rationales. Evidence: WORK-149 plan had SKIPPED for Tests First, Current/Desired State code blocks, Exact Code Change, Call Chain, Function Signatures, Backward Compatibility.

### Desired State

```python
# .claude/haios/lib/scaffold.py - load_plan_template() NEW
def load_plan_template(work_type: str = "implementation") -> str:
    """Load work-type-specific plan template.

    Routing: .claude/templates/plans/{work_type}.md
    Fallback: _legacy/implementation_plan.md (backward compat)
    """
    plan_dir = PROJECT_ROOT / ".claude" / "templates" / "plans"
    type_path = plan_dir / f"{work_type}.md"
    if type_path.exists():
        return type_path.read_text(encoding="utf-8-sig")
    # Fallback to monolithic template
    return load_template("implementation_plan")
```

**Behavior:** `scaffold_template("implementation_plan", ...)` routes to type-specific template when `variables["TYPE"]` is provided. Each template contains only relevant sections.

**Result:** Design plans have ~8 sections (not 15+). Cleanup plans are even lighter. Skip rationale frequency drops below 20%.

---

## Tests First (TDD)

### Test 1: Type-specific template routing
```python
def test_load_plan_template_routes_by_type(tmp_path):
    """load_plan_template('design') returns design-specific template."""
    plans_dir = tmp_path / ".claude" / "templates" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "design.md").write_text("---\ntemplate: implementation_plan\n---\n# Design Plan")
    # Monkeypatch PROJECT_ROOT
    result = load_plan_template("design")
    assert "Design Plan" in result
```

### Test 2: Fallback to monolithic when type template missing
```python
def test_load_plan_template_fallback_to_legacy(tmp_path):
    """load_plan_template('unknown_type') falls back to implementation_plan."""
    result = load_plan_template("unknown_type")
    assert "Implementation Plan" in result  # Falls back to legacy
```

### Test 3: Backward compatibility - default is implementation
```python
def test_load_plan_template_default_is_implementation(tmp_path):
    """load_plan_template() with no arg loads implementation template."""
    result = load_plan_template()
    assert "Tests First" in result  # Implementation template has TDD section
```

### Test 4: Validate registry has type-specific sections
```python
def test_validate_registry_design_plan_sections():
    """Design plan expected_sections excludes code-specific sections."""
    registry = get_template_registry()
    design_sections = registry["implementation_plan_design"]["expected_sections"]
    assert "Goal" in design_sections
    assert "Tests First (TDD)" not in design_sections
    assert "Exact Code Change" not in design_sections
```

### Test 5: Validate registry has cleanup plan sections
```python
def test_validate_registry_cleanup_plan_sections():
    """Cleanup plan expected_sections is minimal."""
    registry = get_template_registry()
    cleanup_sections = registry["implementation_plan_cleanup"]["expected_sections"]
    assert "Goal" in cleanup_sections
    assert len(cleanup_sections) < len(registry["implementation_plan"]["expected_sections"])
```

### Test 6: scaffold_template auto-extracts TYPE from work item
```python
def test_scaffold_template_auto_extracts_type(tmp_path, monkeypatch):
    """scaffold_template reads work item type and routes to correct template."""
    # Create work item with type: design
    # Create design plan template
    # Call scaffold_template("implementation_plan", backlog_id="WORK-TEST")
    # Verify design template content is used (not monolithic)
```

### Test 7: get_plan_type maps work item types correctly
```python
def test_get_plan_type_mapping():
    """Work item types map to plan template types."""
    from scaffold import get_plan_type
    assert get_plan_type("feature") == "implementation"
    assert get_plan_type("bug") == "cleanup"
    assert get_plan_type("chore") == "cleanup"
    assert get_plan_type("design") == "design"
    assert get_plan_type("spike") == "implementation"
    assert get_plan_type("unknown") == "implementation"  # fallback
```

### Test 8: validate_template routes by subtype
```python
def test_validate_template_routes_by_subtype():
    """Plans with subtype: design validate against design expected_sections."""
    from validate import validate_template
    # Create plan content with template: implementation_plan, subtype: design
    # Verify it validates against implementation_plan_design registry
    # (no errors for missing TDD section)
```

---

## Detailed Design

### Template File Structure

New directory: `.claude/templates/plans/`

```
.claude/templates/
  plans/
    implementation.md   -> symlink or copy of _legacy/implementation_plan.md (full template)
    design.md           -> Goal, Effort, State, Design Decisions, Steps, Risks, Verification
    investigation.md    -> Goal, Effort, Hypotheses, Exploration Plan, Steps, Verification
    cleanup.md          -> Goal, Effort, Change List, Steps, Verification
    README.md           -> Documents the template variants
  _legacy/
    implementation_plan.md  -> Preserved for backward compat (load_template fallback)
```

### Section Matrix (which sections per type)

| Section | implementation | design | investigation | cleanup |
|---------|:-:|:-:|:-:|:-:|
| Pre-Implementation Checklist | Y | Y | Y | Y |
| Goal | Y | Y | Y | Y |
| Effort Estimation | Y | Y | Y | Y |
| Current State vs Desired State | Y (code) | Y (prose) | N | Y (prose) |
| Tests First (TDD) | Y | N | N | N |
| Detailed Design | Y (full) | Y (decisions only) | N | N |
| Exact Code Change | Y | N | N | N |
| Call Chain Context | Y | N | N | N |
| Function Signatures | Y | N | N | N |
| Open Decisions | Y | Y | Y | N |
| Implementation Steps | Y | Y (authoring steps) | Y (exploration steps) | Y (change steps) |
| Verification | Y | Y | Y | Y |
| Risks & Mitigations | Y | Y | Y | N |
| Progress Tracker | Y | Y | Y | Y |
| Ground Truth Verification | Y | Y | Y | Y |

### Exact Code Change 1: scaffold.py - Type mapping function (Critique A1 fix)

**File:** `.claude/haios/lib/scaffold.py`
**Location:** After `load_template()` (line ~279)

Work item `type` values (`feature`, `chore`, `bug`, `spike`, `investigation`, `design`) do NOT match plan template filenames. Need a mapping function.

**New Code:**
```python
# Work item type -> plan template type mapping (WORK-152, Critique A1)
# Work item types: feature, investigation, bug, chore, spike, design
# Plan template types: implementation, design, cleanup
PLAN_TYPE_MAP = {
    "feature": "implementation",
    "investigation": "implementation",  # investigations use investigation-cycle, not plan templates
    "bug": "cleanup",
    "chore": "cleanup",
    "spike": "implementation",
    "design": "design",
}


def get_plan_type(work_type: str) -> str:
    """Map work item type to plan template type.

    Args:
        work_type: Work item type field value (feature, bug, chore, etc.)

    Returns:
        Plan template type (implementation, design, cleanup).
        Defaults to "implementation" for unmapped types.
    """
    return PLAN_TYPE_MAP.get(work_type, "implementation")


def load_plan_template(work_type: str = "implementation") -> str:
    """Load work-type-specific plan template.

    Routes to .claude/templates/plans/{plan_type}.md if it exists,
    otherwise falls back to the monolithic implementation_plan template
    via load_template().

    Args:
        work_type: Work item type from WORK.md type field.
                   Mapped to plan template type via get_plan_type().

    Returns:
        Template content string.
    """
    plan_type = get_plan_type(work_type)
    plan_dir = PROJECT_ROOT / ".claude" / "templates" / "plans"
    type_path = plan_dir / f"{plan_type}.md"
    if type_path.exists():
        return type_path.read_text(encoding="utf-8-sig")
    # Fallback to monolithic template for unknown types
    return load_template("implementation_plan")
```

### Exact Code Change 2: scaffold.py - Route in scaffold_template() with auto-extraction (Critique A2 fix)

**File:** `.claude/haios/lib/scaffold.py`
**Location:** Line ~459 in `scaffold_template()`, where `content = load_template(template)` is called

**Current Code:**
```python
    # Load template
    content = load_template(template)
```

**Changed Code:**
```python
    # Load template - route plan templates by work type (WORK-152)
    if template == "implementation_plan":
        # Auto-extract TYPE from work item if not provided (Critique A2)
        if "TYPE" not in variables and backlog_id:
            work_type = _get_work_type(backlog_id)
            if work_type:
                variables["TYPE"] = work_type
        work_type = variables.get("TYPE", "implementation")
        content = load_plan_template(work_type)
    else:
        content = load_template(template)
```

### Exact Code Change 2b: scaffold.py - New `_get_work_type()` helper (Critique A2 fix)

**File:** `.claude/haios/lib/scaffold.py`
**Location:** After `_get_work_status()` (line ~167)

**New Code:**
```python
def _get_work_type(backlog_id: str) -> Optional[str]:
    """Get type of existing work item for plan template routing.

    Args:
        backlog_id: Work item ID to check

    Returns:
        Type string if work item exists, None otherwise.
    """
    import yaml

    work_path = PROJECT_ROOT / "docs" / "work" / "active" / backlog_id / "WORK.md"
    if not work_path.exists():
        return None

    try:
        content = work_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            return fm.get("type")
    except Exception:
        pass

    return None
```

This follows the exact pattern of existing `_get_work_status()` at line 142-166.

### Exact Code Change 3: validate.py - Type-specific registry entries

**File:** `.claude/haios/lib/validate.py`
**Location:** Inside `get_template_registry()`, after the `implementation_plan` entry

**New entries:**
```python
        "implementation_plan_design": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [
                "version", "author", "plan_id", "title", "session", "priority",
                "lifecycle_phase", "subtype", "directive_id", "parent_id", "completed_session",
                "completion_note", "spawned_by", "blocked_by", "related", "milestone",
                "parent_plan", "children", "absorbs", "enables", "execution_layer",
            ],
            "allowed_status": ["draft", "ready", "approved", "rejected", "complete"],
            "expected_sections": [
                "Goal",
                "Effort Estimation (Ground Truth)",
                "Current State vs Desired State",
                "Detailed Design",
                "Implementation Steps",
                "Verification",
                "Risks & Mitigations",
                "Progress Tracker",
                "Ground Truth Verification (Before Closing)",
            ],
        },
        "implementation_plan_cleanup": {
            "required_fields": ["template", "status", "date", "backlog_id"],
            "optional_fields": [
                "version", "author", "plan_id", "title", "session", "priority",
                "lifecycle_phase", "subtype", "directive_id", "parent_id", "completed_session",
                "completion_note", "spawned_by", "blocked_by", "related", "milestone",
                "parent_plan", "children", "absorbs", "enables", "execution_layer",
            ],
            "allowed_status": ["draft", "ready", "approved", "rejected", "complete"],
            "expected_sections": [
                "Goal",
                "Effort Estimation (Ground Truth)",
                "Implementation Steps",
                "Verification",
                "Progress Tracker",
                "Ground Truth Verification (Before Closing)",
            ],
        },
```

### Exact Code Change 4: validate.py - Subtype routing in validate_template() (Critique A3/A5 fix)

**File:** `.claude/haios/lib/validate.py`
**Location:** Line ~549-617, inside `validate_template()`

Plans with `template: implementation_plan` and `subtype: design` must route to `implementation_plan_design` registry key. Without this, type-specific plans fail validation against the full monolithic expected_sections list.

**Current Code (line 549-558):**
```python
    template_type = metadata["template"]
    result["template_type"] = template_type

    if template_type not in registry:
        valid_types = ", ".join(sorted(registry.keys()))
        result["is_valid"] = False
        result["errors"].append(f"Unknown template type '{template_type}'. Valid types: {valid_types}")
        return result

    rules = registry[template_type]
```

**Changed Code:**
```python
    template_type = metadata["template"]

    # WORK-152: Route plan templates by subtype for type-specific validation
    if template_type == "implementation_plan" and "subtype" in metadata:
        subtype_key = f"implementation_plan_{metadata['subtype']}"
        if subtype_key in registry:
            template_type = subtype_key

    result["template_type"] = template_type

    if template_type not in registry:
        valid_types = ", ".join(sorted(registry.keys()))
        result["is_valid"] = False
        result["errors"].append(f"Unknown template type '{template_type}'. Valid types: {valid_types}")
        return result

    rules = registry[template_type]
```

This ensures `check_section_coverage(template_type, content)` on line 617 receives the mapped type (`implementation_plan_design`) not the raw frontmatter type (`implementation_plan`).

Also add `subtype` to the `optional_fields` list for the existing `implementation_plan` entry:
```python
        "implementation_plan": {
            ...
            "optional_fields": [
                "version", "author", "plan_id", "title", "session", "priority",
                "lifecycle_phase", "subtype", ...  # <-- ADD "subtype"
            ],
```

### Call Chain Context

```
scaffold_template("implementation_plan", backlog_id="WORK-149")
    |
    +-> _get_work_type("WORK-149")       # <-- NEW: reads type from WORK.md
    |       Returns: "design"
    |
    +-> load_plan_template("design")     # <-- NEW: routes via get_plan_type()
    |       get_plan_type("design") -> "design"
    |       Returns: str (design-specific template content)
    |       Fallback: load_template("implementation_plan")
    |
    +-> substitute_variables(content, variables)
    |
    +-> write output file (with subtype: design in frontmatter)

validate_template(file_path)
    |
    +-> metadata["template"] == "implementation_plan"
    +-> metadata["subtype"] == "design"
    +-> template_type = "implementation_plan_design"  # <-- NEW: subtype routing
    |
    +-> get_template_registry()["implementation_plan_design"]
    |       Returns: type-specific rules with reduced expected_sections
    |
    +-> check_section_coverage("implementation_plan_design", content)
            Uses: design-specific expected_sections (no TDD, no code diffs)
```

### Function/Component Signatures

```python
# Mapping constant
PLAN_TYPE_MAP = {
    "feature": "implementation",
    "investigation": "implementation",
    "bug": "cleanup",
    "chore": "cleanup",
    "spike": "implementation",
    "design": "design",
}

def get_plan_type(work_type: str) -> str:
    """Map work item type to plan template type.

    Args:
        work_type: Work item type field value (feature, bug, chore, design, etc.)

    Returns:
        Plan template type: "implementation", "design", or "cleanup".
        Defaults to "implementation" for unmapped types.
    """

def _get_work_type(backlog_id: str) -> Optional[str]:
    """Get type of existing work item for plan template routing.

    Args:
        backlog_id: Work item ID (e.g., "WORK-152")

    Returns:
        Type string ("feature", "design", etc.) if found, None otherwise.
    """

def load_plan_template(work_type: str = "implementation") -> str:
    """Load work-type-specific plan template.

    Args:
        work_type: Work item type from WORK.md 'type' field.
                   Mapped via get_plan_type() to template type.
                   Defaults to "implementation" for backward compat.

    Returns:
        Template content string.
    """
```

### Behavior Logic

**Current Flow:**
```
scaffold_template("implementation_plan") → load_template("implementation_plan")
                                         → always returns monolithic 446-line template
```

**New Flow (with auto-extraction):**
```
scaffold_template("implementation_plan", backlog_id="WORK-149")
    → TYPE not in variables? → _get_work_type("WORK-149") → "design"
    → variables["TYPE"] = "design"
    → load_plan_template("design")
        → get_plan_type("design") → "design"
        → check .claude/templates/plans/design.md exists?
            ├─ YES → return design template (~200 lines, with subtype: design in frontmatter)
            └─ NO  → load_template("implementation_plan") → monolithic fallback

scaffold_template("implementation_plan", backlog_id="WORK-153")
    → _get_work_type("WORK-153") → "bug"
    → load_plan_template("bug")
        → get_plan_type("bug") → "cleanup"
        → check .claude/templates/plans/cleanup.md exists?
            ├─ YES → return cleanup template (~150 lines, with subtype: cleanup)
            └─ NO  → fallback
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Template location | `.claude/templates/plans/{plan_type}.md` | Follows E2.5 lifecycle fracturing pattern (`.claude/templates/{lifecycle}/{PHASE}.md`) — consistency over novelty |
| Type mapping layer | `PLAN_TYPE_MAP` dict + `get_plan_type()` | Work item types (feature/bug/chore) don't match template types (implementation/cleanup/design). Explicit mapping prevents silent fallback (Critique A1). |
| Auto-extract TYPE from work item | `_get_work_type(backlog_id)` in scaffold_template | No caller currently passes TYPE. Auto-extraction from WORK.md frontmatter ensures routing works without caller changes (Critique A2). |
| Validation subtype routing | `subtype` field in frontmatter, detected by `validate_template()` | Plans keep `template: implementation_plan` for scaffold compat, but `subtype: design` routes to type-specific registry (Critique A3). |
| New function vs modify load_template | New `load_plan_template()` | load_template() is generic; plan routing is plan-specific. Separation of concerns. |
| Fallback behavior | Unknown types fall back to monolithic | Backward compat — no existing workflow breaks if type is missing |
| Validation registry naming | `implementation_plan_{subtype}` | Extends existing `implementation_plan` key with subtype suffix; existing tests unaffected (additive only). |
| No `investigation` plan template file | Not needed | Investigation work items use investigation-cycle with their own template. WORK.md acceptance criteria to be updated to remove investigation from scope (Critique A4). |
| `_get_work_type()` follows `_get_work_status()` pattern | Reuse existing YAML parsing pattern | Consistency with scaffold.py:142-166 (Critique verified). |

### Input/Output Examples

**Before (with real data from WORK-149, type: design):**
```
scaffold_template("implementation_plan", backlog_id="WORK-149", title="Three-Tier ADR")
  _get_work_type("WORK-149") → "design" (from WORK.md but not used today)
  load_template("implementation_plan") → 446-line monolithic template
  Result: 6 of 15 sections require SKIPPED rationale (40%)
```

**After (expected, same call — auto-extraction makes it transparent):**
```
scaffold_template("implementation_plan", backlog_id="WORK-149", title="Three-Tier ADR")
  _get_work_type("WORK-149") → "design"
  get_plan_type("design") → "design"
  load_plan_template("design") → .claude/templates/plans/design.md (~200 lines)
  Result: ~8 sections, 0 SKIPPED rationales needed

validate_template("docs/work/active/WORK-149/plans/PLAN.md")
  metadata["template"] → "implementation_plan"
  metadata["subtype"] → "design"
  template_type → "implementation_plan_design"
  expected_sections: Goal, Effort, State, Design, Steps, Verify, Risks, Progress, Ground Truth
  Result: validates against reduced section list
```

**Bug-type example (WORK-153, type: bug):**
```
scaffold_template("implementation_plan", backlog_id="WORK-153", title="Bug Batch")
  _get_work_type("WORK-153") → "bug"
  get_plan_type("bug") → "cleanup"
  load_plan_template("bug") → .claude/templates/plans/cleanup.md (~150 lines)
  Result: ~6 sections, minimal template
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| TYPE variable not provided, no backlog_id | Default to "implementation" (full template) | Test 3 |
| TYPE variable not provided, backlog_id exists | Auto-extract from WORK.md type field | Test 6 |
| Work item type "feature" | Maps to "implementation" via PLAN_TYPE_MAP | Test 7 |
| Work item type "bug" or "chore" | Maps to "cleanup" via PLAN_TYPE_MAP | Test 7 |
| Unknown work type (e.g. "experimental") | get_plan_type returns "implementation" (fallback) | Test 7 |
| Plan template file missing for mapped type | Fallback to monolithic template | Test 2 |
| Existing plans without `subtype` field | Validate against `implementation_plan` registry (backward compat) | Existing tests |
| Plan with `subtype: design` | Validate against `implementation_plan_design` registry | Test 8 |
| Work item WORK.md not found | _get_work_type returns None, uses default | Test 3 (no backlog_id case) |

### Open Questions

All resolved during critique-revise loop:

**Q: How does validate.py know which registry key to use?** (Resolved — Critique A3)

Type-specific templates include `subtype: design` (or `cleanup`) in frontmatter. `validate_template()` detects `subtype` field, maps to `implementation_plan_{subtype}` registry key. If no subtype, uses `implementation_plan` (backward compat). See Exact Code Change 4.

**Q: How does TYPE get passed to scaffold_template?** (Resolved — Critique A2)

`scaffold_template()` auto-extracts TYPE from work item WORK.md via `_get_work_type(backlog_id)` when TYPE is not in variables. No caller changes needed. See Exact Code Change 2.

---

## Open Decisions (MUST resolve before implementation)

No `operator_decisions` in WORK-152 frontmatter. No blocking decisions.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No operator decisions required |

---

## Implementation Steps

### Step 0: Update WORK.md acceptance criteria (Critique A4)
- [ ] Remove "investigation" from acceptance criteria (investigation work uses investigation-cycle, not plan templates)
- [ ] Update to: "Plan templates exist per work type (implementation, design, cleanup)"

### Step 1: Write Failing Tests
- [ ] Add test_get_plan_type_mapping to tests/test_lib_scaffold.py (Test 7)
- [ ] Add test_load_plan_template_routes_by_type to tests/test_lib_scaffold.py (Test 1)
- [ ] Add test_load_plan_template_fallback_to_legacy to tests/test_lib_scaffold.py (Test 2)
- [ ] Add test_load_plan_template_default_is_implementation to tests/test_lib_scaffold.py (Test 3)
- [ ] Add test_scaffold_template_auto_extracts_type to tests/test_lib_scaffold.py (Test 6)
- [ ] Add test_validate_registry_design_plan_sections to tests/test_lib_validate.py (Test 4)
- [ ] Add test_validate_registry_cleanup_plan_sections to tests/test_lib_validate.py (Test 5)
- [ ] Add test_validate_template_routes_by_subtype to tests/test_lib_validate.py (Test 8)
- [ ] Verify all 8 tests fail (red)

### Step 2: Create type-specific plan templates
- [ ] Create `.claude/templates/plans/` directory
- [ ] Create `design.md` template with `subtype: design` in frontmatter (Goal, Effort, State (prose), Design Decisions, Steps, Verify, Risks, Ground Truth)
- [ ] Create `cleanup.md` template with `subtype: cleanup` in frontmatter (Goal, Effort, Change List, Steps, Verify, Ground Truth)
- [ ] Create `implementation.md` as copy of `_legacy/implementation_plan.md` (no subtype — backward compat)
- [ ] Create `README.md` documenting the variants and type mapping

### Step 3: Implement scaffold.py changes
- [ ] Add `PLAN_TYPE_MAP` constant and `get_plan_type()` function (Code Change 1)
- [ ] Add `_get_work_type()` helper after `_get_work_status()` (Code Change 2b)
- [ ] Add `load_plan_template()` function after `load_template()` (Code Change 1)
- [ ] Modify `scaffold_template()` to auto-extract TYPE and route via `load_plan_template()` (Code Change 2)
- [ ] Tests 1, 2, 3, 6, 7 pass (green)

### Step 4: Extend validate.py
- [ ] Add `implementation_plan_design` entry to `get_template_registry()` (Code Change 3)
- [ ] Add `implementation_plan_cleanup` entry to `get_template_registry()` (Code Change 3)
- [ ] Add `subtype` to `optional_fields` for existing `implementation_plan` entry
- [ ] Add subtype routing in `validate_template()` (Code Change 4)
- [ ] Tests 4, 5, 8 pass (green)

### Step 5: Integration Verification
- [ ] All 8 new tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 6: Consumer Verification (MUST)
- [ ] Grep for `implementation_plan` in skills, commands, hooks
- [ ] Update plan-authoring-cycle SKILL.md "Related" section reference
- [ ] Update plan-validation-cycle SKILL.md "Related" section reference
- [ ] Update `.claude/templates/README.md` with new plans/ directory
- [ ] Verify no stale references remain

---

## Verification

- [ ] Tests pass (8 new + existing suite)
- [ ] **MUST:** All READMEs current (templates/plans/README.md, templates/README.md)
- [ ] Design template has ~8 sections (not 15+)
- [ ] Cleanup template has ~6 sections
- [ ] Existing `implementation_plan` scaffold still works unchanged (backward compat)
- [ ] Type mapping: feature->implementation, bug->cleanup, design->design
- [ ] Validate subtype routing: plan with `subtype: design` uses design registry

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing test fixtures reference `implementation_plan` expected_sections | Med | Don't change existing registry entry — ADD new entries alongside. Existing tests continue to pass. Additive only. |
| Type vocabulary mismatch (Critique A1) | High | Explicit PLAN_TYPE_MAP mapping with fallback to "implementation". Test 7 covers all known types + unknown fallback. |
| No caller passes TYPE (Critique A2) | High | Auto-extraction via _get_work_type(backlog_id). No caller changes needed. Test 6 verifies. |
| validate_template doesn't route to subtype (Critique A3) | High | Explicit subtype detection added (Code Change 4). Test 8 verifies. |
| Template drift — fractured templates get out of sync with shared sections | Low | Shared sections (Goal, Effort, Verification, Ground Truth) are identical across types. Document in README that changes to shared sections must be applied to all variants. |
| Memory note CH-006 lesson: fracturing broke 8+ consumers | High | Consumer verification step is explicit. Grep for all references before declaring done. Memory: 83973, 83974. |
| plans/implementation.md copy drift from _legacy/ (Critique A7) | Low | Document in README that plans/implementation.md is canonical for new work. _legacy/ is fallback only. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 389 | 2026-02-16 | - | Plan authored | PLAN phase |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-152/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Plan templates exist per work type (implementation, design, cleanup) | [ ] | Glob `.claude/templates/plans/*.md` |
| Each template contains only sections relevant to its work type | [ ] | Read each template, count sections |
| Type mapping routes work item types to correct plan template | [ ] | Test 7 passes, PLAN_TYPE_MAP verified |
| scaffold_template auto-extracts TYPE from work item | [ ] | Test 6 passes, _get_work_type verified |
| validate_template routes by subtype for section coverage | [ ] | Test 8 passes, Code Change 4 verified |
| Existing plan-authoring-cycle and plan-validation-cycle references updated | [ ] | Read skill MDs, verify reference updates |
| Skip rationale frequency drops to <20% of sections per plan | [ ] | Count sections in design.md vs monolithic |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/plans/design.md` | ~8 sections, subtype: design in frontmatter | [ ] | |
| `.claude/templates/plans/cleanup.md` | ~6 sections, subtype: cleanup in frontmatter | [ ] | |
| `.claude/templates/plans/implementation.md` | Full template (same as monolithic), no subtype | [ ] | |
| `.claude/templates/plans/README.md` | Documents all variants and type mapping | [ ] | |
| `.claude/haios/lib/scaffold.py` | PLAN_TYPE_MAP, get_plan_type(), _get_work_type(), load_plan_template(), routing in scaffold_template() | [ ] | |
| `.claude/haios/lib/validate.py` | Registry has design/cleanup entries, subtype routing in validate_template(), subtype in optional_fields | [ ] | |
| `tests/test_lib_scaffold.py` | 5 new tests (Tests 1,2,3,6,7) | [ ] | |
| `tests/test_lib_validate.py` | 3 new tests (Tests 4,5,8) | [ ] | |
| `docs/work/active/WORK-152/WORK.md` | Acceptance criteria updated (no investigation) | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_scaffold.py tests/test_lib_validate.py -v
# Expected: all existing + 8 new tests passed
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
- [ ] **Runtime consumer exists** (scaffold_template calls load_plan_template at runtime)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] **MUST:** Consumer verification complete (grep for stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/templates/_legacy/implementation_plan.md (current monolithic template)
- @docs/work/active/WORK-149/plans/PLAN.md (evidence of skip rationale overhead)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md (prior fracturing pattern)
- Memory: 85528-85531 (S378 plan template skew observation)
- Memory: 85666 (lightweight plan template for bugfix/cleanup)
- Memory: 83973-83974 (CH-006 consumer update lesson)

---
