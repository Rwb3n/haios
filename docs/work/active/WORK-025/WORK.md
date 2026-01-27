---
template: work_item
id: WORK-025
title: Delete stale .claude/lib/*.py files - keep only __init__.py shim
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
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T00:05:52'
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

- [ ] Delete `.claude/lib/*.py` files (except `__init__.py`)
- [ ] Delete `.claude/lib/agents/` directory
- [ ] Delete `.claude/lib/preprocessors/` directory
- [ ] Verify `pytest` passes after deletion
- [ ] Verify deprecation warning still works

---

## History

### 2026-01-27 - Spawned (Session 249)
- Spawned from WORK-024 investigation
- Blocks WORK-026 (justfile) and WORK-027 (tests)

---

## References

- @docs/work/active/WORK-024/WORK.md (parent investigation)
