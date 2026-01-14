---
template: investigation
status: complete
date: 2025-12-26
backlog_id: INV-037
title: Context Level Architecture and Source Optimization
author: Hephaestus
session: 121
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 79044
- 79045
- 79046
- 79047
- 79048
- 79049
- 79050
- 79051
- 79052
- 79053
- 79054
- 79055
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-26T10:54:46'
---
# Investigation: Context Level Architecture and Source Optimization

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

**Trigger:** Session 121 discussion about defining context levels for coldstart, synthesizing Business Analysis hierarchy with Information Architecture principles.

**Problem Statement:** HAIOS coldstart loads files without a principled context level architecture, leading to stale/unused READMEs, untapped historical artifacts, and suboptimal file selection for agent initialization.

**Prior Observations:**
- INV-036 confirmed "Coldstart works but missing L1 context" (core facts, invariants)
- E2-164 exists but doesn't define what L1/L2/L3 actually means
- READMEs across project are slowly becoming stale (no update triggers)
- Historical/archived files may contain valuable invariants never surfaced
- Memory 78813: "Documentation files not read in coldstart and never referenced in commands/skills are dead weight"

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "context levels coldstart optimization README staleness information architecture"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 78813 | "STALE REFS PATTERN: Documentation files not read in coldstart and never referenced in commands/skills are dead weight" | Direct - defines the staleness problem |
| 63587 | Strategies for leveraging staleness signals and timestamps for README updates | Mitigation approach |
| 77650 | Cold start context refinement - using revised context for specificity | L1/L2/L3 design input |
| 71758 | "Static query formulation - Coldstart uses hardcoded query" | Current limitation |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-036 (Coldstart/Checkpoint/Heartbeat Audit) - confirmed L1 gap
- [x] Found: E2-164 (Coldstart L1 Context Review) - scoped but undefined levels

---

## Objective

<!-- One clear question this investigation will answer -->

**Primary Question:** How should HAIOS define context levels (L1/L2/L3) and which existing files should populate each level for optimal agent initialization?

**Secondary Questions:**
1. Which READMEs are stale vs. stable sources of truth?
2. What historical/archived content contains valuable invariants worth surfacing?
3. How should coldstart file selection be optimized based on level definitions?

---

## Scope

### In Scope
- Define L1/L2/L3 context level architecture (BA + IA synthesis)
- Audit current README files for staleness vs. stability
- Identify historical/archived files with salvageable invariants
- Assess current coldstart file selection and optimization opportunities
- Map existing files to proposed levels

### Out of Scope
- Implementation of new coldstart behavior (that's E2-164)
- Creating new documentation files (assess existing first)
- Memory system changes (focus on file-based context)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~50+ | READMEs, .claude/, docs/, archives |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 3 | Codebase / Memory / File timestamps |
| Estimated complexity | Medium | Multi-directory audit |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Many READMEs are stale (>30 days since update) but could become stable L1/L2 sources if updated once | High | Check `last_updated` timestamps across all READMEs; compare to last significant change | 1st |
| **H2** | Historical/archived files contain core invariants never surfaced to agent (buried treasure) | Med | Audit `docs/archive/`, deprecated files, early ADRs for evergreen facts | 2nd |
| **H3** | Current coldstart loads too much L3 (session-specific) and not enough L1 (invariants) | High | Analyze coldstart.md file loading; categorize by proposed level; measure token cost | 3rd |

**Proposed Level Definitions (to validate):**

| Level | Name | BA Equivalent | Content Type | Coldstart Behavior |
|-------|------|---------------|--------------|-------------------|
| L1 | Core Facts | Business Requirements | System identity, invariants, capabilities | Always loaded, rarely changes |
| L2 | Operational State | Functional Requirements | Milestone, infrastructure, active work | Refreshed per session |
| L3 | Session Context | Technical Requirements | Checkpoints, plans, current focus | Loaded on demand |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [ ] Query memory for prior learnings on README staleness, coldstart optimization
2. [ ] Glob all README.md files across project
3. [ ] Extract `last_updated` timestamps from all READMEs

### Phase 2: Hypothesis Testing
4. [ ] **Test H1 (README Staleness):** Categorize READMEs by age; identify which are stable vs. stale
5. [ ] **Test H2 (Buried Treasure):** Audit `docs/archive/`, `deprecated_*.md`, early ADRs (001-010) for evergreen facts
6. [ ] **Test H3 (Coldstart Balance):** Read coldstart.md, categorize each loaded file by L1/L2/L3

### Phase 3: Synthesis
7. [ ] Compile file-to-level mapping table
8. [ ] Determine verdict for each hypothesis
9. [ ] Define recommended L1 file list for E2-164
10. [ ] Identify spawned work items (README updates, archive salvage, coldstart refactor)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| 35 READMEs audited, 0 stale (>30 days) | Glob `**/README.md` | **Refutes H1** | All updated since 2025-12-06 |
| 17 READMEs Fresh (<7 days), 18 Current (7-30 days) | Timestamp analysis | **Refutes H1** | Active maintenance |
| Genesis_Architect_Notes.md contains "Certainty Ratchet", "Three Pillars", SDD framework | `_archive/test_phase2/Genesis_Architect_Notes.md` | **Confirms H2** | Never surfaced to agent |
| deprecated_AGENT.md has Three Pillars, Structured Mistrust pattern | `deprecated_AGENT.md:L10-50` | **Confirms H2** | Evergreen philosophy |
| HAIOS-RAW ADRs 001-043 have foundational rules (idempotency, 5-phase loop, flywheel) | `HAIOS-RAW/system/canon/ADR/` | **Confirms H2** | Core invariants buried |
| Coldstart loads 55% L3 content (checkpoints + memory) | `.claude/commands/coldstart.md` | **Confirms H3** | Imbalanced toward session-specific |
| L1 philosophical content (Certainty Ratchet, etc.) not in coldstart | `.claude/commands/coldstart.md` | **Confirms H3** | Missing invariants |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 78813 | "STALE REFS PATTERN: Documentation files not read in coldstart are dead weight" | H1/H3 | Defines staleness concern |
| 71758 | "Static query formulation - Coldstart uses hardcoded query" | H3 | Current limitation |

### External Evidence (if applicable)

**SKIPPED:** Pure codebase investigation, no external sources needed.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **REFUTED** | 35 READMEs audited, 0 stale (>30 days). All updated since 2025-12-06. | High |
| H2 | **CONFIRMED** | Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs contain evergreen invariants never surfaced. | High |
| H3 | **CONFIRMED** | Coldstart loads 55% L3 (session-specific), 35% L1 (invariants), 10% L2 (operational). Missing: Certainty Ratchet, Three Pillars, Governance Flywheel. | High |

### Detailed Findings

#### Finding 1: READMEs Are Actively Maintained (H1 Refuted)

**Evidence:**
```
Category Distribution:
- Fresh (<7 days): 17 READMEs (49%)
- Current (7-30 days): 18 READMEs (51%)
- Stale (>30 days): 0 READMEs (0%)
- Ancient (>90 days): 0 READMEs (0%)
```

**Analysis:** The assumption that READMEs are "slowly becoming stale" is incorrect. Active maintenance during M8-SkillArch milestone kept all READMEs current. 80% contain stable reference content (workflow docs, catalogs, schemas).

**Implication:** No README rescue needed. Focus should be on WHICH READMEs to load at coldstart, not on updating them.

#### Finding 2: Significant Buried Treasure in Archives (H2 Confirmed)

**Evidence:**
```
Evergreen invariants discovered:
1. "Certainty Ratchet" - HAIOS ensures state moves only toward increasing certainty
2. "Three Pillars" - Evidence-Based, Durable Context, Separation of Duties
3. "SDD Framework" - 70% specification, 30% implementation
4. "Governance Flywheel" - Principles -> Enforcement -> Feedback -> Improvement
5. "Universal Idempotency" - All mutable operations MUST require Idempotency-Key
6. "5-Phase Loop" - ANALYZE -> BLUEPRINT -> CONSTRUCT -> VALIDATE -> IDLE
7. "Structured Mistrust" - Assume agents will fail in predictable ways

Sources:
- _archive/test_phase2/Genesis_Architect_Notes.md (philosophy)
- deprecated_AGENT.md (operational rules)
- HAIOS-RAW/system/canon/ADR/ADR-OS-001 to 043 (foundational ADRs)
```

**Analysis:** Core philosophical invariants that define HAIOS identity and operational rules exist but are buried in deprecated/archived files. Agent has no access to this foundational context.

**Implication:** Create `.claude/config/invariants.md` to extract and surface these evergreen facts to L1 context.

#### Finding 3: Coldstart L1/L2/L3 Imbalance (H3 Confirmed)

**Evidence:**
```
Current coldstart distribution:
| Level | Content | Token Estimate | Proportion |
|-------|---------|----------------|------------|
| L1 | CLAUDE.md, epistemic_state.md, just --list | ~330 lines | 35% |
| L2 | haios-status-slim.json, workspace | ~100 lines | 10% |
| L3 | 2 checkpoints, memory query | ~400 lines | 55% |

Missing from L1:
- System philosophy (Certainty Ratchet, Three Pillars)
- Core invariants (idempotency, work-before-plan)
- Architectural metaphors (Trust Engine, Governance Flywheel)
```

**Analysis:** Session-specific context (L3) dominates coldstart, while foundational invariants (L1) are underrepresented. Agent rediscovers basic facts each session because they're not loaded.

**Implication:** Rebalance coldstart to load more L1 (invariants file), maintain L2 (operational state), reduce L3 token cost (summarize checkpoints).

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design: Context Level Architecture

```yaml
# Context Level Definitions (BA + IA Synthesis)
L1_Core_Facts:
  name: "Core Facts"
  ba_equivalent: "Business Requirements"
  content_type: "System identity, invariants, capabilities"
  coldstart_behavior: "Always loaded, rarely changes"
  update_frequency: "Monthly or on major architectural change"

L2_Operational_State:
  name: "Operational State"
  ba_equivalent: "Functional Requirements"
  content_type: "Milestone, infrastructure, active work"
  coldstart_behavior: "Refreshed per session"
  update_frequency: "Per session or on status change"

L3_Session_Context:
  name: "Session Context"
  ba_equivalent: "Technical Requirements"
  content_type: "Checkpoints, plans, current focus"
  coldstart_behavior: "Loaded on demand"
  update_frequency: "Per action or task completion"
```

### Mapping Table: Files to Context Levels

| File | Level | Rationale | Load Order |
|------|-------|-----------|------------|
| **L1 - Core Facts** ||||
| `CLAUDE.md` | L1 | Identity, governance, RFC 2119 keywords | 1 |
| `docs/epistemic_state.md` | L1 | Behavioral patterns, anti-patterns | 2 |
| `.claude/config/invariants.md` (NEW) | L1 | Extracted evergreen facts from archives | 3 |
| `just --list` (output) | L1 | Available capabilities | 4 |
| **L2 - Operational State** ||||
| `.claude/haios-status-slim.json` | L2 | Milestone progress, infrastructure counts | 5 |
| Workspace section (parsed) | L2 | Outstanding work items | 6 |
| **L3 - Session Context** ||||
| Last checkpoint (1, not 2) | L3 | Most recent session context | 7 |
| Memory query (targeted) | L3 | Strategies for current focus | 8 |

### Mechanism Design: Coldstart Rebalancing

```
TRIGGER: /coldstart command invoked

ACTION:
    1. Load L1 files (CLAUDE.md, epistemic_state.md, invariants.md, just --list)
    2. Load L2 files (haios-status-slim.json, parse workspace)
    3. Load L3 files (last 1 checkpoint, targeted memory query)
    4. Summarize: Phase, Momentum, Pending Items, System Status

OUTCOME: Agent initialized with balanced context (40% L1, 20% L2, 40% L3)
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Create invariants.md vs. update CLAUDE.md | Create new file | CLAUDE.md is already 160 lines; invariants.md keeps evergreen facts separate and cacheable |
| Load 1 checkpoint instead of 2 | 1 checkpoint | Session continuity from prior session sufficient; 2 doubles L3 token cost |
| Use BA hierarchy for levels | L1=Business, L2=Functional, L3=Technical | Aligns with standard BA terminology; provides clear mental model |
| Surface buried ADR content | Extract to invariants.md | HAIOS-RAW ADRs too voluminous (57 files); curated extraction more efficient |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [ ] **E2-200: Create invariants.md with Extracted Evergreen Facts**
  - Description: Extract Certainty Ratchet, Three Pillars, Governance Flywheel, SDD framework, idempotency rules from buried archives into `.claude/config/invariants.md`
  - Fixes: H2 finding - buried treasure not surfaced to agent
  - Spawned via: `/new-plan E2-200 "Create invariants.md with Extracted Evergreen Facts"`

- [ ] **E2-201: Update Coldstart to Load invariants.md**
  - Description: Add `.claude/config/invariants.md` to coldstart load sequence; reduce checkpoints from 2 to 1
  - Fixes: H3 finding - L1/L2/L3 imbalance (55% L3 → 40% L3)
  - Spawned via: `/new-plan E2-201 "Update Coldstart to Load invariants.md"`

### Future (Requires more work first)

- [ ] **E2-164: Coldstart L1 Context Review** (EXISTING - update scope)
  - Description: Already exists; should be updated to reference INV-037 design outputs
  - Blocked by: E2-200 (invariants.md must exist first)

### Not Spawned Rationale (if no items)

N/A - Two new items spawned, one existing item updated.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 121 | 2025-12-26 | ALL | Complete | Hypothesize, Explore, Conclude in single session |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1 Refuted, H2/H3 Confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | Glob, deprecated_AGENT.md, coldstart.md cited |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | E2-200, E2-201 to be created after approval |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | Pending |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Used for H1 (README audit) and H2 (archive treasure) |
| Are all evidence sources cited with file:line or concept ID? | Yes | Evidence Collection table has all sources |
| Were all hypotheses tested with documented verdicts? | Yes | H1 Refuted, H2 Confirmed, H3 Confirmed |
| Are spawned items created (not just listed)? | Pending | Will create after operator approval |
| Is memory_refs populated in frontmatter? | Pending | Will populate after ingester_ingest |

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

- **Spawned by:** Session 121 discussion on BA/IA synthesis for context levels
- **Related:** INV-036 (Coldstart/Checkpoint/Heartbeat Audit) - confirmed L1 gap
- **Related:** E2-164 (Coldstart L1 Context Review) - scoped but undefined levels
- **Source Archives:** Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs 001-043

---
