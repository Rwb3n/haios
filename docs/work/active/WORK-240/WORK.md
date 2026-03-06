---
template: work_item
id: WORK-240
title: "Investigation: Epoch/Arc/Chapter File Format Structuring"
type: investigation
status: active
owner: Hephaestus
created: '2026-03-06'
spawned_by: WORK-222
spawned_children: []
chapter: ''
arc: ''
closed: null
priority: medium
effort: medium
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_8/EPOCH.md
- .claude/haios/epochs/E2_8/arcs/call/ARC.md
- .claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md
- .claude/haios/lib/status_propagator.py
- .claude/haios/lib/hierarchy_engine.py
acceptance_criteria:
- "Inventory of all fields currently expressed as markdown conventions vs frontmatter across EPOCH.md, ARC.md, CHAPTER.md"
- "Design proposal: which fields should become structured frontmatter (exit_criteria, status, work items, dependencies)"
- "Migration path: how to transition existing files without breaking consumers (HierarchyQueryEngine, StatusPropagator, coldstart loaders)"
- "Consumer impact assessment: which modules parse these files and what they expect"
- "Decision on scope: CHAPTER.md only, or also ARC.md and EPOCH.md"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-06T22:11:36.437963'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-06T22:11:36.437963'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-06'
last_updated: '2026-03-06T22:11:36.437963'
---
# WORK-240: Investigation: Epoch/Arc/Chapter File Format Structuring

---

## Context

WORK-222 investigation revealed that CHAPTER.md (and ARC.md, EPOCH.md) use unstructured markdown conventions for machine-relevant fields: exit criteria are checkboxes, status is bold text, work item tables are markdown. Every machine consumer (StatusPropagator, HierarchyQueryEngine, coldstart loaders, drift detection) must regex-parse these conventions, leading to fragile code and silent drift.

Work items already have structured YAML frontmatter that WorkEngine parses reliably. This investigation asks: should epoch/arc/chapter files follow the same pattern?

**Operator signal (S462):** "Are we reaching a stage where we need to review the formal format of our epoch/arc/chapter files?"

---

## Deliverables

- [ ] Inventory of markdown-convention fields vs frontmatter across hierarchy files
- [ ] Design proposal for structured frontmatter on CHAPTER.md (at minimum)
- [ ] Migration path and consumer impact assessment
- [ ] Scope decision (CHAPTER only vs full hierarchy)

---

## References

- @docs/work/active/WORK-222/WORK.md (spawning investigation)
- @.claude/haios/lib/status_propagator.py (consumer example: regex parsing)
- @.claude/haios/lib/hierarchy_engine.py (consumer example: markdown table parsing)
- Memory: 87133, 87137, 87141 (prior observations on propagator limitations)
