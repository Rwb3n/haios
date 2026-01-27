---
template: work_item
id: WORK-026
title: Update justfile recipes from .claude/lib to .claude/haios/lib
type: task
status: active
owner: Hephaestus
created: 2026-01-27
spawned_by: WORK-024
chapter: null
arc: migration
closed: null
priority: high
effort: low
traces_to: []
requirement_refs: []
source_files:
- justfile
acceptance_criteria:
- No justfile recipes use .claude/lib path
- All 13 recipes updated to .claude/haios/lib
- All recipes still functional after update
blocked_by:
- WORK-025
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 00:05:59
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T00:06:43'
---
# WORK-026: Update justfile recipes from .claude/lib to .claude/haios/lib

@docs/work/active/WORK-024/WORK.md

---

## Context

**Problem:** 13 justfile recipes use deprecated `.claude/lib` path.

**Root Cause (WORK-024 Finding F2):** Recipes use `sys.path.insert(0, '.claude/lib')` which loads stale files instead of canonical location.

**Affected Recipes (from WORK-024):**
1. `obs-validate` (line 70)
2. `obs-scaffold` (line 74)
3. `obs-uncaptured` (line 78)
4. `obs-archived` (line 83)
5. `obs-triage` (line 89)
6. `gov-metrics` (line 93)
7. `status-full` (line 98)
8. `status-debug` (line 103)
9. `status-slim` (line 107)
10. `milestone` (line 313)
11. `audit-sync` (line 389)
12. `audit-gaps` (line 393)
13. `audit-stale` (line 397)

**Solution:** Update path from `.claude/lib` to `.claude/haios/lib`.

---

## Deliverables

- [ ] Update 13 justfile recipes to use `.claude/haios/lib`
- [ ] Verify each recipe still works after update
- [ ] Run `pytest` to ensure no regressions

---

## History

### 2026-01-27 - Spawned (Session 249)
- Spawned from WORK-024 investigation
- Blocked by WORK-025 (stale file deletion)

---

## References

- @docs/work/active/WORK-024/WORK.md (parent investigation)
- @docs/work/active/WORK-025/WORK.md (blocking work)
