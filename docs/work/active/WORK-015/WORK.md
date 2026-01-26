---
template: work_item
id: WORK-015
title: RequirementExtractor Module Implementation
type: feature
status: complete
owner: Hephaestus
created: 2026-01-25
spawned_by: null
chapter: CH-002
arc: pipeline
closed: '2026-01-26'
priority: medium
effort: medium
traces_to:
- REQ-TRACE-004
- REQ-TRACE-005
requirement_refs: []
source_files:
- .claude/haios/modules/requirement_extractor.py
acceptance_criteria:
- TRDParser extracts R0-R8 style requirement tables
- ManifestoParser extracts REQ-{DOMAIN}-{NNN} patterns
- NaturalLanguageParser extracts "must allow" statements
- Output conforms to RequirementSet schema
- Provenance tracked (file, line_range, doc_type)
- CLI command extract-requirements works
- Tests verify extraction from sample docs
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-25 22:35:52
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82430
- 82431
- 82432
- 82438
- 65046
- 82447
- 82448
- 65048
- 82449
- 82450
- 82451
- 82452
- 82453
- 82454
extensions: {}
version: '2.0'
generated: 2026-01-25
last_updated: '2026-01-26T18:46:42'
---
# WORK-015: RequirementExtractor Module Implementation

@docs/README.md
@docs/epistemic_state.md
@.claude/haios/epochs/E2_3/arcs/pipeline/CH-002-requirement-extractor.md

---

## Context

HAIOS has requirements scattered across multiple document formats (TRDs, L4 manifesto, prose). The pipeline PLAN stage needs structured RequirementSet as input, but no extractor produces it.

This work item implements the RequirementExtractor module as defined in CH-002.

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

- [x] TRDParser class that extracts R0-R8 requirement tables
- [x] ManifestoParser class that extracts REQ-{DOMAIN}-{NNN} patterns
- [x] NaturalLanguageParser class that extracts "must allow" statements
- [x] RequirementSet dataclass conforming to schema
- [x] RequirementExtractor main class with extract() and extract_from_file()
- [x] CLI integration via cli.py extract-requirements command
- [x] Tests covering all parsers with sample documents

---

## History

### 2026-01-25 - Created (Session 242)
- Initial creation (with placeholder type)

### 2026-01-26 - Fixed (Session 243)
- Fixed type placeholder: {{TYPE}} -> feature
- Added chapter: CH-002, arc: pipeline
- Added traces_to: REQ-TRACE-004, REQ-TRACE-005
- Populated deliverables from CH-002 success criteria
- Added source_files and acceptance_criteria

---

## References

- @.claude/haios/epochs/E2_3/arcs/pipeline/CH-002-requirement-extractor.md (chapter definition)
- @docs/work/active/INV-019/investigations/001-requirements-synthesis.md (design source)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (stage interface)
