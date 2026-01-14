---
template: work_item
id: E2-152
title: "Work-Item Tooling Cutover"
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-29
milestone: M7b-WorkInfra
priority: high
effort: low
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: [E2-151, E2-170]
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-23T19:06:12
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-23
last_updated: 2025-12-24T18:27:51
---
# WORK-E2-152: Work-Item Tooling Cutover

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Commands and hooks still reference deprecated `docs/pm/backlog.md`. Work files now live in `docs/work/` but tooling hasn't been updated.

**Root Cause:** E2-170 (backfill) created work files from backlog.md, but the tooling cutover was marked complete without actual implementation.

**Files to Update:**
1. `.claude/commands/close.md` - Has ~100 lines of backlog.md fallback logic (lines 38-268)
2. `.claude/hooks/hooks/pre_tool_use.py` - References `docs/pm/backlog.md` for validation (line 156)

---

## Current State

Reopened in Session 112 after discovering false closure. Work files exist, tooling still points to deprecated backlog.md.

---

## Deliverables

- [ ] Remove backlog.md fallback flow from `/close` command (lines 38-268)
- [ ] Update `pre_tool_use.py` to validate `docs/work/` instead of `docs/pm/backlog.md`
- [ ] Verify no other active code references `docs/pm/backlog.md`
- [ ] Test `/close` command with work file flow only

---

## History

### 2025-12-24 - Reopened (Session 112)
- Discovered false closure during backlog audit
- E2-152 was stub with placeholder deliverables
- Populated with real scope and deliverables
- Assigned M7b-WorkInfra milestone

### 2025-12-23 - Created (Session 105)
- Initial creation as stub

---

## References

- E2-151: Backlog Migration Script (data migration - completed via E2-170)
- E2-170: Backfill Work Items from Archived Backlog (completed)
- Session 112: False closure discovery
