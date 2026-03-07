---
template: work_item
id: WORK-272
title: ARC.md Status Propagation Drift — Batch Fix 6 Stale Entries
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-251
spawned_children:
- WORK-277
- WORK-280
- WORK-281
- WORK-282
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_8/arcs/call/ARC.md
- .claude/haios/epochs/E2_8/arcs/infrastructure/ARC.md
- .claude/haios/lib/status_propagator.py
acceptance_criteria:
- 'Fix 6 stale ARC.md entries: WORK-160, WORK-167, WORK-162, WORK-180, WORK-244, WORK-245
  (complete in WORK.md but stale in ARC.md)'
- 'Investigate root cause: StatusPropagator not triggered or failing silently on close'
- 'Convergence: 10 related memory entries across 9 affected work items (enrichment)'
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-07T18:20:43.176037'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T18:20:43.176037'
  exited: '2026-03-07T20:41:45.123257'
- position: working
  entered: '2026-03-07T20:41:45.123257'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89840
- 89841
- 89842
- 89843
- 89844
- 89845
- 89846
- 89847
- 89865
- 89866
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T20:47:09.913617'
---
# WORK-272: ARC.md Status Propagation Drift — Batch Fix 6 Stale Entries
