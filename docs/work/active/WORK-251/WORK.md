---
template: work_item
id: WORK-251
title: Coldstart Crash Recovery — Detect Unclosed Sessions
type: implementation
status: complete
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children:
- WORK-272
chapter: CH-061
arc: call
closed: '2026-03-07'
priority: medium
effort: small
traces_to:
- REQ-CONTEXT-001
requirement_refs:
- REQ-CONTEXT-001
- REQ-CEREMONY-001
source_files:
- .claude/haios/lib/governance_events.py
- .claude/haios/lib/coldstart_orchestrator.py
acceptance_criteria:
- Coldstart detects unclosed sessions in governance-events.jsonl (SessionStarted without
  SessionEnded)
- 'Surfaces recovery items: uncommitted CHAIN work, missing retros, split state'
- Emits synthetic SessionEnded for crashed sessions
- WORK items left in CHAIN phase flagged for closure
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-07T14:24:09.607712'
  exited: '2026-03-07T18:12:52.542179'
queue_history:
- position: backlog
  entered: '2026-03-07T14:24:09.607712'
  exited: '2026-03-07T17:25:37.953685'
- position: ready
  entered: '2026-03-07T17:25:37.953685'
  exited: '2026-03-07T17:25:41.643087'
- position: working
  entered: '2026-03-07T17:25:41.643087'
  exited: '2026-03-07T18:12:52.542179'
- position: done
  entered: '2026-03-07T18:12:52.542179'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89755
- 89756
- 89757
- 89767
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T18:12:52.548547'
---
# WORK-251: Coldstart Crash Recovery — Detect Unclosed Sessions
