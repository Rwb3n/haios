---
template: work_item
id: WORK-295
title: "Fix coldstart drift detection \u2014 Query WORK.md chapter fields instead\
  \ of ARC.md work_items list"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-10'
spawned_by: WORK-275
spawned_children: []
chapter: CH-061
arc: call
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/coldstart_orchestrator.py
acceptance_criteria:
- 'Coldstart VALIDATION phase checks chapter completion by scanning WORK.md chapter:
  fields, not ARC.md work_items list'
- CH-059 with 41 work items assigned via WORK.md chapter field no longer produces
  false drift warning
- ARC.md work_items list treated as documentation hint, not source of truth for completion
  check
- 'Tests: chapter with incomplete WORK.md items correctly detected as incomplete even
  if ARC.md work_items subset is complete'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T21:59:20.884926'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T21:59:20.884926'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T21:59:20.884926'
---
# WORK-295: Fix coldstart drift detection — Query WORK.md chapter fields instead of ARC.md work_items list
