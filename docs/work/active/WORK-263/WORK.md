---
template: work_item
id: WORK-263
title: Hook-Level Gate-Skip Injection for Plan-Validation and Preflight Gates
type: implementation
status: active
owner: Hephaestus
created: '2026-03-07'
spawned_by: WORK-250
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: low
effort: medium
traces_to:
- REQ-LIFECYCLE-005
- REQ-CEREMONY-005
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
- .claude/haios/lib/critique_injector.py
acceptance_criteria:
- PreToolUse hook detects PLAN->DO transition and injects gate-skip/gate-run instructions
  based on tier
- Gates 2 (plan-validation) and 3 (preflight) have hook-level enforcement, not just
  skill-text reliance
- Complements existing critique_injector.py (Gate 1) with gate_injector.py or equivalent
  for Gates 2+3
- "Agent cannot bypass gates by ignoring skill text \u2014 hook provides safety net"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-07T16:12:57.553567'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-07T16:12:57.553567'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T16:12:57.553567'
---
# WORK-263: Hook-Level Gate-Skip Injection for Plan-Validation and Preflight Gates
