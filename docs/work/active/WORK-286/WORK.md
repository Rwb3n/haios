---
template: work_item
id: WORK-286
title: Retire Just Recipes for Agent Use — Formal Tier 3 Demotion
type: implementation
status: active
owner: Hephaestus
created: '2026-03-08'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- justfile
- .claude/skills/survey-cycle/SKILL.md
acceptance_criteria:
- Grep all SKILL.md files for 'just ' commands — replace with MCP tool equivalents
  or remove
- Survey-cycle 'just set-queue' replaced with MCP tool call
- ADR-045 Tier 3 designation documented in justfile header comment
- PreToolUse hook warns on agent 'just' usage (soft gate)
- Arc exit criterion 'Just recipes retired for agent use' can be checked off
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-08T12:32:09.768909'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-08T12:32:09.768909'
  exited: '2026-03-08T12:32:14.828892'
- position: parked
  entered: '2026-03-08T12:32:14.828892'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-08'
last_updated: '2026-03-08T12:32:14.831890'
---
# WORK-286: Retire Just Recipes for Agent Use — Formal Tier 3 Demotion
