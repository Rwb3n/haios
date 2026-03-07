---
template: work_item
id: WORK-259
title: Mechanical Retro-Before-Close Enforcement
type: implementation
status: complete
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-03-07'
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria:
- close-work-cycle blocks /close if no retro-cycle completed for the work item in
  current session
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
  entered: '2026-03-07T14:33:11.417463'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:33:11.417463'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T14:33:11.417463'
---
# WORK-259: Mechanical Retro-Before-Close Enforcement

**CLOSED AS DUPLICATE** of WORK-253. Same title, same ACs. Created ~2 min after WORK-253 by duplicate session-end ceremony.
