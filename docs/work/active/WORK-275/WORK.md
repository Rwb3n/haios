---
template: work_item
id: WORK-275
title: Fix ceremony_contract false-positive GateViolations in queue-commit
type: investigation
status: complete
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-256
spawned_children:
- WORK-293
- WORK-294
chapter: CH-059
arc: call
closed: '2026-03-10'
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/queue_ceremonies.py
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- Investigate why queue-commit ceremony logs 'missing work_id' GateViolation when
  work_id is present in the MCP call
- Investigate why backlog_id_uniqueness check matches unrelated IDs (E2-141, WORK-190)
  during WORK-256 operations
- 'Root cause identified: contract definition vs invocation mismatch, or overly broad
  scanning'
- Findings doc with fix recommendation
- 'Evidence: S476 governance-events.jsonl — 3 ceremony_contract + 2 backlog_id_uniqueness
  false positives'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-07T19:38:13.946228'
  exited: '2026-03-10T21:54:43.512378'
queue_history:
- position: backlog
  entered: '2026-03-07T19:38:13.946228'
  exited: '2026-03-08T16:23:23.853720'
- position: ready
  entered: '2026-03-08T16:23:23.853720'
  exited: '2026-03-10T21:43:34.555082'
- position: working
  entered: '2026-03-10T21:43:34.555082'
  exited: '2026-03-10T21:52:22.007007'
- position: done
  entered: '2026-03-10T21:52:22.007007'
  exited: '2026-03-10T21:54:43.512378'
- position: done
  entered: '2026-03-10T21:54:43.512378'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 90104
- 90105
- 90106
- 90107
- 90108
- 90126
- 90127
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-10T21:54:43.519387'
---
# WORK-275: Fix ceremony_contract false-positive GateViolations in queue-commit
