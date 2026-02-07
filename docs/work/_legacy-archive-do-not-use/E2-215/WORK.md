---
template: work_item
id: E2-215
title: Create just close-work Recipe
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: small
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
  entered: 2025-12-28 12:46:31
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T12:47:05'
---
# WORK-E2-215: Create just close-work Recipe

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Work item closure requires 3 manual Edit calls + 1 Bash mv, consuming ~450 tokens per closure with potential for date format errors and path typos.

**Root cause:** Existing Python functions in `.claude/lib/work_item.py` (update_work_file_status, update_work_file_closed_date, move_work_file_to_archive) are not exposed as a unified just recipe.

**Solution:** Create `just close-work <id>` recipe that atomically calls all 3 functions plus cascade and status update.

---

## Current State

Work item in BACKLOG node. Ready to implement - design complete in INV-046.

---

## Deliverables

- [ ] Add `close-work` recipe to justfile calling work_item.py functions
- [ ] Include cascade and update-status in recipe chain
- [ ] Test with a sample work item (dry run)
- [ ] Update close-work-cycle skill to reference new recipe

---

## History

### 2025-12-28 - Created (Session 133)
- Spawned from INV-046 findings: infrastructure exists but no unified recipe

---

## References

- Spawned by: INV-046 (Mechanical Action Automation)
- Design: INV-046 investigation findings
- Functions: `.claude/lib/work_item.py:42-91`
