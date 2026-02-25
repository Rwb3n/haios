---
template: work_item
id: WORK-223
title: "MCP Operations Extended Tools (Phase 2)"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-25
spawned_by: WORK-220
spawned_children: []
chapter: CH-066
arc: call
closed: null
priority: high
effort: medium
traces_to:
- REQ-DISCOVER-002
- REQ-CONFIG-001
requirement_refs: []
source_files:
- .claude/haios/haios_ops/mcp_server.py
acceptance_criteria:
- "Scaffold tools added: scaffold_work, scaffold_plan (wrapping scaffold_template)"
- "Hierarchy tools added: cascade, update_status, close_work (wrapping just recipes)"
- "Coldstart tool added: coldstart_orchestrator (wrapping cli.py coldstart)"
- "MCP Resources for read-only queries (CQRS pattern from WORK-218 F2)"
- "All new tools return typed JSON dicts"
- "Tests cover all new tool groups"
blocked_by: []
blocks: [WORK-224]
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-25T12:10:11
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-25
last_updated: 2026-02-25T12:10:11
---
# WORK-223: MCP Operations Extended Tools (Phase 2)

---

## Context

WORK-220 (Phase 1) delivered work, queue, and session tools. But agents still call `just` recipes for scaffold, hierarchy, close-work, update-status, and coldstart operations. Phase 2 adds these remaining tool groups plus MCP Resources (CQRS read pattern from WORK-218 F2) to complete CH-066 exit criterion 1: "haios-operations MCP server exposes work/hierarchy/session/scaffold tools."

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

- [ ] Scaffold tool group added to haios_ops/mcp_server.py
- [ ] Hierarchy/status tool group added (cascade, update_status, close_work)
- [ ] Coldstart orchestrator tool added
- [ ] MCP Resources for read-only queries (CQRS)
- [ ] Tests for all new tool groups

---

## History

### 2026-02-25 - Created (Session 451)
- Initial creation

---

## References

- @docs/work/active/WORK-220/WORK.md (Phase 1 — prerequisite)
- @docs/work/active/WORK-218/investigations/INVESTIGATION-WORK-218.md (F2: Resources/CQRS)
- @.claude/haios/haios_ops/mcp_server.py (extend with new tool groups)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (Tier 2 completion)
