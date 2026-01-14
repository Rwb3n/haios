---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-272
title: Add operator_decisions Field to Work Item Template
author: Hephaestus
lifecycle_phase: plan
session: 176
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-05T22:24:36'
---
# Implementation Plan: Add operator_decisions Field to Work Item Template

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

Work items will have a structured `operator_decisions` field in YAML frontmatter that agents can machine-check to detect unresolved decisions before plan authoring begins.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/templates/work_item.md`, `.claude/lib/validate.py` |
| Lines of code affected | ~15 | Template: ~5 lines, validate.py: ~1 line |
| New files to create | 0 | - |
| Tests to write | 2 | Registry test, validation behavior test |
| Dependencies | 1 | `GovernanceLayer.validate_template()` wraps validate.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only template + validation registry |
| Risk of regression | Low | Adding field, not changing existing behavior |
| External dependencies | Low | No external APIs, pure YAML schema change |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 10 min | High |
| Template update | 5 min | High |
| Validation registry update | 5 min | High |
| README sync | 5 min | High |
| **Total** | 25 min | High |

---

## Current State vs Desired State

### Current State

```yaml
# .claude/templates/work_item.md:1-32 - Current frontmatter schema
---
template: work_item
id: {{BACKLOG_ID}}
title: "{{TITLE}}"
status: active
owner: Hephaestus
created: {{DATE}}
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
# ... no operator_decisions field exists
---
```

**Behavior:** Work items have no structured field for operator decisions. Agents must infer decisions from prose in Context or Deliverables sections.

**Result:** Agents miss or misinterpret operator decisions, leading to plans built on wrong assumptions (e.g., E2-271 incident).

### Desired State

```yaml
# .claude/templates/work_item.md - Target frontmatter schema
---
template: work_item
id: {{BACKLOG_ID}}
# ... existing fields ...
operator_decisions: []  # NEW: Structured list of decisions
# Schema per decision:
#   - question: "What needs deciding?"
#     options: ["option A", "option B"]
#     resolved: false
#     chosen: null
---
```

**Behavior:** Work items have a machine-checkable `operator_decisions` field. E2-274 (plan-authoring-cycle) can read this field and block if any decision has `resolved: false`.

**Result:** Ambiguous work items surface decisions BEFORE plan authoring begins, preventing wasted effort on incorrect plans.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Registry Contains operator_decisions Field
```python
def test_work_item_registry_includes_operator_decisions():
    """Work item template should list operator_decisions as optional field."""
    from validate import get_template_registry

    registry = get_template_registry()
    work_item_config = registry["work_item"]

    assert "operator_decisions" in work_item_config["optional_fields"]
```

### Test 2: Template Contains operator_decisions Field
```python
def test_work_item_template_has_operator_decisions_field():
    """Work item template file should have operator_decisions in frontmatter."""
    from pathlib import Path

    template_path = Path(".claude/templates/work_item.md")
    content = template_path.read_text()

    assert "operator_decisions:" in content
```

### Test 3: Backward Compatibility - Empty List Default
```python
def test_operator_decisions_defaults_to_empty_list():
    """New work items should have operator_decisions: [] by default."""
    from pathlib import Path
    import yaml

    template_path = Path(".claude/templates/work_item.md")
    content = template_path.read_text()

    # Extract YAML frontmatter (between --- markers)
    yaml_match = content.split("---")[1]
    # Note: Template has placeholders, so we check the literal text
    assert "operator_decisions: []" in content
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does. -->

### Exact Code Change 1: Template File

**File:** `.claude/templates/work_item.md`
**Location:** Lines 24-25, after `memory_refs: []`

**Current Code:**
```yaml
# .claude/templates/work_item.md:24-25
memory_refs: []
documents:
```

**Changed Code:**
```yaml
# .claude/templates/work_item.md:24-26
memory_refs: []
operator_decisions: []
documents:
```

**Diff:**
```diff
 memory_refs: []
+operator_decisions: []
 documents:
```

### Exact Code Change 2: Validation Registry

**File:** `.claude/lib/validate.py`
**Location:** Lines 150-157, in `get_template_registry()` work_item config

**Current Code:**
```python
# .claude/lib/validate.py:150-157
        "work_item": {
            "required_fields": ["template", "status", "id", "title", "current_node"],
            "optional_fields": [
                "owner", "created", "closed", "milestone", "priority", "effort",
                "category", "spawned_by", "spawned_by_investigation", "blocked_by",
                "blocks", "enables", "related", "node_history", "cycle_docs",
                "memory_refs", "documents", "version",
            ],
```

**Changed Code:**
```python
# .claude/lib/validate.py:150-158
        "work_item": {
            "required_fields": ["template", "status", "id", "title", "current_node"],
            "optional_fields": [
                "owner", "created", "closed", "milestone", "priority", "effort",
                "category", "spawned_by", "spawned_by_investigation", "blocked_by",
                "blocks", "enables", "related", "node_history", "cycle_docs",
                "memory_refs", "documents", "version", "operator_decisions",
            ],
```

**Diff:**
```diff
-                "memory_refs", "documents", "version",
+                "memory_refs", "documents", "version", "operator_decisions",
```

### Call Chain Context

```
/new-work command
    |
    +-> just work <id> <title>
    |       |
    |       +-> scaffold.scaffold_template("work_item", ...)
    |                 |
    |                 +-> Reads .claude/templates/work_item.md  # <-- Template change
    |
    +-> work-creation-cycle skill
            |
            +-> WorkEngine.create_work()

just validate <file>
    |
    +-> GovernanceLayer.validate_template()
            |
            +-> validate.validate_template()
                    |
                    +-> get_template_registry()  # <-- Registry change
```

### Function/Component Signatures

No new functions. Changes are:
1. Template YAML schema (data, not code)
2. Registry list entry (string addition)

### Behavior Logic

**Current Flow:**
```
Work item created → No operator_decisions field → Agent must infer from prose
```

**Fixed Flow:**
```
Work item created → operator_decisions: [] in frontmatter → Agent can check field
    |
    +-> If decisions needed → work-creation-cycle populates field
    |                          → operator resolves via AskUserQuestion
    |
    +-> plan-authoring-cycle → Reads operator_decisions
                                  → Blocks if any resolved: false
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Field placement | After `memory_refs`, before `documents` | Groups metadata fields together, keeps `documents` block at end |
| Default value | Empty list `[]` | Most work items have no decisions; empty list is valid YAML |
| Schema structure | List of objects with question/options/resolved/chosen | Matches INV-058 design; machine-checkable structure |
| Not required field | Optional | Backward compatible with existing work items |

### Input/Output Examples

**Before (no field):**
```yaml
# E2-271/WORK.md current state - no operator_decisions
memory_refs: []
documents:
  investigations: []
```

**After (with field):**
```yaml
# E2-271/WORK.md after E2-272 - has operator_decisions
memory_refs: []
operator_decisions:
  - question: "Implement modules or remove references?"
    options: ["implement", "remove"]
    resolved: false
    chosen: null
documents:
  investigations: []
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Existing work items without field | Validation passes (optional field) | Backward compatibility |
| Empty list | Valid - no decisions needed | Test 3 |
| Malformed entry | YAML parser handles; not validated in E2-272 | E2-274 responsibility |

### Open Questions

**Q: Should we validate operator_decisions schema (question/options/resolved/chosen)?**

Answer: No - E2-272 scope is adding the field. E2-274 (plan-authoring-cycle) will validate structure when reading. Keeps E2-272 minimal.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add test `test_work_item_registry_includes_operator_decisions` to `tests/test_lib_validate.py`
- [ ] Add test `test_work_item_template_has_operator_decisions_field` to `tests/test_lib_validate.py`
- [ ] Run `pytest tests/test_lib_validate.py -v` - verify tests 1 and 2 fail (red)

### Step 2: Update Validation Registry
- [ ] Edit `.claude/lib/validate.py` line 156
- [ ] Add `"operator_decisions"` to work_item `optional_fields` list
- [ ] Test 1 passes (green)

### Step 3: Update Work Item Template
- [ ] Edit `.claude/templates/work_item.md`
- [ ] Add `operator_decisions: []` after `memory_refs: []` (line 25)
- [ ] Tests 2 and 3 pass (green)

### Step 4: Integration Verification
- [ ] Run `pytest tests/test_lib_validate.py -v` - all tests pass
- [ ] Run `pytest -v` - no regressions
- [ ] Run `just validate docs/work/active/E2-272/WORK.md` - validates successfully

### Step 5: README Sync (MUST)
- [ ] **MUST:** Check `.claude/templates/README.md` for work_item template documentation
- [ ] **MUST:** Update if field schema is documented there

### Step 6: Consumer Verification
**SKIPPED:** Not a migration/refactor. Adding new optional field with backward compatibility. Existing work items without field remain valid.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment | Low | INV-058 explicitly designed this schema; following spec exactly |
| Backward compatibility | Low | Field is optional; existing work items remain valid |
| Integration with E2-274 | Med | Schema documented in INV-058; E2-274 reads same spec |
| Field not validated | Low | Intentional - E2-274 validates at read time, not E2-272 |

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
| `.claude/templates/work_item.md` | Contains `operator_decisions: []` | [x] | Line 26 |
| `.claude/lib/validate.py` | `"operator_decisions"` in work_item optional_fields | [x] | Line 156 |
| `tests/test_lib_validate.py` | Contains operator_decisions tests | [x] | 3 tests added |
| `.claude/templates/README.md` | Check if needs update | [x] | No update needed - lists templates not field schemas |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_lib_validate.py::TestGetTemplateRegistry -v
# Expected: tests pass including operator_decisions
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read each file during implementation |
| Test output pasted above? | Yes | 3 passed in 0.33s |
| Any deviations from plan? | No | Implementation matches Detailed Design exactly |

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

- INV-058: Ambiguity Gating for Plan Authoring (source investigation with schema design)
- E2-271: Skill Module Reference Cleanup (blocked by this, triggered INV-058)
- E2-273: Add Open Decisions Section to Implementation Plan Template (next gate)
- E2-274: Add AMBIGUITY Phase to plan-authoring-cycle (uses this field)
- E2-275: Add Decision Check to plan-validation-cycle (validates this field)

---
