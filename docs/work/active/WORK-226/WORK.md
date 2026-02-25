---
template: work_item
id: WORK-226
title: 'MCP Operations Server Phase 4: Scaffold and Query Tools'
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-25
spawned_by: WORK-224
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
- .claude/haios/haios_ops/mcp_server.py
- .claude/haios/modules/work_engine.py
- .claude/haios/modules/spawn_tree.py
- .claude/haios/modules/cli.py
- .claude/haios/lib/scaffold.py
acceptance_criteria:
- scaffold_checkpoint MCP tool creates checkpoint files (replaces just checkpoint)
- scaffold_investigation MCP tool creates investigation work items (replaces just
  inv)
- scaffold_adr MCP tool creates ADR files (replaces just adr)
- link_document MCP tool links documents to work items (replaces just link)
- spawn_tree MCP tool returns spawn tree for a work item (replaces just spawns)
- Tests cover all new tools with mocked backends
blocked_by: []
blocks:
- WORK-225
enables: []
queue_position: done
cycle_phase: done
current_node: DONE
node_history:
- node: backlog
  entered: 2026-02-25 14:22:53
  exited: '2026-02-25T15:03:21.112667'
artifacts: []
cycle_docs: {}
memory_refs:
- 88876
- 88877
- 88878
- 88879
- 88880
- 88881
- 88882
- 88883
- 88884
- 88885
- 88886
- 88887
- 88888
- 88889
- 88890
- 88891
- 88892
- 88893
- 88894
- 88895
- 88896
- 88897
- 88898
- 88899
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T15:03:21.117343'
queue_history:
- position: ready
  entered: '2026-02-25T14:34:17.268879'
  exited: '2026-02-25T14:34:21.411756'
- position: working
  entered: '2026-02-25T14:34:21.411756'
  exited: '2026-02-25T15:03:21.112667'
- position: done
  entered: '2026-02-25T15:03:21.112667'
  exited: null
---
# WORK-226: MCP Operations Server Phase 4: Scaffold and Query Tools

---

## Context

Phases 1-3 (WORK-220/223/224) built the MCP Operations Server with 25 tools covering work, queue, session, scaffold (work+plan), hierarchy, and coldstart operations. Session 454 audit of `just --list` vs MCP tools found 5 agent-facing recipes with no MCP equivalent. These recipes are used in skills (checkpoint-cycle, /new-investigation, /new-adr, work-creation-cycle, close ceremonies) and force agents back to Bash when MCP tools should be available.

New tools needed:
1. `scaffold_checkpoint` — checkpoint-cycle uses `just checkpoint`
2. `scaffold_investigation` — /new-investigation uses `just inv`
3. `scaffold_adr` — /new-adr uses `just adr`
4. `link_document` — work-creation-cycle uses `just link`
5. `spawn_tree` — close ceremonies use `just spawns`

WORK-225 (skill consumer migration) is partially blocked by this — some skills reference recipes that have no MCP equivalent yet.

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

- [ ] scaffold_checkpoint MCP tool added to mcp_server.py
- [ ] scaffold_investigation MCP tool added to mcp_server.py
- [ ] scaffold_adr MCP tool added to mcp_server.py
- [ ] link_document MCP tool added to mcp_server.py
- [ ] spawn_tree MCP tool added to mcp_server.py (read-only query)
- [ ] All 5 tools gated with _check_tool_gate per WORK-224 pattern
- [ ] Tests for all 5 new tools
- [ ] CH-066 CHAPTER.md work item table updated with WORK-225 and WORK-226

---

## History

### 2026-02-25 - Created (Session 454)
- Initial creation

---

## References

- @docs/work/active/WORK-220/WORK.md (Phase 1 — MCP server core)
- @docs/work/active/WORK-223/WORK.md (Phase 2 — extended tools)
- @docs/work/active/WORK-224/WORK.md (Phase 3 — governance integration)
- @docs/work/active/WORK-225/WORK.md (consumer migration — partially blocked by this)
- @.claude/haios/haios_ops/mcp_server.py (integration target)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md
