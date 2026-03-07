---
template: work_item
id: WORK-262
title: Validate Chapter Status at Work Item Scaffold Time
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-250
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-TRACE-003
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
acceptance_criteria:
- scaffold_work validates that referenced chapter exists and has status != Complete
  before assigning
- If chapter is Complete, scaffold warns or blocks with suggestion to use a different
  chapter
- Prevents WORK-250-style misassignment (CH-058 was Complete but work item assigned
  to it)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T16:12:51.656982'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T16:12:51.656982'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T16:12:51.656982'
---
# WORK-262: Validate Chapter Status at Work Item Scaffold Time
