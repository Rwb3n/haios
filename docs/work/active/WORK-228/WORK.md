---
template: work_item
id: WORK-228
title: Audit Just Recipe Consumers and Migrate to MCP Operations Tools
type: investigation
status: complete
owner: Hephaestus
created: '2026-02-25'
spawned_by: null
spawned_children:
- WORK-229
- WORK-230
chapter: CH-066
arc: call
closed: '2026-02-25'
priority: medium
effort: medium
traces_to:
- REQ-DISCOVER-002
requirement_refs: []
source_files:
- .claude/skills
- .claude/commands
- .claude/templates
- justfile
acceptance_criteria:
- Complete inventory of all just recipe references in skills, commands, templates,
  and hooks
- 'Each reference classified: MCP equivalent exists (migrate) vs no MCP equivalent
  (keep as Tier 3)'
- Spawned implementation work items for each migration batch
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CONCLUDE
node_history:
- node: backlog
  entered: '2026-02-25T16:34:04.295315'
  exited: '2026-02-25T16:44:39.978162'
artifacts: []
cycle_docs: {}
memory_refs:
- 89022
- 89023
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T16:44:39.984867'
queue_history:
- position: backlog
  entered: '2026-02-25T16:34:04.295315'
  exited: '2026-02-25T16:37:27.854460'
- position: ready
  entered: '2026-02-25T16:37:27.854460'
  exited: '2026-02-25T16:44:39.978162'
- position: done
  entered: '2026-02-25T16:44:39.978162'
  exited: null
---
# WORK-228: Audit Just Recipe Consumers and Migrate to MCP Operations Tools

---

## Context

WORK-225 (S456) migrated 9 skill/command files from `just` recipes to MCP tool references. However, the migration was scoped to known Tier 2 operations — it did not audit ALL `just` references across the entire skill/command/template surface. S457 discovered that `scaffold_checkpoint` MCP tool (added in WORK-226) has no consumer in checkpoint-cycle skill, confirming residual `just` references remain.

This investigation will:
1. Grep all skills, commands, templates, and hooks for `just ` references
2. Cross-reference against the MCP operations tool registry (25 tools as of WORK-226)
3. Classify each: MCP equivalent exists (should migrate) vs genuinely Tier 3 (keep)
4. Spawn implementation work for each migration batch

CH-066 exit criterion 2: "Just recipes retired for agent use — MCP tools replace Tier 2 operations."

---

## Deliverables

- [x] Complete inventory of `just` recipe references in agent-facing files
- [x] Classification table: migrate vs keep-as-Tier-3
- [x] Spawned implementation work items for migration batches

---

## History

### 2026-02-25 - Investigated (Session 457)
- Grepped all skills (58 hits), commands (35 hits), templates (3 natural language), agents (4 hits)
- Cross-referenced against 25 MCP tools in mcp_server.py
- Result: ~62 migratable references across 20 files, ~25 correctly Tier 3
- Spawned WORK-229 (skills cycle_set/clear/ready migration, 11 files)
- Spawned WORK-230 (scaffold commands + agent files, 11 files)
- Tier 3 keepers: git ops (commit-session, commit-close), audit-*, validate, tree, health, triage-observations, governance-metrics, events

---

## References

- @docs/work/active/WORK-225/WORK.md (prior targeted migration)
- @docs/work/active/WORK-226/WORK.md (scaffold/query MCP tools added)
- @.claude/haios/haios_ops/mcp_server.py (MCP tool registry)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md
