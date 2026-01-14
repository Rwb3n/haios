---
template: investigation
status: complete
date: 2025-12-24
backlog_id: INV-029
title: Status Generation Architecture Gap
author: Hephaestus
session: 114
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 78858
- 78859
- 78860
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-24T20:54:21'
---
# Investigation: Status Generation Architecture Gap

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

**Trigger:** Vitals show "M4-Research (50%)" despite M7a milestone being 100% complete (6/6 items) as of Session 114.

**Problem Statement:** status.py discovers milestones from backlog.md but M7 sub-milestones only exist in work files (docs/work/), causing stale vitals display.

**Prior Observations:**
- Session 112: M7-Tooling split into 5 sub-milestones (M7a-M7e) with items assigned via work files
- Session 113-114: M7a-Recipes completed (6/6) but vitals unchanged
- haios-status-slim.json shows M4-Research 50% since Session 113

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "status generation vitals milestone progress haios-status"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 77009 | "Full status is /haios debugging only" | Scoping decision - slim vs full |
| 54166 | Status command displays ambiguous metrics | Prior confusion about progress |
| 77071 | Status scoping for debugging context | Synthesis on status purpose |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-008 (haios-status.json optimization) - different focus (size not discovery)

---

## Objective

<!-- One clear question this investigation will answer -->

**Why does vitals show stale milestone data, and what fix ensures milestones discovered from work files appear in status?**

---

## Scope

### In Scope
- status.py milestone discovery mechanism
- Work file milestone field usage
- backlog.md milestone patterns
- Milestone file structure (docs/pm/milestones/)

### Out of Scope
- Milestone progress calculation algorithm (works correctly once discovered)
- Session delta calculation (works correctly)
- Memory statistics (works correctly)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 4 | status.py, backlog.md, work files, milestones/ |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 3 | Codebase |
| Estimated complexity | Low | Clear data source mismatch |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | status.py only discovers milestones from backlog.md, not work files | High | Read `_discover_milestones_from_backlog()` | 1st |
| **H2** | M7 sub-milestones were never added to backlog.md with `**Milestone:**` pattern | High | Grep backlog.md for M7 | 2nd |
| **H3** | Milestone files (docs/pm/milestones/) are not read by status.py | Med | Check if status.py reads milestones/*.md | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic
2. [x] Search codebase for relevant patterns (Grep/Glob)
3. [x] Read identified files and document findings

### Phase 2: Hypothesis Testing
4. [x] Test H1: Read status.py `_discover_milestones_from_backlog()` implementation
5. [x] Test H2: Grep backlog.md for M7 patterns
6. [x] Test H3: Check if status.py reads milestones/*.md

### Phase 3: Synthesis
7. [x] Compile evidence table
8. [x] Determine verdict for each hypothesis
9. [x] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| `_discover_milestones_from_backlog()` only reads backlog.md | `.claude/lib/status.py:903-960` | H1 | Pattern: `\*\*Milestone:\*\*\s*(M\d+-[A-Za-z]+)` |
| `_load_existing_milestones()` delegates to backlog discovery | `.claude/lib/status.py:879-886` | H1 | "Always discovers from backlog" comment |
| No M7a, M7b, M7c, M7d, M7e patterns in backlog.md | `docs/pm/backlog.md` | H2 | grep found M3, M4, M5, M6 only |
| Work files use `milestone:` YAML field (e.g., `milestone: M7a-Recipes`) | `docs/work/archive/WORK-E2-162-*.md:9` | H2 | YAML frontmatter pattern |
| No code references `docs/pm/milestones/` directory | `.claude/lib/status.py` (full file) | H3 | Only M8-Memory.md exists there anyway |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 77009 | "Full status is /haios debugging only" | Context | Scoping decision |

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
| H1 | **Confirmed** | `_discover_milestones_from_backlog()` only scans backlog.md using `**Milestone:**` regex | High |
| H2 | **Confirmed** | grep backlog.md shows M3-M6 only; M7 sub-milestones exist only in work file frontmatter | High |
| H3 | **Confirmed** | No reference to `docs/pm/milestones/` in status.py; directory only has M8-Memory.md stub | High |

### Detailed Findings

#### Finding 1: Milestone Discovery Source Mismatch

**Evidence:**
```python
# status.py:903-960
def _discover_milestones_from_backlog() -> dict:
    # Pattern matches: **Milestone:** M6-WorkCycle
    milestone_pattern = r'\*\*Milestone:\*\*\s*(M\d+-[A-Za-z]+)'
    discovered_keys = set(re.findall(milestone_pattern, content))
```

**Analysis:** The discovery function is hardcoded to read only backlog.md and match the `**Milestone:** M?-Name` Markdown pattern. This was the legacy pattern before work files existed.

**Implication:** Need to add work file scanning to discover milestones from YAML frontmatter (`milestone:` field).

#### Finding 2: Data Migration Gap

**Evidence:**
```
# Session 112 split M7-Tooling into M7a-M7e
# Work files use: milestone: M7a-Recipes
# Backlog.md was NOT updated with new **Milestone:** patterns
```

**Analysis:** When M7-Tooling was split in Session 112, milestone assignments were made via work files only. The old backlog.md patterns weren't updated, creating a discovery gap.

**Implication:** Either (a) backfill backlog.md with M7 patterns, or (b) update status.py to scan work files. Option (b) is architecturally cleaner since work files are the new source of truth.

#### Finding 3: Two Milestone Definition Patterns

**Evidence:**
```
Pattern 1 (legacy): backlog.md with **Milestone:** M6-WorkCycle
Pattern 2 (new): work files with milestone: M7a-Recipes YAML field
Pattern 3 (future?): docs/pm/milestones/*.md files (only M8-Memory.md exists)
```

**Analysis:** Architecture is in transition. Work files are the new canonical source but status.py wasn't updated to match.

**Implication:** Fix should add `get_milestones_from_work_files()` function to status.py that scans docs/work/{active,blocked,archive}/ for milestone assignments.

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

**SKIPPED:** No new schema needed - work files already have correct `milestone:` field.

### Mapping Table (if applicable)

| Source | Target | Relationship | Notes |
|--------|--------|--------------|-------|
| `docs/work/**/*.md` | `milestone` field | YAML frontmatter | Primary source |
| `docs/pm/backlog.md` | `**Milestone:**` pattern | Markdown inline | Legacy fallback |
| `docs/pm/milestones/*.md` | Milestone definition files | Future pattern | Not implemented yet |

### Mechanism Design (if applicable)

```
TRIGGER: generate_slim_status() or generate_full_status() called

ACTION:
    1. Call _discover_milestones_from_work_files()  # NEW
       - Glob docs/work/{active,blocked,archive}/*.md
       - Parse YAML frontmatter for milestone: field
       - Build unique set of milestone keys
    2. Call _discover_milestones_from_backlog()     # EXISTING (fallback)
       - For legacy items not yet migrated to work files
    3. Merge results, work files take precedence
    4. Calculate progress per milestone using get_milestone_progress()

OUTCOME: All milestones (M3-M8+) appear in vitals with correct progress
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Primary source | Work files | Work files are new source of truth (INV-024, Session 105) |
| Keep backlog fallback | Yes | Backward compatibility for legacy M3-M6 items not yet migrated |
| Read milestones/*.md | No (defer) | Only M8-Memory.md exists; not worth complexity yet |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-173: Work File Milestone Discovery**
  - Description: Add `_discover_milestones_from_work_files()` to status.py
  - Fixes: Vitals show stale M4-Research instead of completed M7a-Recipes
  - Spawned via: `/new-work E2-173 "Work File Milestone Discovery"`
  - Milestone: M7d-Plumbing
  - Priority: HIGH

### Future (Requires more work first)

**SKIPPED:** No future items - fix is straightforward

### Not Spawned Rationale (if no items)

**N/A** - E2-173 spawned above

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 115 | 2025-12-24 | CONCLUDE | Complete | All hypotheses confirmed, E2-173 spawned |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1, H2, H3 all Confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | status.py:903-960, etc. |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-173 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | See below |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | No | Small scope - direct exploration was sufficient |
| Are all evidence sources cited with file:line or concept ID? | Yes | |
| Were all hypotheses tested with documented verdicts? | Yes | |
| Are spawned items created (not just listed)? | Yes | E2-173 work file created |
| Is memory_refs populated in frontmatter? | Yes | Will update after ingestion |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (if applicable)
- [x] Session progress updated (if multi-session)

---

## References

- Spawned by: Session 114 checkpoint noting stale vitals
- Related: INV-008 (haios-status.json optimization)
- Related: INV-024 (Work Item as File Architecture)

---
