---
template: work_item
id: WORK-117
title: "Unify test module loading via shared conftest.py"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-10
spawned_by: WORK-116
chapter: null
arc: ceremonies
closed: null
priority: medium
effort: medium
traces_to: []  # REQUIRED: L4 requirement IDs (e.g., REQ-TRACE-001) - enforced by REQ-TRACE-002
requirement_refs: []  # DEPRECATED: use traces_to instead
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-10T21:54:08
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-10
last_updated: 2026-02-10T21:54:08
---
# WORK-117: Unify test module loading via shared conftest.py

---

## Context

Multiple test files (`test_work_engine.py`, `test_queue_ceremonies.py`, `test_ceremony_context.py`) each use their own module loading pattern (`_load_module` vs `_ensure_module` vs `from X import`). The `_load_module` pattern unconditionally creates new module instances and overwrites `sys.modules`, causing ContextVar divergence when modules share state via `contextvars.ContextVar`. This was discovered in Session 338 (WORK-116) where `ceremony_context` set one ContextVar but `check_ceremony_required` read another because they were bound to different governance_layer module instances.

Fix: Create a shared `conftest.py` that loads governance_layer, work_engine, and queue_ceremonies once via session-scoped fixtures, eliminating per-file `_load_module` / `_ensure_module` / `sys.path.insert` boilerplate.

Also includes: fix checkpoint scaffold `prior_session` auto-detection (reads `.claude/session` instead of stale value).

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] Create `tests/conftest.py` with session-scoped fixtures for governance_layer, work_engine, queue_ceremonies modules
- [ ] Update `test_work_engine.py` to use conftest fixtures instead of `_load_module`
- [ ] Update `test_queue_ceremonies.py` to use conftest fixtures instead of `_load_module`
- [ ] Update `test_ceremony_context.py` to use conftest fixtures, remove `_ensure_module` / `_get_gov_mod()` workaround
- [ ] All existing tests pass with no regressions
- [ ] Fix checkpoint scaffold `prior_session` auto-detection from `.claude/session`

---

## History

### 2026-02-10 - Created (Session 338)
- Spawned from WORK-116 observation: _load_module creates duplicate module instances causing ContextVar divergence

---

## References

- @docs/work/active/WORK-116/observations.md (root cause analysis)
- @tests/test_ceremony_context.py (_get_gov_mod() workaround)
- @tests/test_work_engine.py (_load_module pattern)
- @tests/test_queue_ceremonies.py (_load_module pattern)
