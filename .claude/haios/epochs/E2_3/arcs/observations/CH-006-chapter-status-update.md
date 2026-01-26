---
id: CH-006
arc: observations
name: ChapterStatusOnClosure
status: Active
created: 2026-01-26
spawned_from:
- obs-244-02
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:18'
---
# Chapter: Chapter Status Update on Work Closure

## Purpose

Update chapter file status when all its work items are complete.

## Context

obs-244-02 documented that CH-002's status stayed "Active" after WORK-015 completed all its success criteria. Chapter status diverges from actual completion state.

## Deliverables

1. Add chapter-status-check step to close-work-cycle
2. If work item has `chapter` field, check if all chapter work items are complete
3. If all complete, update chapter status to "Complete"

## Success Criteria

- [ ] close-work-cycle checks chapter status
- [ ] Chapter file updated when work completes

## References

- obs-244-02: Chapter file not updated on closure
- close-work-cycle skill
