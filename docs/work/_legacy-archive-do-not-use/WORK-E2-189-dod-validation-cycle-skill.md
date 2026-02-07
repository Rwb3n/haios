---
template: work_item
id: E2-189
title: DoD Validation Cycle Skill
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
  entered: 2025-12-25 18:16:53
  exited: null
cycle_docs:
  backlog: docs/plans/PLAN-E2-189-dod-validation-cycle-skill.md
memory_refs:
- 78972
- 78973
- 78974
- 78975
documents:
  investigations: []
  plans:
  - docs/plans/PLAN-E2-189-dod-validation-cycle-skill.md
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T18:29:13'
---
# WORK-E2-189: DoD Validation Cycle Skill

@docs/README.md
@docs/epistemic_state.md

---

## Context

INV-035 identified a gap in the validation skill layer: dod-validation-skill (Post-DO validation) was listed as needed but not assigned a backlog ID. The close-work-cycle skill currently validates DoD inline, but per the 4-layer architecture, validation should be a separate bridge skill that close-work-cycle chains to via MUST gate. This formalizes "are we ready to close?" as a quality gate with its own CHECK->VALIDATE->APPROVE workflow.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Create `.claude/skills/dod-validation-cycle/SKILL.md` with CHECK->VALIDATE->APPROVE workflow
- [ ] Create `.claude/skills/dod-validation-cycle/README.md`
- [ ] Update close-work-cycle to MUST invoke dod-validation-cycle
- [ ] Update skills README with new skill
- [ ] Verify runtime discovery

---

## History

### 2025-12-25 - Created (Session 116)
- Initial creation

---

## References

- INV-035: Skill Architecture Refactoring (spawned this)
- plan-validation-cycle: Pre-DO validation (parallel pattern)
- design-review-validation: During-DO validation (parallel pattern)
- close-work-cycle: Will chain to this skill
