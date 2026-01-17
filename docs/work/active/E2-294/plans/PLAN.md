---
template: implementation_plan
status: complete
date: 2026-01-16
backlog_id: E2-294
title: Wire implementation-cycle and investigation-cycle with set-cycle
author: Hephaestus
lifecycle_phase: plan
session: 195
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-17T11:52:31'
---
# Implementation Plan: Wire implementation-cycle and investigation-cycle with set-cycle

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

Wire `just set-cycle` and `just clear-cycle` calls into implementation-cycle and investigation-cycle skill markdown, enabling session_state to reflect active cycle and phase during execution.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | implementation-cycle/SKILL.md, investigation-cycle/SKILL.md |
| Lines of code affected | ~557 | wc -l on target files |
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
| Wire implementation-cycle | 10 min | High |
| Wire investigation-cycle | 10 min | High |
| Test | 5 min | High |
| **Total** | ~25 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/implementation-cycle/SKILL.md
### 1. PLAN Phase
**Goal:** Verify plan exists...
# NO set-cycle call at phase entry
```

**Behavior:** Skills execute but session_state remains null throughout.

**Result:** No observability of which cycle/phase is active.

### Desired State

```markdown
# .claude/skills/implementation-cycle/SKILL.md
### 1. PLAN Phase

**On Entry:**
\`\`\`bash
just set-cycle implementation-cycle PLAN {work_id}
\`\`\`

**Goal:** Verify plan exists...
```

**Behavior:** Each phase entry calls `just set-cycle`, final phase calls `just clear-cycle`.

**Result:** session_state reflects active cycle and phase. UserPromptSubmit can display context.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: implementation-cycle Has set-cycle Calls
```bash
# Grep verification
grep -n "just set-cycle" .claude/skills/implementation-cycle/SKILL.md
# Expected: Multiple matches at PLAN, DO, CHECK, DONE, CHAIN
```

### Test 2: investigation-cycle Has set-cycle Calls
```bash
# Grep verification
grep -n "just set-cycle" .claude/skills/investigation-cycle/SKILL.md
# Expected: Matches at HYPOTHESIZE, EXPLORE, CONCLUDE, CHAIN
```

### Test 3: Manual Execution Test
```bash
# Start implementation-cycle and check session_state
just set-cycle implementation-cycle PLAN E2-test
cat .claude/haios-status-slim.json | grep -A5 session_state
# Expected: active_cycle = "implementation-cycle", current_phase = "PLAN"
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

### Wiring Pattern (from E2-292 plan)

For each phase in a cycle skill, add:

**At phase entry:**
```markdown
**On Entry:**
\`\`\`bash
just set-cycle {skill-name} {phase} {work_id}
\`\`\`
```

**At cycle exit (CHAIN phase):**
```markdown
**On Complete:**
\`\`\`bash
just clear-cycle
\`\`\`
```

### implementation-cycle Wiring Points

| Phase | Location | Call |
|-------|----------|------|
| PLAN | After "### 1. PLAN Phase" | `just set-cycle implementation-cycle PLAN {work_id}` |
| DO | After "### 2. DO Phase" | `just set-cycle implementation-cycle DO {work_id}` |
| CHECK | After "### 3. CHECK Phase" | `just set-cycle implementation-cycle CHECK {work_id}` |
| DONE | After "### 4. DONE Phase" | `just set-cycle implementation-cycle DONE {work_id}` |
| CHAIN | After "### 5. CHAIN Phase" | `just clear-cycle` at exit |

### investigation-cycle Wiring Points

| Phase | Location | Call |
|-------|----------|------|
| HYPOTHESIZE | After "### 1. HYPOTHESIZE Phase" | `just set-cycle investigation-cycle HYPOTHESIZE {work_id}` |
| EXPLORE | After "### 2. EXPLORE Phase" | `just set-cycle investigation-cycle EXPLORE {work_id}` |
| CONCLUDE | After "### 3. CONCLUDE Phase" | `just set-cycle investigation-cycle CONCLUDE {work_id}` |
| CHAIN | At end | `just clear-cycle` at exit |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Call at phase entry | Before "Goal:" section | Ensures state is set before phase work begins |
| {work_id} as variable | Agent substitutes actual ID | Skills are templates, not hardcoded |
| clear-cycle at CHAIN | After close, before routing | Prevents state leak to next cycle |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Agent skips set-cycle | UserPromptSubmit warning (E2-287) | Soft enforcement |
| Nested cycles | N/A - cycles don't nest | N/A |

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

### Step 1: Wire implementation-cycle PLAN Phase
- [ ] Add "On Entry:" section after "### 1. PLAN Phase" heading
- [ ] Add bash block with `just set-cycle implementation-cycle PLAN {work_id}`

### Step 2: Wire implementation-cycle DO Phase
- [ ] Add "On Entry:" section after "### 2. DO Phase" heading
- [ ] Add bash block with `just set-cycle implementation-cycle DO {work_id}`

### Step 3: Wire implementation-cycle CHECK Phase
- [ ] Add "On Entry:" section after "### 3. CHECK Phase" heading
- [ ] Add bash block with `just set-cycle implementation-cycle CHECK {work_id}`

### Step 4: Wire implementation-cycle DONE Phase
- [ ] Add "On Entry:" section after "### 4. DONE Phase" heading
- [ ] Add bash block with `just set-cycle implementation-cycle DONE {work_id}`

### Step 5: Wire implementation-cycle CHAIN Phase
- [ ] Add "On Complete:" section at end of CHAIN phase
- [ ] Add bash block with `just clear-cycle`

### Step 6: Wire investigation-cycle HYPOTHESIZE Phase
- [ ] Add "On Entry:" section after "### 1. HYPOTHESIZE Phase" heading
- [ ] Add bash block with `just set-cycle investigation-cycle HYPOTHESIZE {work_id}`

### Step 7: Wire investigation-cycle EXPLORE Phase
- [ ] Add "On Entry:" section after "### 2. EXPLORE Phase" heading
- [ ] Add bash block with `just set-cycle investigation-cycle EXPLORE {work_id}`

### Step 8: Wire investigation-cycle CONCLUDE Phase
- [ ] Add "On Entry:" section after "### 3. CONCLUDE Phase" heading
- [ ] Add bash block with `just set-cycle investigation-cycle CONCLUDE {work_id}`

### Step 9: Wire investigation-cycle CHAIN Phase
- [ ] Add "On Complete:" section with `just clear-cycle`

### Step 10: Verification
- [ ] Grep both files for "just set-cycle" - verify matches
- [ ] Manual test: run set-cycle and check haios-status-slim.json

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

**MUST** read `docs/work/active/E2-294/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Wire implementation-cycle at PLAN/DO/CHECK/DONE | [ ] | Grep for "just set-cycle" |
| Wire implementation-cycle clear-cycle at CHAIN | [ ] | Grep for "just clear-cycle" |
| Wire investigation-cycle at HYPOTHESIZE/EXPLORE/CONCLUDE | [ ] | Grep for "just set-cycle" |
| Wire investigation-cycle clear-cycle at CHAIN | [ ] | Grep for "just clear-cycle" |
| Manual test passes | [ ] | session_state updated correctly |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/implementation-cycle/SKILL.md` | Has set-cycle at 5 phases | [ ] | |
| `.claude/skills/investigation-cycle/SKILL.md` | Has set-cycle at 4 phases | [ ] | |
| `.claude/haios-status-slim.json` | session_state updated on test | [ ] | |

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
- @.claude/skills/implementation-cycle/SKILL.md
- @.claude/skills/investigation-cycle/SKILL.md

---
