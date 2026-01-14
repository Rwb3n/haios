---
template: work_item
id: E2-263
title: CycleRunner Scaffold Commands
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: high
effort: small
category: implementation
spawned_by: null
spawned_by_investigation: INV-056
blocked_by: []
blocks:
- E2-264
enables: []
related:
- INV-056
- E2-259
- E2-260
- E2-261
- E2-262
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 19:39:04
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T19:41:34'
---
# WORK-E2-263: CycleRunner Scaffold Commands

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The `post_tool_use.py` hook imports `node_cycle.build_scaffold_command()` directly from `.claude/lib/`. Per Epoch 2.2 Strangler Fig pattern, all lib/ imports should be routed through modules.

**Root cause:** CycleRunner module exists but doesn't expose scaffold command building. The hook was not migrated when other recipes were wired to modules.

**Source:** INV-056 finding (Memory 80685): `node_cycle.build_scaffold_command() -> CycleRunner (E2-263)`

---

## Current State

Work item in BACKLOG node. Part of Epoch 2.2 hook migration batch.

---

## Deliverables

- [ ] Add `build_scaffold_command(node, work_id)` method to CycleRunner module
- [ ] Method delegates to existing `.claude/lib/node_cycle.py` implementation
- [ ] Unit tests in `tests/test_cycle_runner.py`
- [ ] README.md updated with new method documentation

---

## History

### 2026-01-04 - Created (Session 169)
- Spawned from INV-056 investigation
- Part of hook-to-module migration for Epoch 2.2 completion

---

## References

- INV-056: Hook-to-Module Migration Investigation
- `.claude/lib/node_cycle.py`: Current implementation
- `.claude/haios/modules/cycle_runner.py`: Target module
- Memory 80685: Mapping finding
