---
template: work_item
id: WORK-272
title: "ARC.md Status Propagation Drift \u2014 Batch Fix 6 Stale Entries"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-251
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_8/arcs/call/ARC.md
- .claude/haios/lib/status_propagator.py
acceptance_criteria:
- 'Fix 6 stale ARC.md entries: WORK-160, WORK-167, WORK-162, WORK-180, WORK-244, WORK-245
  (complete in WORK.md but stale in ARC.md)'
- 'Investigate root cause: StatusPropagator not triggered or failing silently on close'
- 'Convergence: 10 related memory entries across 9 affected work items (enrichment)'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T18:20:43.176037'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T18:20:43.176037'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T18:20:43.176037'
---
# WORK-272: ARC.md Status Propagation Drift — Batch Fix 6 Stale Entries
