---
template: work_item
id: WORK-175
title: Fix plan_tree.py --ready Blocked_by Filter
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: null
spawned_children: []
chapter: CH-065
arc: infrastructure
closed: 2026-02-19
priority: high
effort: small
traces_to:
- REQ-QUEUE-003
requirement_refs: []
source_files:
- scripts/plan_tree.py
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- plan_tree.py --ready filters out items where blocked_by contains unclosed work IDs
- Output matches WorkEngine.get_ready() results
- Tests verify blocked items are excluded from ready list
- Existing test_routing_gate.py tests updated if affected
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-19 20:14:06
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 86617
- 86836
- 86837
- 86838
- 86839
- 86840
- 86841
- 86842
- 86843
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-19T21:46:45.259209'
queue_history: []
---
# WORK-175: Fix plan_tree.py --ready Blocked_by Filter

---

## Context

`plan_tree.py --ready` (invoked by `just ready`) does not filter `blocked_by` field. `WorkEngine.get_ready()` does. Two code paths for the same semantic query ("what work is ready?") produce different results. Blocked items appear as ready in `just ready` output.

Observed in S399: WORK-169 (blocked_by: [WORK-167]) and WORK-171 (blocked_by: [WORK-168]) appeared in `just ready` output despite being blocked (mem:86617).

**Fix:** Add blocked_by filtering to `plan_tree.py --ready`, or delegate to WorkEngine.get_ready() to ensure a single code path.

---

## Deliverables

- [x] plan_tree.py --ready filters blocked_by (resolves against actual work item status)
- [x] Output matches WorkEngine.get_ready() semantics (demo verified: identical 13-item list)
- [x] Test verifying blocked items excluded (4 tests in tests/test_plan_tree.py)
- [x] Existing test failures (test_routing_gate) are pre-existing, not caused by this change

---

## History

### 2026-02-19 - Implemented (Session 405)
- Fixed two bugs: (1) YAML list blocked_by parsing, (2) ready filter using deprecated milestones
- Added per-item status resolution matching WorkEngine._is_actually_blocked() semantics
- 4 tests added to tests/test_plan_tree.py — all pass
- Demo verified exact parity with WorkEngine.get_ready()
- WHY captured: mem:86836-86842

### 2026-02-19 - Created (Session 403)
- From E2.8 retro triage: severity HIGH, divergent code paths

---

## References

- @scripts/plan_tree.py (target file)
- @.claude/haios/modules/work_engine.py (WorkEngine.get_ready() reference)
- Memory: 86617
