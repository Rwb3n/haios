---
template: work_item
id: WORK-296
title: Add MCP migration tracking to ceremony_registry.yaml
type: implementation
status: active
owner: Hephaestus
created: '2026-03-10'
spawned_by: WORK-275
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/config/ceremony_registry.yaml
acceptance_criteria:
- 'ceremony_registry.yaml entries have optional mcp_tool field (e.g., mcp_tool: mcp__haios-operations__queue_commit)'
- Queue ceremonies (commit, prioritize, intake, unpark) annotated with their MCP tool
  equivalents
- has_skill field reflects actual invocation path (true only if Skill path is actively
  used)
- Registry consumers can distinguish Skill-path vs MCP-path ceremonies for contract
  validation routing
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T21:59:25.242437'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T21:59:25.242437'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T21:59:25.242437'
---
# WORK-296: Add MCP migration tracking to ceremony_registry.yaml
