---
template: work_item
id: WORK-277
title: "Investigation: Frontmatter-Based Hierarchy Tracking \u2014 Replace ARC.md\
  \ Table Surgery with Structured Data"
type: investigation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-272
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: medium
effort: medium
traces_to:
- REQ-TRACE-003
requirement_refs: []
source_files:
- .claude/haios/lib/status_propagator.py
- .claude/haios/lib/epoch_validator.py
- .claude/haios/lib/chapter_frontmatter.py
- .claude/haios/lib/arc_frontmatter.py
- .claude/haios/epochs/E2_8/arcs/call/ARC.md
acceptance_criteria:
- Investigate whether ARC.md markdown tables can be replaced by frontmatter-based
  progress tracking (work items already have frontmatter with chapter/arc fields)
- Map all consumers of ARC.md table rows for chapter status (StatusPropagator, EpochValidator,
  coldstart, work_loader, etc.)
- 'Evaluate query pattern: ''all work items in CH-059'' via glob + frontmatter parse
  vs ARC.md table lookup'
- Determine if WORK.md frontmatter (chapter, arc, status fields) is sufficient as
  single source of truth for hierarchy relationships
- 'Findings doc with recommendation: migrate to frontmatter-derived hierarchy vs keep
  ARC.md tables vs hybrid approach'
- 'Address root cause of WORK-272 drift: 6 stale ARC.md entries because StatusPropagator
  table surgery is fragile and fails silently'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T20:19:40.207749'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T20:19:40.207749'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T20:19:40.207749'
---
# WORK-277: Investigation: Frontmatter-Based Hierarchy Tracking — Replace ARC.md Table Surgery with Structured Data
