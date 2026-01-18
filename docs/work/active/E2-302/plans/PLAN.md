---
template: implementation_plan
status: complete
date: 2026-01-18
backlog_id: E2-302
title: Update S2 Lifecycle Diagram
author: Hephaestus
lifecycle_phase: plan
session: 204
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-18T13:02:38'
---
# Implementation Plan: Update S2 Lifecycle Diagram

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

Remove stale "REMAINING WORK" section from S2-lifecycle-diagram.md that references config files and implementation patterns superseded by Epoch 2.2 architecture consolidation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/epochs/E2/architecture/S2-lifecycle-diagram.md` |
| Lines of code affected | ~9 | Lines 340-348 (REMAINING WORK section) |
| New files to create | 0 | Pure removal/update |
| Tests to write | 0 | Documentation-only change, no code |
| Dependencies | 0 | No modules import this file |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | No code integration, pure documentation |
| Risk of regression | Low | Architecture doc, not executable code |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Review REMAINING WORK section | 5 min | High |
| Update/remove stale content | 5 min | High |
| Verify diagram accuracy | 10 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# S2-lifecycle-diagram.md:340-348
│  REMAINING WORK:                                                            │
│  ───────────────                                                            │
│  - [ ] Create .claude/config/cycle-definitions.yaml                         │
│  - [ ] Create .claude/config/gates.yaml                                     │
│  - [ ] Implement .claude/lib/cycle_executor.py                              │
│  - [ ] Spawn E2-* implementation items                                      │
```

**Behavior:** S2 claims work remains to create config files at `.claude/config/` path using old naming.

**Result:** Misleading - these files were never created at that path. Config consolidation (E2-246) created different files at `.claude/haios/config/` (haios.yaml, cycles.yaml, components.yaml). Cycle execution is now in `.claude/haios/modules/cycle_runner.py`.

### Desired State

```markdown
# S2-lifecycle-diagram.md:340-348
│  REMAINING WORK:                                                            │
│  ───────────────                                                            │
│  None - superseded by Epoch 2.2 config consolidation.                       │
│  See .claude/haios/config/ for current config architecture.                 │
│  See .claude/haios/modules/cycle_runner.py for cycle execution.             │
```

**Behavior:** S2 accurately reflects that original TODOs are obsolete.

**Result:** Documentation matches reality. Readers understand where to find current implementation.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task, no code changes. No tests required.

Verification is manual: read the file after edit and confirm REMAINING WORK section accurately reflects current architecture.

---

## Detailed Design

**SKIPPED:** Pure documentation task. No code changes, no function signatures, no call chains.

### Exact Text Change

**File:** `.claude/haios/epochs/E2/architecture/S2-lifecycle-diagram.md`
**Location:** Lines 340-346 in Section 8 (KEY DECISIONS SUMMARY)

**Current Text:**
```markdown
│  REMAINING WORK:                                                            │
│  ───────────────                                                            │
│  - [ ] Create .claude/config/cycle-definitions.yaml                         │
│  - [ ] Create .claude/config/gates.yaml                                     │
│  - [ ] Implement .claude/lib/cycle_executor.py                              │
│  - [ ] Spawn E2-* implementation items                                      │
```

**Changed Text:**
```markdown
│  REMAINING WORK:                                                            │
│  ───────────────                                                            │
│  None - superseded by Epoch 2.2 config consolidation.                       │
│  See .claude/haios/config/ for current config architecture.                 │
│  See .claude/haios/modules/cycle_runner.py for cycle execution.             │
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep REMAINING WORK section | Yes, with updated content | Section header exists in ASCII table structure; removing it breaks visual alignment. Update content instead. |
| Reference new locations | Point to `.claude/haios/config/` and `cycle_runner.py` | Guides readers to where config actually lives now. |
| Mark as "superseded" | Use explicit "superseded" language | Clear signal that original plan evolved, not abandoned. |

### Diagram Accuracy Verification

Before closing, verify the diagrams in sections 1-7 still match current reality:

| Section | Diagram | Verification Method |
|---------|---------|---------------------|
| 1. NODE-LEVEL DAG | Work item nodes | Compare against `cycles.yaml` node bindings |
| 2. PHASE-LEVEL DAG | Cycle phases | Compare against skill markdown files |
| 3. CYCLE ORCHESTRATOR | Routing logic | Compare against `cycle_runner.py` |
| 4. OBJECTIVE_COMPLETE GATE | Gate checks | Compare against governance_layer.py |
| 5. STATE STORAGE | WORK.md fields | Compare against work_item template |
| 6. WORK ITEM DIRECTORY | Directory structure | Compare against actual `docs/work/active/` layout |
| 7. CONFIG FILES | Config paths | Compare against `.claude/haios/config/` |

### Open Questions

**Q: Should the REMAINING WORK section be removed entirely or updated?**

Updated. Removing it breaks the ASCII table visual structure. The table uses box-drawing characters that expect content in that row.

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No operator decisions in work item. `operator_decisions: []`

---

## Implementation Steps

### Step 1: Read REMAINING WORK Section
- [ ] Read S2-lifecycle-diagram.md lines 340-348
- [ ] Confirm stale TODO items referencing `.claude/config/` paths

### Step 2: Update REMAINING WORK Content
- [ ] Replace stale TODO checkboxes with "superseded" note
- [ ] Add references to current config location (`.claude/haios/config/`)
- [ ] Add reference to current cycle execution (`cycle_runner.py`)
- [ ] Preserve ASCII table structure

### Step 3: Verify Diagram Accuracy
- [ ] Skim sections 1-7 for obvious staleness
- [ ] Section 7 (CONFIG FILES): Verify paths match `.claude/haios/config/`
- [ ] Note any additional updates needed (out of scope for this work item)

### Step 4: Final Review
- [ ] Re-read updated section for clarity
- [ ] Verify box-drawing characters still align

---

## Verification

- [ ] REMAINING WORK section updated with current paths
- [ ] ASCII table structure preserved (box-drawing characters align)
- [ ] Document still renders correctly

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking ASCII table formatting | Low | Preserve same line count, same column width |
| Missing other stale content in S2 | Low | Skim sections 1-7; note but don't fix (scope creep) |
| Wrong current paths | Low | Verified via Glob: `.claude/haios/config/` exists with 4 YAML files |

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

**MUST** read `docs/work/active/E2-302/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Review REMAINING WORK section in S2-lifecycle-diagram.md | [ ] | Read lines 340-348 |
| Remove or update stale TODO items with current status | [ ] | Edit replaced stale TODOs with superseded note |
| Verify diagram still accurately reflects current lifecycle | [ ] | Skimmed sections 1-7, noted any issues |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/epochs/E2/architecture/S2-lifecycle-diagram.md` | REMAINING WORK section updated | [ ] | |
| `.claude/haios/config/haios.yaml` | Exists (referenced in update) | [ ] | Pre-verified via Glob |
| `.claude/haios/modules/cycle_runner.py` | Exists (referenced in update) | [ ] | Pre-verified via Glob |

**Verification Commands:**
```bash
# Read updated section
Read(.claude/haios/epochs/E2/architecture/S2-lifecycle-diagram.md, offset=338, limit=15)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| REMAINING WORK section updated? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] REMAINING WORK section updated with current architecture references
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] WHY captured (reasoning stored to memory)
- [ ] ASCII table formatting preserved
- [ ] Ground Truth Verification completed above

> **Note:** No tests, no runtime consumer, no README updates - this is pure documentation cleanup.

---

## References

- @docs/work/active/INV-069/WORK.md - Source investigation
- @.claude/haios/epochs/E2/architecture/S2-lifecycle-diagram.md - File to update
- Session 150 - Original creation of S2 with REMAINING WORK section

---
