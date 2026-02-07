---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-274
title: Add AMBIGUITY Phase to plan-authoring-cycle
author: Hephaestus
lifecycle_phase: plan
session: 177
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-05T23:09:21'
---
# Implementation Plan: Add AMBIGUITY Phase to plan-authoring-cycle

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

The plan-authoring-cycle skill will include an AMBIGUITY phase that reads the work item, checks for unresolved operator decisions, and blocks with AskUserQuestion before proceeding to plan authoring.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/skills/plan-authoring-cycle/SKILL.md`, `tests/test_lib_validate.py` |
| Lines of code affected | ~262 | SKILL.md is 262 lines (adding ~80 lines for new phase) |
| New files to create | 0 | Modification only |
| Tests to write | 3 | Template validation tests for new phase content |
| Dependencies | 0 | Skill is markdown instructions, no code imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skill is standalone markdown |
| Risk of regression | Low | Additive change to skill, existing phases unchanged |
| External dependencies | Low | No APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Add AMBIGUITY phase | 20 min | High |
| Update diagram/composition | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/plan-authoring-cycle/SKILL.md:19-25
## The Cycle

```
ANALYZE --> AUTHOR --> VALIDATE --> CHAIN
                                      |
                              plan-validation-cycle
```
```

**Behavior:** Skill starts directly with ANALYZE phase, reading the plan file without checking the source work item for operator decisions.

**Result:** Agent proceeds to design plans without surfacing ambiguous decisions, leading to wasted effort when operator catches wrong assumptions.

### Desired State

```markdown
# .claude/skills/plan-authoring-cycle/SKILL.md (target)
## The Cycle

```
AMBIGUITY --> ANALYZE --> AUTHOR --> VALIDATE --> CHAIN
```
```

**Behavior:** Skill starts with AMBIGUITY phase that reads WORK.md, checks `operator_decisions` field, and blocks with AskUserQuestion if unresolved decisions exist.

**Result:** Operator decisions are surfaced and resolved BEFORE plan authoring begins, preventing wasted effort.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Skill Contains AMBIGUITY Phase
```python
def test_skill_has_ambiguity_phase():
    """SKILL.md should contain AMBIGUITY phase section."""
    skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-authoring-cycle" / "SKILL.md"
    content = skill_path.read_text()

    # Phase section exists
    assert "### 0. AMBIGUITY Phase" in content or "### AMBIGUITY Phase" in content
    # Phase is in cycle diagram
    assert "AMBIGUITY" in content
```

### Test 2: AMBIGUITY Phase Reads Work Item
```python
def test_ambiguity_phase_reads_work_item():
    """AMBIGUITY phase instructions must read WORK.md before proceeding."""
    skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-authoring-cycle" / "SKILL.md"
    content = skill_path.read_text()

    # Must mention reading work item
    assert "WORK.md" in content or "work item" in content.lower()
    # Must mention operator_decisions field
    assert "operator_decisions" in content
```

### Test 3: AMBIGUITY Phase Has Block Behavior
```python
def test_ambiguity_phase_blocks_on_unresolved():
    """AMBIGUITY phase must BLOCK when unresolved decisions exist."""
    skill_path = Path(__file__).parent.parent / ".claude" / "skills" / "plan-authoring-cycle" / "SKILL.md"
    content = skill_path.read_text()

    # Must mention blocking behavior
    assert "BLOCK" in content or "block" in content
    # Must mention AskUserQuestion
    assert "AskUserQuestion" in content
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/skills/plan-authoring-cycle/SKILL.md`
**Location:** Insert new section after line 18 (before "## The Cycle")

**Current Cycle Diagram (line 21-25):**
```markdown
```
ANALYZE --> AUTHOR --> VALIDATE --> CHAIN
                                      |
                              plan-validation-cycle
```
```

**Changed Cycle Diagram:**
```markdown
```
AMBIGUITY --> ANALYZE --> AUTHOR --> VALIDATE --> CHAIN
    |                                               |
    |                                       plan-validation-cycle
    +-- BLOCK if unresolved decisions
```
```

**New AMBIGUITY Phase Section (insert before "### 1. ANALYZE Phase"):**
```markdown
### 0. AMBIGUITY Phase (Gate 3)

**Goal:** Surface and resolve operator decisions BEFORE plan authoring begins.

**Actions:**
1. Read the work item: `docs/work/active/{backlog_id}/WORK.md`
2. Parse frontmatter for `operator_decisions` field
3. Check for unresolved decisions:
   ```yaml
   # Unresolved decision has resolved: false or missing chosen
   operator_decisions:
     - question: "Implement modules or remove references?"
       options: ["implement", "remove"]
       resolved: false
   ```
4. **IF any unresolved decisions exist:**
   - **BLOCK** with message: "Unresolved operator decisions in work item."
   - Present `AskUserQuestion` with options from the work item:
     ```
     AskUserQuestion(questions=[{
       "question": "<question from operator_decisions>",
       "header": "Decision",
       "options": [{"label": opt, "description": ""} for opt in options]
     }])
     ```
   - Wait for operator response
   - Update work item with chosen decision
5. **IF all decisions resolved (or none exist):**
   - Proceed to ANALYZE phase
   - Populate "Open Decisions" section in plan from resolved decisions

**Exit Criteria:**
- [ ] Work item WORK.md read
- [ ] `operator_decisions` field checked
- [ ] All decisions resolved (or none exist)
- [ ] Open Decisions section populated in plan (if any decisions existed)

**Tools:** Read, AskUserQuestion, Edit
```

### Composition Map Update

Add row to existing table:

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| **AMBIGUITY** | Read, AskUserQuestion | - |
| ANALYZE | Read | - |
| AUTHOR | Read, Edit, Glob | Query for prior patterns |
| VALIDATE | Read, Edit | - |
| CHAIN | Skill | - |

### Behavior Logic

**Fixed Flow:**
```
Skill Invoked
    │
    ▼
[0. AMBIGUITY Phase]
    │
    ├── Read WORK.md
    │
    ├── Parse operator_decisions
    │
    └── Unresolved decisions?
          │
          ├─ YES → BLOCK + AskUserQuestion → Wait → Update WORK.md → Continue
          │
          └─ NO  → Proceed
                    │
                    ▼
            [1. ANALYZE Phase]
                    │
                    ▼
               (existing flow)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Phase number | "0." (before "1. ANALYZE") | Indicates it runs first; keeps existing phase numbers unchanged |
| Gate label | "Gate 3" | Matches INV-058 naming (E2-272=Gate 1, E2-273=Gate 2, E2-274=Gate 3, E2-275=Gate 4) |
| Block vs warn | BLOCK | L3 LLM Nature: "No internal friction" - warnings are ignored |
| Populate Open Decisions | After resolution | Ensures plan template section reflects actual resolved decisions |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No `operator_decisions` field | Proceed (empty list treated as "all resolved") | Test work item without field |
| Empty `operator_decisions: []` | Proceed normally | Test work item with empty list |
| All decisions already resolved | Proceed, populate Open Decisions section | Test work item with resolved decisions |
| Multiple unresolved decisions | Present each via AskUserQuestion sequentially | Test work item with multiple decisions |

### Open Questions

**Q: Should the skill update the work item's `operator_decisions` after AskUserQuestion?**

Yes - the AMBIGUITY phase should update the work item WORK.md with `resolved: true` and `chosen: <value>` so the decision is captured persistently. This enables other skills and tools to see the resolved state.

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
| (No operator decisions in work item) | - | - | Work item E2-274 has no `operator_decisions` field populated |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 3 tests to `tests/test_lib_validate.py` in new `TestPlanAuthoringCycleSkill` class
- [ ] Verify all 3 tests fail (red)

### Step 2: Add AMBIGUITY Phase to Skill
- [ ] Insert "### 0. AMBIGUITY Phase (Gate 3)" section before "### 1. ANALYZE Phase"
- [ ] Add AMBIGUITY to cycle diagram
- [ ] Test 1 passes (green)

### Step 3: Add Work Item Reading Instructions
- [ ] Add instructions to read WORK.md and parse `operator_decisions`
- [ ] Add blocking behavior and AskUserQuestion instructions
- [ ] Tests 2, 3 pass (green)

### Step 4: Update Composition Map and Quick Reference
- [ ] Add AMBIGUITY row to Composition Map table
- [ ] Add AMBIGUITY row to Quick Reference table
- [ ] All tests pass (green)

### Step 5: Integration Verification
- [ ] All 3 new tests pass
- [ ] Run full test suite (no regressions): `pytest tests/test_lib_validate.py -v`

### Step 6: README Sync (MUST)
- [ ] Verify `.claude/skills/plan-authoring-cycle/` has no README (skill is single file)
- [ ] No parent README updates needed (skill structure unchanged)

### Step 7: Consumer Verification
- [ ] Not a migration - no consumer updates needed
- [ ] New phase is additive to existing skill

---

## Verification

- [ ] Tests pass
- [ ] Skill content matches design
- [ ] No regressions in existing skill behavior

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing skill consumers confused by new phase | Low | Phase is first in chain, transparent to callers |
| Tests too loose | Medium | Tests check for specific content strings |
| Phase instructions unclear | Medium | Based on INV-058 design with concrete examples |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 177 | 2026-01-05 | - | In progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/plan-authoring-cycle/SKILL.md` | Contains "AMBIGUITY Phase" section | [x] | Lines 28-75 |
| `tests/test_lib_validate.py` | Contains TestPlanAuthoringCycleSkill class with 3 tests | [x] | Lines 891-929 |

**Verification Commands:**
```bash
pytest tests/test_lib_validate.py::TestPlanAuthoringCycleSkill -v
# Output:
# 3 passed in 0.12s
# - test_skill_has_ambiguity_phase PASSED
# - test_ambiguity_phase_reads_work_item PASSED
# - test_ambiguity_phase_blocks_on_unresolved PASSED
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read SKILL.md, verified AMBIGUITY section present |
| Test output pasted above? | Yes | 3/3 passed |
| Any deviations from plan? | No | Implementation matches design |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **Runtime consumer exists** - plan-authoring-cycle is invoked by implementation-cycle
- [ ] WHY captured (reasoning stored to memory)
- [ ] No README updates needed (skill is single file, no directory structure change)
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Skills are consumed by agent following instructions, not code imports.

---

## References

- @docs/work/archive/INV-058/investigations/001-ambiguity-gating-for-plan-authoring.md (source design)
- @docs/checkpoints/2026-01-05-03-SESSION-175-inv-058-ambiguity-gating-complete-e2-272-through-e2-275-spawned.md (investigation session)

---
