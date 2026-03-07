---
template: work_item
id: WORK-251
title: "Coldstart Crash Recovery \u2014 Detect Unclosed Sessions"
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-061
arc: call
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria:
- Coldstart detects unclosed sessions in governance-events.jsonl (SessionStarted without
  SessionEnded)
- 'Surfaces recovery items: uncommitted CHAIN work, missing retros, split state'
- Emits synthetic SessionEnded for crashed sessions
- WORK items left in CHAIN phase flagged for closure
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T14:24:09.607712'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T14:24:09.607712'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T14:24:09.607712'
---
# WORK-251: Coldstart Crash Recovery — Detect Unclosed Sessions
