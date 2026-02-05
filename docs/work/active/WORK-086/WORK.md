---
template: work_item
id: WORK-086
title: Implement Batch Mode (CH-003)
type: feature
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-003-BatchMode
arc: lifecycles
closed: '2026-02-05'
priority: medium
effort: medium
traces_to:
- REQ-LIFECYCLE-003
requirement_refs: []
source_files:
- .claude/haios/modules/cycle_runner.py
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- Multiple items can be in design lifecycle simultaneously
- WorkEngine.get_in_lifecycle() returns multiple items
- CycleRunner.run_batch() processes multiple items
- No governance errors for batch design
blocked_by: []
blocks: []
enables: []
current_node: active
node_history:
- node: backlog
  entered: 2026-02-03 19:30:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84017
- 84018
- 84019
- 84020
- 84021
extensions:
  epoch: E2.5
  implementation_type: CREATE_NEW
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-05T22:15:08.370996'
queue_position: backlog
cycle_phase: active
---
# WORK-086: Implement Batch Mode (CH-003)

---

## Context

No explicit single-item constraint exists, but also no support for intentional batch operations. Batch design (design A, B, C before implementing) requires new methods.

**What exists:**
- Multiple work items can have `status: active` simultaneously (no enforcement)
- work_queues.yaml has `batch` queue type (for queue grouping, not lifecycle batching)

**What doesn't exist:**
- `CycleRunner.run_batch()` method
- `WorkEngine.get_in_lifecycle()` method
- `WorkEngine.count_active_in_lifecycle()` method

---

## Deliverables

- [x] Implement WorkEngine.get_in_lifecycle(lifecycle, phase=None) -> List[WorkState]
- [x] Implement WorkEngine.count_active_in_lifecycle(lifecycle) -> int
- [x] Implement CycleRunner.run_batch(work_ids, lifecycle, until_phase=None) -> Dict[str, LifecycleOutput]
- [x] Extract TYPE_TO_LIFECYCLE module-level constant, refactor is_at_pause_point
- [x] Unit tests: T1-T9 (WorkEngine), T10-T18 (CycleRunner) — 18 tests pass
- [x] Integration test: T19 batch design 3 items — passes

---

## History

### 2026-02-05 - Implemented (Session 317)
- Extracted TYPE_TO_LIFECYCLE constant (work_engine.py:131-141)
- Implemented get_in_lifecycle() and count_active_in_lifecycle() (work_engine.py:685-740)
- Implemented run_batch() with per-item error handling (cycle_runner.py:444-496)
- 19 tests (T1-T19), all passing. Full suite: 86 pass, 0 fail.
- TDD methodology: red-green on first pass for all tests.

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-003-BatchMode
- Depends on WORK-084 for lifecycle signatures

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-003-BatchMode.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-003)
