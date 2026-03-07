---
template: work_item
id: WORK-273
title: Coldstart RECOVERY Phase Signal Quality Test
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-251
spawned_children: []
chapter: CH-061
arc: call
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- tests/test_coldstart_orchestrator.py
- .claude/haios/lib/coldstart_orchestrator.py
acceptance_criteria:
- Integration test verifies RECOVERY phase output contains only lifecycle-phase stuck
  items, not backlog noise
- 'Test for _check_for_orphans() output quality: backlog items absent, DO/PLAN items
  present when stuck'
- Prevents regression of WORK-251 false-positive fix (existing test asserted wrong
  behavior)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T18:20:47.832111'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T18:20:47.832111'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T18:20:47.832111'
---
# WORK-273: Coldstart RECOVERY Phase Signal Quality Test
