---
id: queue
epoch: E2.5
theme: Implement orthogonal queue tracking
status: Complete
completed: 2026-02-09 (Session 331)
chapters:
- id: CH-007
  title: QueuePositionField
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-QUEUE-001
- id: CH-008
  title: CompleteWithoutSpawn
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-QUEUE-002
- id: CH-009
  title: QueueLifecycle
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-QUEUE-003
- id: CH-010
  title: QueueCeremonies
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-QUEUE-004
exit_criteria:
- text: queue_position field tracked independently with 5 states (parked/backlog/ready/working/done)
  checked: true
- text: Queue ceremonies (Unpark, Intake, Prioritize, Commit, Release) implemented
  checked: true
- text: Work item can be queue:done + status:complete without spawn
  checked: true
- text: WorkEngine.get_queue() respects queue_position
  checked: true
- text: Parked items excluded from survey-cycle and `just ready`
  checked: true
- text: Parked vs blocked distinction enforced (parked = scope, blocked = dependency)
  checked: true
---
# generated: 2026-02-03
# System Auto: last updated on: 2026-02-07T15:36:07
# Arc: Queue

## Definition

**Arc ID:** queue
**Epoch:** E2.5
**Theme:** Implement orthogonal queue tracking
**Status:** Complete
**Completed:** 2026-02-09 (Session 331)

---

## Purpose

Implement queue as separate state machine from lifecycle per REQ-QUEUE-001 to 004.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-QUEUE-001 | Queue position orthogonal to lifecycle phase |
| REQ-QUEUE-002 | "Complete without spawn" is valid terminal state |
| REQ-QUEUE-003 | Queue has own lifecycle (parked→backlog→ready→active→done) |
| REQ-QUEUE-004 | Queue ceremonies govern transitions |
| REQ-QUEUE-005 | Parked items excluded from current epoch scope (Session 314) |

---

## Chapters

| CH-ID | Title | Requirements | Dependencies |
|-------|-------|--------------|--------------|
| CH-007 | QueuePositionField | REQ-QUEUE-001 | None |
| CH-008 | CompleteWithoutSpawn | REQ-QUEUE-002 | CH-007, Lifecycles:CH-004 |
| CH-009 | QueueLifecycle | REQ-QUEUE-003 | CH-007 |
| CH-010 | QueueCeremonies | REQ-QUEUE-004 | CH-009 |

---

## Exit Criteria

- [x] queue_position field tracked independently with 5 states (parked/backlog/ready/working/done)
- [x] Queue ceremonies (Unpark, Intake, Prioritize, Commit, Release) implemented
- [x] Work item can be queue:done + status:complete without spawn
- [x] WorkEngine.get_queue() respects queue_position
- [x] Parked items excluded from survey-cycle and `just ready`
- [x] Parked vs blocked distinction enforced (parked = scope, blocked = dependency)
