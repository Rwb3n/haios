---
template: work_item
id: WORK-175
title: "Fix plan_tree.py --ready Blocked_by Filter"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: null
spawned_children: []
chapter: CH-065
arc: infrastructure
closed: null
priority: high
effort: small
traces_to:
  - REQ-CEREMONY-001
requirement_refs: []
source_files:
  - scripts/plan_tree.py
  - .claude/haios/modules/work_engine.py
acceptance_criteria:
  - "plan_tree.py --ready filters out items where blocked_by contains unclosed work IDs"
  - "Output matches WorkEngine.get_ready() results"
  - "Tests verify blocked items are excluded from ready list"
  - "Existing test_routing_gate.py tests updated if affected"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-19T20:14:06
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 86617
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T20:14:06
---
# WORK-175: Fix plan_tree.py --ready Blocked_by Filter

---

## Context

`plan_tree.py --ready` (invoked by `just ready`) does not filter `blocked_by` field. `WorkEngine.get_ready()` does. Two code paths for the same semantic query ("what work is ready?") produce different results. Blocked items appear as ready in `just ready` output.

Observed in S399: WORK-169 (blocked_by: [WORK-167]) and WORK-171 (blocked_by: [WORK-168]) appeared in `just ready` output despite being blocked (mem:86617).

**Fix:** Add blocked_by filtering to `plan_tree.py --ready`, or delegate to WorkEngine.get_ready() to ensure a single code path.

---

## Deliverables

- [ ] plan_tree.py --ready filters blocked_by (or delegates to WorkEngine)
- [ ] Output matches WorkEngine.get_ready() semantics
- [ ] Test verifying blocked items excluded
- [ ] Existing test failures (test_routing_gate) resolved if caused by this

---

## History

### 2026-02-19 - Created (Session 403)
- From E2.8 retro triage: severity HIGH, divergent code paths

---

## References

- @scripts/plan_tree.py (target file)
- @.claude/haios/modules/work_engine.py (WorkEngine.get_ready() reference)
- Memory: 86617
