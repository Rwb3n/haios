---
template: work_item
id: WORK-140
title: "Detect Status vs Node History Divergence in Audit"
type: bugfix
status: active
owner: Hephaestus
created: 2026-02-12
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/audit.py
acceptance_criteria:
- "Audit flags items where status field disagrees with current_node/node_history"
- "E2-295 pattern (status: archived, node: complete) would be caught"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-12T22:40:28
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-12
last_updated: 2026-02-12T22:40:28
---
# WORK-140: Detect Status vs Node History Divergence in Audit

---

## Context

E2-295 had `status: archived` but `current_node: complete` — the status and node fields diverged without detection. This is a data integrity issue. During S358 legacy triage, the subagent found the discrepancy but nothing in the audit system catches it automatically. The `/audit` skill should flag items where `status` disagrees with the terminal state implied by `current_node` or `node_history`.

---

## Deliverables

- [ ] Add status/node divergence check to audit module
- [ ] Flag items where status is archived but node is complete (and vice versa)
- [ ] Add test for divergence detection

---

## History

### 2026-02-12 - Created (Session 358)
- Discovered during legacy triage: E2-295 had mismatched status/node

---

## References

- @.claude/haios/lib/audit.py
- E2-295 (exemplar of the bug)
