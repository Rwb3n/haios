---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-275
title: Add Decision Check to plan-validation-cycle
author: Hephaestus
lifecycle_phase: plan
session: 177
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-05T23:18:59'
---
# Implementation Plan: Add Decision Check to plan-validation-cycle

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

The plan-validation-cycle skill will BLOCK plans that have unresolved decisions in the "Open Decisions" section (entries with `[BLOCKED]` in the Chosen column).

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/skills/plan-validation-cycle/SKILL.md`, `tests/test_lib_validate.py` |
| Lines of code affected | ~218 | SKILL.md is 218 lines (adding ~15 lines for new check) |
| New files to create | 0 | Modification only |
| Tests to write | 2 | Template validation tests for new check |
| Dependencies | 0 | Skill is markdown instructions, no code imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skill is standalone markdown |
| Risk of regression | Low | Additive change, existing phases unchanged |
| External dependencies | Low | No APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 5 min | High |
| Add decision check | 10 min | High |
| Update tables | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/plan-validation-cycle/SKILL.md:88-116 (VALIDATE phase)
### 3. VALIDATE Phase

**Quality Checks:**
- Goal: Single sentence, measurable outcome
- Effort: Real numbers from file analysis
- Tests: Concrete assertions, not placeholders
- Design: File paths, code snippets present
- Key Design Decisions: Rationale column filled
- Steps: Actionable checklist items
- Risks: At least one risk with mitigation
```

**Behavior:** VALIDATE phase checks section quality but has no check for "Open Decisions" section.

**Result:** A plan can pass validation while having unresolved operator decisions.

### Desired State

```markdown
# .claude/skills/plan-validation-cycle/SKILL.md (target)
### 3. VALIDATE Phase

**Quality Checks:**
- [existing checks...]
- **Open Decisions: No [BLOCKED] entries in Chosen column** (Gate 4)
```

**Behavior:** VALIDATE phase checks that "Open Decisions" table has no `[BLOCKED]` entries.

**Result:** Plans with unresolved decisions are BLOCKED before reaching implementation.

---

## Tests First (TDD)

### Test 1: Skill Contains Decision Check
```python
def test_skill_has_decision_check():
    """SKILL.md should mention checking Open Decisions section."""
    skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-validation-cycle" / "SKILL.md"
    content = skill_path.read_text()

    # Must mention Open Decisions check
    assert "Open Decisions" in content, "Must check Open Decisions section"
    # Must mention BLOCKED detection
    assert "BLOCKED" in content, "Must detect [BLOCKED] entries"
```

### Test 2: Decision Check Is Gate 4
```python
def test_decision_check_is_gate_4():
    """Decision check should be labeled as Gate 4 of INV-058."""
    skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-validation-cycle" / "SKILL.md"
    content = skill_path.read_text()

    # Should reference Gate 4
    assert "Gate 4" in content, "Must be labeled as Gate 4"
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/skills/plan-validation-cycle/SKILL.md`
**Location:** Insert in VALIDATE phase (Section 3), after existing Quality Checks

**New Quality Check (add to list at line ~98):**
```markdown
- **Open Decisions: No [BLOCKED] entries in Chosen column** (Gate 4 - E2-275)
```

**New Exit Criterion (add after line ~115):**
```markdown
- [ ] **MUST:** Open Decisions table has no [BLOCKED] entries
```

**New Action (add after "Flag sections with insufficient detail"):**
```markdown
6. **Check Open Decisions section (Gate 4):**
   - Scan "## Open Decisions" section for table
   - Check Chosen column for `[BLOCKED]` pattern
   - If ANY [BLOCKED] found: **BLOCK** with message listing unresolved decisions
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Location in VALIDATE | Add as quality check | VALIDATE already checks section content quality |
| String detection | Look for `[BLOCKED]` | Template uses this exact marker in E2-273 |
| Gate label | "Gate 4" | Final gate of INV-058 defense-in-depth |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No Open Decisions section | Pass (section is optional if no decisions exist) | - |
| Empty table | Pass (no [BLOCKED] entries) | - |
| Multiple [BLOCKED] | Report all in block message | - |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (No operator decisions in work item) | - | - | E2-275 has no `operator_decisions` field |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 2 tests to `tests/test_lib_validate.py` in new `TestPlanValidationCycleSkill` class
- [ ] Verify all tests fail (red)

### Step 2: Add Decision Check to VALIDATE Phase
- [ ] Add "Open Decisions: No [BLOCKED] entries" to Quality Checks list
- [ ] Add exit criterion for Open Decisions check
- [ ] Add action step for checking [BLOCKED] pattern
- [ ] Tests pass (green)

### Step 3: Update Tables
- [ ] No table updates needed (check is part of existing VALIDATE phase)

### Step 4: Integration Verification
- [ ] All 2 new tests pass
- [ ] Run `pytest tests/test_lib_validate.py -v`

---

## Verification

- [ ] Tests pass
- [ ] Skill content matches design

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing validation consumers confused | Low | Change is additive to existing checks |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 177 | 2026-01-05 | - | In progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/plan-validation-cycle/SKILL.md` | Contains "Open Decisions" check and "Gate 4" | [ ] | |
| `tests/test_lib_validate.py` | Contains TestPlanValidationCycleSkill class with 2 tests | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_validate.py::TestPlanValidationCycleSkill -v
# Expected: 2 tests passed
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
- [ ] **Runtime consumer exists** - plan-validation-cycle is invoked by implementation-cycle
- [ ] WHY captured (reasoning stored to memory)
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/archive/INV-058/investigations/001-ambiguity-gating-for-plan-authoring.md (source design)
- @docs/checkpoints/2026-01-05-04-SESSION-176-e2-272-e2-273-ambiguity-gating-gates-1-2-complete.md

---
