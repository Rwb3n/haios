---
template: implementation_plan
status: complete
date: 2026-01-16
backlog_id: E2-295
title: Wire survey, close, and work-creation cycles with set-cycle
author: Hephaestus
lifecycle_phase: plan
session: 195
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-17T12:00:54'
---
# Implementation Plan: Wire survey, close, and work-creation cycles with set-cycle

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

Wire `just set-cycle`, `just set-queue`, and `just clear-cycle` calls into survey-cycle, close-work-cycle, and work-creation-cycle, completing the session_state cascade wiring.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | survey-cycle, close-work-cycle, work-creation-cycle |
| Lines of code affected | ~447 | wc -l on target files |
| New files to create | 0 | Editing existing skills |
| Tests to write | 1 | Manual verification |
| Dependencies | 1 | E2-293 (schema must exist first) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only skill markdown files |
| Risk of regression | Low | Additive prose changes |
| External dependencies | Low | Depends only on justfile recipes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Wire survey-cycle | 5 min | High |
| Wire close-work-cycle | 10 min | High |
| Wire work-creation-cycle | 10 min | High |
| Test | 5 min | High |
| **Total** | ~30 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/survey-cycle/SKILL.md (45 lines)
# Simple skill with Logic, Gate, Output sections
# NO set-cycle or set-queue calls
```

**Behavior:** Skills execute but session_state has no queue context.

**Result:** routing-gate doesn't know which queue was used by survey-cycle.

### Desired State

```markdown
# .claude/skills/survey-cycle/SKILL.md
## Logic
1. **Continue prior work?**
   ...

**After queue selection:**
\`\`\`bash
just set-queue {queue_name}
\`\`\`
```

**Behavior:** survey-cycle sets active_queue, close-work-cycle and work-creation-cycle set their cycles.

**Result:** Full session_state observability across all cycle types.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: survey-cycle Has set-queue Call
```bash
# Grep verification
grep -n "just set-queue" .claude/skills/survey-cycle/SKILL.md
# Expected: At least one match after queue selection logic
```

### Test 2: close-work-cycle Has set-cycle Calls
```bash
# Grep verification
grep -n "just set-cycle" .claude/skills/close-work-cycle/SKILL.md
# Expected: Matches at VALIDATE, ARCHIVE, MEMORY phases
```

### Test 3: work-creation-cycle Has set-cycle Calls
```bash
# Grep verification
grep -n "just set-cycle" .claude/skills/work-creation-cycle/SKILL.md
# Expected: Matches at VERIFY, POPULATE, READY phases
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### survey-cycle Wiring Points

| Location | Call |
|----------|------|
| After queue selection in "## Logic" section | `just set-queue {queue_name}` |

**Note:** survey-cycle is minimal (45 lines). Add set-queue call after step 2 (queue selection).

### close-work-cycle Wiring Points

| Phase | Location | Call |
|-------|----------|------|
| VALIDATE | After "### 1. VALIDATE Phase" | `just set-cycle close-work-cycle VALIDATE {work_id}` |
| ARCHIVE | After "### 2. ARCHIVE Phase" | `just set-cycle close-work-cycle ARCHIVE {work_id}` |
| MEMORY | After "### 3. MEMORY Phase" | `just set-cycle close-work-cycle MEMORY {work_id}` |
| CHAIN | At end | `just clear-cycle` |

### work-creation-cycle Wiring Points

| Phase | Location | Call |
|-------|----------|------|
| VERIFY | After "### 1. VERIFY Phase" | `just set-cycle work-creation-cycle VERIFY {work_id}` |
| POPULATE | After "### 2. POPULATE Phase" | `just set-cycle work-creation-cycle POPULATE {work_id}` |
| READY | After "### 3. READY Phase" | `just set-cycle work-creation-cycle READY {work_id}` |
| CHAIN | Before routing | Clear or let next cycle set |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| survey-cycle uses set-queue only | No set-cycle | survey-cycle is a routing utility, not a work cycle |
| clear-cycle at close-work-cycle end | After MEMORY phase | Clean state for next session |
| work-creation-cycle no clear-cycle | Chains to plan-authoring or await | Next skill will set its own cycle |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Queue name from operator input | Quote in recipe call | Manual test |
| close-work-cycle called without prior cycle | Works standalone | N/A |

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

**No open decisions.** Design inherited from E2-292 plan (approved by INV-065).

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Wire survey-cycle with set-queue
- [ ] Add "After queue selection:" section with `just set-queue {queue_name}` bash block
- [ ] Place after step 2 in Logic section

### Step 2: Wire close-work-cycle VALIDATE Phase
- [ ] Add "On Entry:" section after "### 1. VALIDATE Phase" heading
- [ ] Add bash block with `just set-cycle close-work-cycle VALIDATE {work_id}`

### Step 3: Wire close-work-cycle ARCHIVE Phase
- [ ] Add "On Entry:" section after "### 2. ARCHIVE Phase" heading
- [ ] Add bash block with `just set-cycle close-work-cycle ARCHIVE {work_id}`

### Step 4: Wire close-work-cycle MEMORY Phase
- [ ] Add "On Entry:" section after "### 3. MEMORY Phase" heading
- [ ] Add bash block with `just set-cycle close-work-cycle MEMORY {work_id}`

### Step 5: Wire close-work-cycle Exit
- [ ] Add `just clear-cycle` at end of MEMORY phase or CHAIN

### Step 6: Wire work-creation-cycle VERIFY Phase
- [ ] Add "On Entry:" section after "### 1. VERIFY Phase" heading
- [ ] Add bash block with `just set-cycle work-creation-cycle VERIFY {work_id}`

### Step 7: Wire work-creation-cycle POPULATE Phase
- [ ] Add "On Entry:" section after "### 2. POPULATE Phase" heading
- [ ] Add bash block with `just set-cycle work-creation-cycle POPULATE {work_id}`

### Step 8: Wire work-creation-cycle READY Phase
- [ ] Add "On Entry:" section after "### 3. READY Phase" heading
- [ ] Add bash block with `just set-cycle work-creation-cycle READY {work_id}`

### Step 9: Verification
- [ ] Grep all three files for "just set-" - verify matches
- [ ] Manual test: run set-queue and check haios-status-slim.json

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent ignores recipe calls | Medium | Soft enforcement via UserPromptSubmit warning (E2-287) |
| Markdown formatting breaks | Low | Test with skill invocation after edits |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/E2-295/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Wire survey-cycle with set-queue | [ ] | Grep for "just set-queue" |
| Wire close-work-cycle at VALIDATE/ARCHIVE/MEMORY | [ ] | Grep for "just set-cycle" |
| Wire close-work-cycle with clear-cycle | [ ] | Grep for "just clear-cycle" |
| Wire work-creation-cycle at VERIFY/POPULATE/READY | [ ] | Grep for "just set-cycle" |
| Manual test: UserPromptSubmit shows queue context | [ ] | Run and verify |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/survey-cycle/SKILL.md` | Has set-queue call | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | Has set-cycle at 3 phases + clear-cycle | [ ] | |
| `.claude/skills/work-creation-cycle/SKILL.md` | Has set-cycle at 3 phases | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/E2-292/plans/PLAN.md (original plan with wiring pattern)
- @docs/work/active/INV-065/investigations/001-session-state-cascade-architecture.md
- @.claude/skills/survey-cycle/SKILL.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/skills/work-creation-cycle/SKILL.md

---
