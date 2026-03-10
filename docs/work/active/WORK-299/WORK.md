---
template: work_item
id: WORK-299
title: "Retro EXTRACT Auto-Spawn to Parked \u2014 Materialize findings as work items\
  \ for triage"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-10'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: high
effort: small
traces_to:
- REQ-LIFECYCLE-004
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/skills/retro-cycle/SKILL.md
- .claude/haios/lib/retro_scale.py
acceptance_criteria:
- 'Retro EXTRACT phase auto-spawns work items at queue_position: parked for each extracted
  item with confidence >= medium'
- Spawned items have spawned_by traceability to the parent work item
- Spawned items include type (bug/feature/refactor/upgrade), evidence, suggested_priority
  from EXTRACT output
- Triage becomes prioritization of parked items, not memory search for buried entries
- Trivial-scale retros (max 2 extracts) spawn max 2 parked items
- Substantial-scale retros spawn uncapped parked items
- 'Memory storage still happens (dual-write: memory + work item) for cross-session
  convergence signal'
- "Operator directive S479: capture the thought, don't lose it \u2014 filter happens\
  \ at prioritization"
- Dependent on WORK-289 (tiered sessions) for full value but can be implemented independently
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T22:19:12.986318'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T22:19:12.986318'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T22:19:12.986318'
---
# WORK-299: Retro EXTRACT Auto-Spawn to Parked — Materialize findings as work items for triage
