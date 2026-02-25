---
template: work_item
id: WORK-230
title: Migrate Scaffold Commands and Agent Files to MCP Operations Tools
type: implementation
status: active
owner: Hephaestus
created: '2026-02-25'
spawned_by: WORK-228
spawned_children: []
chapter: CH-066
arc: call
closed: null
priority: medium
effort: medium
traces_to:
- REQ-DISCOVER-002
requirement_refs: []
source_files:
- .claude/commands/new-plan.md
- .claude/commands/new-work.md
- .claude/commands/new-investigation.md
- .claude/commands/new-checkpoint.md
- .claude/commands/new-adr.md
- .claude/commands/close.md
- .claude/commands/ready.md
- .claude/commands/haios.md
- .claude/commands/README.md
- .claude/agents/close-work-cycle-agent.md
- .claude/agents/validation-agent.md
acceptance_criteria:
- "new-plan.md uses scaffold_plan MCP tool instead of just plan"
- "new-work.md uses scaffold_work MCP tool instead of just work"
- "new-investigation.md uses scaffold_investigation MCP tool instead of just inv"
- "new-checkpoint.md uses scaffold_checkpoint MCP tool instead of just scaffold checkpoint"
- "new-adr.md uses scaffold_adr MCP tool instead of just adr"
- "close.md uses hierarchy_update_status instead of just update-status"
- "ready.md uses queue_ready MCP tool instead of just ready"
- "Agent files reference MCP tools instead of just recipes"
- "README.md updated to reflect MCP tools"
- "No regressions: all existing tests pass"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-02-25T16:39:53.301524'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T16:39:53.301524'
queue_history:
- position: backlog
  entered: '2026-02-25T16:39:53.301524'
  exited: null
---
# WORK-230: Migrate Scaffold Commands and Agent Files to MCP Operations Tools

---

## Context

WORK-228 audit found ~24 migratable `just` references across 11 command and agent files. These are scaffold commands (just plan/work/inv/adr/checkpoint) that now have MCP equivalents (scaffold_plan/work/investigation/adr/checkpoint), plus agent files still referencing just close-work and just update-status-slim.

Note: new-report.md and new-handoff.md have no MCP scaffold equivalent — these stay as Tier 3 (just recipes).

---

## Deliverables

- [ ] new-plan.md: just plan -> scaffold_plan MCP
- [ ] new-work.md: just work -> scaffold_work MCP
- [ ] new-investigation.md: just inv -> scaffold_investigation MCP
- [ ] new-checkpoint.md: just scaffold checkpoint -> scaffold_checkpoint MCP
- [ ] new-adr.md: just adr -> scaffold_adr MCP
- [ ] close.md: just update-status -> hierarchy_update_status MCP
- [ ] ready.md: just ready -> queue_ready MCP
- [ ] haios.md: just update-status-slim -> hierarchy_update_status MCP
- [ ] close-work-cycle-agent.md: just close-work -> hierarchy_close_work MCP
- [ ] validation-agent.md: just update-status-slim -> hierarchy_update_status MCP
- [ ] README.md: references updated

---

## References

- @docs/work/active/WORK-228/WORK.md (parent audit)
- @docs/work/active/WORK-225/WORK.md (prior migration — pattern to follow)
