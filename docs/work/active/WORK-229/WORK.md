---
template: work_item
id: WORK-229
title: Migrate Remaining Skill cycle_set/clear/ready References to MCP
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
- .claude/skills/investigation-cycle/SKILL.md
- .claude/skills/work-creation-cycle/SKILL.md
- .claude/skills/close-arc-ceremony/SKILL.md
- .claude/skills/close-epoch-ceremony/SKILL.md
- .claude/skills/close-chapter-ceremony/SKILL.md
- .claude/skills/implementation-cycle/SKILL.md
- .claude/skills/implementation-cycle/phases/PLAN.md
- .claude/skills/implementation-cycle/phases/CHAIN.md
- .claude/skills/implementation-cycle/phases/CHECK.md
- .claude/skills/implementation-cycle/reference/composition.md
- .claude/skills/routing-gate/SKILL.md
acceptance_criteria:
- All just set-cycle references replaced with cycle_set MCP tool in skills
- All just clear-cycle references replaced with cycle_clear MCP tool in skills
- All just ready references replaced with queue_ready MCP tool in skills
- just update-status/update-status-slim replaced with hierarchy_update_status where
  applicable
- 'No regressions: all existing tests pass'
blocked_by: []
blocks: []
enables: []
queue_position: ready
cycle_phase: DO
current_node: DO
node_history:
- node: backlog
  entered: '2026-02-25T16:39:52.533618'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T16:48:25.604677'
queue_history:
- position: backlog
  entered: '2026-02-25T16:39:52.533618'
  exited: '2026-02-25T16:48:25.601161'
- position: ready
  entered: '2026-02-25T16:48:25.601161'
  exited: null
---
# WORK-229: Migrate Remaining Skill cycle_set/clear/ready References to MCP

---

## Context

WORK-228 audit found ~35 migratable `just` references across 10 skill files. These are all `just set-cycle`, `just clear-cycle`, `just ready`, and `just update-status` calls that have direct MCP equivalents (cycle_set, cycle_clear, queue_ready, hierarchy_update_status).

Files: investigation-cycle, work-creation-cycle, close-arc/chapter/epoch ceremonies, implementation-cycle (PLAN, CHAIN, CHECK, composition, routing-gate).

---

## Deliverables

- [ ] investigation-cycle/SKILL.md: 8 references migrated (5x set-cycle, 1x clear-cycle, 2x ready)
- [ ] work-creation-cycle/SKILL.md: 4 references migrated (4x set-cycle)
- [ ] close-arc-ceremony/SKILL.md: 4 references migrated (3x set-cycle, 1x clear-cycle)
- [ ] close-epoch-ceremony/SKILL.md: 4 references migrated (3x set-cycle, 1x clear-cycle)
- [ ] close-chapter-ceremony/SKILL.md: 4 references migrated (3x set-cycle, 1x clear-cycle)
- [ ] implementation-cycle secondary files: PLAN.md, CHAIN.md, CHECK.md, composition.md migrated
- [ ] routing-gate/SKILL.md: queue/ready references migrated

---

## References

- @docs/work/active/WORK-228/WORK.md (parent audit)
- @docs/work/active/WORK-225/WORK.md (prior migration — pattern to follow)
