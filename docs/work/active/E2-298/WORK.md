---
template: work_item
id: E2-298
title: Consumer Migration to WorkEngine
status: active
owner: Hephaestus
created: 2026-01-17
closed: null
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
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-17
last_updated: '2026-01-17T14:50:23'
---
# WORK-E2-298: Consumer Migration to WorkEngine

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** WorkEngine (E2-242) is implemented but existing consumers still use the old work_item.py patterns. Specifically: plan_tree.py, node_cycle.py, and /close command need migration to use WorkEngine for full strangler fig completion.

**Trigger:** E2-242 observations.md noted "Consumer migration work items" as future work.

**Root Cause:** E2-242 scope was limited to WorkEngine implementation, not consumer migration.

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

- [ ] Migrate plan_tree.py to use WorkEngine
- [ ] Migrate node_cycle.py to use WorkEngine
- [ ] Migrate /close command to use WorkEngine
- [ ] Verify no remaining imports from work_item.py

---

## History

### 2026-01-17 - Created (Session 199)
- Initial creation

---

## References

- @docs/work/archive/E2-242/observations.md (source observation)
- @docs/work/archive/E2-242/WORK.md (WorkEngine implementation)
