---
template: work_item
id: WORK-086
title: Implement Batch Mode (CH-003)
type: feature
status: active
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-003-BatchMode
arc: lifecycles
closed: null
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
blocked_by:
- WORK-084
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 19:30:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
  implementation_type: CREATE_NEW
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T19:42:49'
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

- [ ] Implement WorkEngine.get_in_lifecycle(lifecycle, phase=None) -> List[WorkState]
- [ ] Implement WorkEngine.count_active_in_lifecycle(lifecycle) -> int
- [ ] Implement CycleRunner.run_batch(work_ids, lifecycle, until_phase=None) -> Dict[str, LifecycleOutput]
- [ ] Unit tests: 3 items in design phase concurrently
- [ ] Integration test: Batch design 3 features -> all complete with specs -> then batch implement

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-003-BatchMode
- Depends on WORK-084 for lifecycle signatures

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-003-BatchMode.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-003)
