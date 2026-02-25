---
template: work_item
id: WORK-230
title: Migrate Scaffold Commands and Agent Files to MCP Operations Tools
type: implementation
status: complete
owner: Hephaestus
created: '2026-02-25'
spawned_by: WORK-228
spawned_children: []
chapter: CH-066
arc: call
closed: '2026-02-25'
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
- new-plan.md uses scaffold_plan MCP tool instead of just plan
- new-work.md uses scaffold_work MCP tool instead of just work
- new-investigation.md uses scaffold_investigation MCP tool instead of just inv
- new-checkpoint.md uses scaffold_checkpoint MCP tool instead of just scaffold checkpoint
- new-adr.md uses scaffold_adr MCP tool instead of just adr
- close.md uses hierarchy_update_status instead of just update-status
- ready.md uses queue_ready MCP tool instead of just ready
- haios.md uses hierarchy_update_status MCP tool instead of just update-status-slim
- close-work-cycle-agent.md uses hierarchy_close_work MCP tool instead of just close-work
- validation-agent.md uses hierarchy_update_status MCP tool instead of just update-status-slim
- README.md updated to reflect MCP tools
- 'No regressions: all existing tests pass'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-02-25T16:39:53.301524'
  exited: '2026-02-25T22:02:41.407264'
artifacts: []
cycle_docs: {}
memory_refs:
- 89051
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T22:02:41.411922'
queue_history:
- position: backlog
  entered: '2026-02-25T16:39:53.301524'
  exited: '2026-02-25T21:34:23.770956'
- position: ready
  entered: '2026-02-25T21:34:23.770956'
  exited: '2026-02-25T21:34:26.478248'
- position: working
  entered: '2026-02-25T21:34:26.478248'
  exited: '2026-02-25T22:02:41.407264'
- position: done
  entered: '2026-02-25T22:02:41.407264'
  exited: null
---
# WORK-230: Migrate Scaffold Commands and Agent Files to MCP Operations Tools

---

## Context

WORK-228 audit found ~24 migratable `just` references across 11 command and agent files. These are scaffold commands (just plan/work/inv/adr/checkpoint) that now have MCP equivalents (scaffold_plan/work/investigation/adr/checkpoint), plus agent files still referencing just close-work and just update-status-slim.

Note: new-report.md and new-handoff.md have no MCP scaffold equivalent — these stay as Tier 3 (just recipes).

---

## Deliverables

- [x] new-plan.md: just plan -> scaffold_plan MCP
- [x] new-work.md: just work -> scaffold_work MCP
- [x] new-investigation.md: just inv -> scaffold_investigation MCP
- [x] new-checkpoint.md: just scaffold checkpoint -> scaffold_checkpoint MCP
- [x] new-adr.md: just adr -> scaffold_adr MCP
- [x] close.md: just update-status -> hierarchy_update_status MCP
- [x] ready.md: just ready -> queue_ready MCP
- [x] haios.md: just update-status-slim -> hierarchy_update_status MCP
- [x] close-work-cycle-agent.md: just close-work -> hierarchy_close_work MCP
- [x] validation-agent.md: just update-status-slim -> hierarchy_update_status MCP
- [x] README.md: references updated

---

## History

### 2026-02-25 - Implemented (Session 458)
- All 11 command/agent markdown files migrated from `just` recipes to MCP tool references
- Critique caught 3 issues (haios.md placeholder tokens, README prose verify gap, close.md `just ready` verify gap) across 2 passes
- Design review: PASS — 26 alignment points verified, 0 deviations
- 1767 tests pass, 0 new failures (2 pre-existing unrelated)
- Zero-iteration success (text-only migration, no Python code changed)

### 2026-02-25 - Created (Session 457)
- Spawned from WORK-228 audit

---

## References

- @docs/work/active/WORK-228/WORK.md (parent audit)
- @docs/work/active/WORK-225/WORK.md (prior migration — pattern to follow)
