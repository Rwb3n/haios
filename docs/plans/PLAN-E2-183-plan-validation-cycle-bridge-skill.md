---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-183
title: plan-validation-cycle bridge skill
author: Hephaestus
lifecycle_phase: plan
session: 117
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T17:35:54'
---
# Implementation Plan: plan-validation-cycle bridge skill

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

## Goal

After this plan is complete, the plan-validation-cycle bridge skill will validate that implementation plans are complete and ready for the DO phase, acting as a quality gate between plan-authoring and implementation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/README.md` |
| Lines of code affected | ~10 | Add skill to list |
| New files to create | 2 | `.claude/skills/plan-validation-cycle/SKILL.md`, `README.md` |
| Tests to write | 0 | Skill is markdown/prompt, verification is runtime discovery |
| Dependencies | 0 | No code dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone validation skill |
| Risk of regression | Low | New skill, no existing behavior to break |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create SKILL.md | 15 min | High |
| Update READMEs | 5 min | High |
| Verify runtime | 5 min | High |
| **Total** | 25 min | |

---

## Current State vs Desired State

### Current State

```markdown
# implementation-cycle PLAN phase - Current behavior
1. Read the plan file
2. Verify plan has filled-in sections (not template placeholders)
3. Check status: draft -> if so, fill in design first
# No formal validation skill - checks are inline
```

**Behavior:** implementation-cycle's PLAN phase does basic placeholder detection but no structured validation

**Result:** Plans may have incomplete sections that pass detection but fail during DO phase

### Desired State

```markdown
# plan-validation-cycle - Target behavior
1. CHECK: Verify all required sections exist
2. VALIDATE: Check section content quality
3. APPROVE: Mark plan as validated
# Validation Skill that bridges plan-authoring and implementation
```

**Behavior:** plan-validation-cycle provides structured CHECK→VALIDATE→APPROVE workflow

**Result:** Plans are validated for completeness and quality before DO phase begins

---

## Tests First (TDD)

**SKIPPED:** Skill is markdown prompt injection, not Python code. Verification is runtime discovery.

### Verification Criteria (replaces pytest)

1. **Skill file exists:** `.claude/skills/plan-validation-cycle/SKILL.md` file present
2. **Frontmatter valid:** Has `name`, `description`, `generated`, `last_updated` fields
3. **Runtime discovery:** Skill appears in `haios-status-slim.json` under `infrastructure.skills`

```bash
# Verification commands
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('plan-validation-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

---

## Detailed Design

### Skill File Structure

**File:** `.claude/skills/plan-validation-cycle/SKILL.md`

```markdown
---
name: plan-validation-cycle
description: HAIOS Plan Validation Bridge for validating plan readiness. Use before
  entering DO phase. Guides CHECK->VALIDATE->APPROVE workflow.
generated: 2025-12-25
last_updated: 2025-12-25
---
# Plan Validation Cycle (Bridge Skill)

This is a **Validation Skill** (bridge) that validates implementation plans are complete
before entering the DO phase. It acts as a quality gate between plan-authoring-cycle
and implementation-cycle.

## When to Use

**Manual invocation:** `Skill(skill="plan-validation-cycle")` before starting implementation.
**Called from:** implementation-cycle PLAN phase exit (optional quality gate).

---

## The Cycle

```
CHECK --> VALIDATE --> APPROVE
```

### 1. CHECK Phase

**Goal:** Verify all required plan sections exist.

**Required Sections:**
- Goal (one sentence, >20 chars)
- Effort Estimation (metrics filled)
- Current State (code or description)
- Desired State (code or description)
- Tests First (at least one test)
- Detailed Design (implementation details)
- Implementation Steps (checklist items)
- Verification (criteria defined)

**Actions:**
1. Read plan file
2. Check each required section exists
3. Detect placeholder text: `[...]`, `[N]`, `[X]`
4. Report missing or incomplete sections

**Exit Criteria:**
- [ ] All required sections present
- [ ] No placeholder text detected

**Tools:** Read

---

### 2. VALIDATE Phase

**Goal:** Check section content quality.

**Quality Checks:**
- Goal: Single sentence, measurable outcome
- Effort: Real numbers from file analysis
- Tests: Concrete assertions, not placeholders
- Design: File paths, code snippets present
- Steps: Actionable checklist items

**Actions:**
1. For each section, verify content quality
2. Flag sections with insufficient detail
3. Report validation status

**Exit Criteria:**
- [ ] Goal is measurable
- [ ] Effort based on real analysis
- [ ] Tests have concrete assertions
- [ ] Design has implementation details

**Tools:** Read

---

### 3. APPROVE Phase

**Goal:** Mark plan as validated and ready.

**Actions:**
1. If all checks pass, plan is approved
2. Report validation summary
3. Recommend proceeding to DO phase

**Exit Criteria:**
- [ ] All CHECK criteria passed
- [ ] All VALIDATE criteria passed
- [ ] Plan ready for implementation

**Tools:** -

---

## Composition Map

| Phase | Primary Tool | Output |
|-------|--------------|--------|
| CHECK | Read | List of missing sections |
| VALIDATE | Read | Quality assessment |
| APPROVE | - | Validation summary |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| CHECK | Are all sections present? | Report missing sections |
| CHECK | Any placeholders? | Report placeholder locations |
| VALIDATE | Is Goal measurable? | Flag for revision |
| VALIDATE | Are Tests concrete? | Flag for revision |
| APPROVE | All checks passed? | Return to authoring |
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | CHECK → VALIDATE → APPROVE | Mirrors other cycle skills |
| Validation not authoring | Separate from plan-authoring-cycle | Different concerns: completeness vs quality |
| No auto-approval | Manual approval step | Agent must confirm validation passed |
| Lightweight | Read-only, no modifications | Bridge skills validate, don't modify |

### Edge Cases

| Case | Handling |
|------|----------|
| Plan already complete | CHECK passes quickly, proceed to APPROVE |
| Minor issues | VALIDATE flags but allows continuation |
| Major gaps | CHECK fails, redirect to plan-authoring-cycle |

---

## Implementation Steps

### Step 1: Create skill directory and SKILL.md
- [ ] Create directory: `.claude/skills/plan-validation-cycle/`
- [ ] Create SKILL.md with content from Detailed Design
- [ ] Verify frontmatter includes required fields

### Step 2: Create skill README
- [ ] Create `.claude/skills/plan-validation-cycle/README.md`
- [ ] Document skill purpose and usage

### Step 3: Update parent skills README
- [ ] Add plan-validation-cycle to `.claude/skills/README.md` skill list
- [ ] Add to Validation Skills section
- [ ] Add to directory structure

### Step 4: Verify runtime discovery
- [ ] Run `just update-status-slim`
- [ ] Check skill appears in `haios-status-slim.json`

---

## Verification

- [ ] Skill file exists: `.claude/skills/plan-validation-cycle/SKILL.md`
- [ ] Runtime discovery: skill in `haios-status-slim.json`
- [ ] **MUST:** All READMEs current

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill not discovered | Low | Run `just update-status` and verify JSON |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 117 | 2025-12-25 | - | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/plan-validation-cycle/SKILL.md` | Has frontmatter + 3 phases | [ ] | |
| `.claude/haios-status-slim.json` | Lists plan-validation-cycle in skills | [ ] | |
| `.claude/skills/plan-validation-cycle/README.md` | Exists, describes skill | [ ] | |
| `.claude/skills/README.md` | Lists plan-validation-cycle | [ ] | |

**Verification Commands:**
```bash
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('plan-validation-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Runtime discovery verified? | [ ] | |
| Any deviations from plan? | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Skill file exists and has valid content
- [ ] Runtime discovery works
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] Ground Truth Verification completed above

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- INV-035: Skill Architecture Refactoring
- E2-182: plan-authoring-cycle skill (companion)
- E2-181: close-work-cycle skill (parallel pattern)

---
