---
template: work_item
id: WORK-055
title: Multi-Level Governance - Decomposition Leakage Pattern
type: investigation
status: complete
owner: null
created: 2026-01-31
spawned_by: obs-268-1
chapter: null
arc: null
closed: '2026-02-01'
priority: high
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-31 18:07:09
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83018
- 83019
- 83020
- 83021
- 83022
- 83023
- 83024
- 83025
- 83026
- 83027
- 83028
- 83029
- 83030
- 83031
- 83032
- 83033
- 83034
- 83035
- 83036
- 83037
- 83038
- 83039
- 83040
- 83041
- 83042
- 83043
- 83044
- 83045
- 83046
- 83047
- 83048
extensions: {}
version: '2.0'
generated: 2026-01-31
last_updated: '2026-02-01T23:06:55'
---
# WORK-055: Multi-Level Governance - Decomposition Leakage Pattern

---

## Context

Spawned from observation `obs-268-1` during WORK-040 closure review.

**Problem:** We have governance for leaf nodes (work items) but not branch nodes (chapters, arcs, epochs). Decomposition happens without verification that the decomposition is complete.

**Symptoms:**
1. Epoch decisions don't trace to chapters - decisions can fall through cracks
2. No batch critique at arc level - only per-plan critique exists
3. DoD only at work item level - no Chapter/Arc/Epoch DoD
4. No pre-scaffold review - chapters worked independently without completeness check

**Example:** E2.4 Decision 4 (Critique as Hard Gate) wasn't explicitly assigned to CH-002 or CH-003. It could be missed.

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

- [x] **Gap Analysis** - Document where multi-level governance is missing
- [x] **Traceability Design** - How epoch decisions trace to chapters
- [x] **Batch Critique Pattern** - Arc-level critique before chapter work
- [x] **Multi-Level DoD** - DoD cascade: Work → Chapter → Arc → Epoch
- [x] **Pre-Decomposition Gate** - Review decomposition completeness before work begins
- [x] **Findings Document** - Investigation conclusions with recommendations

---

## Investigation Findings (Session 279)

### Gap Analysis

Three governance gaps identified at branch nodes (chapters, arcs, epochs):

| Gap | Description | Evidence |
|-----|-------------|----------|
| **Decision-to-Chapter** | Epoch decisions have no `assigned_to` field linking to chapters | EPOCH.md decisions are prose only |
| **Traceability** | REQ-TRACE-005 traces hierarchy but not decision coverage | Decisions are orphaned from traceability chain |
| **DoD** | DoD exists only at work item level (ADR-033) | No Chapter/Arc/Epoch DoD |

### Recommended Patterns

**Pattern 1: Decision Traceability Schema**
- Add to EPOCH.md: `decisions[].assigned_to: [{arc, chapters}]`
- Add to chapter files: `implements_decisions: [D1, D3]`

**Pattern 2: Multi-Level DoD Cascade**
| Level | DoD Criteria |
|-------|--------------|
| Work Item | Tests pass, runtime consumer, WHY captured |
| Chapter | All work complete + exit criteria + implements_decisions verified |
| Arc | All chapters complete + no unassigned epoch decisions |
| Epoch | All arcs complete + all decisions implemented |

**Pattern 3: Pre-Decomposition Review Gate**
- When decomposing arc → chapters, require critique verifying:
  - All epoch decisions for arc have chapter assignment
  - Sum of chapter scopes covers arc theme

**Pattern 4: New Requirements**
- REQ-TRACE-006: Decisions MUST have chapter assignment before work begins
- REQ-DOD-001: Chapter closure verifies decision implementation
- REQ-DOD-002: Arc closure verifies no orphan decisions

### Spawned Work Items

| ID | Type | Title |
|----|------|-------|
| WORK-069 | design | Decision Traceability Schema Design |
| WORK-070 | design | Multi-Level DoD Cascade Design |
| WORK-071 | design | Pre-Decomposition Review Gate Design |

---

## History

### 2026-02-01 - Completed (Session 279)
- EXPLORE: Gathered evidence from EPOCH.md, chapter files, functional_requirements.md, obs-268-1.md
- HYPOTHESIZE: Formed 4 hypotheses about decomposition leakage causes
- VALIDATE: All 4 hypotheses CONFIRMED (high/medium confidence)
- CONCLUDE: Documented 4 patterns, spawned 3 design work items
- Memory refs: 83018-83029

### 2026-01-31 - Created (Session 268)
- Spawned from obs-268-1
- Operator identified decomposition leakage risk during WORK-040 review

---

## References

- @.claude/haios/epochs/E2_4/observations/obs-268-1.md (source observation)
- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 4 - example of untraced decision)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (chapter decomposition)
