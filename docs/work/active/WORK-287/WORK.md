---
template: work_item
id: WORK-287
title: 'Investigation: Decouple Plan-Authoring from Implementation Across Session
  Boundaries'
type: investigation
status: complete
owner: Hephaestus
created: '2026-03-08'
spawned_by: null
spawned_children:
- WORK-289
chapter: ''
arc: ''
closed: '2026-03-08'
priority: high
effort: medium
traces_to:
- REQ-LIFECYCLE-001
- REQ-LIFECYCLE-005
requirement_refs: []
source_files:
- .claude/skills/plan-authoring-cycle/SKILL.md
- .claude/skills/implementation-cycle/SKILL.md
- .claude/haios/manifesto/L4/functional_requirements.md
acceptance_criteria:
- 'Investigate session-boundary decoupling: Design/Plan in session N, Build/Test in
  session N+1'
- 'Evaluate tiering: small items stay single-session, standard/architectural items
  split'
- 'Compare approaches: (1) session-boundary split vs (2) sub-agent delegation for
  plan-authoring vs (3) hybrid'
- 'Address context taint problem: planning artifacts polluting implementation reasoning'
- 'Address context budget problem: PLAN phase consuming ~70% of session context (mem:87482)'
- Findings doc with recommendation for E2.9/E3.0 lifecycle restructuring
- Define handoff contract between plan-session and build-session (what persists, what
  gets loaded)
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-08T13:00:20.947417'
  exited: '2026-03-08T14:33:12.437844'
queue_history:
- position: backlog
  entered: '2026-03-08T13:00:20.947417'
  exited: '2026-03-08T14:23:32.997702'
- position: ready
  entered: '2026-03-08T14:23:32.997702'
  exited: '2026-03-08T14:23:35.384053'
- position: working
  entered: '2026-03-08T14:23:35.384053'
  exited: '2026-03-08T14:33:12.437844'
- position: done
  entered: '2026-03-08T14:33:12.437844'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89910
- 89911
- 89912
- 89913
- 89914
- 89915
- 89916
- 89917
- 89918
- 87482
- 86695
- 86707
- 84117
- 84160
- 84125
- 88191
- 89508
- 90012
- 90013
- 90014
- 90015
- 90016
- 90028
- 90029
extensions: {}
version: '2.0'
generated: '2026-03-08'
last_updated: '2026-03-08T14:33:12.442846'
---
# WORK-287: Investigation: Decouple Plan-Authoring from Implementation Across Session Boundaries
