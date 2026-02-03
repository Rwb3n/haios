# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:00:52
# Arc: Queue

## Definition

**Arc ID:** queue
**Epoch:** E2.5
**Theme:** Implement orthogonal queue tracking
**Status:** Planned

---

## Purpose

Implement queue as separate state machine from lifecycle per REQ-QUEUE-001 to 004.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-QUEUE-001 | Queue position orthogonal to lifecycle phase |
| REQ-QUEUE-002 | "Complete without spawn" is valid terminal state |
| REQ-QUEUE-003 | Queue has own lifecycle (backlog→ready→active→done) |
| REQ-QUEUE-004 | Queue ceremonies govern transitions |

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

- [ ] queue_position field tracked independently
- [ ] Queue ceremonies (Intake, Prioritize, Commit, Release) implemented
- [ ] Work item can be queue:done + status:complete without spawn
- [ ] WorkEngine.get_queue() respects queue_position
