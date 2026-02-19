---
template: work_item
id: WORK-173
title: Blocked_by Cascade on Work Closure
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-19'
priority: high
effort: small
traces_to:
- REQ-CEREMONY-001
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/haios/lib/status_propagator.py
- .claude/haios/modules/work_engine.py
- .claude/skills/close-work-cycle/SKILL.md
acceptance_criteria:
- When a work item closes, all active WORK.md files with blocked_by referencing it
  are updated
- Cleared references follow fail-permissive pattern (never blocks closure, but logs
  warning to governance-events.jsonl on failure)
- Cascade runs as part of close-work-cycle ARCHIVE phase or just close-work recipe
- Tests verify blocked_by is cleared in downstream items
- close_work_item functionality satisfied by existing WorkEngine.close() — no new
  lib function needed
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-19 20:14:06
  exited: '2026-02-19T22:31:31.485702'
artifacts: []
cycle_docs: {}
memory_refs:
- 86603
- 86632
- 86643
- 86666
- 86680
- 72314
- 86861
- 86862
- 86863
- 86864
- 86865
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-19T22:31:31.490275'
queue_history:
- position: ready
  entered: '2026-02-19T22:02:57.032815'
  exited: '2026-02-19T22:02:57.068589'
- position: working
  entered: '2026-02-19T22:02:57.068589'
  exited: '2026-02-19T22:31:31.485702'
- position: done
  entered: '2026-02-19T22:31:31.485702'
  exited: null
---
# WORK-173: Blocked_by Cascade on Work Closure

---

## Context

When a work item closes (e.g., WORK-101), nothing automatically clears `blocked_by: [WORK-101]` in downstream items. status_propagator.py handles chapter/arc status cascade but not blocked_by. This forces manual cleanup — the agent must find and edit each downstream WORK.md, which is mechanical bookkeeping.

Observed in S399: WORK-160 had stale `blocked_by: [WORK-101]` after WORK-101 closed in S398. 5+ convergent retro entries (mem:86603, 86632, 86643, 86666, 86680).

**Fix:** Extend close-work recipe or status_propagator to grep `docs/work/active/*/WORK.md` for `blocked_by:.*{closed_id}` and remove references. Same fail-permissive pattern as existing cascades.

---

## Deliverables

- [x] blocked_by cascade function in lib/ (fail-permissive) — `blocked_by_cascade.py:clear_blocked_by()`
- [x] close_work_item functionality satisfied by existing `WorkEngine.close()` (no new lib function needed)
- [x] Integration into close-work recipe — justfile calls `cli.py clear-blocked-by` after cascade
- [x] Tests verifying cascade clears references — 18 tests, all pass
- [x] Tests verifying close_work_item writes status — pre-existing WorkEngine tests
- [x] close-work-cycle SKILL.md updated — ARCHIVE phase documents blocked_by cascade step

---

## History

### 2026-02-19 - Created (Session 403)
- From E2.8 retro triage: 5+ convergent entries across S399-S403

---

## References

- @.claude/haios/lib/status_propagator.py (pattern template)
- @.claude/haios/modules/work_engine.py (WorkEngine)
- Memory: 86603, 86632, 86643, 86666, 86680
