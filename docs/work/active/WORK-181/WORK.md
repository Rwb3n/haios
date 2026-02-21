---
template: work_item
id: WORK-181
title: "Investigate Test Failure Root Causes"
type: investigation
status: active
owner: Hephaestus
created: 2026-02-21
spawned_by: null
spawned_children: []
chapter: CH-065
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to:
  - REQ-CEREMONY-001
requirement_refs: []
source_files:
  - tests/test_coldstart_orchestrator.py
acceptance_criteria:
  - "Root cause identified for each pre-existing test failure category"
  - "Each failure classified: deprecated code, environment-dependent, validator logic bug, or genuine regression"
  - "Findings documented with file paths and line numbers"
  - "Spawned work items for actionable fixes (if any)"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-21T08:16:37
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 85721
  - 85369
  - 84816
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-21
last_updated: 2026-02-21T08:18:00
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

---

## References

- @tests/test_coldstart_orchestrator.py (breathe marker test)
- Memory: 85721 (breathe test root cause), 85369 (16 pre-existing failures), 84816 (re-triage directive)
- MEMORY.md "Pre-existing failures (19)" section
