---
template: work_item
id: WORK-039
title: Scaffold CH-001 ActivityMatrix
type: design
status: complete
owner: Hephaestus
created: 2026-01-30
spawned_by: null
chapter: activities/CH-001
arc: activities
closed: '2026-01-30'
priority: medium
effort: medium
traces_to:
- REQ-ACTIVITY-001
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 21:50:28
  exited: null
artifacts:
- .claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md
cycle_docs: {}
memory_refs:
- 82745
- 82746
- 82747
- 82748
- 82749
- 82750
- 82751
- 82752
- 82753
- 82754
- 82755
- 82756
- 82757
- 82758
- 82759
- 82760
- 82761
- 82762
- 82763
- 82764
- 82765
- 82766
- 82767
- 82768
- 82773
- 82774
- 82775
- 82776
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-01-30T22:34:00'
---
# WORK-039: Scaffold CH-001 ActivityMatrix

---

## Context

E2.4 introduces the governed activities paradigm: Governed Activity = Primitive × State × Governance Rules (Decision 82706).

The Activities arc needs a CH-001 ActivityMatrix chapter file to define the full matrix of:
- Primitives (explore-read, explore-search, spec-write, artifact-write, etc.)
- States (EXPLORE, DESIGN, PLAN, DO, CHECK, DONE)
- Governance rules per intersection (blocked vs allowed)

This chapter is foundational - it defines WHAT governed activities exist before implementation can begin.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] Chapter file scaffolded: `.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md`
- [x] Chapter has Problem section defining the design question
- [x] Chapter has Activity Matrix table (Primitive × State × Rule) - Full enumeration: 17 primitives × 6 states
- [x] Chapter lists governed activities from Session 265 (Governed Activity Names table)
- [x] Chapter has Memory Refs section linking to Session 265 decisions (82706-82710)

---

## History

### 2026-01-30 - Created (Session 265)
- Bulk spawned as part of E2.4 ChapterFlow (CH-006 pattern)

### 2026-01-30 - Populated (Session 266)
- Context, deliverables, traces_to populated via work-creation-cycle

### 2026-01-30 - Implemented (Session 266)
- Exploration: Queried memory 82706-82710, reviewed PreToolUse hook, enumerated Claude Code primitives
- Created CH-001-ActivityMatrix.md with full matrix enumeration (17 primitives × 6 states)
- Defined primitive taxonomy (6 categories), state definitions, DO phase restrictions
- Added governed activity names table and path classification for write operations

### 2026-01-30 - Critique & Revise (Session 266)
- Invoked critique-agent on CH-001-ActivityMatrix.md
- Verdict: REVISE (2 blocking assumptions)
- Addressed A3 (phase-to-state mapping): Added mapping tables for 5 existing cycles
- Addressed A6 (redirect behavior): Added redirect section with deny messages and skill restrictions
- Also addressed A1 (state detection), A2 (path fallback), Module-First gap
- Chapter revised with all Exit Criteria complete

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/epochs/E2_4/EPOCH.md (epoch context)
- Memory refs: 82706-82710 (Session 265 governed activities decision)
