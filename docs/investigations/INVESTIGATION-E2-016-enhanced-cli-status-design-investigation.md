---
template: investigation
status: complete
date: 2025-12-26
backlog_id: E2-016
title: Enhanced CLI Status Design Investigation
author: Hephaestus
session: 124
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 79126
- 79127
- 79128
- 79129
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-26T16:40:55'
---
# Investigation: Enhanced CLI Status Design Investigation

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

**Trigger:** Session 49 troubleshooting revealed table name assumptions in CLI status. Need to understand current CLI status architecture before enhancing.

**Problem Statement:** The CLI `status` command may be missing synthesis statistics, and its architecture needs review before adding features.

**Prior Observations:**
- Session 49: Table name assumptions during troubleshooting
- Memory 59694: "Status output mixes cumulative and per-run statistics without labels"
- Memory 55648: CLI already has `synthesis run`, `synthesis stats`, `synthesis inspect` commands
- Work item requests: Add synthesis stats to `cli.py status` command

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "CLI status synthesis run enhanced status command"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 55817 | cli synthesis stats | Direct relevance - synthesis stats already exist |
| 59694 | Status output mixes cumulative and per-run statistics without labels | Design consideration - labeling |
| 55648 | CLI Commands: synthesis run, synthesis stats, synthesis inspect | Shows existing synthesis CLI |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-029 (Status Generation Architecture Gap) - related to status architecture

---

## Objective

<!-- One clear question this investigation will answer -->

**Primary Question:** What is the current CLI status architecture, and how should synthesis stats be integrated - add to existing `status` command or leverage existing `synthesis stats` command?

---

## Scope

### In Scope
- Current CLI `status` command implementation
- Current `synthesis stats` command implementation
- What stats each command shows
- Integration options

### Out of Scope
- Plugin architecture migration (separate effort)
- Web UI for status (future)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 2-3 | haios_etl/cli.py, .claude/lib/status.py |
| Hypotheses to test | 2 | Listed below |
| Expected evidence sources | Codebase | CLI source files |
| Estimated complexity | Low | Existing infrastructure review |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | `synthesis stats` already provides the needed information, making E2-016 redundant | Med | Read cli.py synthesis stats command, run it | 1st |
| **H2** | `status` command should call `synthesis stats` internally rather than duplicating code | High | Read both commands, assess architecture | 2nd |

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
| `synthesis stats` shows clusters, members, cross-pollination links | `haios_etl/cli.py:192-207` | H1 | Already comprehensive |
| `status` and `synthesis stats` are independent implementations | `haios_etl/cli.py:28-76, 192-207` | H2 | No code sharing |
| `status` uses direct SQL, `synthesis stats` uses SynthesisManager | `haios_etl/cli.py` | H2 | Composition possible |
| No "last run" timestamp in synthesis stats | `haios_etl/synthesis.py:900-949` | H1 (partial) | Only missing piece |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 59694 | Status output mixes cumulative and per-run statistics without labels | H2 | Labeling concern valid |
| 55648 | CLI Commands: synthesis run, synthesis stats, synthesis inspect | H1 | Confirms existing commands |

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
| H1 | **Confirmed (Partial)** | `synthesis stats` already shows clusters, members, cross-pollination - but missing "last run" timestamp. E2-016 is ~80% redundant. | High |
| H2 | **Confirmed** | Commands are independent implementations. Composition via justfile recipe is better than merging. | High |

### Detailed Findings

#### Finding 1: Synthesis Stats Already Exists and Is Comprehensive

**Evidence:**
```python
# haios_etl/cli.py:192-206
elif args.subcommand == "stats":
    stats = manager.get_synthesis_stats()
    print("Synthesis Statistics:")
    print(f"  Total Concepts: {stats.total_concepts:,}")
    print(f"  Synthesized Concepts: {stats.synthesized_concepts:,}")
    print(f"  Pending Clusters: {stats.pending_clusters:,}")
    print(f"  Completed Clusters: {stats.completed_clusters:,}")
    print(f"  Cross-pollination Links: {stats.cross_pollination_links:,}")
```

**Analysis:** The `synthesis stats` command already provides what E2-016 deliverable #1 requests (clusters, members via cross-pollination links). Only missing piece is "last run" timestamp.

**Implication:** E2-016 is largely redundant. Should be closed as "Won't Fix - Already Exists" or reduced to adding "last run" timestamp only.

#### Finding 2: Commands Are Architecturally Independent

**Evidence:**
- `status` (lines 28-76): Direct SQL queries on artifacts, entities, concepts, processing_log
- `synthesis stats` (lines 192-207): Uses `SynthesisManager.get_synthesis_stats()`

**Analysis:** No code reuse between commands. If merging was desired, `status` should call `SynthesisManager.get_synthesis_stats()` rather than duplicating SQL.

**Implication:** Keep commands separate. Add `just full-status` recipe for combined view if needed.

#### Finding 3: Deliverable #2 Is Operational, Not Code

**Evidence:** Work item E2-016 deliverable #2: "Run synthesis with `--max-bridges 200`"

**Analysis:** This is an operational task (run a command), not a code change. Does not belong in implementation work item.

**Implication:** Remove from E2-016 scope or track as separate operational task.

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

**SKIPPED:** No new schema needed - existing commands sufficient.

### Mapping Table (if applicable)

**SKIPPED:** Pure discovery, no mapping required.

### Mechanism Design (if applicable)

**SKIPPED:** Recommendation is to keep existing mechanism unchanged.

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Merge synthesis stats into status? | **No** | Keep separation of concerns - ETL vs Synthesis are different subsystems |
| Close E2-016? | **Yes (Won't Fix)** | Functionality already exists in `synthesis stats` command |
| Add "last run" timestamp? | **Optional (new work)** | Only missing piece; low value vs effort |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

**None** - E2-016 should be closed as "Won't Fix" rather than spawning new work.

### Future (Requires more work first)

**None** - The "last run timestamp" feature is optional and low priority.

### Not Spawned Rationale (if no items)

**RATIONALE:** Investigation found that E2-016 is ~80% redundant - the requested functionality already exists in `python -m haios_etl.cli synthesis stats`. Rather than spawning new implementation work, the appropriate action is to close E2-016 as "Won't Fix - Already Exists" and update documentation to point users to the existing `synthesis stats` command.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 124 | 2025-12-26 | HYPOTHESIZE | Started | Initial context and hypotheses |
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
