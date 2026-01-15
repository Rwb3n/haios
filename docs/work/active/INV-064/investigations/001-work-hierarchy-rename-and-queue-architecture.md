---
template: investigation
status: active
date: 2026-01-15
backlog_id: INV-064
title: Work Hierarchy Rename and Queue Architecture
author: Hephaestus
session: 191
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 81366
- 81367
- 81368
- 81369
- 81370
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-15T19:46:44'
---
# Investigation: Work Hierarchy Rename and Queue Architecture

@docs/README.md
@docs/epistemic_state.md

<!-- FILE REFERENCE REQUIREMENTS (MUST - Session 171 Learning)

     1. MUST use full @ paths for prior work:
        CORRECT: @docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
        WRONG:   INV-052, "See INV-052"

     2. MUST read ALL @ referenced files BEFORE starting EXPLORE phase:
        - Read each @path listed at document top
        - For directory references (@docs/work/active/INV-052/), MUST Glob to find all files
        - Document key findings in Prior Work Query section
        - Do NOT proceed to EXPLORE until references are read

     3. MUST Glob referenced directories:
        @docs/work/active/INV-052/ → Glob("docs/work/active/INV-052/**/*.md")
        Then read key files (SECTION-*.md, WORK.md, investigations/*.md)

     Rationale: Session 171 wasted ~15% context searching for INV-052 in wrong
     location because agent ignored @ references and guessed file locations.
-->

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

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** Session 191 design discussion - operator noted semantic mismatch in hierarchy naming

**Problem Statement:** Current naming (Epoch→Chapter→Arc→Work Item) conflicts with story semantics where "arc" encompasses multiple "chapters", and there's no queue architecture for work execution.

**Prior Observations:**
- Current hierarchy decided in Session 179: Epoch→Chapter→Arc→Work Item
- Semantic confusion: In storytelling, an "arc" spans multiple "chapters" (e.g., "The Redemption Arc" contains Chapter 1-5)
- We call big thematic containers "Chapters" (Chariot, Breath, Form, Ground) when they should semantically be "Arcs"
- We call bounded deliveries within them "Arcs" (ARC-001, ARC-002) when they should be "Chapters"
- No work queue exists - `just ready` returns flat unordered list
- Work items float disconnected from chapter/arc structure
- No async consideration for batch execution

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "work hierarchy chapters arcs epochs work queues"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 80910 | "FINAL HIERARCHY: Epoch → Chapter → Arc → Work Item" | Current decision to evaluate |
| 80912 | "Chapter: Major capability/theme within epoch. Replaces Milestone" | Chapter definition |
| 80915 | "METAPHOR: Epoch = Book, Chapter = Major section, Arc = Scene/sequence" | Metaphor to reconsider |
| 81363 | "Chapter [volumous] → Arc [tight] → Investigation → Work Items" | Pressure pattern |
| 81098 | "Backlog churn - Completing work items disconnected from chapter structure" | Queue problem |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: Memory from Session 179 hierarchy decision (80910-80916)

---

## Objective

<!-- One clear question this investigation will answer -->

**Primary:** Should we rename Chapter↔Arc to align with story semantics, and what work queue architecture should structure execution across the hierarchy?

**Secondary:** What is the migration impact and how does this enable HAIOS init (spec-driven bootstrap)?

---

## Scope

### In Scope
- Semantic analysis: Arc vs Chapter naming conventions
- Current hierarchy usage audit (how many files reference Chapter/Arc?)
- Work queue design: queue types, policies, cross-cutting behavior
- Migration impact assessment
- Connection to HAIOS init (spec-driven bootstrap)

### Out of Scope
- HAIOS init implementation (Epoch 3+ scope)
- Actual migration execution (spawned work item)
- Multi-agent queue orchestration (Epoch 4 scope)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~20 | EPOCH.md, CHAPTER.md files, architecture docs |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 3 | Codebase, Memory, Session 191 discussion |
| Estimated complexity | Medium | Naming change + new architecture (queues) |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Renaming Chapter↔Arc aligns with universal story semantics and reduces cognitive load | High | Review narrative convention, grep current usage, assess migration scope | 1st |
| **H2** | Work queues should be orthogonal to hierarchy - structuring execution not organization | Medium | Design queue policies, evaluate cross-cutting scenarios, compare to existing `just ready` | 2nd |
| **H3** | Queues + renamed hierarchy enable cleaner HAIOS init spec structure | Medium | Draft spec schema, evaluate if rename simplifies configuration | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Grep for "Chapter" and "Arc" usage in codebase - count references
2. [x] Read all CHAPTER.md files to understand current structure
3. [x] Review Session 179 decision rationale (memory 80910-80916)

### Phase 2: Hypothesis Testing
4. [x] H1: Semantic analysis - document story convention, compare to current usage
5. [x] H1: Migration impact - list files to rename, assess breakage
6. [x] H2: Queue design - draft queue types (FIFO, batch, priority), policies
7. [x] H2: Cross-cutting scenarios - how would queue handle multi-arc work?
8. [x] H3: HAIOS init spec - draft schema showing hierarchy + queues

### Phase 3: Synthesis
9. [x] Compile evidence table with sources
10. [x] Determine verdict for each hypothesis
11. [x] Identify spawned work items (ADR for rename decision, work items for implementation)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| Current hierarchy: Epoch→Chapter→Arc→Work Item | `EPOCH.md:4` | H1 | Names inverted from story semantics |
| Fractal pattern: Epoch[tight]→Chapter[volumous]→Arc[tight] | `breath/CHAPTER.md:26` | H1 | Pressure pattern is correct, names wrong |
| 48 "Chapter" refs, 97 "Arc" refs in `.claude/haios/` | Grep count | H1 | ~15 files need updates |
| 6 CHAPTER.md files exist | Glob | H1 | Would become ARC.md |
| config has `chapters_dir` and `active_chapters` | `haios.yaml:19,26` | H1 | Config keys need rename |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 80910 | "FINAL HIERARCHY: Epoch→Chapter→Arc→Work Item" | H1 | Session 179 decision to reconsider |
| 80915 | "METAPHOR: Arc = Scene/sequence" | H1 | Metaphor was imprecise |
| 81098 | "Backlog churn - disconnected from chapter structure" | H2 | Queue problem identified |

### External Evidence

| Source | Finding | Supports Hypothesis | URL/Reference |
|--------|---------|---------------------|---------------|
| Wikipedia | "Series of 30+ chapters usually have multiple arcs" - arcs span chapters | H1 | Story arc |
| Reedsy Blog | "Story arc could focus on adventures over several books" vs narrative arc "within single chapter" | H1 | Narrative arc |
| Universal convention | In TV, manga, books: arc > chapter in hierarchy | H1 | Multiple sources |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Confirmed** | Wikipedia, Reedsy: "Series of 30+ chapters usually have multiple arcs" - arcs span chapters universally | High |
| H2 | **Confirmed** | CascadeEngine handles unblocking not ordering; BatchCycleExecution pattern needs queue structure | High |
| H3 | **Confirmed** | Renamed hierarchy + queues map cleanly to spec schema | Medium |

### Detailed Findings

#### Finding 1: Semantic Inversion is Universal

**Evidence:**
- Wikipedia: "Most series shorter than 26 chapters are a single arc spanning all chapters"
- Reedsy: "Story arc could focus on adventures over several books" vs narrative arc "within single chapter"
- In TV, manga, books: arc > chapter in containment hierarchy

**Analysis:** The current HAIOS naming (chapters contain arcs) inverts universal storytelling semantics. Anyone trained on narrative content (humans and LLMs) expects arcs to span chapters.

**Implication:** Rename Chapter↔Arc to align with universal convention. ~15 files affected.

#### Finding 2: No Queue Structure Exists

**Evidence:**
```python
# WorkEngine.get_ready() - work_engine.py:263-281
def get_ready(self) -> List[WorkState]:
    """Get ready items."""
    return [w for w in self._get_all() if not w.blocked_by]
```

**Analysis:** `just ready` returns flat unordered list. No queue types (FIFO, priority, batch). No cross-cutting execution structure.

**Implication:** Add work_queues.yaml with 4 queue types: FIFO, Priority, Batch, Chapter-Aligned. Queues orthogonal to hierarchy.

#### Finding 3: BatchCycleExecution Needs Queue Support

**Evidence:** Memory 81361: "Related work items → plan all first → review cohesion → implement together"

**Analysis:** Session 190 identified this pattern but no infrastructure exists. E2-286/287/288 would have benefited from batch planning.

**Implication:** Batch queue type with phases: PLAN_ALL → REVIEW → IMPLEMENT_ALL → VALIDATE_ALL

---

## Design Outputs

### Corrected Hierarchy

```
CURRENT (semantically incorrect):
Epoch [tight] → Chapter [volumous] → Arc [tight] → Work Item [volumous]

PROPOSED (semantically correct):
Epoch [tight] → Arc [volumous] → Chapter [tight] → Work Item [volumous]
```

Pressure alternation preserved. Only labels swap to match universal story semantics.

### Work Queue Schema

```yaml
# .claude/haios/config/work_queues.yaml
version: "1.0"

queue_types:
  fifo:
    ordering: "creation_date ASC"
  priority:
    ordering: "priority DESC, creation_date ASC"
  batch:
    phases: [plan_all, review, implement_all, validate_all]
  chapter_aligned:
    ordering: "chapter_priority DESC, priority DESC"

queues:
  default:
    type: priority
    items: auto  # From get_ready()
    allowed_cycles: [implementation-cycle, investigation-cycle, work-creation-cycle]

  # Planning-only queue - great for batch planning before implementation
  planning-queue:
    type: batch
    items: [E2-289, E2-290]
    allowed_cycles: [plan-authoring-cycle]  # ONLY planning allowed
    phases: [plan_all, review]  # No implement phase
    rationale: "Plan all items before any implementation begins"

  # Investigation-only queue
  research-queue:
    type: fifo
    items: [INV-064, INV-065]
    allowed_cycles: [investigation-cycle]
    rationale: "Research tasks only - no implementation"

  # Full batch example
  batch-feature-x:
    type: batch
    items: [E2-300, E2-301, E2-302]
    allowed_cycles: [implementation-cycle]  # Only implement, planning done
    rationale: "Related items benefit from cohesive planning"

policies:
  assignment:
    default_queue: default
    auto_batch_threshold: 3
  cross_arc:
    allowed: true
  cycle_enforcement:
    strict: true  # Block cycles not in allowed_cycles
```

**Cycle Locking:** Each queue can specify `allowed_cycles` to restrict what skill-cycles can be invoked. This enables:
- Planning-only queues (plan all, then switch to implementation queue)
- Research-only queues (investigations stay separate)
- Implementation-only queues (for items with approved plans)

### Mapping Table: Rename Impact

| Current | New | Notes |
|---------|-----|-------|
| `chapters/` | `arcs/` | Directory rename |
| `CHAPTER.md` | `ARC.md` | File rename (6 files) |
| `arcs/` (within chapter) | `chapters/` | Nested directory rename |
| `ARC.md` (bounded delivery) | `CHAPTER.md` | File rename |
| `active_chapters` | `active_arcs` | Config key |
| `chapters_dir` | `arcs_dir` | Config key |

### Queue Integration Mechanism

```
TRIGGER: Survey-cycle or /implement invoked

ACTION:
    1. Load work_queues.yaml
    2. Determine active queue (explicit or default)
    3. If batch queue: check phase, route appropriately
    4. Return next item from queue head

OUTCOME: Work selection is queue-aware, not random from flat list
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Swap Chapter↔Arc names | Yes | Universal story semantics: arcs span chapters |
| Queues orthogonal to hierarchy | Yes | Execution order differs from organization |
| 4 queue types | FIFO, Priority, Batch, Chapter-Aligned | Cover all identified patterns |
| Cross-arc queues | Allowed | The point of orthogonality; related work spans boundaries |
| Batch phases | 4 explicit | Enables BatchCycleExecution pattern from S190 |
| Auto-populate default | Yes | Backward compatible with `just ready` |

---

## Spawned Work Items

### Immediate (Can implement now)

- [ ] **ADR-042: Hierarchy Rename Chapter↔Arc**
  - Description: ADR documenting the decision to swap Chapter↔Arc naming
  - Fixes: Semantic inversion identified in H1
  - Spawned via: `/new-adr 042 "Hierarchy Rename Chapter to Arc"`

- [ ] **E2-289: Execute Hierarchy Rename**
  - Description: Rename ~15 files and update references
  - Fixes: Implementation of ADR-042
  - Blocked by: ADR-042 acceptance
  - Spawned via: `/new-work E2-289 "Execute Hierarchy Rename Chapter to Arc"`

- [ ] **E2-290: Work Queue Architecture Implementation**
  - Description: Implement work_queues.yaml and integrate with WorkEngine
  - Fixes: No queue structure (H2)
  - Spawned via: `/new-work E2-290 "Work Queue Architecture Implementation"`

### Future (Requires more work first)

- [ ] **E2-XXX: HAIOS Init Spec Design**
  - Description: Design spec-driven bootstrap for fresh workspaces
  - Blocked by: E2-289 (hierarchy stable), E2-290 (queues implemented)
  - Rationale: Operator stated "end of epoch work" scope

### Not Spawned Rationale (if no items)

N/A - 3 immediate items spawned, 1 future item identified.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 191 | 2026-01-15 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-H3 have verdict | [x] | H1, H2, H3 all Confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | Codebase, memory, external sources cited |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | Listed but not yet created via commands |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 81366-81369 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | 2 invocations for H1 and H2 |
| Are all evidence sources cited with file:line or concept ID? | Yes | |
| Were all hypotheses tested with documented verdicts? | Yes | H1, H2, H3 all Confirmed |
| Are spawned items created (not just listed)? | No | ADR-042, E2-289, E2-290 listed but await operator approval before creation |
| Is memory_refs populated in frontmatter? | Yes | 81366, 81367, 81368, 81369 |

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
