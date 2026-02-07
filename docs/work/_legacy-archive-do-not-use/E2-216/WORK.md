---
template: work_item
id: E2-216
title: Update Cycle Skills to Use Recipes
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: INV-046
spawned_by_investigation: INV-046
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 12:46:36
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T15:53:41'
---
# WORK-E2-216: Update Cycle Skills to Use Recipes

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Cycle skills prescribe manual Edit/Bash calls for node transitions and document linking, even though `just node` and `just link` recipes already exist. This wastes ~350 tokens per transition.

**Root cause:** Skills were written before recipes were created, and weren't updated when recipes were added.

**Solution:** Update all cycle skills to reference existing recipes (`just node`, `just link`, `just close-work`) instead of prescribing manual tool calls.

---

## Current State

**Session 135 Analysis:** Upon inspection, the cycle skills already use recipes appropriately:

1. `close-work-cycle`: Uses `just close-work`, `just scaffold-observations`, `just validate-observations`
2. `implementation-cycle`: Uses `/close` command (chains to close-work-cycle which uses recipes)
3. `investigation-cycle`: Uses `/close` command (chains to close-work-cycle which uses recipes)
4. `work-creation-cycle`: Uses `/new-plan`, `/new-investigation` commands (handle linking internally)

No raw Edit/Bash calls for node transitions or document linking exist in the skills.

---

## Deliverables

- [x] Update close-work-cycle skill to use `just close-work` - **Already done (E2-215)**
- [x] Update implementation-cycle skill to use `just node` for transitions - **N/A: No manual node transitions prescribed**
- [x] Update investigation-cycle skill to use `just node` and `just link` - **N/A: Uses /close which chains appropriately**
- [x] Update work-creation-cycle skill to use `just link` - **N/A: Linking done via slash commands**
- [x] Document token savings in skill comments - **N/A: No changes needed**

---

## History

### 2025-12-28 - Closed (Session 135)
- Analysis revealed work already complete
- close-work-cycle already uses recipes (E2-215)
- Other skills use slash commands which chain appropriately
- No manual Edit/Bash calls for node/link operations in any cycle skill

### 2025-12-28 - Created (Session 133)
- Spawned from INV-046: recipes exist but skills don't use them

---

## References

- Spawned by: INV-046 (Mechanical Action Automation)
- Blocked by: E2-215 (need close-work recipe)
- Existing recipes: `just node`, `just link` in justfile:38-43
