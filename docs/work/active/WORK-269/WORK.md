---
template: work_item
id: WORK-269
title: "Frontmatter-First Migration \u2014 StatusPropagator and EpochValidator"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/status_propagator.py
- .claude/haios/lib/epoch_validator.py
acceptance_criteria:
- StatusPropagator uses frontmatter-first with table surgery fallback (mem:89488)
- 'EpochValidator guard: test mode uses legacy path to avoid fixture conflicts (mem:89487)'
- Backward-compatible fallback per L3.6 at every consumer (mem:89486)
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T17:05:30.577133'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T17:05:30.577133'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T17:05:30.577133'
---
# WORK-269: Frontmatter-First Migration — StatusPropagator and EpochValidator
