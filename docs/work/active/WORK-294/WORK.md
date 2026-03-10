---
template: work_item
id: WORK-294
title: "Fix backlog_id_uniqueness false-positive \u2014 Scope search to frontmatter\
  \ only"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-10'
spawned_by: WORK-275
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-005
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- _check_backlog_id_uniqueness searches only frontmatter of existing files, not full
  content
- Use _extract_frontmatter() on each candidate file before matching backlog_id pattern
- Legacy plan files with backlog_id in code examples/test fixtures no longer trigger
  false positive
- "Exclude docs/plans/ (legacy path) from search scope \u2014 only check docs/work/active/"
- "Tests: Write file with backlog_id while legacy plan exists with same ID in body\
  \ text \u2014 no block"
- "Tests: Write file with genuinely duplicate backlog_id in active work \u2014 correctly\
  \ blocks"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T21:49:46.123207'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T21:49:46.123207'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T21:49:46.123207'
---
# WORK-294: Fix backlog_id_uniqueness false-positive — Scope search to frontmatter only
