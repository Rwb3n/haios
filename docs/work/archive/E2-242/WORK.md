---
template: work_item
id: E2-242
title: Implement WorkEngine Module
status: complete
owner: Hephaestus
created: 2026-01-03
closed: 2026-01-03
milestone: M7b-WorkInfra
priority: high
effort: high
category: implementation
spawned_by: null
spawned_by_investigation: INV-053
blocked_by:
- E2-240
- E2-241
blocks: []
enables: []
related:
- INV-052
- INV-053
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 13:07:57
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-242/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T16:14:00'
---
# WORK-E2-242: Implement WorkEngine Module

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Work item state management (WORK.md operations, node transitions, history) is scattered across lib and hooks.

**Root cause:** Organic growth without module boundary. INV-052 designed WorkEngine as state owner; INV-053 validated it.

**Goal:** Create black-box WorkEngine module that owns WORK.md. Single source of truth for work item state. Swappable for different project management paradigms.

---

## Current State

Work item in BACKLOG node. Phase 3 of implementation sequence (depends on E2-240, E2-241).

---

## Deliverables

- [ ] WorkEngine module in `.claude/haios/modules/work_engine.py`
- [ ] WORK.md parser/serializer
- [ ] Node transition logic with validation (calls GovernanceLayer)
- [ ] node_history management
- [ ] Work item CRUD operations
- [ ] Ready items query (for routing)
- [ ] Typed callback interface for MemoryBridge auto-linking
- [ ] Unit tests in `tests/test_work_engine.py`
- [ ] Integration tests with file system

---

## History

### 2026-01-03 - Created (Session 158)
- Spawned from INV-053 (HAIOS Modular Architecture Review)
- Phase 3 of implementation sequence (blocked by E2-240, E2-241)

---

## References

- INV-052: HAIOS Architecture Reference (design source)
- INV-053: HAIOS Modular Architecture Review (spawn source)
- docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md (module spec)
- docs/work/active/INV-052/SECTION-17.12-IMPLEMENTATION-SEQUENCE.md (Phase 3)
