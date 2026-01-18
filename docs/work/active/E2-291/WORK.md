---
template: work_item
id: E2-291
title: Wire Queue into Survey-Cycle and Routing-Gate
status: dismissed
owner: Hephaestus
created: 2026-01-15
closed: '2026-01-15'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: E2-290
spawned_by_investigation: INV-064
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-15 20:44:55
  exited: null
cycle_docs: {}
memory_refs:
- 81376
- 81377
- 81378
- 81379
- 81380
- 81381
- 81382
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-15
last_updated: '2026-01-18T21:56:50'
---
# WORK-E2-291: Wire Queue into Survey-Cycle and Routing-Gate

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** E2-290 built queue infrastructure (work_queues.yaml, WorkEngine methods, just recipes) but didn't wire it into governance. Survey-cycle still uses `just ready` (flat list), routing-gate doesn't check `is_cycle_allowed()`.

**Root cause:** INV-064 designed "Queue Integration Mechanism" but E2-290 deliverables only covered infrastructure, not integration. Session 192 identified this gap and hardened work-creation-cycle to prevent recurrence.

---

## Current State

Queue infrastructure exists but has no runtime consumers in governance flow.

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

- [ ] Update survey-cycle to use `get_queue()` instead of `just ready`
- [ ] Update routing-gate to call `is_cycle_allowed()` before invoking cycles
- [ ] Add queue name parameter to survey-cycle (default: "default")
- [ ] Tests for cycle-locking enforcement in routing
- [ ] Demo: blocked cycle shows warning message

---

## History

### 2026-01-15 - Created (Session 192)
- Spawned from E2-290 gap discovery
- INV-064 designed integration, E2-290 built infrastructure, E2-291 wires it in

---

## References

- @docs/work/active/E2-290/WORK.md (parent - queue infrastructure)
- @docs/work/active/INV-064/investigations/001-work-hierarchy-rename-and-queue-architecture.md (source design)
