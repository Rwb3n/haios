---
template: work_item
id: WORK-173
title: "Blocked_by Cascade on Work Closure"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
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
  - "When a work item closes, all active WORK.md files with blocked_by referencing it are updated"
  - "Cleared references follow fail-permissive pattern (never blocks closure)"
  - "Cascade runs as part of close-work-cycle ARCHIVE phase or just close-work recipe"
  - "Tests verify blocked_by is cleared in downstream items"
  - "close_work_item(work_id) lib function sets status: complete and closed: {date} in WORK.md via regex replacement (same pattern as sync_work_md_phase from WORK-171)"
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
  - 86603
  - 86632
  - 86643
  - 86666
  - 86680
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T20:14:06
---
# WORK-173: Blocked_by Cascade on Work Closure

---

## Context

When a work item closes (e.g., WORK-101), nothing automatically clears `blocked_by: [WORK-101]` in downstream items. status_propagator.py handles chapter/arc status cascade but not blocked_by. This forces manual cleanup — the agent must find and edit each downstream WORK.md, which is mechanical bookkeeping.

Observed in S399: WORK-160 had stale `blocked_by: [WORK-101]` after WORK-101 closed in S398. 5+ convergent retro entries (mem:86603, 86632, 86643, 86666, 86680).

**Fix:** Extend close-work recipe or status_propagator to grep `docs/work/active/*/WORK.md` for `blocked_by:.*{closed_id}` and remove references. Same fail-permissive pattern as existing cascades.

---

## Deliverables

- [ ] blocked_by cascade function in lib/ (fail-permissive)
- [ ] close_work_item(work_id) lib function: sets status/closed fields via regex replacement
- [ ] Integration into close-work recipe or status_propagator
- [ ] Tests verifying cascade clears references
- [ ] Tests verifying close_work_item writes status: complete and closed: {date}
- [ ] close-work-cycle SKILL.md updated to reference lib/ functions instead of manual edits

---

## History

### 2026-02-19 - Created (Session 403)
- From E2.8 retro triage: 5+ convergent entries across S399-S403

---

## References

- @.claude/haios/lib/status_propagator.py (pattern template)
- @.claude/haios/modules/work_engine.py (WorkEngine)
- Memory: 86603, 86632, 86643, 86666, 86680
