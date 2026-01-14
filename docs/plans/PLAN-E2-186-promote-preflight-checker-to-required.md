---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-186
title: Promote preflight-checker to REQUIRED
author: Hephaestus
lifecycle_phase: plan
session: 116
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T19:29:13'
---
# Implementation Plan: Promote preflight-checker to REQUIRED

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

The preflight-checker agent will be promoted from OPTIONAL to REQUIRED, invoked as a MUST gate between PLAN and DO phases in implementation-cycle, enforcing plan readiness and file scope validation before implementation begins.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | preflight-checker.md, implementation-cycle/SKILL.md |
| Lines of code affected | ~20 | Update requirement level, add MUST gate |
| New files to create | 0 | Agent already exists |
| Tests to write | 0 | Pure markdown changes - manual verification |
| Dependencies | 1 | implementation-cycle invokes preflight-checker |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only implementation-cycle affected |
| Risk of regression | Low | Adding enforcement, not changing behavior |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update preflight-checker.md | 5 min | High |
| Add MUST gate to implementation-cycle | 10 min | High |
| Verify runtime discovery | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/agents/preflight-checker.md:14`
```markdown
## Requirement Level

**OPTIONAL** but **RECOMMENDED** before DO phase. The implementation-cycle skill will invoke this when available.
```

**Behavior:** Preflight checker is optional. Implementation can proceed without validating plan readiness or file scope.

**Result:** Plans may transition to DO phase with incomplete sections, or with >3 file manifests without operator confirmation.

### Desired State

**File:** `.claude/agents/preflight-checker.md:14`
```markdown
## Requirement Level

**REQUIRED** before DO phase. Implementation-cycle **MUST** invoke preflight-checker as a gate at PLAN→DO transition.
```

**Behavior:** Preflight checker is mandatory. Implementation-cycle invokes `Task(subagent_type='preflight-checker')` before entering DO phase. Agent validates plan completeness and scope, blocks if issues found.

**Result:** Plans cannot transition to DO phase unless preflight validation passes. >3 file manifests require explicit operator confirmation.

---

## Tests First (TDD)

**SKIPPED:** Pure markdown changes to skill/agent files. Verification via manual inspection and runtime discovery.

**Manual Verification Steps:**
1. Read `.claude/agents/preflight-checker.md` - confirm `**REQUIRED**` wording
2. Read `.claude/skills/implementation-cycle/SKILL.md` - confirm MUST gate with `Task(subagent_type='preflight-checker')`
3. Run `just update-status-slim` - confirm agent still in discovery list

---

## Detailed Design

### Part 1: Update preflight-checker Agent

**File:** `.claude/agents/preflight-checker.md`
**Location:** Lines 12-14

**Current Code:**
```markdown
## Requirement Level

**OPTIONAL** but **RECOMMENDED** before DO phase. The implementation-cycle skill will invoke this when available.
```

**Changed Code:**
```markdown
## Requirement Level

**REQUIRED** before DO phase. Implementation-cycle **MUST** invoke preflight-checker as a gate at PLAN→DO transition.

**Enforcement:** The implementation-cycle skill invokes this agent via:
```
Task(subagent_type='preflight-checker', prompt='Check plan for {backlog_id}')
```
```

### Part 2: Add MUST Gate to implementation-cycle

**File:** `.claude/skills/implementation-cycle/SKILL.md`
**Location:** Between PLAN phase Exit Criteria and Exit Gate sections (around line 60)

**Current Code (line 60-68):**
```markdown
**Exit Criteria:**
- [ ] Plan file exists with complete design
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **MUST:** Invoke `Skill(skill="plan-validation-cycle")` before proceeding to DO

**Exit Gate (MUST):**
Before transitioning to DO phase, **MUST** invoke plan-validation-cycle:
```

**Changed Code:**
```markdown
**Exit Criteria:**
- [ ] Plan file exists with complete design
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **MUST:** Invoke `Skill(skill="plan-validation-cycle")` before proceeding to DO
- [ ] **MUST:** Invoke `Task(subagent_type='preflight-checker')` to validate readiness

**Exit Gate (MUST):**
Before transitioning to DO phase, **MUST** invoke plan-validation-cycle:
```
Skill(skill="plan-validation-cycle")
```

**THEN MUST** invoke preflight-checker agent to validate plan readiness:
```
Task(subagent_type='preflight-checker', prompt='Check plan for {backlog_id}')
```
This validates plan completeness and file scope. DO phase is blocked until preflight passes.
```

### Call Chain Context

```
/new-plan command
    |
    +-> implementation-cycle skill (PLAN phase)
            |
            +-> plan-validation-cycle skill (bridge)  # Validates plan content
            |
            +-> preflight-checker agent (REQUIRED)    # <-- NOW REQUIRED
            |       Validates: plan sections, file manifest, >3 file gate
            |       Returns: {ready: true|false, issues: [...]}
            |
            +-> DO phase (blocked if preflight fails)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| REQUIRED vs OPTIONAL | REQUIRED | INV-035 identified preflight as part of BRIDGE 1 pattern |
| Agent vs Skill | Agent (Task) | Isolated context for unbiased validation per 4-layer architecture |
| Order: plan-validation-cycle THEN preflight | Sequential | plan-validation checks content quality, preflight checks readiness |

### Edge Cases

| Case | Handling |
|------|----------|
| Plan status: draft | preflight-checker blocks, returns issue |
| File manifest >3 files | preflight-checker warns, requires confirmation |
| Empty file manifest | Pass (0 < 3 threshold) |
| No plan file found | preflight-checker errors, suggests /new-plan |

---

## Implementation Steps

### Step 1: Update preflight-checker Agent
- [ ] Edit `.claude/agents/preflight-checker.md`
- [ ] Change "OPTIONAL" to "REQUIRED"
- [ ] Add enforcement description

### Step 2: Add MUST Gate to implementation-cycle
- [ ] Edit `.claude/skills/implementation-cycle/SKILL.md`
- [ ] Add preflight-checker to Exit Criteria
- [ ] Add preflight-checker invocation to Exit Gate section

### Step 3: Verification
- [ ] Run `just update-status-slim`
- [ ] Verify preflight-checker still appears in agents list
- [ ] Read both files to confirm changes

---

## Verification

- [ ] Agent file updated with REQUIRED level
- [ ] implementation-cycle has MUST gate for preflight-checker
- [ ] Runtime discovery still shows preflight-checker

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflow | Medium | Only adding enforcement, not changing behavior |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 119 | 2025-12-25 | - | In Progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/preflight-checker.md` | Contains `**REQUIRED**` | [ ] | |
| `.claude/skills/implementation-cycle/SKILL.md` | Contains preflight-checker MUST gate | [ ] | |
| `.claude/haios-status-slim.json` | preflight-checker in agents list | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Runtime discovery confirmed? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Agent file updated
- [ ] Skill file updated
- [ ] WHY captured (reasoning stored to memory)
- [ ] Runtime discovery verified

---

## References

- INV-035: Skill Architecture Refactoring (spawned this)
- E2-093: Original preflight-checker implementation
- Session 118: Validation pipeline completion

---
