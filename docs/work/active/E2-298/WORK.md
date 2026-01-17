---
template: work_item
id: E2-298
title: Consumer Migration to WorkEngine
status: complete
owner: Hephaestus
created: 2026-01-17
closed: '2026-01-17'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: E2-296
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-17 14:49:39
  exited: null
cycle_docs: {}
memory_refs:
- 81458
- 81459
- 81460
- 81461
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-17
last_updated: '2026-01-17T15:48:04'
---
# WORK-E2-298: Consumer Migration to WorkEngine

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** WorkEngine (E2-242) is implemented but test files still import the old work_item.py module. The observation mentioned "plan_tree.py, node_cycle.py, and /close command" but investigation reveals:
- `plan_tree.py` doesn't exist
- `node_cycle.py` provides hook-specific functionality (node transitions), not work item CRUD
- `/close` is a markdown skill that chains to close-work-cycle, doesn't import Python

Actual migration needed: Test files `test_work_item.py` and `test_close_work_item.py` still import from `work_item.py` instead of using WorkEngine.

**Trigger:** E2-242 observations.md noted "Consumer migration work items" as future work.

**Root Cause:** E2-242 scope was limited to WorkEngine implementation, not consumer migration. Observation was written before full analysis of actual consumers.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.
-->

- [ ] Migrate test_work_item.py to test WorkEngine methods instead of work_item.py
- [ ] Migrate test_close_work_item.py to test WorkEngine methods instead of work_item.py
- [ ] Add deprecation notice to work_item.py header
- [ ] Verify no runtime (non-test) imports from work_item.py exist

---

## History

### 2026-01-17 - Created (Session 199)
- Initial creation

---

## References

- @docs/work/archive/E2-242/observations.md (source observation)
- @docs/work/archive/E2-242/WORK.md (WorkEngine implementation)
- @.claude/lib/work_item.py (old module to deprecate)
- @.claude/haios/modules/work_engine.py (new module)
