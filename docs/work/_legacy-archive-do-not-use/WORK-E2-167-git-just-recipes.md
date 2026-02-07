---
template: work_item
id: E2-167
title: "Git Just Recipes"
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
current_node: implement
node_history:
  - node: implement
    entered: 2025-12-24T18:49:00
    exited: null
  - node: implement
    entered: 2025-12-24T18:49:00
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-24
last_updated: 2025-12-24T18:51:18
---
# WORK-E2-167: Git Just Recipes

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Git operations are manual command-line work. Not integrated into `just` interface.

**Solution:** Add just recipes for common git operations at lifecycle boundaries.

---

## Current State

Manual: `git add ... && git commit -m "..."`. No recipes.

---

## Deliverables

- [x] `just commit-session <N> "<title>"` - Commit checkpoint + session changes
- [x] `just commit-close <id>` - Commit work file + plan + investigation changes
- [x] `just stage-governance` - Stage all governance files (bonus)
- [x] Commit message format per CLAUDE.md git conventions
- [x] Foundation for E2-165, E2-166

---

## History

### 2025-12-24 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
