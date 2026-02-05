---
template: work_item
id: WORK-103
title: Dynamic Blocker Resolution in Queue Engine
type: feature
status: active
owner: Hephaestus
created: 2026-02-05
spawned_by: Session-316-observation
chapter: null
arc: queue
closed: null
priority: medium
effort: small
traces_to:
- REQ-QUEUE-003
requirement_refs: []
source_files:
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- Queue engine checks blocked_by items' actual status before reporting blocked
- Items with all blockers status:complete appear as unblocked
- No false positives (items with active blockers still show blocked)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 21:35:43
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T21:36:10'
---
# WORK-103: Dynamic Blocker Resolution in Queue Engine

---

## Context

Session 316 found WORK-091 and WORK-092 listed as blocked (blocked_by: WORK-088) even though WORK-088 had status: complete (closed 2026-02-04). The queue engine reads the static `blocked_by` frontmatter field but does not check whether the referenced items are actually still active. This causes items to appear stuck when their blockers have been resolved.

**Root cause:** `WorkEngine.get_queue()` filters on `blocked_by` presence without resolving blocker status.

---

## Deliverables

- [ ] WorkEngine.get_queue() resolves blocked_by against actual work item status
- [ ] Items whose blockers are all status:complete are treated as unblocked
- [ ] Unit test: item blocked by complete work item appears in queue
- [ ] Unit test: item blocked by active work item does NOT appear in queue

---

## History

### 2026-02-05 - Created (Session 316)
- Spawned from WORK-091/WORK-092 observation: blocked_by not dynamically resolved

---

## References

- @docs/work/active/WORK-091/observations.md (source observation)
- @.claude/haios/modules/work_engine.py (affected code)
