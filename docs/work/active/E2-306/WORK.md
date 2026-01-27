---
template: work_item
id: E2-306
title: Remove Legacy new-investigation Compound Recipe
type: implementation
status: active
owner: Hephaestus
created: 2026-01-27
spawned_by: INV-070
chapter: CH-004
arc: migration
closed: null
priority: medium
effort: small
traces_to:
- REQ-GOVERN-002
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 22:12:21
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T22:13:12'
---
# E2-306: Remove Legacy new-investigation Compound Recipe

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The `new-investigation` compound recipe in the justfile calls both `just work` and `just inv` sequentially. It is not called by any skill or module — it exists only for direct agent use, which bypasses governance. The `/new-investigation` command already exists and properly chains into work-creation-cycle.

**Fix:** Remove the `new-investigation` recipe from the justfile. The `/new-investigation` command is the correct entry point.

---

## Deliverables

- [ ] Remove `new-investigation` recipe from justfile
- [ ] Verify `/new-investigation` command still works without the recipe
- [ ] Verify no skill/module references the removed recipe

---

## History

### 2026-01-27 - Created (Session 251)
- Spawned from INV-070 Legacy Scaffold Recipe Audit

---

## References

- @docs/work/active/INV-070/WORK.md (parent investigation)
- @.claude/haios/epochs/E2_3/arcs/migration/CH-004-recipe-audit.md
