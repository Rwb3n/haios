---
template: work_item
id: WORK-244
title: CHAPTER.md YAML Frontmatter Migration (Phase 1)
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-240
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: medium
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/lib/status_propagator.py
- .claude/haios/lib/dod_validation.py
- .claude/haios/lib/scaffold.py
acceptance_criteria:
- 'CHAPTER.md files have YAML frontmatter with: id, name, arc, epoch, status, work_items,
  exit_criteria, dependencies'
- status_propagator.py reads CHAPTER.md frontmatter instead of regex-parsing exit
  criteria checkboxes
- dod_validation.py reads CHAPTER.md frontmatter instead of _parse_markdown_field()
  for Status
- scaffold.py update_chapter_manifest() updates frontmatter dict instead of line-by-line
  table surgery
- Migration script converts all existing CHAPTER.md files to frontmatter format
- All existing tests pass after migration (backward-compatible fallback for missing
  frontmatter)
blocked_by: []
blocks:
- WORK-245
enables:
- WORK-245
queue_position: working
cycle_phase: DONE
current_node: DONE
node_history:
- node: backlog
  entered: '2026-03-07T00:07:54.769183'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T00:07:54.769183'
  exited: '2026-03-07T00:39:29.189954'
- position: ready
  entered: '2026-03-07T00:39:29.189954'
  exited: '2026-03-07T00:39:32.891248'
- position: working
  entered: '2026-03-07T00:39:32.891248'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89402
- 89403
- 89404
- 89405
- 89406
- 89407
- 89441
- 89442
- 89443
- 89444
- 89445
- 89446
- 89447
- 89448
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T01:11:05.141412'
---
# WORK-244: CHAPTER.md YAML Frontmatter Migration (Phase 1)

---

## Context

WORK-240 investigation found that CHAPTER.md files have zero YAML frontmatter, forcing 3 consumer modules (status_propagator, dod_validation, scaffold) to regex-parse machine-relevant fields. Each consumer reimplements parsing independently: exit criteria checkboxes parsed by 2 different regex patterns, status extracted via bold-markdown regex, work items table manipulated line-by-line.

WORK.md files already have structured YAML frontmatter that WorkEngine parses reliably. This work applies the same pattern to CHAPTER.md.

---

## Deliverables

- [ ] CHAPTER.md frontmatter schema defined (id, name, arc, epoch, status, work_items, exit_criteria, dependencies)
- [ ] Migration script: parse existing CHAPTER.md bold-markdown + tables -> inject frontmatter
- [ ] status_propagator.py: read frontmatter for exit criteria instead of regex
- [ ] dod_validation.py: read frontmatter for Status instead of _parse_markdown_field()
- [ ] scaffold.py: update frontmatter dict instead of table row surgery
- [ ] Backward-compatible fallback: if frontmatter missing, fall back to regex (L3.6)
- [ ] All tests pass

---

## References

- @docs/work/active/WORK-240/WORK.md (spawning investigation)
- @.claude/haios/lib/status_propagator.py (consumer: exit criteria, chapter status)
- @.claude/haios/lib/dod_validation.py (consumer: chapter Status, exit criteria)
- @.claude/haios/lib/scaffold.py (consumer: work items table read/write)
- Memory: 89402-89407 (WORK-240 investigation findings)
