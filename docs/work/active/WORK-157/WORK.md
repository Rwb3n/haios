---
template: work_item
id: WORK-157
title: Hierarchy Query Engine
type: feature
status: active
owner: Hephaestus
created: 2026-02-17
spawned_by: null
spawned_children: []
chapter: CH-044
arc: engine-functions
closed: null
priority: high
effort: large
traces_to:
- REQ-TRACE-005
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- get_arcs() returns list of arc metadata from EPOCH.md or arc directory
- get_chapters(arc_id) returns list of chapters for a given arc
- get_work(chapter_id) returns list of work items for a given chapter
- 'get_hierarchy(work_id) returns full chain: work -> chapter -> arc -> epoch'
- No manual path resolution needed for hierarchy navigation
- Engine functions are callable from modules and lib
- Tests for all query functions (unit + integration)
blocked_by: []
blocks: []
enables:
- CH-048
queue_position: working
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-17 08:22:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.7
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-17T18:50:57.146729'
queue_history:
- position: ready
  entered: '2026-02-17T18:50:57.116571'
  exited: '2026-02-17T18:50:57.143204'
- position: working
  entered: '2026-02-17T18:50:57.143204'
  exited: null
---
# WORK-157: Hierarchy Query Engine

---

## Context

**Problem:** Agents currently navigate the hierarchy (epoch -> arc -> chapter -> work item) by reading files manually with hardcoded path patterns. There are no callable functions to query "which arcs exist?", "which chapters are in this arc?", or "what's the full hierarchy chain for WORK-157?". This makes hierarchy discovery fragile and non-composable.

**Root cause:** The hierarchy is stored in markdown files (EPOCH.md, ARC.md) with table-formatted data. No engine functions exist to parse and query this structure programmatically.

**Evidence:** CH-045 (StatusCascade, WORK-034) had to implement cascade logic without engine functions. The engine-functions arc exit criteria explicitly require `get_arcs()`, `get_chapters()`, `get_work()` as callable functions.

**Scope:** Build engine query functions that parse the existing markdown hierarchy into queryable data structures. No schema migration — read from existing files.

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

- [ ] `get_arcs()` function returning arc metadata from epoch config
- [ ] `get_chapters(arc_id)` function returning chapter list from ARC.md
- [ ] `get_work(chapter_id)` function returning work items for a chapter
- [ ] `get_hierarchy(work_id)` function returning full chain (work -> chapter -> arc -> epoch)
- [ ] Unit tests for all query functions
- [ ] Integration test with real epoch/arc/chapter files

---

## History

### 2026-02-17 - Created (Session 392)
- Spawned from CH-044 HierarchyQueryEngine (engine-functions arc, E2.7)
- REQ-TRACE-005 traceability

---

## References

- @.claude/haios/epochs/E2_7/arcs/engine-functions/ARC.md
- @.claude/haios/epochs/E2_7/EPOCH.md
- @.claude/haios/manifesto/L4/functional_requirements.md
