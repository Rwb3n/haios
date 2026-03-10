---
template: work_item
id: WORK-305
title: Implement get_ready() chapter-existence filter per REQ-TRACE-004
type: implementation
status: active
owner: Hephaestus
created: '2026-03-10'
spawned_by: null
spawned_children: []
chapter: CH-066
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- get_ready() filters out items where chapter field is empty or chapter file doesn't
  exist
- CLAUDE.md claim 'No chapter file -> work item BLOCKED' becomes mechanically true
- Tests verify filtering behavior
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T23:09:10.171996'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T23:09:10.171996'
  exited: '2026-03-10T23:10:24.351933'
- position: parked
  entered: '2026-03-10T23:10:24.351933'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T23:10:24.356946'
---
# WORK-305: Implement get_ready() chapter-existence filter per REQ-TRACE-004
