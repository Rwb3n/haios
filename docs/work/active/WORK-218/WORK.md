---
template: work_item
id: WORK-218
title: MCP Operations Server Investigation
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-25
spawned_by: null
spawned_children:
- WORK-219
- WORK-220
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
- .mcp.json
- haios_etl/mcp_server.py
- .claude/haios/modules/cli.py
- .claude/haios/lib/queue_ceremonies.py
- .claude/haios/modules/work_engine.py
- justfile
acceptance_criteria:
- 'Tool taxonomy: complete mapping of operations to MCP tool names with naming convention'
- 'Scope boundary: which operations move to MCP vs stay in just (Tier 3)'
- 'Transport and packaging decision: single server vs multiple, stdio vs other'
- 'Unknown challenges identified: import paths, state management, error handling patterns'
- 'Innovation opportunities documented: what MCP enables beyond just-recipe parity'
- Spawned implementation work items with clear deliverables
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-25 09:42:29
  exited: '2026-02-25T10:06:15.395692'
artifacts: []
cycle_docs: {}
memory_refs:
- 86035
- 85949
- 85956
- 86012
- 85948
- 85950
- 85951
- 85958
- 88698
- 88699
- 88700
- 88701
- 88702
- 88703
- 88704
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T10:06:15.399251'
queue_history:
- position: ready
  entered: '2026-02-25T09:44:36.991424'
  exited: '2026-02-25T09:44:46.319434'
- position: working
  entered: '2026-02-25T09:44:46.319434'
  exited: '2026-02-25T10:06:15.395692'
- position: done
  entered: '2026-02-25T10:06:15.395692'
  exited: null
---
# WORK-218: MCP Operations Server Investigation

---

## Context

CH-066 (MCP Operations Server) is the largest remaining piece of E2.8 Arc 1 (call). The goal: expose work/queue/session/scaffold operations as native MCP tools, replacing `just` recipes for agent use (ADR-045 Tier 2).

**The problem:** Agents currently invoke operational recipes via `just X` through the Bash tool. This has three costs: (1) shell overhead and string parsing, (2) untyped inputs/outputs, (3) no discoverability — agents must be told which recipes exist via SKILL.md or CLAUDE.md (violates REQ-DISCOVER-002).

**What exists:** The `haios-memory` MCP server (FastMCP, stdio transport, 13 tools) provides a working pattern. All operational Python modules (`WorkEngine`, `queue_ceremonies`, `governance_events`, `scaffold`, `status`, `cycle_state`) are importable and ready to wrap. ~18 just recipes have no Tier 2 wrapper today.

**What's unknown:**
- Tool naming convention (S419 design note: naming is first-class UX)
- Scope boundary: not all 87 recipes should become MCP tools — which ones?
- Single server vs split (haios-operations vs per-domain servers)
- Import path challenges: lib/ and modules/ have different sys.path requirements
- State management: some recipes write to haios-status-slim.json inline — how does that translate?
- Innovation beyond parity: MCP enables typed returns, streaming, resource subscriptions — what new capabilities become possible?
- Integration with existing hooks: PreToolUse already gates some operations — how do MCP tool calls interact with hook governance?

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

- [ ] Investigation document with findings across all hypotheses
- [ ] Tool taxonomy: complete operation-to-tool mapping with naming convention
- [ ] Scope boundary analysis: MCP vs just, with rationale per operation group
- [ ] Technical feasibility: import paths, state management, error handling patterns validated
- [ ] Innovation analysis: capabilities beyond just-recipe parity
- [ ] Spawned implementation work item(s) with clear deliverables

---

## History

### 2026-02-25 - Created (Session 449)
- CH-066 MCPOperationsServer chapter exists at Planning status
- All dependency chapters complete (CH-061 ColdstartContextInjection)
- Operator direction: investigate before implement — discover unknown challenges and innovation opportunities
- Existing pattern: haios-memory MCP server (FastMCP, stdio, 13 tools)

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (Tier model)
- @.mcp.json (existing MCP server registration)
- @haios_etl/mcp_server.py (existing MCP server pattern)
- @justfile (recipes to be replaced)
- @.claude/haios/modules/work_engine.py (primary backing module)
- @.claude/haios/lib/queue_ceremonies.py (queue operations)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-002, REQ-CONFIG-001)
- Memory: 85390 (104% context problem), 85915-85922 (200k agent bypass observation)
