---
template: work_item
id: WORK-253
title: Mechanical Retro-Before-Close Enforcement
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria:
- PreToolUse or close-work-cycle blocks /close if no retro-cycle completed for the
  work item in current session
- Check governance-events.jsonl for RetroCompleted event matching work_id
- Prevents the pattern where retro is skipped and learnings are lost (mem:89182)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T14:31:39.178759'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:31:39.178759'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T14:31:39.178759'
---
# WORK-253: Mechanical Retro-Before-Close Enforcement
