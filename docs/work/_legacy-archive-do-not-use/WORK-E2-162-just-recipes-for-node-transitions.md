---
template: work_item
id: E2-162
title: Just Recipes for Node Transitions
status: complete
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-24
milestone: M7a-Recipes
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: check
node_history:
- node: check
  entered: '2025-12-24T19:50:36.543964'
  exited: null
- node: check
  entered: '2025-12-24T19:50:36.543964'
  exited: null
- node: check
  entered: '2025-12-24T19:50:36.543964'
  exited: null
- node: check
  entered: '2025-12-24T19:50:36.543964'
  exited: null
cycle_docs:
  plan: docs/plans/PLAN-E2-162-node-transition-just-recipes.md
memory_refs: []
documents:
  investigations: []
  plans: null
  checkpoints: []
version: '1.0'
generated: 2025-12-24
last_updated: 2025-12-24T19:51:17
---
# WORK-E2-162: Just Recipes for Node Transitions

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Changing work file frontmatter (current_node, node_history) requires Read+Edit dance. Error-prone and verbose.

**Solution:** Just recipes that update well-typed frontmatter fields directly.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] `just node <id> <node>` - Move work item to node, update history
- [ ] `just link <id> <type> <path>` - Add document to cycle_docs and documents
- [ ] Python helpers in `.claude/lib/work_file.py` for frontmatter manipulation
- [ ] Tests for work file update logic

---

## History

### 2025-12-24 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
