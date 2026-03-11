---
template: work_item
id: WORK-307
title: 'Investigation: Lib Functions Without CLI/MCP Wrappers — Agent Forced to Use
  Bash Python One-Liners'
type: investigation
status: active
owner: Hephaestus
created: '2026-03-11'
spawned_by: WORK-289
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/retro_scale.py
- .claude/haios/lib/scaffold.py
- .claude/haios/haios_ops/mcp_server.py
acceptance_criteria:
- Audit .claude/haios/lib/*.py for functions that agents call but have no MCP tool
  or just recipe wrapper
- Identify which lib functions are called via Bash python one-liners (e.g., assess_scale,
  get_next_work_id, scaffold_template)
- Determine which should get MCP tool wrappers in haios-operations server vs just
  recipes vs stay as-is
- 'Findings doc with prioritized list: high-frequency agent calls first'
- 'CLAUDE.md rule 1 violation: Module-First Principle requires cli/just/modules path,
  not raw python -c'
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-11T00:11:33.405606'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-11T00:11:33.405606'
  exited: '2026-03-11T00:11:38.100365'
- position: parked
  entered: '2026-03-11T00:11:38.100365'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-11'
last_updated: '2026-03-11T00:11:38.103363'
---
# WORK-307: Investigation: Lib Functions Without CLI/MCP Wrappers — Agent Forced to Use Bash Python One-Liners
