---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-189
title: DoD Validation Cycle Skill
author: Hephaestus
lifecycle_phase: plan
session: 116
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T18:28:51'
---
# Implementation Plan: DoD Validation Cycle Skill

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

A dod-validation-cycle skill will exist that validates Definition of Done criteria before work item closure, acting as a MUST gate for close-work-cycle.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | close-work-cycle/SKILL.md, skills/README.md |
| Lines of code affected | ~10 | Add MUST gate + skill entry |
| New files to create | 2 | dod-validation-cycle/SKILL.md, README.md |
| Tests to write | 0 | Pure markdown skill |
| Dependencies | 1 | close-work-cycle invokes this |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only close-work-cycle |
| Risk of regression | Low | New skill, additive |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create skill files | 15 min | High |
| Update close-work-cycle | 5 min | High |
| Update README | 5 min | High |
| **Total** | 25 min | High |

---

## Current State vs Desired State

### Current State

close-work-cycle validates DoD inline in its VALIDATE phase. No separate validation skill exists for Post-DO validation.

**Behavior:** DoD validation is embedded in close-work-cycle, not a separate bridge skill.

**Result:** Inconsistent with plan-validation-cycle (Pre-DO) and design-review-validation (During-DO) pattern.

### Desired State

dod-validation-cycle skill exists with CHECK->VALIDATE->APPROVE workflow. close-work-cycle MUST invoke it before proceeding.

**Behavior:** DoD validation is a separate bridge skill, consistent with validation layer architecture.

**Result:** Complete validation pipeline: Pre-DO -> During-DO -> Post-DO.

---

## Tests First (TDD)

**SKIPPED:** Pure markdown skill - no Python code. Verification via runtime discovery.

---

## Detailed Design

### Part 1: Create dod-validation-cycle Skill

**File:** `.claude/skills/dod-validation-cycle/SKILL.md`

```markdown
---
name: dod-validation-cycle
description: HAIOS DoD Validation Cycle for validating Definition of Done before closure. Use before DONE phase. Guides CHECK->VALIDATE->APPROVE workflow.
---
# DoD Validation Cycle (Bridge Skill)

This is a **Validation Skill** (bridge) that validates Definition of Done criteria before work item closure.

## When to Use

**Invoked automatically** by close-work-cycle before VALIDATE phase.
**Manual invocation:** `Skill(skill="dod-validation-cycle")` before closing.

## The Cycle

```
CHECK --> VALIDATE --> APPROVE
```

### 1. CHECK Phase
**Goal:** Verify DoD prerequisites exist.
- Tests ran and results available
- Memory refs captured (WHY documented)
- Docs updated (CLAUDE.md, READMEs)

### 2. VALIDATE Phase
**Goal:** Validate each DoD criterion.
- Tests MUST pass
- WHY MUST be captured
- Docs MUST be current
- Associated plans MUST be complete

### 3. APPROVE Phase
**Goal:** Confirm work item is ready for closure.
- All criteria passed -> proceed to close
- Any failure -> report blockers, return to work

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | CHECK -> VALIDATE -> APPROVE | Consistent with other validation skills |
| Read-only | No modifications | Bridge skills validate, don't modify |
| MUST gate | Required before close | Ensures quality before closure |
```

### Part 2: Update close-work-cycle

**File:** `.claude/skills/close-work-cycle/SKILL.md`

Add MUST gate before VALIDATE phase:

```markdown
**Entry Gate (MUST):**
Before starting VALIDATE phase, **MUST** invoke dod-validation-cycle:
```
Skill(skill="dod-validation-cycle")
```
This validates DoD criteria. VALIDATE phase is blocked until validation passes.
```

### Call Chain Context

```
/close command
    |
    +-> close-work-cycle (SKILL)
            |
            +-> **dod-validation-cycle (SKILL)** # <-- NEW MUST gate
            |       CHECK->VALIDATE->APPROVE
            |
            +-> VALIDATE phase (if dod passes)
            +-> ARCHIVE phase
            +-> CAPTURE phase
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate skill | Not inline | Consistent with validation layer pattern |
| MUST gate | Required | Skills create harnesses |
| Before VALIDATE | Entry gate | Validates before close-work-cycle proceeds |

---

## Implementation Steps

### Step 1: Create dod-validation-cycle directory and SKILL.md
- [ ] mkdir `.claude/skills/dod-validation-cycle/`
- [ ] Create SKILL.md with CHECK->VALIDATE->APPROVE workflow

### Step 2: Create README.md for skill
- [ ] Create README.md with usage and examples

### Step 3: Update close-work-cycle
- [ ] Add MUST gate to invoke dod-validation-cycle

### Step 4: Update skills README
- [ ] Add dod-validation-cycle to Validation Skills section

### Step 5: Verify Runtime Discovery
- [ ] Run `just update-status-slim`
- [ ] Verify dod-validation-cycle appears in skills list

---

## Verification

- [ ] Skill file exists
- [ ] README exists
- [ ] close-work-cycle has MUST gate
- [ ] Runtime discovery confirmed

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill not discovered | Low | Same pattern as other skills |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 118 | 2025-12-25 | - | In Progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/dod-validation-cycle/SKILL.md` | CHECK->VALIDATE->APPROVE | [ ] | |
| `.claude/skills/dod-validation-cycle/README.md` | Usage documented | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | MUST gate added | [ ] | |
| `.claude/skills/README.md` | dod-validation-cycle listed | [ ] | |
| `.claude/haios-status-slim.json` | skill in list | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Runtime discovery confirmed? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Skill files created
- [ ] WHY captured (reasoning stored to memory)
- [ ] close-work-cycle updated
- [ ] Runtime discovery verified

---

## References

- INV-035: Skill Architecture Refactoring
- plan-validation-cycle: Parallel Pre-DO pattern
- design-review-validation: Parallel During-DO pattern

---
