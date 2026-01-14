---
template: investigation
status: complete
date: 2025-12-26
backlog_id: INV-040
title: Plan Tree Missing Titles Bug
author: Hephaestus
session: 123
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 79108
- 79109
- 79110
- 79111
- 79112
- 79113
- 79114
- 79115
- 79116
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-26T15:20:08'
---
# Investigation: Plan Tree Missing Titles Bug

@docs/README.md
@docs/epistemic_state.md

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** During M7d milestone review (Session 123), `just tree` and `just ready` showed work item IDs but many titles were empty.

**Problem Statement:** The `plan_tree.py` script fails to extract the `title:` field from YAML frontmatter for some work items, causing empty titles in output.

**Prior Observations:**
- `just tree-current` shows entries like `[x] E2-109:` with no title after the colon
- `just ready` shows `E2-004:` with no title
- Some items DO have titles (e.g., `E2-081: Heartbeat Scheduler`)
- Pattern suggests selective failure, not complete parsing breakdown

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "plan_tree script missing titles frontmatter parsing"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 78861 | status.py only discovers milestones from backlog.md, missing work file frontmatter | Similar parsing gap |
| 77347 | Script parses ### [PRIORITY] ID: Title headers from backlog.md | Shows where titles come from |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No direct match, but related parsing issues found in memory

---

## Objective

<!-- One clear question this investigation will answer -->

Why do some work items show empty titles in `just tree` and `just ready` output, and how do we fix it?

---

## Scope

### In Scope
- `scripts/plan_tree.py` - the script producing the output
- Work file frontmatter parsing logic
- Specific work items with missing titles (E2-109, E2-132, INV-029, etc.)

### Out of Scope
- Status.py (separate module)
- Memory system integration
- Other just recipes

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 1-3 | plan_tree.py, sample work files |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + work files |
| Estimated complexity | Low | Likely simple parsing bug |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Script reads from backlog.md (now archived) not work files | High | Read plan_tree.py, check data source | 1st |
| **H2** | Work files exist in archive but script only reads active/ | Med | Check if E2-109 is in archive vs active | 2nd |
| **H3** | YAML parsing fails for certain frontmatter formats | Low | Compare working vs failing work files | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [ ] Query memory for prior learnings on topic
2. [ ] Search codebase for relevant patterns (Grep/Glob)
3. [ ] Read identified files and document findings

### Phase 2: Hypothesis Testing
4. [ ] Test H1: [Specific actions]
5. [ ] Test H2: [Specific actions]
6. [ ] Test H3: [Specific actions]

### Phase 3: Synthesis
7. [ ] Compile evidence table
8. [ ] Determine verdict for each hypothesis
9. [ ] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| Script only reads `docs/plans/PLAN-E2-*.md` | `scripts/plan_tree.py:71` | H1/H2 | Pattern too restrictive |
| Pattern misses INV-*, PLAN-EPOCH2-*, PLAN-ADR-* | `scripts/plan_tree.py:71` | H2 | Only matches E2-NNN |
| E2-109 has no plan file but work file exists | `docs/work/archive/WORK-E2-109-*.md` | H2 | Work file has title |
| INV-029 work file has title field | `docs/work/archive/WORK-INV-029-*.md:4` | H3 refuted | YAML parsing works fine |
| Work files use `id:` not `backlog_id:` | `docs/work/archive/WORK-INV-029-*.md:3` | - | Parsing adjustment needed |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 78861 | status.py only discovers milestones from backlog.md | H1 | Similar pattern - wrong data source |
| 77347 | Script parses backlog.md headers | H1 | Legacy approach |

### External Evidence (if applicable)

**SKIPPED:** Pure codebase investigation, no external sources needed

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | Partial | Script reads plan files not backlog.md, but still wrong source | High |
| H2 | **CONFIRMED** | Script ignores work files entirely - only reads `docs/plans/PLAN-E2-*.md` | High |
| H3 | Refuted | YAML parsing works fine, work files have correct title fields | High |

### Detailed Findings

#### Root Cause: Wrong Data Source

**Evidence:**
```python
# scripts/plan_tree.py:71
for plan_path in glob.glob("docs/plans/PLAN-E2-*.md"):
```

**Analysis:** The script reads titles from plan files, but:
1. Pattern `PLAN-E2-*.md` only matches E2-NNN items with plans
2. Many work items (INV-*, small E2-* tasks) have NO plan file
3. Work files (`docs/work/*/WORK-*.md`) are the canonical title source

**Implication:** Script must read from work files as primary source.

#### Pattern Too Restrictive

**Evidence:**
- Missing INV-029, INV-032, E2-109, E2-132 because no plan files exist
- E2-109 work file: `docs/work/archive/WORK-E2-109-heartbeat-scheduled-task-environment-fix.md`
- These work files have `title:` field in YAML frontmatter

**Analysis:** ADR-039 established work files as source of truth, but plan_tree.py predates this.

**Implication:** Refactor to read work files (both active/ and archive/), fall back to plan files for legacy.

---

## Design Outputs

**SKIPPED:** Pure bug fix, no architectural design needed. Fix is straightforward code change.

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-205: Fix plan_tree.py to read work files**
  - Description: Refactor plan_tree.py to read titles from work files (docs/work/*/WORK-*.md) instead of plan files
  - Fixes: Missing titles in `just tree` and `just ready` output
  - Note: Simple fix, implementing directly in this session

### Future (Requires more work first)

None - fix is straightforward.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 122 | 2025-12-26 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
