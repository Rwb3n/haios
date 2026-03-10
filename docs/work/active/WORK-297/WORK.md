---
template: work_item
id: WORK-297
title: "Investigation: MCP tool contract validation \u2014 Extend ceremony contracts\
  \ to MCP invocation path"
type: investigation
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
- .claude/hooks/hooks/pre_tool_use.py
- .claude/haios/lib/ceremony_contracts.py
- .claude/haios/haios_ops/mcp_server.py
acceptance_criteria:
- Investigate whether MCP tool inputs should be validated against ceremony contracts
- Determine if PreToolUse hook matcher should include MCP tools or if validation belongs
  in mcp_server.py
- 'Evaluate: is contract validation at MCP layer redundant with MCP tool parameter
  validation?'
- 'Findings doc with recommendation: extend hook matcher vs inline validation vs accept
  MCP-path is unvalidated'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T21:59:30.966626'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T21:59:30.966626'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T21:59:30.966626'
---
# WORK-297: Investigation: MCP tool contract validation — Extend ceremony contracts to MCP invocation path
