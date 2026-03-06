---
template: work_item
id: WORK-239
title: Implement Exit Criteria Gate in StatusPropagator
type: implementation
status: complete
owner: Hephaestus
created: '2026-03-06'
spawned_by: WORK-222
spawned_children: []
chapter: CH-066
arc: call
closed: '2026-03-06'
priority: medium
effort: small
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/lib/status_propagator.py
- tests/test_status_propagator.py
acceptance_criteria:
- is_chapter_complete() checks both work item statuses AND exit criteria checkboxes
  from CHAPTER.md
- 'New _check_exit_criteria() method parses ## Exit Criteria section from CHAPTER.md'
- 'Graceful degradation: returns True (count-only) when CHAPTER.md or exit criteria
  section missing'
- New action 'chapter_criteria_unmet' returned when all work items done but exit criteria
  unchecked
- 'Tests cover: all criteria checked, some unchecked, no CHAPTER.md, no exit criteria
  section'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-06T22:09:18.890077'
  exited: '2026-03-06T22:23:02.668053'
queue_history:
- position: backlog
  entered: '2026-03-06T22:09:18.890077'
  exited: '2026-03-06T22:17:56.366660'
- position: ready
  entered: '2026-03-06T22:17:56.366660'
  exited: '2026-03-06T22:17:59.828466'
- position: working
  entered: '2026-03-06T22:17:59.828466'
  exited: '2026-03-06T22:23:02.668053'
- position: done
  entered: '2026-03-06T22:23:02.668053'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89202
- 89203
extensions: {}
version: '2.0'
generated: '2026-03-06'
last_updated: '2026-03-06T22:23:02.672053'
---
# WORK-239: Implement Exit Criteria Gate in StatusPropagator

---

## Context

WORK-222 investigation found that `StatusPropagator.is_chapter_complete()` uses only a work-item-count predicate (all items status=complete), ignoring CHAPTER.md exit criteria checkboxes entirely. This allows premature chapter closure when work items are done but chapter goals remain unmet (e.g., CH-066 had 3 unchecked exit criteria when propagator marked it complete).

**Design (from WORK-222):** Add `_check_exit_criteria(chapter_id)` method that parses `## Exit Criteria` section checkboxes from CHAPTER.md. Make `is_chapter_complete()` a conjunction: `all_work_items_complete AND all_exit_criteria_checked`. Gracefully degrade to count-only when CHAPTER.md or criteria section is missing (L3.6).

---

## Deliverables

- [ ] `_check_exit_criteria()` method added to StatusPropagator
- [ ] `is_chapter_complete()` enhanced with exit criteria gate
- [ ] New `chapter_criteria_unmet` action in propagation result
- [ ] Tests for all paths (checked, unchecked, missing file, missing section)
- [ ] Existing tests still pass

---

## References

- @.claude/haios/lib/status_propagator.py (implementation target)
- @tests/test_status_propagator.py (test file)
- @docs/work/active/WORK-222/WORK.md (parent investigation)
