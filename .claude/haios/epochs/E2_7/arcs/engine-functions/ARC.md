---
id: engine-functions
epoch: E2.7
theme: Functions over file reads — engine query functions and status cascade
status: Complete
completed: 2026-02-17 (Session 393)
chapters:
- id: CH-044
  title: HierarchyQueryEngine
  work_items:
  - WORK-157
  requirements:
  - REQ-TRACE-005
  dependencies: []
  status: Complete
- id: CH-045
  title: StatusCascade
  work_items:
  - WORK-034
  requirements:
  - REQ-QUEUE-001
  dependencies:
  - CH-044 (engine functions needed for cascade)
  status: Complete
exit_criteria:
- text: Engine functions for hierarchy queries exist and are callable (get_arcs, get_chapters,
    get_work)
  checked: true
- text: Status cascades automatically on work/chapter/arc closure
  checked: true
- text: No manual path resolution for hierarchy navigation
  checked: true
---
# generated: 2026-02-16
# System Auto: last updated on: 2026-02-16T19:00:00
# Arc: Engine Functions

## Definition

**Arc ID:** engine-functions
**Epoch:** E2.7
**Theme:** Functions over file reads — engine query functions and status cascade
**Status:** Complete
**Completed:** 2026-02-17 (Session 393)

---

## Purpose

Replace manual path resolution and file reads with engine functions. Work items, arcs, chapters, and epoch hierarchy should be queryable via `get_arcs()`, `get_chapters()`, `get_work()`. Status changes cascade automatically on closure instead of requiring manual propagation.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-TRACE-005 | Full traceability chain L4 -> Epoch -> Arc -> Chapter -> Work |
| REQ-QUEUE-001 | Queue position is orthogonal to lifecycle phase |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-044 | HierarchyQueryEngine | WORK-157 | REQ-TRACE-005 | None | Complete |
| CH-045 | StatusCascade | WORK-034 | REQ-QUEUE-001 | CH-044 (engine functions needed for cascade) | Complete |

---

## Exit Criteria

- [x] Engine functions for hierarchy queries exist and are callable (get_arcs, get_chapters, get_work)
- [x] Status cascades automatically on work/chapter/arc closure
- [x] No manual path resolution for hierarchy navigation

---

## Notes

- CH-045 depends on CH-044: cascade logic needs engine functions to discover parent hierarchy
- WORK-034 is a carry-forward from E2.3, now properly scoped to composability

---

## References

- @docs/work/active/WORK-034/WORK.md (status propagation)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-005, REQ-QUEUE-001)
