---
template: work_item
id: WORK-105
title: Queue Position Field (CH-007)
type: feature
status: active
owner: Hephaestus
created: 2026-02-05
spawned_by: null
chapter: CH-007
arc: queue
closed: null
priority: medium
effort: medium
traces_to:
- REQ-QUEUE-001
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by:
- WORK-106
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 23:07:02
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-07T15:36:25'
---
# WORK-105: Queue Position Field (CH-007)

---

## Context

Queue position is not tracked as a field in WorkState. The WORK-065 finding identified conflation between lifecycle status and queue selection state. Currently, items exist in named queues via `work_queues.yaml`, but individual work items don't track their own queue position (backlog/ready/working/done) independently from lifecycle phase.

CH-007 requires adding a `queue_position` field to WorkState and WORK.md frontmatter, implementing four-dimensional work tracking (lifecycle, queue, cycle_phase, activity_state) per REQ-QUEUE-001. The terminology uses "working" (not "active") to avoid collision with `status: active`.

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

- [ ] WorkState `queue_position` field expanded to 5 values (parked/backlog/ready/working/done)
- [ ] WORK.md template updated with 5-value comment
- [ ] `in_progress` renamed to `working` in WorkEngine (VALID_POSITIONS, get_in_progress→get_working)
- [ ] `ready` value added and validated
- [ ] `parked` value added and validated
- [ ] Parked items excluded from `get_ready()` and `get_queue()`
- [ ] `queue_position` changes don't affect `cycle_phase` (independence)
- [ ] `cycle_phase` changes don't affect `queue_position` (independence)
- [ ] Forbidden state combinations enforced (complete+working, blocked+working, archived+!done)
- [ ] Migration: existing `in_progress` values renamed to `working` in WORK.md files
- [ ] Unit tests for five-value validation, independence, forbidden combos, parked exclusion

---

## History

### 2026-02-05 - Created (Session 319)
- Initial creation for CH-007 (Queue Position Field)
- Populated from chapter spec: four-dimensional work tracking per REQ-QUEUE-001

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-007-QueuePositionField.md (chapter spec)
- @.claude/haios/epochs/E2_5/arcs/queue/ARC.md (parent arc)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-001)
- @.claude/haios/modules/work_engine.py (WorkState dataclass)
