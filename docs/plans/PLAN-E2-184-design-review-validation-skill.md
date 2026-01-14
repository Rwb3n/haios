---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-184
title: design-review validation skill
author: Hephaestus
lifecycle_phase: plan
session: 117
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T17:45:39'
---
# Implementation Plan: design-review validation skill

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4) -->

---

## Goal

After this plan is complete, the design-review-validation skill will validate that implementation aligns with the plan's Detailed Design before completing the DO phase, acting as a quality gate during implementation.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/README.md` |
| Lines of code affected | ~10 | Add skill to list |
| New files to create | 2 | `.claude/skills/design-review-validation/SKILL.md`, `README.md` |
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
# implementation-cycle DO phase - Current behavior
1. Create file manifest
2. Write tests first
3. Implement changes
# No structured review against Detailed Design
```

**Behavior:** implementation-cycle's DO phase has no formal checkpoint to verify implementation matches plan design

**Result:** Implementation may drift from design without detection

### Desired State

```markdown
# design-review-validation - Target behavior
1. COMPARE: Read implementation vs Detailed Design
2. VERIFY: Check alignment on key points
3. APPROVE: Confirm implementation matches design
# Validation Skill bridges DO and CHECK phases
```

**Behavior:** design-review-validation provides structured COMPARE→VERIFY→APPROVE workflow

**Result:** Implementation drift detected before entering CHECK phase

---

## Tests First (TDD)

**SKIPPED:** Skill is markdown prompt injection, not Python code. Verification is runtime discovery.

### Verification Criteria (replaces pytest)

1. **Skill file exists:** `.claude/skills/design-review-validation/SKILL.md` file present
2. **Frontmatter valid:** Has `name`, `description`, `generated`, `last_updated` fields
3. **Runtime discovery:** Skill appears in `haios-status-slim.json` under `infrastructure.skills`

```bash
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('design-review-validation' in d['infrastructure']['skills'])"
# Expected: True
```

---

## Detailed Design

### Skill File Structure

**File:** `.claude/skills/design-review-validation/SKILL.md`

```markdown
---
name: design-review-validation
description: HAIOS Design Review Validation for verifying implementation alignment.
  Use during DO phase. Guides COMPARE->VERIFY->APPROVE workflow.
generated: 2025-12-25
last_updated: 2025-12-25
---
# Design Review Validation (Bridge Skill)

This is a **Validation Skill** (bridge) that verifies implementation aligns with
the plan's Detailed Design. Use during or after DO phase.

## When to Use

**Manual invocation:** `Skill(skill="design-review-validation")` after implementation.
**Called from:** implementation-cycle DO phase exit (optional quality gate).

---

## The Cycle

```
COMPARE --> VERIFY --> APPROVE
```

### 1. COMPARE Phase

**Goal:** Read implementation and compare against Detailed Design.

**Actions:**
1. Read plan's Detailed Design section
2. Read implemented files from the file manifest
3. Create comparison checklist

**Comparison Points:**
- File paths match plan
- Function signatures match plan
- Logic flow matches design diagrams
- Key design decisions followed

**Exit Criteria:**
- [ ] Plan's Detailed Design read
- [ ] Implementation files read
- [ ] Comparison checklist created

**Tools:** Read

---

### 2. VERIFY Phase

**Goal:** Check each comparison point for alignment.

**Verification Checks:**
- [ ] File manifest matches implemented files
- [ ] Function signatures match (names, params, returns)
- [ ] Logic flow matches design
- [ ] No undocumented deviations

**Actions:**
1. For each comparison point, verify alignment
2. Flag deviations as intentional or unintentional
3. Report verification status

**Exit Criteria:**
- [ ] All comparison points checked
- [ ] Deviations documented
- [ ] Verification report created

**Tools:** Read, Grep

---

### 3. APPROVE Phase

**Goal:** Confirm implementation is aligned or document deviations.

**Actions:**
1. If all checks pass, approve implementation
2. If deviations found:
   - Document why (intentional improvement or error)
   - Update plan if intentional change
   - Fix implementation if error
3. Report final status

**Exit Criteria:**
- [ ] Implementation approved, OR
- [ ] Deviations documented and addressed

**Tools:** Edit (for plan updates)

---

## Composition Map

| Phase | Primary Tool | Output |
|-------|--------------|--------|
| COMPARE | Read | Comparison checklist |
| VERIFY | Read, Grep | Deviation report |
| APPROVE | Edit (optional) | Approval status |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| COMPARE | Is Detailed Design read? | Read plan |
| COMPARE | Are implementation files read? | Read manifested files |
| VERIFY | Do signatures match? | Flag deviation |
| VERIFY | Does logic flow match? | Flag deviation |
| APPROVE | Is implementation aligned? | Document and fix |
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | COMPARE → VERIFY → APPROVE | Consistent with other validation skills |
| Optional gate | Not required | Some implementations may be straightforward |
| Deviation handling | Document and decide | Not all deviations are errors |
| Read-only except APPROVE | Only modifies if updating plan | Validation doesn't change implementation |

### Edge Cases

| Case | Handling |
|------|----------|
| No Detailed Design | Skip skill - nothing to compare against |
| Intentional deviation | Document in plan as design update |
| Minor drift | Flag but allow continuation |

---

## Implementation Steps

### Step 1: Create skill directory and SKILL.md
- [ ] Create directory: `.claude/skills/design-review-validation/`
- [ ] Create SKILL.md with content from Detailed Design
- [ ] Verify frontmatter includes required fields

### Step 2: Create skill README
- [ ] Create `.claude/skills/design-review-validation/README.md`
- [ ] Document skill purpose and usage

### Step 3: Update parent skills README
- [ ] Add design-review-validation to `.claude/skills/README.md` skill list
- [ ] Add to Validation Skills (Bridges) section
- [ ] Add to directory structure

### Step 4: Verify runtime discovery
- [ ] Run `just update-status-slim`
- [ ] Check skill appears in `haios-status-slim.json`

---

## Verification

- [ ] Skill file exists: `.claude/skills/design-review-validation/SKILL.md`
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
| `.claude/skills/design-review-validation/SKILL.md` | Has frontmatter + 3 phases | [ ] | |
| `.claude/haios-status-slim.json` | Lists design-review-validation in skills | [ ] | |
| `.claude/skills/design-review-validation/README.md` | Exists, describes skill | [ ] | |
| `.claude/skills/README.md` | Lists design-review-validation | [ ] | |

**Verification Commands:**
```bash
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('design-review-validation' in d['infrastructure']['skills'])"
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
- E2-183: plan-validation-cycle skill (parallel pattern)

---
