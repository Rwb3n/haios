---
template: work_item
id: E2-181
title: close-work-cycle skill
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
current_node: close
node_history:
- node: backlog
  entered: 2025-12-25 09:33:31
  exited: 2025-12-25 15:06:00
- node: close
  entered: 2025-12-25 15:06:00
  exited: null
cycle_docs: {}
memory_refs:
- 78926
- 78927
documents:
  investigations: []
  plans:
  - PLAN-E2-181-close-work-cycle-skill.md
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T15:06:25'
---
# WORK-E2-181: close-work-cycle skill

@docs/README.md
@docs/epistemic_state.md

---

## Context

The /close command contained all closure logic inline without skill-level behavioral contracts. This created inconsistency with the Gate Contract pattern established in INV-033. Work items closed without structured phase guidance.

---

## Current State

COMPLETE - Skill implemented and verified.

---

## Deliverables

- [x] Create close-work-cycle skill with VALIDATE->ARCHIVE->CAPTURE phases
- [x] Chain /close command to skill
- [x] Verify runtime discovery (skill in haios-status-slim.json)
- [x] Update READMEs (skills/, commands/)

---

## History

### 2025-12-25 - Created (Session 116)
- Initial creation from INV-035 spawned work

### 2025-12-25 - Implemented (Session 117)
- Created SKILL.md with 3-phase workflow
- Updated /close command chaining
- Verified runtime discovery
- Created READMEs

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- INV-035: Skill Architecture Refactoring
- PLAN-E2-181-close-work-cycle-skill.md
