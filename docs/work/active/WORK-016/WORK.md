---
template: work_item
id: WORK-016
title: Node Transitions Value Assessment
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-26
spawned_by: obs-244-01
chapter: CH-006
arc: workuniversal
closed: '2026-02-01'
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files:
- docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
- .claude/haios/modules/governance_layer.py
- .claude/haios/modules/work_engine.py
- .claude/haios/manifesto/L5-execution.md
acceptance_criteria:
- Determine if current_node and node_history provide value
- Decision documented (wire transitions OR remove fields)
- If wire, spawn implementation work item
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 19:31:32
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82952
- 82953
- 82954
- 82963
- 82964
- 82965
- 82966
- 82967
- 82968
- 82969
- 82970
- 82971
- 82972
- 82973
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-02-01T20:56:12'
---
# WORK-016: Node Transitions Value Assessment

@docs/work/active/WORK-065/WORK.md
@.claude/haios/epochs/E2_3/arcs/workuniversal/CH-006-node-transitions.md
@.claude/haios/epochs/E2_3/observations/obs-230-001.md

---

## Context

**Problem:** Multiple observations (obs-244-01, obs-230-001) report that `current_node` stays stuck at `backlog` despite work items completing full lifecycle.

**CH-006 Questions:**
1. Are `current_node` and `node_history` used by any code?
2. Do they provide value for debugging/auditing?
3. Should cycles wire transitions, or remove the fields entirely?

---

## Deliverables

- [x] Determine if current_node and node_history provide value
- [x] Decision documented (wire transitions OR remove fields)
- [x] If wire, spawn implementation work item

---

## Investigation (Session 276)

### Findings from WORK-065 (Queue Position Model)

WORK-065 investigated the broader context of work item state management and answered all CH-006 questions.

### Q1: Are `current_node` and `node_history` used by any code?

**YES**, but not by cycles:

| Component | Uses current_node? | Details |
|-----------|-------------------|---------|
| GovernanceLayer.VALID_TRANSITIONS | Yes | Defines allowed transitions (governance_layer.py:61-68) |
| WorkEngine.transition() | Yes | Validates and executes transitions (work_engine.py:285-323) |
| Cycle skills | **NO** | No cycle calls WorkEngine.transition() |
| Close-work-cycle | **NO** | Only updates `status`, not `current_node` |

**Evidence:** 121/128 work items (94%) have `current_node: backlog` regardless of actual status.

### Q2: Do they provide value for debugging/auditing?

**NOT CURRENTLY** - because they're never updated.

**POTENTIALLY YES** - if properly wired:
- `node_history` with timestamps would show lifecycle progression
- Useful for performance analysis (time-in-phase)
- Enables audit trail for governance compliance

### Q3: Should cycles wire transitions, or remove the fields entirely?

**DECISION: WIRE TRANSITIONS + REFACTOR**

WORK-065 revealed a deeper issue: `current_node` conflates two orthogonal concerns:

1. **Queue position:** Where in work selection pipeline (backlog/todo/in_progress/done)
2. **Cycle phase:** What phase of work cycle (discovery/plan/implement/close)

**Recommended architecture (from WORK-065):**

```
┌─────────────────────────────────────────────────────────────────┐
│  Four Orthogonal Dimensions of Work Item State                  │
├─────────────────────────────────────────────────────────────────┤
│  1. status         │ active | blocked | complete | archived     │
│     (ADR-041)      │ "Is this item alive?"                      │
├────────────────────┼────────────────────────────────────────────┤
│  2. queue_position │ backlog | todo | in_progress | done        │
│     (NEW FIELD)    │ "Where in work selection pipeline?"        │
├────────────────────┼────────────────────────────────────────────┤
│  3. cycle_phase    │ discovery | plan | implement | close       │
│     (RENAME)       │ "What phase of the cycle?"                 │
├────────────────────┼────────────────────────────────────────────┤
│  4. activity_state │ EXPLORE | DESIGN | PLAN | DO | CHECK | DONE│
│     (E2.4)         │ "What activities are allowed?"             │
└────────────────────┴────────────────────────────────────────────┘
```

### Implementation Plan

**Phase 1: Add queue_position field**
- Add to TRD-WORK-ITEM-UNIVERSAL
- Default: `backlog`
- Wire survey-cycle to set `in_progress` on selection
- Wire close-work-cycle to set `done` on closure

**Phase 2: Rename current_node to cycle_phase**
- Update TRD, GovernanceLayer, WorkEngine
- Align vocabulary: use GovernanceLayer values (discovery/plan/implement/close/complete)
- Wire cycles to call WorkEngine.transition()

**Phase 3: Enforce single in_progress constraint**
- survey-cycle gate: block if any item has `queue_position: in_progress`
- Forces focus, prevents context-switching waste

---

## Decision

**WIRE TRANSITIONS + REFACTOR per WORK-065 four-dimensional model.**

Spawned work items:
- **WORK-066** (to be created): Implement queue_position field and wire cycles

---

## History

### 2026-01-26 - Created (Session 244)
- Initial creation from obs-244-01

### 2026-02-01 - Completed (Session 276)
- Merged findings from WORK-065 (Queue Position Model investigation)
- Decision: WIRE + REFACTOR using four-dimensional model
- Answered all CH-006 questions

---

## References

- @docs/work/active/WORK-065/WORK.md (comprehensive investigation)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (current spec)
- @.claude/haios/modules/governance_layer.py:59-68 (VALID_TRANSITIONS)
- @.claude/haios/epochs/E2_3/arcs/workuniversal/CH-006-node-transitions.md
- @.claude/haios/epochs/E2_3/observations/obs-230-001.md
- @.claude/haios/epochs/E2_4/observations/obs-276-01.md
