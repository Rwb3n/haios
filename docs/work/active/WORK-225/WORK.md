---
template: work_item
id: WORK-225
title: Migrate Skill Consumers from Just Recipes to MCP Operations Tools
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-25
spawned_by: WORK-224
spawned_children: []
chapter: CH-066
arc: call
closed: '2026-02-25'
priority: high
effort: medium
traces_to:
- REQ-DISCOVER-002
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/commands/coldstart.md
- .claude/skills/survey-cycle/SKILL.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/checkpoint-cycle/SKILL.md
- .claude/skills/implementation-cycle/phases/DO.md
- .claude/skills/implementation-cycle/phases/CHECK.md
- .claude/skills/implementation-cycle/phases/DONE.md
- .claude/skills/session-start-ceremony/SKILL.md
- .claude/skills/session-end-ceremony/SKILL.md
acceptance_criteria:
- Skills reference MCP tools (cycle_set, cycle_clear, queue_ready, etc.) instead of
  just recipes for Tier 2 operations
- session-start/end skills use session_start/session_end MCP tools
- close-work-cycle uses hierarchy_close_work MCP tool instead of just close-work
- coldstart skill uses coldstart_orchestrator MCP tool instead of just coldstart-orchestrator
- 'No regressions: all existing tests pass after migration'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-25 14:19:10
  exited: 2026-02-25 15:15:00
- node: PLAN
  entered: 2026-02-25 15:15:00
  exited: '2026-02-25T15:55:20.312843'
artifacts: []
cycle_docs: {}
memory_refs:
- 88929
- 88930
- 88931
- 88932
- 88933
- 88973
- 88974
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T15:55:20.317292'
queue_history:
- position: done
  entered: '2026-02-25T15:55:20.312843'
  exited: null
---
# WORK-225: Migrate Skill Consumers from Just Recipes to MCP Operations Tools

---

## Context

WORK-220/223/224 (Sessions 451-454) built the MCP Operations Server with 25 tools covering work, queue, session, scaffold, hierarchy, and coldstart operations. However, all existing skills still reference `just` recipes (Tier 2) instead of MCP tools (Tier 1). Session 454 audit found 8 of 12 Bash/just invocations had direct MCP equivalents that were not used — because the skill templates hardcode `just` commands. This is the consumer migration that CH-066 exit criterion 2 requires: "Just recipes retired for agent use — MCP tools replace Tier 2 operations."

Migration map:
- `just coldstart-orchestrator` → `coldstart_orchestrator` MCP tool
- `just session-start {N}` → `session_start(N)` MCP tool
- `just session-end {N}` → `session_end(N)` MCP tool
- `just ready` → `queue_ready` MCP tool
- `just set-cycle {cycle} {phase} {work_id}` → `cycle_set(cycle, phase, work_id)` MCP tool
- `just clear-cycle` → `cycle_clear` MCP tool
- `just close-work {id}` → `hierarchy_close_work(id)` MCP tool
- `just update-status` → absorbed into `hierarchy_close_work` / `hierarchy_update_status`

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] coldstart command migrated: `just coldstart-orchestrator` → `coldstart_orchestrator` MCP tool
- [x] session-start-ceremony migrated: `just session-start` → `session_start` MCP tool
- [x] session-end-ceremony migrated: `just session-end` → `session_end` MCP tool
- [x] survey-cycle migrated: `just ready` → `queue_ready` MCP tool
- [x] close-work-cycle migrated: `just close-work` → `hierarchy_close_work`, `just set-cycle` → `cycle_set`, `just clear-cycle` → `cycle_clear`
- [x] implementation-cycle phases migrated: `just set-cycle` → `cycle_set` in DO.md, DONE.md, CHECK.md
- [x] checkpoint-cycle migrated: `just commit-session` remains (git — no MCP equivalent)

---

## History

### 2026-02-25 - Implemented (Session 456)
- All 9 skill/command files migrated from `just` recipes to MCP tool references
- Critique caught 5 work item issues (blocking: coldstart path wrong) + 6 plan assumptions across 2 passes
- Design review caught 1 missed prose reference in session-start-ceremony
- 1767 tests pass, 0 new failures (2 pre-existing unrelated)
- Zero-iteration TDD success (text-only migration, no Python code changed)

### 2026-02-25 - Created (Session 454)
- Initial creation

---

## References

- @docs/work/active/WORK-224/WORK.md (Phase 3 — built governance integration, session 454 audit identified this gap)
- @docs/work/active/WORK-220/WORK.md (Phase 1 — MCP server core)
- @docs/work/active/WORK-223/WORK.md (Phase 2 — extended tools)
- @.claude/haios/haios_ops/mcp_server.py (MCP tool implementations)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md (exit criterion 2)
