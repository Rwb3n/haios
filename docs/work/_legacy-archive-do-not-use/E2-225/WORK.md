---
template: work_item
id: E2-225
title: 'Path Governance Gap: New Work Directory Structure'
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 21:23:31
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T21:24:29'
---
# WORK-E2-225: Path Governance Gap: New Work Directory Structure

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** PreToolUse hook path governance only covered legacy flat paths (docs/plans/, docs/checkpoints/, etc.) but not the new work directory structure from E2-212. Agent could bypass governance by directly writing to docs/work/active/*/plans/PLAN.md.

**Root cause:** When E2-212 introduced the new directory structure, the governed_paths in pre_tool_use.py was not updated.

**Solution:** Add new work directory structure checks to _check_path_governance() in pre_tool_use.py.

---

## Current State

FIXED in Session 140. Path governance now blocks:
- `docs/work/active/*/WORK.md` -> Use `/new-work` or `just work`
- `docs/work/active/*/plans/PLAN.md` -> Use `/new-plan` or `just plan`
- `docs/work/active/*/observations.md` -> Use `just scaffold-observations`

---

## Deliverables

- [x] Add work directory checks to _check_path_governance() in pre_tool_use.py
- [x] Block WORK.md raw creation
- [x] Block PLAN.md raw creation in /plans/
- [x] Block observations.md raw creation

---

## History

### 2025-12-28 - Created (Session 140)
- Initial creation

---

## References

- [Related documents]
