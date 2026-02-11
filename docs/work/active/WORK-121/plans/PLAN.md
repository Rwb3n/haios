---
template: implementation_plan
status: complete
date: 2026-02-11
backlog_id: WORK-121
title: "Enforce Critique Gate Before DO Phase"
author: Hephaestus
lifecycle_phase: plan
session: 344
version: "1.5"
generated: 2026-02-11
last_updated: 2026-02-11T20:20:00
---
# Implementation Plan: Enforce Critique Gate Before DO Phase

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | S343 drift warning + critique-agent findings are source evidence |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Critique-agent invocation with revise loop is enforced in implementation-cycle PLAN phase before plan-validation-cycle, and plan-validation-cycle's redundant CRITIQUE phase is removed to establish clean separation: critique = assumption surfacing (implementation-cycle), validation = structural quality (plan-validation-cycle).

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | implementation-cycle/SKILL.md, plan-validation-cycle/SKILL.md |
| Lines affected | ~60 | PLAN phase exit gate (~30 lines) + CRITIQUE phase removal (~40 lines) |
| New files to create | 1 | tests/test_implementation_cycle_critique.py |
| Tests to write | 4 | 2 for implementation-cycle, 2 for plan-validation-cycle |
| Dependencies | 0 | Skill text changes only, no module imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Two skill markdown files |
| Risk of regression | Low | No code logic, skill instructions only |
| External dependencies | Low | critique-agent already exists and works |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| implementation-cycle SKILL.md | 15 min | High |
| plan-validation-cycle SKILL.md | 10 min | High |
| Verification | 5 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

**File 1:** `.claude/skills/implementation-cycle/SKILL.md` — PLAN phase exit gate

```markdown
**Exit Gate (MUST):**
Before transitioning to DO phase, **MUST** invoke plan-validation-cycle:

Skill(skill="plan-validation-cycle")

**THEN MUST** invoke preflight-checker agent to validate plan readiness:

Task(subagent_type='preflight-checker', prompt='Check plan for {backlog_id}')

This validates plan completeness and file scope. DO phase is blocked until preflight passes.
```

No mention of critique-agent anywhere in implementation-cycle.

**File 2:** `.claude/skills/plan-validation-cycle/SKILL.md` — 5-phase cycle

```
CHECK --> SPEC_ALIGN --> CRITIQUE --> VALIDATE --> APPROVE
```

CRITIQUE phase (phase 3) invokes critique-agent. But by the time the agent reaches CRITIQUE, CHECK and SPEC_ALIGN have already given positive signals ("sections present, specs aligned"), creating momentum to skip or rush through CRITIQUE.

**Result:** S343 skipped critique entirely. The structural validation "blessed" the plan before assumptions were surfaced.

### Desired State

**File 1:** implementation-cycle SKILL.md — critique as Gate 1 before validation

```
plan done → Gate 1: critique-agent (revise loop) → Gate 2: plan-validation-cycle → Gate 3: preflight → DO
```

Critique runs on the raw plan FIRST, before any validation blessing.

**File 2:** plan-validation-cycle SKILL.md — 4-phase cycle (CRITIQUE removed)

```
CHECK --> SPEC_ALIGN --> VALIDATE --> APPROVE
```

Clean separation: implementation-cycle owns critique, plan-validation-cycle owns structural validation.

**Result:** Assumptions surfaced before the plan gets any positive validation signals.

---

## Tests First (TDD)

### Test 1: Implementation-cycle references critique-agent in PLAN phase
```python
def test_implementation_cycle_plan_phase_references_critique():
    """PLAN phase exit gate must reference critique-agent."""
    skill_path = Path(".claude/skills/implementation-cycle/SKILL.md")
    content = skill_path.read_text()

    # Must mention critique-agent in the document
    assert "critique-agent" in content, (
        "implementation-cycle SKILL.md must reference critique-agent"
    )

    # Must be in PLAN phase section (before DO phase)
    plan_section_start = content.index("### 1. PLAN Phase")
    do_section_start = content.index("### 2. DO Phase")
    plan_section = content[plan_section_start:do_section_start]

    assert "critique-agent" in plan_section, (
        "critique-agent must appear in PLAN phase section, not elsewhere"
    )
```

### Test 2: PLAN phase exit criteria includes critique with revise loop and verdicts
```python
def test_plan_phase_exit_criteria_includes_critique():
    """PLAN phase exit criteria checklist must include critique with verdicts."""
    skill_path = Path(".claude/skills/implementation-cycle/SKILL.md")
    content = skill_path.read_text()

    plan_section_start = content.index("### 1. PLAN Phase")
    do_section_start = content.index("### 2. DO Phase")
    plan_section = content[plan_section_start:do_section_start]

    # Exit criteria must mention critique
    assert "critique" in plan_section.lower(), (
        "PLAN phase must mention critique"
    )

    # Must describe the revise loop
    assert "revise" in plan_section.lower(), (
        "PLAN phase must describe critique-revise loop"
    )

    # Must describe the three verdicts
    assert "PROCEED" in plan_section, "Must describe PROCEED verdict"
    assert "REVISE" in plan_section, "Must describe REVISE verdict"
    assert "BLOCK" in plan_section, "Must describe BLOCK verdict"
```

### Test 3: Plan-validation-cycle no longer has CRITIQUE phase
```python
def test_plan_validation_cycle_no_critique_phase():
    """plan-validation-cycle should not have a CRITIQUE phase."""
    skill_path = Path(".claude/skills/plan-validation-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should NOT have a CRITIQUE phase header
    assert "### 3. CRITIQUE Phase" not in content, (
        "plan-validation-cycle should not have CRITIQUE phase (moved to implementation-cycle)"
    )

    # The cycle diagram should be 4-phase
    assert "CHECK --> SPEC_ALIGN --> VALIDATE --> APPROVE" in content, (
        "plan-validation-cycle should be 4-phase: CHECK->SPEC_ALIGN->VALIDATE->APPROVE"
    )
```

### Test 4: Plan-validation-cycle phase numbering is consistent
```python
def test_plan_validation_cycle_phase_numbering():
    """After CRITIQUE removal, phases should be numbered 1-4."""
    skill_path = Path(".claude/skills/plan-validation-cycle/SKILL.md")
    content = skill_path.read_text()

    assert "### 1. CHECK Phase" in content
    assert "### 2. SPEC_ALIGN Phase" in content
    assert "### 3. VALIDATE Phase" in content
    assert "### 4. APPROVE Phase" in content
```

---

## Detailed Design

### Change 1: implementation-cycle SKILL.md — Add critique Gate 1

**Location:** PLAN phase Exit Criteria and Exit Gate

**Current Exit Criteria:**
```markdown
- [ ] **MUST:** Invoke `Skill(skill="plan-validation-cycle")` before proceeding to DO
- [ ] **MUST:** Invoke `Task(subagent_type='preflight-checker')` to validate readiness
```

**New Exit Criteria (insert before plan-validation-cycle line):**
```markdown
- [ ] **MUST:** Invoke critique-agent and pass critique-revise loop (see Exit Gate)
- [ ] **MUST:** Invoke `Skill(skill="plan-validation-cycle")` before proceeding to DO
- [ ] **MUST:** Invoke `Task(subagent_type='preflight-checker')` to validate readiness
```

**Current Exit Gate:**
```markdown
**Exit Gate (MUST):**
Before transitioning to DO phase, **MUST** invoke plan-validation-cycle:
...
**THEN MUST** invoke preflight-checker...
```

**New Exit Gate (full replacement):**
```markdown
**Exit Gate (MUST):**
Before transitioning to DO phase, execute these three gates in order:

**Gate 1 - MUST: Critique (Assumption Surfacing)**
Invoke critique-agent to surface implicit assumptions on the raw plan:
```
Task(subagent_type='critique-agent', prompt='Critique plan: docs/work/active/{backlog_id}/plans/PLAN.md')
```

Apply critique-revise loop based on verdict:
- **PROCEED:** All assumptions mitigated. Continue to Gate 2.
- **REVISE:** Flagged assumptions exist. Revise plan to address them, then re-invoke critique. Repeat until PROCEED or max 3 iterations (then escalate to operator via AskUserQuestion).
- **BLOCK:** Unmitigated low-confidence assumptions. Return to plan-authoring-cycle. DO phase blocked.

> Critique runs BEFORE validation so assumptions are surfaced on the raw plan, not one already "blessed" by structural checks. This prevents the S343 anti-pattern where validation momentum caused critique to be skipped.

**Gate 2 - MUST: Plan Validation**
```
Skill(skill="plan-validation-cycle")
```
Validates structural completeness and quality. plan-validation-cycle runs CHECK → SPEC_ALIGN → VALIDATE → APPROVE (no duplicate critique).

**Gate 3 - MUST: Preflight Check**
```
Task(subagent_type='preflight-checker', prompt='Check plan for {backlog_id}')
```
Validates plan completeness and file scope. DO phase is blocked until all three gates pass.
```

### Change 2: plan-validation-cycle SKILL.md — Remove CRITIQUE phase

**Actions:**
1. Remove `### 3. CRITIQUE Phase (E2-072)` section entirely (~35 lines)
2. Update cycle diagram from `CHECK --> SPEC_ALIGN --> CRITIQUE --> VALIDATE --> APPROVE` to `CHECK --> SPEC_ALIGN --> VALIDATE --> APPROVE`
3. Renumber VALIDATE from "### 4." to "### 3." and APPROVE from "### 5." to "### 4."
4. Remove "(renumbered from 3)" and "(renumbered from 4)" annotations
5. Update Composition Map to remove CRITIQUE row
6. Update Quick Reference to remove CRITIQUE rows
7. Update Key Design Decisions: change "Five phases" to "Four phases", remove CRITIQUE row
8. Update APPROVE exit criteria to remove CRITIQUE reference
9. Add note explaining critique moved to implementation-cycle

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Move critique out of plan-validation-cycle | Yes | Operator directive: critique before validation, not during. Structural validation momentum causes critique skip |
| Critique as Gate 1 in implementation-cycle | Before plan-validation-cycle | Surface assumptions on raw plan before any positive validation signals |
| Max 3 revise iterations | Then escalate to operator | Addresses critique-agent A6 finding (unbounded loop). Prevents context exhaustion |
| No L4 amendment needed | Aligns with E2.5 REQ-CRITIQUE-001 | Critique is part of plan completion (Design lifecycle boundary), running before the plan is declared valid |
| Text-level enforcement only | Programmatic enforcement is future work | A1 finding acknowledged; hooks/CycleRunner gate enforcement is separate scope |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Plan has no assumptions | critique-agent returns PROCEED | Existing critique-agent tests |
| Revise loop hits 3 iterations | Escalate to operator via AskUserQuestion | Documented in Gate 1 text |
| Agent skips Gate 1 text | Same risk as before (A1) — future programmatic enforcement | Acknowledged limitation |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | N/A | N/A | All decisions resolved via operator discussion |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_implementation_cycle_critique.py` with all 4 tests
- [ ] Verify tests 1-2 fail (critique not yet in implementation-cycle)
- [ ] Verify tests 3-4 fail (CRITIQUE still in plan-validation-cycle)

### Step 2: Update implementation-cycle SKILL.md
- [ ] Add critique-agent to Exit Criteria checklist
- [ ] Replace Exit Gate block with three-gate sequence (Gate 1/2/3)
- [ ] Include critique-revise loop with PROCEED/REVISE/BLOCK verdicts
- [ ] Include max 3 iterations note
- [ ] Tests 1-2 pass (GREEN)

### Step 3: Update plan-validation-cycle SKILL.md
- [ ] Remove CRITIQUE phase section
- [ ] Update cycle diagram to 4-phase
- [ ] Renumber VALIDATE to 3, APPROVE to 4
- [ ] Update Composition Map, Quick Reference, Key Design Decisions
- [ ] Remove CRITIQUE from APPROVE exit criteria
- [ ] Add note: "Critique moved to implementation-cycle Gate 1 (WORK-121)"
- [ ] Tests 3-4 pass (GREEN)

### Step 4: Full Verification
- [ ] All 4 tests pass
- [ ] Run existing test suite (no regressions): `pytest tests/test_critique_agent.py -v`
- [ ] Grep for stale CRITIQUE references in plan-validation-cycle

### Step 5: README Sync (MUST)
- [ ] **SKIPPED:** No new directories. Modifying existing SKILL.md files. No README changes needed.

### Step 6: Consumer Verification (MUST)
- [ ] Grep for references to plan-validation-cycle's CRITIQUE phase in other skills/docs
- [ ] Update any consumers that reference the old 5-phase cycle

---

## Verification

- [ ] Tests pass (4 tests)
- [ ] implementation-cycle SKILL.md has critique in PLAN phase only
- [ ] plan-validation-cycle SKILL.md has no CRITIQUE phase
- [ ] No stale references to plan-validation-cycle CRITIQUE elsewhere

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent ignores Gate 1 text (A1) | Medium | Tests enforce text exists; programmatic enforcement is future scope |
| Consumers reference old 5-phase plan-validation-cycle | Low | Step 6 greps for stale references |
| Existing plan-validation-cycle tests break | Low | Renumbering is cosmetic; test_critique_agent.py tests framework, not phase position |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 344 | 2026-02-11 | - | Plan authored + critique REVISE + revised | Critique A1/A2/A3 addressed |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-121/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| implementation-cycle SKILL.md PLAN phase exit gate updated | [ ] | Read SKILL.md, verify Gate 1 critique section |
| Critique-revise loop documented | [ ] | PROCEED/REVISE/BLOCK + max 3 iterations |
| PLAN phase exit criteria checklist includes critique MUST | [ ] | Critique checkbox in exit criteria |
| plan-validation-cycle CRITIQUE phase removed | [ ] | No "### 3. CRITIQUE Phase" in SKILL.md |
| Test: implementation-cycle references critique-agent | [ ] | test passes |
| Test: plan-validation-cycle no CRITIQUE phase | [ ] | test passes |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/implementation-cycle/SKILL.md` | Gate 1 critique in PLAN phase | [ ] | |
| `.claude/skills/plan-validation-cycle/SKILL.md` | 4-phase cycle, no CRITIQUE | [ ] | |
| `tests/test_implementation_cycle_critique.py` | 4 tests, all passing | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_implementation_cycle_critique.py -v
# Expected: 4 tests passed
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
- [ ] **Runtime consumer exists** (SKILL.md files read by agent at runtime)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated — SKIPPED: no directory structure changes
- [ ] **MUST:** Consumer verification — Step 6 greps for stale references
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/skills/implementation-cycle/SKILL.md (primary target — add critique Gate 1)
- @.claude/skills/plan-validation-cycle/SKILL.md (remove CRITIQUE phase)
- @.claude/agents/critique-agent.md (agent definition, unchanged)
- @docs/work/active/WORK-121/WORK.md (work item)
- @docs/work/active/WORK-121/critique/ (critique-agent output from this plan)

---
