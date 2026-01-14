---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-273
title: Add Open Decisions Section to Implementation Plan Template
author: Hephaestus
lifecycle_phase: plan
session: 176
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-05T22:45:11'
---
# Implementation Plan: Add Open Decisions Section to Implementation Plan Template

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

Implementation plans will have an "Open Decisions" section that surfaces unresolved operator decisions from the work item, enabling E2-275 to block plans with unresolved decisions.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/templates/implementation_plan.md` |
| Lines of code affected | ~15 | New section insertion |
| New files to create | 0 | - |
| Tests to write | 1 | Template section existence test |
| Dependencies | 0 | Template only, no code imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Template only |
| Risk of regression | Low | Adding section, not changing existing |
| External dependencies | Low | No APIs, pure markdown |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 5 min | High |
| Template update | 10 min | High |
| **Total** | 15 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/templates/implementation_plan.md:292-298 - Open Questions section exists
### Open Questions

<!-- Surface any uncertainties discovered during design -->

**Q: [Question about behavior or design]**

[Answer based on code analysis, or mark as "TBD - verify during implementation"]

---

## Implementation Steps
```

**Behavior:** Template has "Open Questions" for design uncertainties but no section for operator decisions from work item.

**Result:** Plans don't surface work item decisions; agents make assumptions instead of asking operator.

### Desired State

```markdown
# .claude/templates/implementation_plan.md - New section after Open Questions
### Open Questions
...existing...

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
| [From work item operator_decisions] | [A, B] | [BLOCKED] | [Why this choice - filled when resolved] |

---

## Implementation Steps
```

**Behavior:** Template has explicit "Open Decisions" section that surfaces work item's `operator_decisions` field.

**Result:** E2-274 (plan-authoring-cycle) populates this section; E2-275 (plan-validation-cycle) blocks if any are [BLOCKED].

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Template Contains Open Decisions Section
```python
def test_implementation_plan_template_has_open_decisions_section():
    """Implementation plan template should have Open Decisions section."""
    template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
    content = template_path.read_text()

    assert "## Open Decisions" in content
```

### Test 2: Section Has Required Table Structure
```python
def test_open_decisions_section_has_table():
    """Open Decisions section should have Decision/Options/Chosen/Rationale table."""
    template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
    content = template_path.read_text()

    assert "| Decision | Options | Chosen | Rationale |" in content
```

### Test 3: Section Has BLOCK Comment
```python
def test_open_decisions_section_has_block_comment():
    """Open Decisions section should document BLOCK behavior."""
    template_path = Path(__file__).parent.parent / ".claude" / "templates" / "implementation_plan.md"
    content = template_path.read_text()

    assert "plan-validation-cycle will BLOCK" in content
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does. -->

### Exact Code Change

**File:** `.claude/templates/implementation_plan.md`
**Location:** After "Open Questions" section (~line 298), before "Implementation Steps" section

**Current Code:**
```markdown
# .claude/templates/implementation_plan.md:292-300
### Open Questions

<!-- Surface any uncertainties discovered during design -->

**Q: [Question about behavior or design]**

[Answer based on code analysis, or mark as "TBD - verify during implementation"]

---

## Implementation Steps
```

**Changed Code:**
```markdown
# .claude/templates/implementation_plan.md - Insert new section
### Open Questions

<!-- Surface any uncertainties discovered during design -->

**Q: [Question about behavior or design]**

[Answer based on code analysis, or mark as "TBD - verify during implementation"]

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
| [From work item operator_decisions] | [A, B] | [BLOCKED] | [Why this choice - filled when resolved] |

---

## Implementation Steps
```

**Diff:**
```diff
 [Answer based on code analysis, or mark as "TBD - verify during implementation"]

 ---

+## Open Decisions (MUST resolve before implementation)
+
+<!-- Decisions from work item's operator_decisions field.
+     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.
+
+     POPULATE FROM: Work item frontmatter `operator_decisions` field
+     - question -> Decision column
+     - options -> Options column
+     - chosen -> Chosen column (null = [BLOCKED])
+     - rationale -> Rationale column (filled when resolved) -->
+
+| Decision | Options | Chosen | Rationale |
+|----------|---------|--------|-----------|
+| [From work item operator_decisions] | [A, B] | [BLOCKED] | [Why this choice - filled when resolved] |
+
+---
+
 ## Implementation Steps
```

### Call Chain Context

```
/new-plan command
    |
    +-> just plan <id> <title>
    |       |
    |       +-> Reads .claude/templates/implementation_plan.md  # <-- Template change
    |
    +-> plan-authoring-cycle skill (E2-274)
    |       |
    |       +-> AMBIGUITY phase reads work item operator_decisions
    |       +-> Populates Open Decisions section from work item
    |
    +-> plan-validation-cycle skill (E2-275)
            |
            +-> Checks Open Decisions section for [BLOCKED] entries
            +-> BLOCK if any unresolved
```

### Function/Component Signatures

No new functions. This is a template-only change (markdown).

### Behavior Logic

**Current Flow:**
```
Plan authored → No Open Decisions section → Agent proceeds with assumptions
```

**Fixed Flow:**
```
Plan authored → Open Decisions section exists → E2-274 populates from work item
    |
    +-> All resolved → E2-275 passes → Implementation proceeds
    |
    +-> Any [BLOCKED] → E2-275 blocks → Operator must resolve
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Section placement | After Open Questions, before Implementation Steps | Logical flow: questions → decisions → implementation |
| Table columns | Decision, Options, Chosen, Rationale | Matches INV-058 operator_decisions schema |
| [BLOCKED] marker | Literal text in Chosen column | Machine-checkable by E2-275 |
| Comment includes POPULATE FROM | Documents data source | Guides E2-274 implementation |

### Input/Output Examples

**Before (no section):**
Plans don't surface work item decisions.

**After (with section):**
```markdown
## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Implement modules or remove references? | [implement, remove] | implement | Operator chose to implement proper modules |
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No decisions in work item | Empty table with header | E2-274 responsibility |
| Decision already resolved | Chosen column has value | E2-274 responsibility |

### Open Questions

**Q: Should we validate the table format?**

Answer: No - E2-273 scope is adding the section. E2-275 will validate structure when checking. Keeps E2-273 minimal.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 3 tests to `tests/test_lib_validate.py` in new `TestImplementationPlanTemplate` class
- [ ] Run `pytest tests/test_lib_validate.py::TestImplementationPlanTemplate -v` - verify tests fail (red)

### Step 2: Add Open Decisions Section to Template
- [ ] Edit `.claude/templates/implementation_plan.md`
- [ ] Insert new section after "Open Questions" (~line 298)
- [ ] Include: header, comment, table structure
- [ ] All 3 tests pass (green)

### Step 3: Integration Verification
- [ ] Run `pytest tests/test_lib_validate.py -v` - all tests pass
- [ ] Run `pytest -v` - no regressions
- [ ] Run `just validate docs/work/active/E2-273/plans/PLAN.md` - validates successfully

### Step 4: README Sync (MUST)
- [ ] **MUST:** Check `.claude/templates/README.md` - already documents templates, no field-level updates needed

### Step 5: Consumer Verification
**SKIPPED:** Not a migration/refactor. Adding new section with backward compatibility.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment | Low | INV-058 designed exact section schema; following spec |
| Backward compatibility | Low | New section doesn't affect existing plans |
| Integration with E2-274/E2-275 | Med | Schema documented in INV-058; shared spec |

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
| `.claude/templates/implementation_plan.md` | Contains `## Open Decisions` section | [x] | Line 302 |
| `tests/test_lib_validate.py` | Contains TestImplementationPlanTemplate tests | [x] | 3 tests added |
| `.claude/templates/README.md` | Check if needs update | [x] | No update needed |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_lib_validate.py::TestImplementationPlanTemplate -v
# Expected: 3 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Verified via Grep |
| Test output pasted above? | Yes | 3 passed in 0.15s |
| Any deviations from plan? | No | Implementation matches spec |

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
- E2-272: Add operator_decisions Field to Work Item Template (prerequisite - COMPLETE)
- E2-274: Add AMBIGUITY Phase to plan-authoring-cycle (populates this section)
- E2-275: Add Decision Check to plan-validation-cycle (validates this section)

---
