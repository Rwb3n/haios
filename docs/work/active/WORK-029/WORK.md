---
template: work_item
id: WORK-029
title: Cleanup Dead MCP Code in .claude/haios/lib
type: cleanup
status: complete
owner: Hephaestus
created: 2026-01-28
spawned_by: WORK-028
chapter: null
arc: null
closed: '2026-01-28'
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
  entered: 2026-01-28 22:27:32
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-28
last_updated: '2026-01-28T23:24:11'
---
# WORK-029: Cleanup Dead MCP Code in .claude/haios/lib

@docs/README.md
@docs/epistemic_state.md

---

## Context

WORK-028 investigation found that `.claude/haios/lib/` contains partial copies of `haios_etl/` files with broken imports. These files were copied during earlier migration attempts but their dependencies weren't included. They cause confusion and will break if anyone tries to use them.

Files to delete:
- `mcp_server.py` - broken, real one is `haios_etl/mcp_server.py`
- `extraction.py` - broken imports from `preprocessors`
- `retrieval.py` - likely has broken dependencies too
- Any other files that import from haios_etl internals

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

- [x] Identify all dead MCP-related files in `.claude/haios/lib/`
- [x] Delete files with broken haios_etl dependencies
- [x] Verify no other code imports from deleted files
- [x] Update any references if found

---

## History

### 2026-01-28 - Completed (Session 255)
- Deleted 4 broken files: mcp_server.py, extraction.py, retrieval.py, synthesis.py
- These were partial copies from haios_etl/ with broken bare imports
- Deleted test_lib_retrieval.py (tested removed code)
- Updated test_lib_migration.py to remove references to deleted files
- Verified no runtime consumers imported from these files

### 2026-01-28 - Created (Session 247)
- Initial creation

---

## References

- [Related documents]
