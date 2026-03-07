---
template: work_item
id: WORK-256
title: Auto-promote queue_position when cycle_phase changes
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-245
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/modules/cycle_runner.py
- .claude/haios/lib/cycle_state.py
acceptance_criteria:
- cycle_set() auto-promotes queue_position to working if currently backlog or ready
- node_history and queue_history entries added atomically with cycle_phase change
- Prevents queue_position:backlog + cycle_phase:PLAN drift (WORK-245 WDN-1)
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: DONE
current_node: DONE
node_history:
- node: backlog
  entered: '2026-03-07T14:28:16.434826'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:28:16.434826'
  exited: '2026-03-07T19:19:43.378862'
- position: ready
  entered: '2026-03-07T19:19:43.378862'
  exited: '2026-03-07T19:19:48.242786'
- position: working
  entered: '2026-03-07T19:19:48.242786'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T19:19:48.244786'
---
# WORK-256: Auto-promote queue_position when cycle_phase changes
