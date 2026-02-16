# generated: 2026-02-16
# System Auto: last updated on: 2026-02-16T19:00:00
# Arc: Engine Functions

## Definition

**Arc ID:** engine-functions
**Epoch:** E2.7
**Theme:** Functions over file reads — engine query functions and status cascade
**Status:** Active

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
| CH-044 | HierarchyQueryEngine | New (TBD) | REQ-TRACE-005 | None | Planning |
| CH-045 | StatusCascade | WORK-034 | REQ-QUEUE-001 | CH-044 (engine functions needed for cascade) | Complete |

---

## Exit Criteria

- [ ] Engine functions for hierarchy queries exist and are callable (get_arcs, get_chapters, get_work)
- [ ] Status cascades automatically on work/chapter/arc closure
- [ ] No manual path resolution for hierarchy navigation

---

## Notes

- CH-045 depends on CH-044: cascade logic needs engine functions to discover parent hierarchy
- WORK-034 is a carry-forward from E2.3, now properly scoped to composability

---

## References

- @docs/work/active/WORK-034/WORK.md (status propagation)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-005, REQ-QUEUE-001)
