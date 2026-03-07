---
id: infrastructure
epoch: E2.8
theme: Fix what's broken
status: Planning
started: 2026-02-17 (Session 393)
chapters:
- id: CH-065
  title: BugBatch-E28
  work_items:
  - New
  requirements:
  - REQ-CEREMONY-001
  dependencies: []
  status: Complete
- id: CH-067
  title: FileFormatMigration
  work_items:
  - WORK-244
  - WORK-245
  - WORK-254
  - WORK-256
  - WORK-257
  - WORK-260
  - WORK-264
  - WORK-265
  - WORK-268
  - WORK-269
  - WORK-272
  - WORK-276
  - WORK-277
  requirements:
  - REQ-TRACE-004
  dependencies: []
  status: Active
exit_criteria:
- text: All confirmed bugs from E2.7 triage resolved (WORK-166, S395)
  checked: true
---
# generated: 2026-02-17
# System Auto: last updated on: 2026-02-17T21:00:00
# Arc: Infrastructure

## Definition

**Arc ID:** infrastructure
**Epoch:** E2.8
**Theme:** Fix what's broken
**Status:** Planning
**Started:** 2026-02-17 (Session 393)

---

## Purpose

Bug fixes and deferred items from E2.7 triage. Clean foundation for the UX arcs. The batch bug pattern (mem:84963) is validated — grouping 4+ small fixes in one session is efficient.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-CEREMONY-001 | Ceremonies are side-effect boundaries |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-065 | BugBatch-E28 | New | REQ-CEREMONY-001 | None | Complete |
| CH-067 | FileFormatMigration | WORK-244, WORK-245, WORK-254, WORK-256, WORK-257, WORK-260, WORK-264, WORK-265, WORK-268, WORK-269, WORK-272, WORK-276, WORK-277 | REQ-TRACE-004 | None | Active |

---

## Exit Criteria

- [x] All confirmed bugs from E2.7 triage resolved (WORK-166, S395)

---

## Known Bugs

From E2.7 triage (memory IDs) and S393 operator report:

| Bug | Source | Description |
|-----|--------|-------------|
| Checkpoint same-session sort | S393 operator | session_loader.py:120 — max(checkpoints, key=_session_number) doesn't break ties when multiple checkpoints share a session number. Need sequence number from filename. |
| Queue state machine gap | S393 operator | No backlog -> done transition path for admin cleanup |
| mem:85712 | E2.7 triage | TBD — needs verification |
| mem:85557 | E2.7 triage | TBD — needs verification |
| mem:85795 | E2.7 triage | TBD — needs verification |
| mem:85573 | E2.7 triage | TBD — needs verification |
| mem:85132 | E2.7 triage | TBD — needs verification |

---

## Notes

- Batch pattern validated (mem:84963): grouping small fixes is efficient
- Memory-referenced bugs need verification — query those IDs before implementing fixes
- This arc has no dependencies and can run in parallel with the UX arcs

---

## References

- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- Memory: 84963 (batch pattern), 85712, 85557, 85795, 85573, 85132 (E2.7 triage bugs)
