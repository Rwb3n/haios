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
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/lib/retro_gate.py
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- PreToolUse or close-work-cycle blocks /close if no retro-cycle completed for the
  work item in current session
- Check governance-events.jsonl for RetroCycleCompleted event matching work_id
- Prevents the pattern where retro is skipped and learnings are lost (mem:89182)
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: DONE
current_node: DONE
node_history:
- node: backlog
  entered: '2026-03-07T14:31:39.178759'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:31:39.178759'
  exited: '2026-03-08T11:26:33.901896'
- position: ready
  entered: '2026-03-08T11:26:33.901896'
  exited: '2026-03-08T11:26:36.865945'
- position: working
  entered: '2026-03-08T11:26:36.865945'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89884
- 89885
- 89886
- 89887
- 89888
- 89889
- 89890
- 89891
- 89892
- 89893
- 89894
- 89895
- 89896
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-08T11:43:55.373989'
---
# WORK-253: Mechanical Retro-Before-Close Enforcement
