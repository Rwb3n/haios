---
template: work_item
id: WORK-028
title: MCP haios-memory Server Connection Failure
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-28
spawned_by: null
chapter: null
arc: null
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-28 22:11:56
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-28
last_updated: '2026-01-28T22:28:55'
---
# WORK-028: MCP haios-memory Server Connection Failure

@docs/README.md
@docs/epistemic_state.md

---

## Context

The MCP (Model Context Protocol) server `haios-memory` is failing to connect during Claude Code sessions. This breaks the intended memory query and ingestion path, forcing fallback to direct `haios_etl` module calls which bypass governance.

**Observed symptoms (Session 254):**
1. `/mcp` command shows "Failed to reconnect to haios-memory"
2. `schema-verifier` subagent reports "mcp__haios-memory__db_query tool not available"
3. Memory operations only work via direct Python calls to `haios_etl` modules
4. `MemoryBridge` module degrades gracefully but loses MCP benefits

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

- [ ] Root cause identified for MCP connection failure
- [ ] MCP server configuration verified or fixed
- [ ] Connection test passes (`/mcp` shows connected)
- [ ] Investigation findings stored to memory

---

## History

### 2026-01-28 - Created (Session 247)
- Initial creation

---

## References

- [Related documents]
