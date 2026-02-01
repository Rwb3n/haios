---
template: work_item
id: WORK-065
title: Queue Position Model - Backlog/Todo/InProgress/Done Visibility
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: null
chapter: null
arc: workuniversal
closed: '2026-02-01'
priority: high
effort: medium
traces_to:
- REQ-CONTEXT-001
requirement_refs: []
source_files:
- docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
- .claude/haios/modules/governance_layer.py
- scripts/plan_tree.py
acceptance_criteria:
- Queue position model defined (backlog/todo/in_progress/done)
- Relationship to current_node and status fields clarified
- Single in_progress constraint per agent instance specified
- Alignment with E2.4 activity states documented
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 20:05:22
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82952
- 82953
- 82954
- 82958
- 82959
- 82960
- 82961
- 82962
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T20:20:16'
---
# WORK-065: Queue Position Model - Backlog/Todo/InProgress/Done Visibility

---

## Context

**Problem:** Current queue system lacks visibility into work item priority stages.

`just ready` returns ALL unblocked items (32+ items as of Session 275). No distinction between:
- Items identified but not yet prioritized (backlog)
- Items selected for near-term work (todo)
- Items actively being worked (in_progress - should be 1 per agent)
- Items completed (done)

**Proposed Model:**
```
[backlog] → [todo] → [in_progress (1 per instance)] → [done]
```

**Key Constraint:** Only 1 item can be `in_progress` per agent instance. This forces focus and prevents context-switching waste.

**Current State Confusion:**

| Field | TRD Values | GovernanceLayer Values |
|-------|------------|----------------------|
| `current_node` | backlog, planning, in_progress, review, complete | backlog, discovery, plan, implement, close, complete |
| `status` | active, blocked, complete, archived | (same) |

These conflate two orthogonal concerns:
1. **Queue position:** Where is this item in the work selection pipeline?
2. **Cycle phase:** What phase of work is being done on this item?

**E2.4 Relationship:**
- E2.4 activity states (EXPLORE, DESIGN, PLAN, DO, CHECK, DONE) govern WHAT you can do
- Queue position governs WHICH item you're doing
- These are orthogonal - E2.4 doesn't specify queue management

**Questions to Investigate:**
1. Should queue_position be a new field or mapped to existing fields?
2. How does survey-cycle interact with queue position?
3. What enforces the "1 in_progress per instance" constraint?
4. Should this become a new chapter in workuniversal arc?

---

## Deliverables

- [x] **Queue position model spec** - Field definition, allowed values, transitions
- [x] **Relationship diagram** - queue_position vs current_node vs status vs activity_state
- [x] **Enforcement mechanism** - How to ensure 1 in_progress per instance
- [x] **Migration plan** - How to evolve from current TRD without breaking existing items
- [x] **Chapter placement recommendation** - Which arc/chapter this belongs in

---

## History

### 2026-02-01 - Created (Session 275)
- Spawned from E2.4 alignment review discussion
- Operator identified gap in queue visibility
- Linked to workuniversal arc

---

## Investigation (Session 276)

### Evidence Gathered (EXPLORE Phase)

1. **TRD-WORK-ITEM-UNIVERSAL.md** defines `current_node` with values: `backlog|planning|in_progress|review|complete`

2. **GovernanceLayer.VALID_TRANSITIONS** (governance_layer.py:59-68) uses: `backlog|discovery|plan|implement|close|complete`

3. **L5-execution.md manifesto** defines: `backlog → ready → in_progress → blocked → complete`

4. **activity_matrix.yaml phase_to_state** maps cycle phases to 6 E2.4 states: `EXPLORE|DESIGN|PLAN|DO|CHECK|DONE`

5. **Memory search** found observation (obs-230-001) that node transitions are NOT being tracked - items stay at `current_node: backlog` even after completion.

6. **Empirical scan**: 121/128 work items have `current_node: backlog` regardless of actual status.

### Hypotheses (HYPOTHESIZE Phase)

| ID | Hypothesis | Evidence | Test Method | Confidence |
|----|------------|----------|-------------|------------|
| H1 | Queue position and cycle phase are orthogonal concerns requiring separate fields | WORK-065 context; E2.4 states describe WHAT not WHICH | Check if any E2.4 mapping depends on queue position | High |
| H2 | `current_node` conflates three vocabularies that should be unified or distinguished | TRD, GovernanceLayer, L5 all use different values | Grep for all `current_node` usage | High |
| H3 | The "1 in_progress per agent" constraint is not currently enforced | No grep results; WorkEngine.get_ready() returns ALL items | Search for any enforcement code | High |
| H4 | Adding `queue_position` field is preferable to overloading `current_node` | obs-230-001 shows nodes unused | Evaluate migration vs. clarity | Medium |

### Scope

**In Scope:** Queue model design, field relationships, enforcement mechanism, migration path

**Out of Scope:** Implementation, GovernanceLayer changes, E2.4 matrix changes

### Hypothesis Verdicts (VALIDATE Phase)

| ID | Hypothesis | Verdict | Confidence | Evidence |
|----|------------|---------|------------|----------|
| H1 | Queue position and cycle phase are orthogonal | **CONFIRMED** | High | activity_matrix.yaml uses only cycle/phase, never queue position |
| H2 | `current_node` conflates three vocabularies | **CONFIRMED** | High | TRD: 5 values, GovernanceLayer: 6 values, L5: 5 different values |
| H3 | "1 in_progress per agent" is not enforced | **CONFIRMED** | High | Zero enforcement code found; WorkEngine.get_ready() returns ALL items |
| H4 | New `queue_position` field preferable | **CONFIRMED** | Medium | obs-230-001 shows current_node not updated; clean separation |

### Findings (CONCLUDE Phase)

**Four Orthogonal Dimensions of Work Item State:**

```
1. status         : active | blocked | complete | archived
   "Is this item alive?" (ADR-041 authoritative)

2. queue_position : backlog | todo | in_progress | done  (PROPOSED)
   "Where in work selection pipeline?"

3. current_node   : discovery | plan | implement | close | complete
   "What cycle phase?" (should rename to cycle_phase)

4. activity_state : EXPLORE | DESIGN | PLAN | DO | CHECK | DONE  (E2.4)
   "What activities allowed?" (derived from cycle/phase)
```

**Enforcement Mechanism Options:**
1. survey-cycle gate: Check if `queue_position: in_progress` before selection
2. WorkEngine.get_next(): Already returns single item from queue head
3. Session state: Store current in_progress ID in session.yaml

**Migration Path:**
1. Add `queue_position` field to TRD-WORK-ITEM-UNIVERSAL (default: backlog)
2. Rename `current_node` to `cycle_phase` for clarity
3. Wire survey-cycle to set `queue_position: in_progress`
4. Wire close-work-cycle to set `queue_position: done`
5. Add constraint: block survey-cycle if any item has `queue_position: in_progress`

**Chapter Placement:**
- Merge with CH-006 (workuniversal arc) and WORK-016 (Node Transitions Value Assessment)
- No new work items spawned - findings feed into existing investigation

---

## References

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (current work item spec)
- @.claude/haios/modules/governance_layer.py:59-68 (VALID_TRANSITIONS)
- @.claude/haios/epochs/E2_4/arcs/workuniversal/ARC.md
- @.claude/haios/epochs/E2_4/EPOCH.md
- @.claude/haios/epochs/E2_3/observations/obs-230-001.md (node transitions not tracked)
- @.claude/haios/manifesto/L5-execution.md (work DAG definition)
