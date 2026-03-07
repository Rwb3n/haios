---
template: work_item
id: WORK-276
title: Add _auto_promote_queue to advance_cycle_phase for completeness
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-256
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/cycle_state.py
acceptance_criteria:
- advance_cycle_phase() calls _auto_promote_queue() after sync_work_md_phase()
- Prevents potential gap where queue_position stays backlog/ready if set_cycle_state
  is skipped at cycle start
- Test covering advance_cycle_phase triggering auto-promote
- "Evidence: S476 WORK-256 retro WMI-1 \u2014 advance_cycle_phase at cycle_state.py:38-131\
  \ is a second entry point that doesn't auto-promote"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T19:38:18.579914'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T19:38:18.579914'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T19:38:18.579914'
---
# WORK-276: Add _auto_promote_queue to advance_cycle_phase for completeness
