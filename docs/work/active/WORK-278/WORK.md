---
template: work_item
id: WORK-278
title: "Governance Events Log Rotation \u2014 Prune or Archive governance-events.jsonl"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-270
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/governance-events.jsonl
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- Implement log rotation or archival for governance-events.jsonl (currently 4.3MB
  unbounded)
- 'Options: epoch-scoped archival, size-based rotation, or session-count pruning'
- Archived events remain queryable (e.g., moved to governance-events-archive/ by epoch)
- Active log stays under a reasonable size threshold (e.g., current epoch only)
- "Evidence: S477 retro S1 \u2014 4,548 events/day across 10 sessions, log growing\
  \ unbounded"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T20:21:10.723794'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T20:21:10.723794'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T20:21:10.723794'
---
# WORK-278: Governance Events Log Rotation — Prune or Archive governance-events.jsonl
