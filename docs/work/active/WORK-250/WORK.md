---
template: work_item
id: WORK-250
title: Tier-Aware Gate Skipping — Proportional Ceremony Enforcement
type: implementation
status: complete
owner: Hephaestus
created: '2026-03-07'
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-03-07'
priority: high
effort: medium
traces_to:
- REQ-LIFECYCLE-005
requirement_refs: []
source_files: []
acceptance_criteria:
- Trivial effort items skip all 3 exit gates (plan-validation, preflight, critique)
- Small effort items skip plan-validation and preflight (keeps critique as inline
  checklist)
- Read effort field from WORK.md in PLAN phase entry to determine tier
- Text-only/metadata work items bypass full ceremony chain
- Directly addresses 104% context budget problem (mem:85606)
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: '2026-03-07T14:24:04.784995'
  exited: '2026-03-07T16:09:42.382954'
queue_history:
- position: backlog
  entered: '2026-03-07T14:24:04.784995'
  exited: '2026-03-07T16:09:42.382954'
- position: done
  entered: '2026-03-07T16:09:42.382954'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85606
- 89650
- 89651
- 80194
- 89652
- 89653
- 89654
- 89655
extensions: {}
version: '2.0'
generated: '2026-03-07'
last_updated: '2026-03-07T16:09:42.386970'
---
# WORK-250: Tier-Aware Gate Skipping — Proportional Ceremony Enforcement
