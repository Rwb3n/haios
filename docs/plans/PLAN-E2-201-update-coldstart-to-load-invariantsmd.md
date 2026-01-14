---
template: implementation_plan
status: complete
date: 2025-12-26
backlog_id: E2-201
title: Update Coldstart to Load invariants.md
author: Hephaestus
lifecycle_phase: plan
session: 121
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-26T11:28:29'
---
# Implementation Plan: Update Coldstart to Load invariants.md

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

Coldstart will load `.claude/config/invariants.md` as L1 context, providing agent with core philosophical invariants at session start.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/commands/coldstart.md` |
| Lines of code affected | ~10 | Add step 3, renumber subsequent |
| New files to create | 0 | invariants.md already exists (E2-200) |
| Tests to write | 0 | Command file, N/A |
| Dependencies | 0 | No code dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single command file |
| Risk of regression | Low | Additive change only |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update coldstart.md | 10 min | High |
| Verify load works | 5 min | High |
| **Total** | 15 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/commands/coldstart.md`

```markdown
Load and summarize these files in order:

1. **Agent Instructions:** Read `CLAUDE.md`
2. **Current State:** Read `docs/epistemic_state.md`
3. **Last 2 Checkpoints:** Find the 2 most recent files in `docs/checkpoints/`...
4. **System Awareness (L2):** Read `.claude/haios-status-slim.json`...
```

**Behavior:** Coldstart loads CLAUDE.md, epistemic_state.md, checkpoints, status. No invariants.

**Result:** Agent lacks core philosophical context (Certainty Ratchet, Three Pillars, etc.)

### Desired State

```markdown
Load and summarize these files in order:

1. **Agent Instructions:** Read `CLAUDE.md`
2. **Current State:** Read `docs/epistemic_state.md`
3. **Core Invariants (L1):** Read `.claude/config/invariants.md`  # <-- NEW
4. **Last 1 Checkpoint:** Find the most recent file in `docs/checkpoints/`  # <-- Changed from 2 to 1
5. **System Awareness (L2):** Read `.claude/haios-status-slim.json`...
```

**Behavior:** Coldstart loads invariants.md as L1 context, reduces checkpoints from 2 to 1.

**Result:** Agent has core philosophical invariants at session start. Balanced L1/L2/L3.

---

## Tests First (TDD)

**SKIPPED:** Pure command file modification (markdown). No code, no pytest tests.

### Manual Verification Instead:
1. Run `/coldstart` and verify invariants.md is read
2. Verify summary includes core invariants reference
3. Verify checkpoint count reduced to 1

---

## Detailed Design

### Exact Code Change

**File:** `.claude/commands/coldstart.md`
**Location:** Lines 14-18 (load order list)

**Current Code:**
```markdown
Load and summarize these files in order:

1. **Agent Instructions:** Read `CLAUDE.md`
2. **Current State:** Read `docs/epistemic_state.md`
3. **Last 2 Checkpoints:** Find the 2 most recent files in `docs/checkpoints/` and read both
```

**Changed Code:**
```markdown
Load and summarize these files in order:

1. **Agent Instructions:** Read `CLAUDE.md`
2. **Current State:** Read `docs/epistemic_state.md`
3. **Core Invariants (L1):** Read `.claude/config/invariants.md`
   - Contains: Certainty Ratchet, Three Pillars, Governance Flywheel, operational rules
   - This is evergreen philosophical context that rarely changes
4. **Last 1 Checkpoint:** Find the most recent file in `docs/checkpoints/` and read it
```

**Diff:**
```diff
 1. **Agent Instructions:** Read `CLAUDE.md`
 2. **Current State:** Read `docs/epistemic_state.md`
-3. **Last 2 Checkpoints:** Find the 2 most recent files in `docs/checkpoints/` and read both
+3. **Core Invariants (L1):** Read `.claude/config/invariants.md`
+   - Contains: Certainty Ratchet, Three Pillars, Governance Flywheel, operational rules
+   - This is evergreen philosophical context that rarely changes
+4. **Last 1 Checkpoint:** Find the most recent file in `docs/checkpoints/` and read it
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add invariants as step 3 | After epistemic_state, before checkpoint | L1 context before L3 session context |
| Reduce checkpoints from 2 to 1 | 1 checkpoint | INV-037: Reduce L3 token cost, prior session sufficient |
| Keep description brief | 2 lines | Coldstart is already long; link to file for details |

---

## Implementation Steps

### Step 1: Add invariants step and renumber
- [ ] Add step 3 for invariants.md
- [ ] Change checkpoint step from "2" to "1"
- [ ] Renumber subsequent steps (4, 5, 6, 7)

### Step 2: Update summary output
- [ ] Add note about invariants in summary template

### Step 3: Manual Verification
- [ ] Read updated coldstart.md and verify correctness

---

## Verification

- [ ] Coldstart.md has step 3 for invariants
- [ ] Checkpoint step says "1" not "2"
- [ ] All steps renumbered correctly

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Invariants file missing | Low | E2-200 already created it |
| Token increase | Low | Offset by reducing checkpoints from 2 to 1 |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/coldstart.md` | Has step 3 for invariants, step 4 for 1 checkpoint | [ ] | |
| `.claude/config/invariants.md` | Exists (created by E2-200) | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| Step 3 is Core Invariants? | [Yes/No] | |
| Step 4 is Last 1 Checkpoint? | [Yes/No] | |
| All steps renumbered? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (N/A - pure docs)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Ground Truth Verification completed above

---

## References

- INV-037: Context Level Architecture and Source Optimization
- E2-200: Create invariants.md (prerequisite, completed)

---
