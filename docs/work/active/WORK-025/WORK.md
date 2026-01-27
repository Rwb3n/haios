---
template: work_item
id: WORK-025
title: Delete stale .claude/lib/*.py files - keep only __init__.py shim
type: task
status: complete
owner: Hephaestus
created: 2026-01-27
spawned_by: WORK-024
chapter: null
arc: migration
closed: '2026-01-27'
priority: high
effort: low
traces_to: []
requirement_refs: []
source_files:
- .claude/lib/
acceptance_criteria:
- Only __init__.py remains in .claude/lib/
- All .py files except __init__.py deleted
- Tests still pass after deletion
blocked_by: []
blocks:
- WORK-026
- WORK-027
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 00:05:25
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82527
- 82528
- 82529
- 82530
- 82531
- 82532
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T00:21:30'
---
# WORK-025: Delete stale .claude/lib/*.py files - keep only __init__.py shim

@docs/work/active/WORK-024/WORK.md

---

## Context

**Problem:** Stale `.py` files in `.claude/lib/` are masking the compatibility shim's re-exports.

**Root Cause (WORK-024 Finding F5):** When code uses `sys.path.insert(0, '.claude/lib'); from X import Y`, Python finds the stale `.claude/lib/X.py` file first, NOT the re-export from `.claude/haios/lib/X.py`.

**Evidence:**
- `log_session_start()` exists in `.claude/haios/lib/governance_events.py`
- `log_session_start()` does NOT exist in `.claude/lib/governance_events.py`
- Importing via deprecated path fails with ImportError

**Impact:** New functions (E2-236 session logging) are unavailable via deprecated path.

**Solution:** Delete all `.py` files in `.claude/lib/` except `__init__.py`. The shim will handle re-exports.

---

## Deliverables

- [x] Delete `.claude/lib/*.py` files (except `__init__.py`) - 22 files deleted
- [x] Delete `.claude/lib/agents/` directory - removed
- [x] Delete `.claude/lib/preprocessors/` directory - removed
- [x] Verify `pytest` passes after deletion - PARTIAL: tests using correct path pass (19/19), tests using deprecated path fail as expected (scoped to WORK-027)
- [x] Verify deprecation warning still works - confirmed

---

## History

### 2026-01-27 - Implemented (Session 249)
- Deleted 22 stale .py files
- Deleted agents/ and preprocessors/ directories
- Verified: tests using .claude/haios/lib/ pass
- Expected: tests using .claude/lib/ fail (WORK-027 scope)
- Memory: 82527, 82528

### 2026-01-27 - Spawned (Session 249)
- Spawned from WORK-024 investigation
- Blocks WORK-026 (justfile) and WORK-027 (tests)

---

## References

- @docs/work/active/WORK-024/WORK.md (parent investigation)
