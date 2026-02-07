---
template: work_item
id: E2-180
title: work-creation-cycle skill
status: complete
owner: Hephaestus
created: 2025-12-25
closed: 2025-12-25
milestone: M8-SkillArch
priority: medium
effort: medium
category: implementation
spawned_by: INV-035
spawned_by_investigation: INV-035
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-25 09:33:31
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T10:44:56'
---
# WORK-E2-180: work-creation-cycle skill

@docs/README.md
@docs/epistemic_state.md

---

## Context

The /new-work command scaffolds work files but leaves placeholder fields. Agents then manually populate Context and Deliverables sections without guidance. This creates inconsistent work items with incomplete information.

INV-035 identified work-creation-cycle as Priority 1 for M8-SkillArch milestone to enable the "work-item-as-fundamental-unit" paradigm.

---

## Current State

COMPLETE - Skill implemented and verified.

---

## Deliverables

- [x] Create work-creation-cycle skill with VERIFY->POPULATE->READY phases
- [x] Chain /new-work command to skill
- [x] Verify runtime discovery (skill in haios-status-slim.json)
- [x] Update READMEs (skills/, commands/)

---

## History

### 2025-12-25 - Created (Session 116)
- Initial creation from INV-035 spawned work

### 2025-12-25 - Implemented (Session 117)
- Created SKILL.md with 3-phase workflow
- Updated /new-work command chaining
- Verified runtime discovery
- Created READMEs

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- INV-035: Skill Architecture Refactoring
- PLAN-E2-180-work-creation-cycle-skill.md
