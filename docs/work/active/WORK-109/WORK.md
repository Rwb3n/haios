---
template: work_item
id: WORK-109
title: Queue Lifecycle State Machine (CH-009)
type: implementation
status: active
owner: Hephaestus
created: 2026-02-09
spawned_by: null
chapter: CH-009
arc: queue
closed: null
priority: high
effort: medium
traces_to:
- REQ-QUEUE-003
- REQ-QUEUE-005
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_5/arcs/queue/CH-009-QueueLifecycle.md
- .claude/haios/modules/work_engine.py
- .claude/haios/modules/governance_layer.py
acceptance_criteria:
- AC1: QUEUE_TRANSITIONS state machine defines 5 phases (parked/backlog/ready/working/done)
- AC2: is_valid_queue_transition() enforces valid transitions only
- AC3: validate_queue_transition() integrated in governance layer
- AC4: get_parked(), get_backlog(), get_ready(), get_working() query methods work
- AC5: Invalid transitions blocked (parked->ready, parked->working, done->working)
- AC6: Valid rollback (ready->backlog) works
- AC7: Park/Unpark (backlog<->parked) works
- AC8: Unit tests for all valid transitions
- AC9: Unit tests for blocked invalid transitions
blocked_by: []
blocks: []
enables:
- CH-010
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-09 00:27:58
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84054
- 84055
extensions: {}
version: '2.0'
generated: 2026-02-09
last_updated: '2026-02-09T00:29:17'
---
# WORK-109: Queue Lifecycle State Machine (CH-009)

---

## Context

CH-009 requires implementing the queue lifecycle as a formal state machine with 5 phases and governed transitions. Currently `queue_position` exists as a field (CH-007/WORK-105) with 5 canonical values, but no transition validation exists. Items can jump between any queue positions without governance enforcement.

**Root Cause:** WORK-066 and WORK-105 added the `queue_position` field and expanded to 5 values (parked/backlog/ready/working/done), but transition rules were explicitly deferred to CH-009.

**What exists (verified):**
- `queue_position` field with 5 values in work items
- `VALID_QUEUE_POSITIONS` constant in `work_engine.py`
- `_validate_state_combination()` catch-all in write path
- `get_working()`, `get_ready()`, `get_queue()` query methods
- `get_backlog()` method (returns items at backlog position)

**What doesn't exist (memory 84054, 84055):**
- `QUEUE_TRANSITIONS` state machine defining valid transitions
- `is_valid_queue_transition()` function
- `validate_queue_transition()` in governance layer
- `get_parked()` query method
- `get_by_queue_position()` generic query method

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

- [ ] `QUEUE_TRANSITIONS` dict defining valid state transitions (6 valid paths)
- [ ] `is_valid_queue_transition(from_pos, to_pos)` function
- [ ] `validate_queue_transition()` in governance layer returning GateResult
- [ ] `get_parked()` query method in WorkEngine
- [ ] `get_by_queue_position(position)` generic query method in WorkEngine
- [ ] Unit tests for all 6 valid transitions (parked->backlog, backlog->ready, backlog->parked, ready->working, ready->backlog, working->done)
- [ ] Unit tests for invalid transitions (parked->ready, parked->working, backlog->working, done->working, working->backlog)
- [ ] Integration with existing `set_queue_position()` write path

---

## History

### 2026-02-09 - Created (Session 326)
- Triaged from CH-009 spec + observations (84054, 84055)
- Severity-as-confidence-gate (84091) parked for post-CH-009 enhancement

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-009-QueueLifecycle.md (chapter spec)
- @.claude/haios/epochs/E2_5/arcs/queue/CH-007-QueuePositionField.md (foundation)
- @docs/work/active/WORK-105/WORK.md (queue_position field implementation)
- @docs/work/active/WORK-066/WORK.md (original queue position work)
- @docs/work/active/WORK-106/WORK.md (design alignment review)
