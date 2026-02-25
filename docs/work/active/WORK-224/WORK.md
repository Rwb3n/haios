---
template: work_item
id: WORK-224
title: "MCP Operations Governance Integration (Phase 3)"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-25
spawned_by: WORK-220
spawned_children: []
chapter: CH-066
arc: call
closed: null
priority: medium
effort: medium
traces_to:
- REQ-DISCOVER-002
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/haios_ops/mcp_server.py
- .claude/haios/modules/governance_layer.py
acceptance_criteria:
- "GovernanceLayer.check_activity() called per-tool in mcp_server.py"
- "Ceremony contract validation enforced for mutation tools"
- "Governance events logged for all MCP tool invocations"
- "Tests verify governance gate enforcement"
blocked_by: [WORK-223]
blocks: []
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
# WORK-224: MCP Operations Governance Integration (Phase 3)

---

## Context

WORK-220 (Phase 1) deferred GovernanceLayer integration per WORK-218 finding F3. Phase 1 tools use `ceremony_context` for ceremony boundaries but do not call `check_activity()` — governance gates are bypassed when agents use MCP tools directly. Phase 3 adds in-server governance: check_activity() per-tool, ceremony contract validation for mutations, and governance event logging. This completes CH-066 exit criterion 2: "Just recipes retired for agent use — MCP tools replace Tier 2 operations" (with governance parity).

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

- [ ] GovernanceLayer.check_activity() integrated per-tool in mcp_server.py
- [ ] Ceremony contract validation for mutation tools (work_create, work_close, queue_commit, etc.)
- [ ] Governance events logged for MCP tool invocations
- [ ] Tests verify governance enforcement and bypass rejection

---

## History

### 2026-02-25 - Created (Session 451)
- Initial creation

---

## References

- @docs/work/active/WORK-220/WORK.md (Phase 1 — deferred governance)
- @docs/work/active/WORK-223/WORK.md (Phase 2 — prerequisite)
- @docs/work/active/WORK-218/investigations/INVESTIGATION-WORK-218.md (F3: governance deferred)
- @.claude/haios/modules/governance_layer.py (check_activity API)
- @.claude/haios/haios_ops/mcp_server.py (integration target)
