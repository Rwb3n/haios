---
template: work_item
id: WORK-220
title: MCP Operations Server Core
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-25
spawned_by: WORK-218
spawned_children: []
chapter: CH-066
arc: call
closed: '2026-02-25'
priority: high
effort: medium
traces_to:
- REQ-DISCOVER-002
- REQ-CONFIG-001
requirement_refs: []
source_files:
- .claude/haios/haios_ops/mcp_server.py
- .claude/haios/haios_ops/__init__.py
- .claude/haios/haios_ops/bootstrap.py
- .mcp.json
acceptance_criteria:
- .claude/haios/haios_ops/ package created under .claude/haios/ for portability
- FastMCP('haios-operations') server with stdio transport
- 'Work tools: work_get, work_create, work_close, work_transition (~4 tools)'
- 'Queue tools: queue_ready, queue_list, queue_next, queue_prioritize, queue_commit,
  queue_park, queue_unpark (~7 tools)'
- 'Session tools: session_start, session_end, cycle_set, cycle_get, cycle_clear (~5
  tools)'
- All tools return typed JSON (not prose strings)
- bootstrap.py handles dual sys.path setup for modules/ and lib/
- .mcp.json updated with haios-operations server entry
- Tests verify each tool group with mocked backends
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-25 10:04:09
  exited: 2026-02-25 11:15:00
- node: PLAN
  entered: 2026-02-25 11:15:00
  exited: '2026-02-25T11:59:30.028032'
artifacts: []
cycle_docs: {}
memory_refs:
- 88750
- 88751
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T11:59:30.035195'
queue_history:
- position: done
  entered: '2026-02-25T11:59:30.028032'
  exited: null
---
# WORK-220: MCP Operations Server Core

---

## Context

WORK-218 investigation confirmed that a single `haios-operations` FastMCP server can wrap all operational Python modules as agent-native MCP tools. This is Phase 1: the core server with work, queue, and session tool groups (~15 tools).

**Architecture:**
- `.claude/haios/haios_ops/mcp_server.py` — FastMCP("haios-operations") with @mcp.tool() decorators
- `.claude/haios/haios_ops/bootstrap.py` — sys.path setup for `.claude/haios/modules/` and `.claude/haios/lib/`
- `.mcp.json` — second server entry alongside haios-memory
- Naming convention: `{domain}_{verb}` (e.g., `work_get`, `queue_ready`, `session_start`)

**Backing modules:** WorkEngine, queue_ceremonies, governance_events, cycle_state (extended by WORK-219), session_mgmt (new from WORK-219).

**Key design decisions (from WORK-218):**
- Single server (not split) — shared module state, one registration
- Tools for mutations, Resources for reads (CQRS) — resources deferred to Phase 2
- In-server governance via GovernanceLayer import — deferred to Phase 3
- Typed JSON returns from WorkState dataclass

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

- [ ] `.claude/haios/haios_ops/` package with `__init__.py`, `bootstrap.py`, `mcp_server.py`
- [ ] `bootstrap.py` with dual sys.path setup (modules/ + lib/) anchored from server location
- [ ] Work tools: `work_get`, `work_create`, `work_close`, `work_transition`
- [ ] Queue tools: `queue_ready`, `queue_list`, `queue_next`, `queue_prioritize`, `queue_commit`, `queue_park`, `queue_unpark`
- [ ] Session tools: `session_start`, `session_end`, `cycle_set`, `cycle_get`, `cycle_clear`
- [ ] All tools return typed JSON dicts (not prose strings)
- [ ] `.mcp.json` updated with haios-operations server entry pointing to `.claude/haios/haios_ops/`
- [ ] Tests in `tests/test_mcp_operations.py` covering all tool groups with mocked backends

---

## History

### 2026-02-25 - Created (Session 449)
- Spawned from WORK-218 (MCP Operations Server Investigation)
- Phase 1: core MCP server with work + queue + session tools
- Blocked by WORK-219 (state management abstractions prerequisite)

### 2026-02-25 - Operator directive (Session 450)
- haios_ops package moved from project root to `.claude/haios/haios_ops/` for portability
- Updated source_files, acceptance criteria, deliverables, context section

---

## References

- @docs/work/active/WORK-218/investigations/INVESTIGATION-WORK-218.md (source investigation)
- @docs/work/active/WORK-219/WORK.md (prerequisite — state management abstractions)
- @haios_etl/mcp_server.py (pattern to follow — note: haios_etl is at root, haios_ops moves to .claude/haios/)
- @.mcp.json (registration target)
- @.claude/haios/modules/work_engine.py (WorkEngine backing)
- @.claude/haios/lib/queue_ceremonies.py (queue operations backing)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (Tier model)
- Memory: 88698-88704 (WORK-218 investigation findings)
