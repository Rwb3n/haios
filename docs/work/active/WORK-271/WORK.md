---
template: work_item
id: WORK-271
title: "Batch Scaffold Traceability \u2014 Enforce traces_to and Chapter Registration\
  \ at Creation"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-251
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
- .claude/skills/work-creation-cycle/SKILL.md
acceptance_criteria:
- scaffold_work validates traces_to is non-empty before creating work item (warn or
  block)
- scaffold_work validates chapter field references an existing, non-Complete chapter
- "WORK-251 retro WCBB-1: S474 batch created 6 items with empty traceability \u2014\
  \ prevent recurrence"
- 'Convergence: 10 related memory entries (enrichment convergence_count=10)'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T18:20:38.183386'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T18:20:38.183386'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T18:20:38.183386'
---
# WORK-271: Batch Scaffold Traceability — Enforce traces_to and Chapter Registration at Creation
