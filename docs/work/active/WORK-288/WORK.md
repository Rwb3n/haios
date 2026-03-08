---
template: work_item
id: WORK-288
title: Auto-Prompt Exit Criteria Review When All Chapter Work Items Complete
type: implementation
status: active
owner: Hephaestus
created: '2026-03-08'
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
- .claude/haios/lib/status_propagator.py
- .claude/haios/lib/coldstart_orchestrator.py
acceptance_criteria:
- When StatusPropagator detects all chapter work items complete but exit criteria
  unchecked, surface a prompt to operator
- Coldstart validation or close-work-cycle CHAIN phase detects 'all items done, exit
  criteria pending' and suggests /close-chapter-ceremony
- Prevents silent drift where chapters stay In Progress indefinitely despite all work
  being done (CH-059/CH-061 S480 evidence)
- Mechanical — no judgment needed, just a computable predicate triggering a notification
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-08T13:23:41.218405'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-08T13:23:41.218405'
  exited: '2026-03-08T13:23:50.872434'
- position: parked
  entered: '2026-03-08T13:23:50.872434'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: [89199, 89200, 89226, 89843, 89865, 87791, 88439, 87835]
extensions: {}
version: '2.0'
generated: '2026-03-08'
last_updated: '2026-03-08T13:23:50.875433'
---
# WORK-288: Auto-Prompt Exit Criteria Review When All Chapter Work Items Complete
