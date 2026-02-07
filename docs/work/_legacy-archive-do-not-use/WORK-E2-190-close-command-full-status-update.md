---
template: work_item
id: E2-190
title: Close Command Full Status Update
status: complete
owner: Hephaestus
created: 2025-12-25
closed: 2025-12-25
milestone: M8-SkillArch
priority: high
effort: low
category: bugfix
spawned_by: Session-119
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-25 19:44:08
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T19:47:21'
---
# WORK-E2-190: Close Command Full Status Update

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Bug:** `/close` command and `close-work-cycle` skill run `just update-status-slim` which only updates `haios-status-slim.json`. The `plan_tree.py --ready` script (used by `just ready`) reads from full `haios-status.json`, causing closed items to still appear as "ready".

**Root Cause:** The close-work-cycle CAPTURE phase calls `just update-status-slim` instead of `just update-status`.

**Impact:** After closing work items, `just ready` shows stale data until someone manually runs `just update-status`.

---

## Current State

Work file created. Bug confirmed and documented during Session 119 bug hunt.

---

## Deliverables

- [ ] Update close-work-cycle to use `just update-status` instead of `just update-status-slim`
- [ ] Update /close command to use `just update-status`
- [ ] Verify `just ready` shows accurate data after close

---

## History

### 2025-12-25 - Created (Session 119)
- Bug discovered during bug hunt
- Confirmed: E2-181 through E2-188 showed as ready even though archived
- Fixed by running `just update-status` manually

---

## References

- close-work-cycle skill: `.claude/skills/close-work-cycle/SKILL.md`
- /close command: `.claude/commands/close.md`
- plan_tree.py: `scripts/plan_tree.py`
