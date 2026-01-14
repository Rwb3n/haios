---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-177
title: Chain new-plan to implementation-cycle
author: Hephaestus
lifecycle_phase: plan
session: 116
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T14:30:19'
---
# Implementation Plan: Chain new-plan to implementation-cycle

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

After `/new-plan` scaffolds a plan file, it will automatically invoke the `implementation-cycle` skill to guide the operator through PLAN→DO→CHECK→DONE phases.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/commands/new-plan.md` |
| Lines of code affected | ~15 | Adding chaining section |
| New files to create | 0 | N/A |
| Tests to write | 0 | Prompt file, no testable code |
| Dependencies | 0 | Self-contained command |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only touches command → skill invocation |
| Risk of regression | Low | Additive change, no existing behavior modified |
| External dependencies | Low | implementation-cycle skill already exists |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add chaining section | 5 min | High |
| Verify behavior | 5 min | High |
| **Total** | 10 min | |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/new-plan.md (lines 30-44)

## Create Plan

Run scaffolding via just recipe:
just plan <backlog_id> "<title>"

Report the created file path to the user.

---

## Allowed Field Values
...
```

**Behavior:** Command scaffolds plan file and reports path. Operator must manually decide next steps.

**Result:** Operator may forget to follow implementation-cycle, leading to inconsistent workflow.

### Desired State

```markdown
# .claude/commands/new-plan.md (lines 30-60)

## Create Plan

Run scaffolding via just recipe:
just plan <backlog_id> "<title>"

Report the created file path to the user.

---

## Chain to Implementation Cycle

After scaffolding, **MUST** immediately invoke the implementation-cycle skill:

Skill(skill="implementation-cycle")

This chains the creation into the structured PLAN→DO→CHECK→DONE workflow.

---

## Allowed Field Values
...
```

**Behavior:** Command scaffolds plan file AND invokes implementation-cycle skill.

**Result:** Seamless transition from plan creation to structured implementation workflow.

---

## Tests First (TDD)

**SKIPPED:** This is a prompt file modification, not executable code. The "test" is manual verification that invoking `/new-plan` chains to the skill. No pytest tests applicable.

---

## Detailed Design

### Exact Code Change

**File:** `.claude/commands/new-plan.md`
**Location:** After line 44 (after "Report the created file path to the user.")

**Current Code:**
```markdown
# .claude/commands/new-plan.md:42-55

Report the created file path to the user.

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `draft`, `approved`, `rejected`, `complete` |

Templates default to `status: draft`. Typical lifecycle: draft → approved → complete.
```

**Changed Code (insert after line 44):**
```markdown
Report the created file path to the user.

---

## Chain to Implementation Cycle

After scaffolding, **MUST** immediately invoke the implementation-cycle skill:

```
Skill(skill="implementation-cycle")
```

This chains the creation into the structured PLAN→DO→CHECK→DONE workflow.
The skill will:
1. Read the newly created plan file
2. Guide filling in design sections (PLAN phase)
3. Execute implementation with TDD (DO phase)
4. Verify tests and integration (CHECK phase)
5. Capture WHY and close (DONE phase)

---

## Allowed Field Values
```

### Call Chain Context

```
User invokes: /new-plan E2-XXX "Title"
    |
    +-> Command parses arguments
    |
    +-> Memory query (E2-083)
    |
    +-> just plan scaffolds file
    |
    +-> Report path to user
    |
    +-> Skill(skill="implementation-cycle")  # <-- NEW
            |
            +-> Skill loads PLAN phase contract
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Placement after scaffold | Insert after "Report the created file path" | Natural flow: create → report → chain to workflow |
| Same pattern as /new-investigation | Match existing pattern | Consistency - /new-investigation already chains to investigation-cycle |
| MUST not SHOULD | Use MUST keyword | Enforce the chain, don't make it optional |

### Edge Cases

| Case | Handling | Notes |
|------|----------|-------|
| User wants to just scaffold | N/A - chaining is the new default | /new-plan is for implementation workflow |
| Plan already exists | Skill handles this - checks if plan is draft | Not our concern here |

---

## Implementation Steps

### Step 1: Add Chaining Section to new-plan.md
- [ ] Edit `.claude/commands/new-plan.md`
- [ ] Insert "## Chain to Implementation Cycle" section after line 44
- [ ] Include Skill invocation and workflow description

### Step 2: Verify Behavior
- [ ] Invoke `/new-plan` with a test ID
- [ ] Confirm implementation-cycle skill is invoked after scaffolding
- [ ] Confirm PLAN phase guidance appears

### Step 3: README Sync
- [ ] **MUST:** Update `.claude/commands/README.md` if it lists command behaviors

---

## Verification

- [ ] `/new-plan` invokes implementation-cycle skill after scaffolding
- [ ] **MUST:** `.claude/commands/README.md` current (if applicable)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| User may not expect automatic workflow | Low | Clear messaging in skill output |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 116 | 2025-12-25 | - | Planning | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/new-plan.md` | Contains "## Chain to Implementation Cycle" section | [ ] | |
| `.claude/commands/README.md` | Updated if it lists command behaviors | [ ] | |

**Verification:**
```
# Read new-plan.md and confirm chaining section exists
Grep(pattern="Chain to Implementation Cycle", path=".claude/commands/new-plan.md")
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| new-plan.md contains chaining section? | [Yes/No] | |
| Skill invokes successfully? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Chaining section added to new-plan.md
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated if applicable
- [ ] Ground Truth Verification completed above

---

## References

- INV-033: Skill as Node Entry Gate Formalization (spawned this item)
- /new-investigation: Reference implementation (already chains to skill)
- Memory 76824: /implement command pattern

---
