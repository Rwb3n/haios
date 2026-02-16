# generated: 2026-02-16
# System Auto: last updated on: 2026-02-16T19:00:00
# Arc: Infrastructure

## Definition

**Arc ID:** infrastructure
**Epoch:** E2.7
**Theme:** Clean the house first — bug fixes, epoch transition validation, staleness detection
**Status:** Active

---

## Purpose

Prerequisite quality work before deeper E2.7 design. Fix known bugs from E2.6 triage, validate the epoch transition configuration, and add staleness detection for checkpoint pending items. A clean foundation enables reliable composability work.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-CEREMONY-001 | Ceremonies govern side-effects (commits, state changes) |
| REQ-CEREMONY-002 | Each ceremony has explicit input/output contract |
| REQ-CONFIG-003 | Config follows single-source-of-truth principle |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-049 | BugBatch | WORK-153 | REQ-CEREMONY-001, REQ-CEREMONY-002 | None | Planning |
| CH-050 | EpochTransition | WORK-154 | REQ-CONFIG-003 | None | Planning |
| CH-051 | StalenessDetection | WORK-136 | REQ-CEREMONY-001 | None | Planning |

---

## Exit Criteria

- [ ] All 6 bugs in WORK-153 resolved (ceremony stubs, doc drift, code duplication)
- [ ] Epoch transition validates work_queues.yaml and EPOCH.md status auto-syncs
- [ ] Checkpoint pending items have staleness detection at session start

---

## Notes

- This arc has no dependencies on other E2.7 arcs — can execute in parallel
- WORK-153 is a batch item (6 bugs) — efficient to batch per validated practice (Memory: 84963)
- All items are concrete implementation, no design phase needed

---

## References

- @docs/work/active/WORK-153/WORK.md (bug batch)
- @docs/work/active/WORK-154/WORK.md (epoch transition)
- @docs/work/active/WORK-136/WORK.md (staleness detection)
- Memory: 85605 (ceremony overhead), 85609 (session boundary gap)
