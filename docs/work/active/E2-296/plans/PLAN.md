---
template: implementation_plan
status: complete
date: 2026-01-17
backlog_id: E2-296
title: Observation Triage Batch - Chariot Arc
author: Hephaestus
lifecycle_phase: plan
session: 199
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-17T14:53:59'
---
# Implementation Plan: Observation Triage Batch - Chariot Arc

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

Triage all 35 pending observations across 12 archived work items, routing each to appropriate action (spawn:WORK, spawn:INV, memory, dismiss) with documented rationale.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to triage | 12 | `just triage-observations` output |
| Observations to process | 35 | Sum of observations across 12 files |
| New files to create | ~5-10 | Spawned work items (estimate based on triage) |
| Tests to write | 0 | Process execution, not code implementation |
| Dependencies | 1 | observation-triage-cycle skill |

**Archived items with pending observations:**
```
E2-163: 2 observations
E2-233: 1 observation
E2-238: 4 observations
E2-242: 2 observations
E2-248: 2 observations
E2-253: 2 observations
E2-254: 6 observations
E2-255: 6 observations
INV-052: 4 observations
INV-056: 1 observation
INV-058: 2 observations
INV-059: 3 observations
```

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Uses existing observation-triage-cycle |
| Risk of regression | Low | No code changes, only spawns work items |
| External dependencies | Low | Only filesystem and memory MCP |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| SCAN | 5 min | High |
| TRIAGE (35 observations) | 45-60 min | Medium |
| PROMOTE (spawn items) | 15-20 min | Medium |
| **Total** | ~70-90 min | Medium |

---

## Current State vs Desired State

### Current State

```yaml
# docs/work/archive/E2-242/observations.md frontmatter
triage_status: pending
```

**Behavior:** 35 observations exist across 12 archived work items with `triage_status: pending`. Observations were captured during closure but never triaged.

**Result:** Valuable insights and gaps sit unactioned. Some may be resolved by recent work (E2-293/294/295), others may need new work items.

### Desired State

```yaml
# docs/work/archive/E2-242/observations.md frontmatter
triage_status: triaged
```

**Behavior:** Each observation has been classified (category, action, priority) and routed to appropriate outcome.

**Result:** No pending observations remain. Actionable items spawned to backlog. Insights stored to memory. Resolved/noise items dismissed with rationale.

---

## Tests First (TDD)

**SKIPPED:** This is a process execution task (running observation-triage-cycle), not code implementation. Verification is via deliverables checklist, not automated tests.

---

## Detailed Design

This is a process execution task using existing infrastructure, not code implementation.

### Process Flow

```
SCAN Phase
    |
    +-> just triage-observations
    |       Returns: 12 items with 35 observations
    |
    v
TRIAGE Phase (for each observation)
    |
    +-> Read observation content
    +-> Classify: category (bug/gap/debt/insight/question/noise)
    +-> Classify: action (spawn:INV/spawn:WORK/spawn:FIX/memory/discuss/dismiss)
    +-> Classify: priority (P0/P1/P2/P3)
    |
    v
PROMOTE Phase (for each triaged observation)
    |
    +-> spawn:WORK → /new-work E2-xxx "title"
    +-> spawn:INV → /new-investigation INV-xxx "title"
    +-> memory → ingester_ingest(content, source_path)
    +-> dismiss → Document rationale, no action
    |
    v
Update observations.md
    |
    +-> Set triage_status: triaged
    +-> Add triage log entry with decisions
```

### Triage Decision Matrix

Based on INV-067 findings and current system state:

| Observation Category | Likely Action | Rationale |
|---------------------|---------------|-----------|
| Session state related | dismiss | E2-293/294/295 resolved these |
| Consumer migration | spawn:WORK | Strangler fig completion needed |
| Template/skill gaps | spawn:WORK or dismiss | Depends on current state |
| Documentation gaps | memory | Store as insight |
| SDK/enforcement related | dismiss | E4 scope per S25 |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Interactive triage | Per-observation prompts | Avoids automated misclassification (memory 79910) |
| Batch processing | All 12 files in one session | Efficiency - context persists across files |
| Verification against current state | Check if resolved before spawning | Prevents duplicate work items |

### Real Data Sample

**E2-242 Observations (triage_status: pending):**
```
1. "Relative import issue in modules" - LIKELY dismiss (standardized in E2-279)
2. "Consumer migration work items" - LIKELY spawn:WORK (plan_tree, node_cycle not migrated)
```

**E2-254 Observations (triage_status: pending):**
```
1. "Spec mismatch discovered late" - LIKELY memory (governance lesson)
2. "No spec-alignment gate in plan cycles" - LIKELY dismiss (added in E2-254)
3. "Memory query was SHOULD, not MUST" - LIKELY dismiss (fixed in skill)
4. "No Risks & Mitigations guidance" - LIKELY dismiss (fixed in template)
5. "Fix ContextLoader to match spec" - LIKELY spawn:WORK (not resolved)
6. "Governance fixes applied this session" - LIKELY dismiss (already done)
```

---

## Open Decisions (MUST resolve before implementation)

**No operator decisions required.** Work item `operator_decisions: []` is empty. Triage decisions are made interactively during TRIAGE phase using the standard observation-triage-cycle dimensions.

---

## Implementation Steps

### Step 1: SCAN - Identify All Pending Observations
- [ ] Run `just triage-observations` to get current state
- [ ] Document count: 12 files, 35 observations (verify current)

### Step 2: TRIAGE - Process Each File
For each of the 12 files:
- [ ] E2-163 (2 observations)
- [ ] E2-233 (1 observation)
- [ ] E2-238 (4 observations)
- [ ] E2-242 (2 observations)
- [ ] E2-248 (2 observations)
- [ ] E2-253 (2 observations)
- [ ] E2-254 (6 observations)
- [ ] E2-255 (6 observations)
- [ ] INV-052 (4 observations)
- [ ] INV-056 (1 observation)
- [ ] INV-058 (2 observations)
- [ ] INV-059 (3 observations)

**For each observation:**
1. Read observation content
2. Check if resolved by recent work (E2-293/294/295)
3. Assign: category, action, priority
4. Document rationale

### Step 3: PROMOTE - Execute Actions
- [ ] For each spawn:WORK → create work item via `/new-work`
- [ ] For each spawn:INV → create investigation via `/new-investigation`
- [ ] For each memory → store via `ingester_ingest`
- [ ] For dismiss → document rationale (no action)

### Step 4: Update Observation Files
- [ ] Set `triage_status: triaged` in each file's frontmatter
- [ ] Add triage log entry with decisions made

### Step 5: Verification
- [ ] Run `just triage-observations` - should return 0 pending
- [ ] Verify all spawned items exist in `docs/work/active/`

---

## Verification

- [ ] `just triage-observations` returns 0 pending items
- [ ] All spawned work items exist in `docs/work/active/`
- [ ] All observations.md files have `triage_status: triaged`
- [ ] Triage decisions documented for audit trail

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Duplicate work items | Low | Check backlog before spawning; use `/new-work` to ensure proper linking |
| Misclassification | Low | Interactive triage with operator confirmation for ambiguous cases |
| Resolved observations spawned | Low | Verify against E2-293/294/295 deliverables before classifying |
| Scope creep (too many spawns) | Medium | Use dismiss liberally for resolved/noise; defer E3/E4 scope per S25 |

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

**MUST** read `docs/work/active/E2-296/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Run observation-triage-cycle on archived work items | [ ] | `just triage-observations` returns 0 |
| Triage each pending observation: promote/dismiss/defer | [ ] | All 35 observations classified |
| Document triage decisions for audit trail | [ ] | Triage log in each observations.md |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `docs/work/archive/E2-163/observations.md` | `triage_status: triaged` | [ ] | |
| `docs/work/archive/E2-242/observations.md` | `triage_status: triaged` | [ ] | |
| `docs/work/archive/E2-254/observations.md` | `triage_status: triaged` | [ ] | |
| (and 9 more observation files) | `triage_status: triaged` | [ ] | |

**Verification Commands:**
```bash
# Verify no pending observations remain
just triage-observations
# Expected: "No untriaged observations found."
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All 12 observation files verified? | [Yes/No] | |
| All spawned items exist in backlog? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] `just triage-observations` returns 0 pending
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] All spawned work items exist and are actionable
- [ ] WHY captured (triage rationale stored to observations.md files)
- [ ] Ground Truth Verification completed above

> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". For process tasks, deliverables are the verification, not tests.

---

## References

- @docs/work/active/INV-067/investigations/001-observation-backlog-verification-and-triage.md (spawning investigation)
- @.claude/skills/observation-triage-cycle/SKILL.md (process definition)
- E2-218: Observation Capture Gate (capture mechanism)
- E2-222: Routing thresholds (observation_pending.max_count: 10)
- Memory 79910: Interactive triage design decision
- Memory 81403: Observation capture works, triage execution is the gap

---
