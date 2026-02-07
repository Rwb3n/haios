---
template: work_item
id: E2-260
title: GovernanceLayer Toggle Access
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
- E2-261
- E2-262
- E2-263
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 19:39:01
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T19:40:44'
---
# WORK-E2-260: GovernanceLayer Toggle Access

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The `pre_tool_use.py` hook imports `config.ConfigLoader.toggles` directly from `.claude/lib/`. Per Epoch 2.2 Strangler Fig pattern, all lib/ imports should be routed through modules.

**Root cause:** GovernanceLayer module exists but doesn't expose toggle access. The hook was not migrated when other recipes were wired to modules.

**Source:** INV-056 finding (Memory 80682): `config.ConfigLoader.toggles -> GovernanceLayer.get_toggle() (E2-260)`

---

## Current State

Work item in BACKLOG node. Part of Epoch 2.2 hook migration batch.

---

## Deliverables

- [ ] Add `get_toggle(name: str)` method to GovernanceLayer module
- [ ] Method delegates to existing `.claude/lib/config.py` ConfigLoader implementation
- [ ] Unit tests in `tests/test_governance_layer.py`
- [ ] README.md updated with new method documentation

---

## History

### 2026-01-04 - Created (Session 169)
- Spawned from INV-056 investigation
- Part of hook-to-module migration for Epoch 2.2 completion

---

## References

- INV-056: Hook-to-Module Migration Investigation
- `.claude/lib/config.py`: Current implementation
- `.claude/haios/modules/governance_layer.py`: Target module
- Memory 80682: Mapping finding
