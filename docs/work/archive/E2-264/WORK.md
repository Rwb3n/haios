---
template: work_item
id: E2-264
title: Hook Import Migration
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-056
blocked_by:
- E2-259
- E2-260
- E2-261
- E2-262
- E2-263
blocks: []
enables: []
related:
- INV-056
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 19:39:05
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T19:41:59'
---
# WORK-E2-264: Hook Import Migration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** All 4 Python hooks (user_prompt_submit, pre_tool_use, post_tool_use, stop) import directly from `.claude/lib/` instead of using the Chariot modules. This is the final step of Epoch 2.2 Strangler Fig migration.

**Root cause:** Module extension work items (E2-259 through E2-263) must complete first to expose the required functionality in modules. Once those are done, hooks can be rewired.

**Source:** INV-056 finding (Memory 80686): `Final step: E2-264 rewires hooks to import from modules instead of lib/`

**Pattern:** Follow E2-085/E2-120 pattern (successful hook migration with 22 tests).

---

## Current State

Work item BLOCKED by E2-259, E2-260, E2-261, E2-262, E2-263. Will become READY once all module extensions are complete.

---

## Deliverables

- [ ] Migrate `user_prompt_submit.py` to use ContextLoader.generate_status()
- [ ] Migrate `pre_tool_use.py` to use GovernanceLayer.get_toggle()
- [ ] Migrate `post_tool_use.py` to use MemoryBridge.capture_error(), CycleRunner.build_scaffold_command()
- [ ] Migrate `stop.py` to use MemoryBridge.extract_learnings()
- [ ] All 4 hooks use modules exclusively - no lib/ imports
- [ ] All existing hook tests pass (22+ tests)
- [ ] README.md updated with migration documentation

---

## History

### 2026-01-04 - Created (Session 169)
- Spawned from INV-056 investigation
- Final step of Epoch 2.2 hook-to-module migration
- Blocked by E2-259 through E2-263

---

## References

- INV-056: Hook-to-Module Migration Investigation
- E2-085: Hook Migration PowerShell to Python (prior pattern)
- E2-120: Complete PowerShell to Python Migration (execution)
- Memory 80686: Final step directive
