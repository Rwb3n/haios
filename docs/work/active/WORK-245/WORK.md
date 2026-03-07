---
template: work_item
id: WORK-245
title: ARC.md YAML Frontmatter Migration (Phase 2)
type: implementation
status: complete
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-240
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: '2026-03-07'
priority: medium
effort: medium
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/lib/hierarchy_engine.py
- .claude/haios/lib/status_propagator.py
- .claude/haios/lib/epoch_loader.py
- .claude/haios/lib/epoch_validator.py
- .claude/haios/lib/dod_validation.py
acceptance_criteria:
- 'ARC.md files have YAML frontmatter with: id, epoch, theme, status, started, chapters
  (list), exit_criteria'
- hierarchy_engine.py reads ARC.md frontmatter instead of bold-markdown + table parsing
- status_propagator.py updates ARC.md frontmatter chapters list instead of pipe-split
  table row surgery
- epoch_loader.py reads ARC.md frontmatter chapters list instead of table extraction
- epoch_validator.py reads ARC.md frontmatter for drift detection
- dod_validation.py reads ARC.md frontmatter Status instead of _parse_markdown_field()
- Migration script converts all existing ARC.md files to frontmatter format
- 4 duplicate chapter table parsers eliminated
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-07T00:07:55.178399'
  exited: '2026-03-07T14:05:00'
- node: PLAN
  entered: '2026-03-07T14:05:00'
  exited: '2026-03-07T14:21:00.216323'
queue_history:
- position: backlog
  entered: '2026-03-07T00:07:55.178399'
  exited: '2026-03-07T14:05:00'
- position: working
  entered: '2026-03-07T14:05:00'
  exited: '2026-03-07T14:21:00.216323'
- position: done
  entered: '2026-03-07T14:21:00.216323'
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
- 89484
- 89485
- 89486
- 89487
- 89488
- 89489
- 89490
- 89491
- 89492
- 89551
- 89552
- 89553
- 89554
- 89555
- 89556
- 89557
- 89558
- 89574
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T14:21:00.222832'
---
# WORK-245: ARC.md YAML Frontmatter Migration (Phase 2)

---

## Context

WORK-240 investigation found that ARC.md's chapter table is the MOST parsed structure in the codebase — 4 separate implementations of pipe-split table parsing exist across hierarchy_engine, status_propagator, epoch_loader, and epoch_validator. Additionally, StatusPropagator updates ARC.md chapter rows but not EPOCH.md, causing silent drift (mem:87137).

Migrating the chapter table to frontmatter eliminates all 4 duplicate parsers and makes status updates a dict write instead of regex table surgery.

Depends on WORK-244 (CHAPTER.md migration) to establish the pattern and shared utilities.

---

## Deliverables

- [ ] ARC.md frontmatter schema defined (id, epoch, theme, status, started, chapters list, exit_criteria)
- [ ] Migration script: parse existing ARC.md bold-markdown + chapter table -> inject frontmatter
- [ ] hierarchy_engine.py: read frontmatter for arc metadata and chapters
- [ ] status_propagator.py: update frontmatter chapters list for status propagation
- [ ] epoch_loader.py: read frontmatter chapters list
- [ ] epoch_validator.py: read frontmatter for drift detection
- [ ] dod_validation.py: read frontmatter Status
- [ ] 4 duplicate table parsers eliminated
- [ ] All tests pass

---

## References

- @docs/work/active/WORK-240/WORK.md (spawning investigation)
- @docs/work/active/WORK-244/WORK.md (Phase 1 prerequisite)
- @.claude/haios/lib/hierarchy_engine.py (consumer: arc metadata, chapter table)
- @.claude/haios/lib/status_propagator.py (consumer: chapter status update)
- @.claude/haios/lib/epoch_loader.py (consumer: chapter table extraction)
- @.claude/haios/lib/epoch_validator.py (consumer: drift detection)
- Memory: 89402-89407 (WORK-240 investigation findings), 87137 (propagator drift)
