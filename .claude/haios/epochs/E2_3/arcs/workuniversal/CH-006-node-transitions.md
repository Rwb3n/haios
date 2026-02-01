---
id: CH-006
arc: workuniversal
name: NodeTransitionsInvestigation
status: Complete
created: 2026-01-26
completed: 2026-02-01
spawned_from:
- obs-244-01
- obs-230-001
generated: '2026-01-26'
last_updated: '2026-02-01T21:04:35'
---
# Chapter: Node Transitions Investigation

## Purpose

Investigate whether `current_node` and `node_history` fields in work items provide value, or should be removed (YAGNI).

## Context

Multiple observations (obs-244-01, obs-230-001) report that `current_node` stays stuck at `backlog` despite work items completing full lifecycle. The `status` field is authoritative per ADR-041.

## Questions to Answer

1. Are `current_node` and `node_history` used by any code?
2. Do they provide value for debugging/auditing?
3. Should cycles wire transitions, or remove the fields entirely?

## Answers (Session 276)

**Investigations:** WORK-016 + WORK-065 (merged findings)

### Q1: Used by code?

**YES**, but not by cycles:
- GovernanceLayer.VALID_TRANSITIONS defines allowed transitions
- WorkEngine.transition() validates and executes
- Cycles do NOT call these methods → 94% stuck at backlog

### Q2: Provide value?

**NOT CURRENTLY** (because never updated)
**POTENTIALLY YES** if wired for lifecycle tracking and audit trail

### Q3: Wire or remove?

**DECISION: WIRE + REFACTOR**

Add `queue_position` field (backlog/todo/in_progress/done) - separate from cycle phase.
Rename `current_node` to `cycle_phase` and align to GovernanceLayer vocabulary.

**Four-dimensional model (WORK-065):**
1. `status` - Is item alive? (ADR-041)
2. `queue_position` - Where in selection pipeline? (NEW)
3. `cycle_phase` - What cycle phase? (RENAME)
4. `activity_state` - What activities allowed? (E2.4)

## Success Criteria

- [x] INV document with findings (WORK-016, WORK-065)
- [x] Decision: wire transitions OR remove fields → **WIRE + REFACTOR**
- [x] If wire: spawn work item for implementation → **WORK-066**

## References

- @docs/work/active/WORK-016/WORK.md (investigation)
- @docs/work/active/WORK-065/WORK.md (queue position model)
- @docs/work/active/WORK-066/WORK.md (implementation)
- obs-244-01: WORK-015 closure drift
- obs-230-001: CH-005 closure drift
- ADR-041: Status over location
