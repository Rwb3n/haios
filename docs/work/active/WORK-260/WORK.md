---
template: work_item
id: WORK-260
title: Frontmatter Schema Validation in Parsers
type: implementation
status: complete
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: '2026-03-07'
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria:
- chapter_frontmatter.py validates required fields on parse (id, name, arc, epoch,
  status)
- arc_frontmatter.py validates required fields on parse
- Malformed YAML raises clear error instead of silent propagation (mem:89456)
- Tests for validation error cases
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T14:33:14.566106'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:33:14.566106'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T14:33:14.566106'
---
# WORK-260: Frontmatter Schema Validation in Parsers

**CLOSED AS DUPLICATE** of WORK-254. Same title, same ACs. Created ~2 min after WORK-254 by duplicate session-end ceremony.
