---
template: work_item
id: E2-168
title: "Synthesis Just Recipes"
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
    entered: 2025-12-24T18:37:00
    exited: null
  - node: implement
    entered: 2025-12-24T18:37:00
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-24
last_updated: 2025-12-24T18:38:59
---
# WORK-E2-168: Synthesis Just Recipes

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Synthesis requires `python -m haios_etl.cli synthesis run ...`. Not discoverable via `just --list`.

**Solution:** Add just recipes wrapping synthesis CLI.

---

## Current State

Manual: `python -m haios_etl.cli synthesis run --concept-sample 0 --max-bridges 500`

---

## Deliverables

- [x] `just synthesis` - Run synthesis with sensible defaults (already existed)
- [x] `just synthesis-status` - Check last run, current counts (added Session 113)
- [x] `just synthesis-full` - Full overnight run (added Session 113)

---

## History

### 2025-12-24 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
