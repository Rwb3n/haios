---
template: work_item
id: WORK-265
title: Duplicate Work Item Detection at Scaffold Time
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
acceptance_criteria:
- scaffold_work checks for existing work items with similar titles before creating
- Exact-title match warns or blocks duplicate creation
- Prevents duplicate WORK pairs like 253/259, 254/260, 255/261 (mem:89639)
blocked_by: []
blocks: []
enables: []
queue_position: ready
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T17:05:13.968544'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T17:05:13.968544'
  exited: '2026-03-08T16:23:26.627070'
- position: ready
  entered: '2026-03-08T16:23:26.627070'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-08T16:23:26.632069'
---
# WORK-265: Duplicate Work Item Detection at Scaffold Time
