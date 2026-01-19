---
template: work_item
id: WORK-001
title: Implement Universal Work Item Structure
type: feature
status: complete
created: 2026-01-18
closed: '2026-01-19'
owner: null
priority: critical
effort: medium
requirement_refs: []
source_files:
- docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
acceptance_criteria:
- work_item.md template updated with universal structure
- WorkEngine handles new fields
- ID generation uses WORK-XXX format
- Validation checks new required fields
- First work item created and tracked
blocked_by: []
blocks: []
enables:
- WORK-002
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-18 16:32:33
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 81543
- 81544
- 81545
- 81546
- 81547
- 81548
- 81549
- 81550
- 81551
- 81552
- 81553
- 82142
- 82143
- 82144
- 82145
- 82146
- 82147
- 82148
- 82149
- 82149
- 82150
- 82151
- 82152
extensions: {}
version: '2.0'
generated: 2026-01-18
last_updated: '2026-01-19T16:41:54'
---
# WORK-001: Implement Universal Work Item Structure

---

## Context

Session 206 strategic review identified that HAIOS is a doc-to-product pipeline, not a PM system for itself. The current work item structure is HAIOS-specific (E2-XXX, INV-XXX prefixes, milestone fields) and not portable.

This work item implements the universal work item structure defined in TRD-WORK-ITEM-UNIVERSAL.md, enabling:
- Type as a field (not ID prefix)
- Pipeline traceability (requirement_refs, source_files, artifacts)
- Portability (no HAIOS-specific fields in core)
- Extensibility (extensions block for project-specific needs)

---

## Acceptance Criteria

- [x] `work_item.md` template updated with universal structure
- [x] WorkEngine handles new fields (requirement_refs, source_files, artifacts, extensions)
- [x] ID generation uses WORK-XXX format
- [x] Validation checks new required fields
- [x] First work item (this one) successfully created and tracked

---

## Deliverables

- [x] `.claude/templates/work_item.md` - Updated template
- [x] `.claude/haios/modules/work_engine.py` - Handle new fields
- [x] `.claude/lib/scaffold.py` - New ID generation
- [x] `.claude/lib/validate.py` - New validation rules
- [x] Tests pass (80 tests in related files)

---

## History

### 2026-01-19 - Implemented (Session 210)
- WorkState dataclass extended with 6 new fields (type, requirement_refs, etc.)
- _parse_work_file updated with backward compat (type fallback to category)
- get_next_work_id() added to scaffold for sequential WORK-XXX IDs
- Template updated to v2.0 with universal structure
- Validation rules added for type enum
- All tests pass (80 in related files)
- Operator decisions resolved: Sequential IDs, 5 types, frontmatter-only acceptance_criteria

### 2026-01-18 - Created (Session 206)
- First work item using universal structure
- Self-referential: implements the structure it uses
- Spawned from Form CH-006 (WorkUniversality) + S26 pipeline needs

---

## References

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md
- @.claude/haios/epochs/E2/arcs/form/ARC.md
