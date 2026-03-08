---
template: work_item
id: WORK-290
title: "Enrich-on-Prioritize Ceremony \u2014 Quality Gate at Backlog-to-Ready Transition"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-08'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: high
effort: medium
traces_to:
- REQ-TRACE-002
- REQ-CEREMONY-005
- REQ-LIFECYCLE-005
requirement_refs: []
source_files:
- .claude/skills/queue-prioritize/SKILL.md
- .claude/haios/lib/scaffold.py
- .claude/haios/haios_ops/mcp_server.py
acceptance_criteria:
- queue-prioritize ceremony validates work item quality before backlog->ready transition
- 'Enrichment checklist: acceptance_criteria has 3+ testable items, source_files has
  1+ entry, traces_to has 1+ requirement, chapter assigned to non-Complete chapter'
- 'Warn-not-block mode: missing fields produce warnings with prompts to fill, not
  hard blocks (preserves batch flow)'
- 'Design reference: CALLSHEET work-item-decomposer 10-step pattern adapted for HAIOS
  (AC coverage, source_files validation, traces_to check)'
- 'Proportional: trivial/small items get inline checklist, standard+ items get full
  enrichment pass'
- 'Zero new infrastructure: enrichment logic in lib/ module, wired into queue_prioritize
  MCP tool or queue-prioritize skill'
- Existing scaffold guards (WORK-262 chapter validation, WORK-265 duplicate detection,
  WORK-271 traces_to enforcement) compose with this as creation-time warn + prioritize-time
  block
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-08T15:11:59.479515'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-08T15:11:59.479515'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-08'
last_updated: '2026-03-08T15:11:59.479515'
---
# WORK-290: Enrich-on-Prioritize Ceremony — Quality Gate at Backlog-to-Ready Transition
