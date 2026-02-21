---
template: work_item
id: WORK-181
title: Investigate Test Failure Root Causes
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-21
spawned_by: null
spawned_children:
- WORK-183
chapter: CH-065
arc: infrastructure
closed: '2026-02-21'
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- tests/test_coldstart_orchestrator.py
acceptance_criteria:
- Root cause identified for each pre-existing test failure category
- 'Each failure classified: deprecated code, environment-dependent, validator logic
  bug, or genuine regression'
- Findings documented with file paths and line numbers
- Spawned work items for actionable fixes (if any)
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-21 08:16:37
  exited: '2026-02-21T23:58:13.101323'
artifacts: []
cycle_docs: {}
memory_refs:
- 85721
- 85369
- 84816
- 87259
- 87260
- 87291
- 87292
- 87293
- 87294
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-21
last_updated: '2026-02-21T23:58:13.104337'
queue_history:
- position: ready
  entered: '2026-02-21T23:45:59.417815'
  exited: '2026-02-21T23:45:59.445757'
- position: working
  entered: '2026-02-21T23:45:59.445757'
  exited: '2026-02-21T23:58:13.101323'
- position: done
  entered: '2026-02-21T23:58:13.101323'
  exited: null
---
# WORK-181: Investigate Test Failure Root Causes

---

## Context

Pre-existing test failures have accumulated across epochs. As of S414, the test suite shows 1 known failure in WORK-180 scope (`test_breathe_markers_between_phases`) and MEMORY.md documents 9 pre-existing failure categories (19 total). Memory 85369 notes "16 pre-existing test failures stable but unfixed — technical debt accumulating." Memory 84816 directs "Pre-existing test failures should be periodically re-triaged, not just accepted."

**The question:** Are these failures from deprecated/retired code, environment-dependent conditions (orphan detection firing on real disk state), validator logic bugs, or genuine regressions? The answer determines whether to fix, retire, or mark them as known-environment-dependent.

**Specific known failure:** `test_breathe_markers_between_phases` (mem:85721) — expects 1 `[BREATHE]` marker but gets 2-3 because RECOVERY phase (orphan detection) and VALIDATION phase add extra markers. The test doesn't mock `_check_for_orphans()`.

**Related prior work:** mem:85721, 85369, 84816, 85025, 85407

---

## Deliverables

- [ ] Full pytest run with failure categorization (deprecated, env-dependent, logic bug, regression)
- [ ] Root cause analysis for each failure category
- [ ] Spawned fix/retire work items for actionable findings

---

## History

### 2026-02-21 - Created (Session 414)
- Spawned during WORK-180 closure. `test_breathe_markers_between_phases` failure surfaced the broader question of pre-existing test debt.
- Memory search found 10 related entries spanning E2.5-E2.8.

### 2026-02-21 - Investigation Complete (Session 417)
- Full pytest: 1565 passed, 13 failed, 4 skipped
- All 13 failures classified: 3 stale assertions, 6 deprecated functionality, 4 environment-dependent
- Zero genuine regressions found
- Spawned WORK-183 to fix all 13

---

## References

- @tests/test_coldstart_orchestrator.py (breathe marker test)
- Memory: 85721, 85369, 84816, 87259, 87260
- WORK-183: Spawned fix work
