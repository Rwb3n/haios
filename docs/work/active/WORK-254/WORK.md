---
template: work_item
id: WORK-254
title: Frontmatter Schema Validation in Parsers
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria:
- chapter_frontmatter.py validates required fields on parse (id, name, arc, epoch,
  status)
- arc_frontmatter.py validates required fields on parse (id, name, epoch, theme, status)
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
  entered: '2026-03-07T14:31:42.800815'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:31:42.800815'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T14:31:42.800815'
---
# WORK-254: Frontmatter Schema Validation in Parsers
