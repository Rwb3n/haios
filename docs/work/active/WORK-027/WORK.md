---
template: work_item
id: WORK-027
title: Update test imports from .claude/lib to .claude/haios/lib
type: task
status: active
owner: Hephaestus
created: 2026-01-27
spawned_by: WORK-024
chapter: null
arc: migration
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files:
- tests/
acceptance_criteria:
- No test files import from .claude/lib path
- All tests pass after migration
blocked_by:
- WORK-025
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 00:06:02
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T00:06:47'
---
# WORK-027: Update test imports from .claude/lib to .claude/haios/lib

@docs/work/active/WORK-024/WORK.md

---

## Context

**Problem:** 20+ test files import from deprecated `.claude/lib` path.

**Root Cause (WORK-024 Finding F3):** Tests use `sys.path.insert(0, '.claude/lib')` which will fail after stale files are deleted.

**Affected Test Files (from WORK-024):**
- test_governance_events.py
- test_governance_layer.py
- test_config.py
- test_exit_gates.py
- test_error_capture.py
- test_backfill.py
- test_dependencies.py
- test_lib_spawn.py (11 occurrences)
- test_lib_scaffold.py
- test_lib_validate.py
- test_lib_status.py
- test_lib_retrieval.py
- test_lib_database.py
- test_lib_cascade.py
- test_lib_audit.py
- test_node_cycle.py
- test_observations.py
- test_work_item.py
- test_ground_truth_parser.py
- test_routing_gate.py

**Solution:** Update path from `.claude/lib` to `.claude/haios/lib` in all test files.

---

## Deliverables

- [ ] Update all test file imports to use `.claude/haios/lib`
- [ ] Run `pytest` - all tests must pass
- [ ] No deprecation warnings from lib imports

---

## History

### 2026-01-27 - Spawned (Session 249)
- Spawned from WORK-024 investigation
- Blocked by WORK-025 (stale file deletion)

---

## References

- @docs/work/active/WORK-024/WORK.md (parent investigation)
- @docs/work/active/WORK-025/WORK.md (blocking work)
