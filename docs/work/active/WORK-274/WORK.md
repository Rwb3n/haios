---
template: work_item
id: WORK-274
title: "Investigation: WORK.md Mutation Ordering \u2014 Prevent Stale-Read Failures\
  \ from MCP Side Effects"
type: investigation
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
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/cycle_state.py
- .claude/haios/haios_ops/mcp_server.py
- .claude/skills/implementation-cycle/phases/PLAN.md
acceptance_criteria:
- Map all MCP tools that mutate WORK.md as side effect (cycle_set, queue_prioritize,
  queue_commit, hierarchy_close_work, etc.)
- Identify every lifecycle step where agent reads WORK.md before calling a mutating
  MCP tool
- 'Determine canonical action ordering at each lifecycle boundary (e.g., PLAN entry:
  critique + edit WORK.md THEN cycle_set)'
- Findings doc with ordering convention or code fix (e.g., cycle_set returns updated
  content, or skill instructions enforce edit-before-set)
- "Evidence: S475 WORK-251 Edit failure at PLAN entry \u2014 cycle_set invalidated\
  \ prior Read of WORK.md"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T18:27:41.690696'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T18:27:41.690696'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T18:27:41.690696'
---
# WORK-274: Investigation: WORK.md Mutation Ordering — Prevent Stale-Read Failures from MCP Side Effects
