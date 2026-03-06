---
template: work_item
id: WORK-235
title: 'Investigation: Post-Work Ceremony Token Efficiency'
status: complete
owner: Hephaestus
created: '2026-02-25'
closed: '2026-03-06'
milestone: null
priority: medium
category: investigation
effort: medium
blocked_by: []
blocks: []
traces_to:
- REQ-CEREMONY-005
- REQ-CEREMONY-002
- REQ-CONTEXT-001
chapter: CH-059
arc: call
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-02-25T22:21:23.637728'
  exited: '2026-03-06T23:21:37.898717'
queue_history:
- position: backlog
  entered: '2026-02-25T22:21:23.637728'
  exited: '2026-03-06T23:21:37.898717'
- position: done
  entered: '2026-03-06T23:21:37.898717'
  exited: null
memory_refs:
- 89078
- 89079
- 89080
- 89081
- 89082
- 89318
documents:
  plans: []
  investigations:
  - investigations/001-post-work-ceremony-token-efficiency.md
  checkpoints: []
queue_position: done
cycle_phase: CHAIN
last_updated: '2026-03-06T23:21:37.902405'
---
# WORK-235: Investigation: Post-Work Ceremony Token Efficiency

## Context

Post-work ceremonies (close-work-cycle, retro-cycle, session-end) consume significant tokens on redundant operations. Multiple observations from S451 (memory refs 89078-89082) identified four concrete waste patterns:

1. **Haiku agent over-exploration:** Subagents (preflight-checker, schema-verifier) read files unnecessarily beyond their verification scope, inflating token cost without new information.
2. **Close-work VALIDATE redundancy:** The VALIDATE phase in close-work-cycle re-checks DoD criteria that were already verified in the CHECK phase of implementation-cycle. No new information is added between CHECK and VALIDATE — pure duplication.
3. **Config double-read:** `haios.yaml` (~150 lines) is read by both the coldstart orchestrator AND the agent during ceremony execution. The agent read is redundant since the orchestrator already injected relevant config into context.
4. **Schema column name confusion:** Recurrent `concept_type` vs `type` errors in SQL queries waste tokens on failed queries and retries. Schema hints in orchestrator output would eliminate this class of error.

These are symptoms of a broader pattern: ceremony phases were designed independently without accounting for information already present in context from prior phases or orchestrator injection.

## Deliverables

- [ ] Token waste map: document which ceremony phases duplicate information from prior phases or orchestrator output, with estimated token cost per redundancy
- [ ] Root cause analysis: why ceremony phases evolved independent context-loading rather than trusting prior context
- [ ] Design proposal: ceremony context contract — what each phase can assume is already in context vs. what it must load
- [ ] Specific recommendations for each of the 4 identified patterns (agent over-exploration, VALIDATE redundancy, config double-read, schema hints)
- [ ] Impact assessment: which ceremony skills need modification and estimated effort

## Acceptance Criteria

- [ ] All 4 observed waste patterns (memory 89078-89081) addressed with specific recommendations
- [ ] Token cost estimates provided (even if approximate) for current vs proposed
- [ ] Design proposal is compatible with L3.20 proportional governance (ceremony depth scaling)
- [ ] No recommendations that break existing ceremony contracts without migration path

## History

- 2026-02-25: Scaffolded from S451 observations (memory refs 89078-89082)
- 2026-03-06: Populated in S464 work-creation-cycle
