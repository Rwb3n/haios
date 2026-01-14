---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-191
title: Work File Population Governance Gate
author: Hephaestus
lifecycle_phase: plan
session: 118
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T19:52:20'
---
# Implementation Plan: Work File Population Governance Gate

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

The work-creation-cycle READY phase will validate that Context and Deliverables sections are populated (not placeholders), warning the user if work item is incomplete before allowing progression.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | work-creation-cycle/SKILL.md |
| Lines of code affected | ~10 | Add validation checks to READY phase |
| New files to create | 0 | - |
| Tests to write | 0 | Pure markdown skill |
| Dependencies | 0 | Self-contained skill |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only affects work-creation-cycle |
| Risk of regression | Low | Adding validation, not changing flow |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update READY phase | 10 min | High |
| Verify | 5 min | High |
| **Total** | 15 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/skills/work-creation-cycle/SKILL.md:68-84`
```markdown
### 3. READY Phase

**Goal:** Validate work item is actionable.

**Actions:**
1. Read work file to verify all fields populated
2. Check Context section contains >20 characters
3. Check Deliverables has at least one checkbox item
4. Update History section with population timestamp

**Exit Criteria:**
- [ ] Context populated with meaningful content
- [ ] Deliverables has actionable checklist
- [ ] Work item ready for further lifecycle progression
```

**Behavior:** READY phase describes validation but doesn't explicitly block or warn when placeholders remain.

**Result:** Work files can be left with `[Problem and root cause]` and `[Deliverable 1]` placeholders.

### Desired State

**File:** `.claude/skills/work-creation-cycle/SKILL.md:68-95`
```markdown
### 3. READY Phase

**Goal:** Validate work item is actionable.

**Guardrails (MUST follow):**
1. **Context MUST NOT contain placeholders** - Detect `[Problem and root cause]`
2. **Deliverables MUST NOT contain placeholders** - Detect `[Deliverable 1]`, `[Deliverable 2]`

**Actions:**
1. Read work file to verify all fields populated
2. Check Context section contains >20 characters AND no placeholder text
3. Check Deliverables has at least one checkbox item AND no placeholder text
4. **If placeholders found:** Report to user, recommend completing POPULATE phase
5. Update History section with population timestamp

**Exit Criteria:**
- [ ] Context populated with meaningful content (no placeholders)
- [ ] Deliverables has actionable checklist (no placeholders)
- [ ] Work item ready for further lifecycle progression
```

**Behavior:** READY phase explicitly checks for placeholder text and warns user.

**Result:** Unpopulated work files are flagged, encouraging proper Context/Deliverables population.

---

## Tests First (TDD)

**SKIPPED:** Pure markdown skill update. Verification via manual inspection.

---

## Detailed Design

### Change to work-creation-cycle SKILL.md

**File:** `.claude/skills/work-creation-cycle/SKILL.md`
**Location:** READY Phase section (lines 68-84)

Replace the current READY phase with enhanced version that includes:
1. Guardrails section defining placeholder detection
2. Updated Actions to check for placeholders
3. Updated Exit Criteria with "(no placeholders)" clarification

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Warn vs Block | Warn | L2 guidance, not L3 enforcement - user may have valid reason |
| Placeholder patterns | `[Problem and root cause]`, `[Deliverable N]` | These are the exact template placeholders |
| Where to check | READY phase | Last gate before work item is "actionable" |

---

## Implementation Steps

### Step 1: Update READY Phase in work-creation-cycle
- [ ] Edit `.claude/skills/work-creation-cycle/SKILL.md`
- [ ] Add Guardrails section with placeholder detection
- [ ] Update Actions to include placeholder checking
- [ ] Update Exit Criteria with "(no placeholders)"

### Step 2: Verify
- [ ] Read skill file to confirm changes
- [ ] Check skill discovery still works

---

## Verification

- [ ] Skill file updated with placeholder validation
- [ ] Skill still discovered by system

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too strict blocking | Low | Using WARN not BLOCK - L2 guidance |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 119 | 2025-12-25 | - | In Progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/work-creation-cycle/SKILL.md` | Contains Guardrails for placeholder detection | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| Skill file updated? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Skill file updated
- [ ] WHY captured (reasoning stored to memory)
- [ ] Skill discovery verified

---

## References

- Session 119: Bug hunt that found 8 unpopulated work files
- work-creation-cycle skill

---
