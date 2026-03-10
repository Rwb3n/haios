---
template: work_item
id: WORK-293
title: "Fix ceremony_contract false-positive \u2014 Remove queue ceremonies from registry\
  \ or enhance input extraction"
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
- .claude/haios/config/ceremony_registry.yaml
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- Queue ceremony skills (queue-commit, queue-prioritize, queue-intake, queue-unpark)
  no longer produce false-positive GateViolation events
- "Option A: Remove queue ceremonies from ceremony_registry.yaml (preferred \u2014\
  \ they are MCP-only now)"
- 'Option B: Enhance _extract_ceremony_inputs() to fall back to _get_current_work_id()
  from cycle state'
- Zero ceremony_contract GateViolations for queue ceremonies in governance-events.jsonl
  after fix
- Existing lifecycle ceremony contract validation (retro-cycle, close-work-cycle,
  checkpoint-cycle) still works
- 'Tests: verify queue-commit Skill invocation without args does not produce GateViolation'
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-03-10T21:49:41.788457'
  exited: null
queue_history:
- position: backlog
  entered: '2026-03-10T21:49:41.788457'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: '2026-03-10'
last_updated: '2026-03-10T21:49:41.788457'
---
# WORK-293: Fix ceremony_contract false-positive — Remove queue ceremonies from registry or enhance input extraction
