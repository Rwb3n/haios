---
template: work_item
id: E2-274
title: Add AMBIGUITY Phase to plan-authoring-cycle
status: complete
owner: Hephaestus
created: 2026-01-05
closed: '2026-01-05'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-058
blocked_by:
- E2-272
- E2-273
blocks:
- E2-271
enables:
- E2-275
related:
- INV-058
- E2-271
current_node: plan
node_history:
- node: backlog
  entered: 2026-01-05 21:34:54
  exited: '2026-01-05T22:57:28.858316'
- node: plan
  entered: '2026-01-05T22:57:28.858316'
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-05
last_updated: '2026-01-05T23:09:35'
---
# WORK-E2-274: Add AMBIGUITY Phase to plan-authoring-cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** During E2-271 plan authoring (Session 175), the agent designed a plan based on incorrect assumptions without consulting the operator. The work item had ambiguous deliverables requiring operator decision (implement modules OR remove references), but the agent proceeded without surfacing the decision.

**Root cause:** The plan-authoring-cycle skill reads the plan file directly but never reads the source work item to check for operator decisions. Even with structured `operator_decisions` field (added by E2-272) and Open Decisions section in templates (added by E2-273), the skill has no mechanism to surface and block on unresolved decisions.

**Evidence from INV-058:**
- plan-authoring-cycle reads plan file (line 32) but NOT work item
- Cycle is ANALYZE->AUTHOR->VALIDATE with no decision surfacing phase
- Memory concept 8220: "agent failures and operator burnout caused by executing on ambiguous or incomplete plans"

---

## Current State

Work item in PLAN node. E2-272 (field) and E2-273 (template section) complete as prerequisites.

---

## Deliverables

- [ ] Add AMBIGUITY phase before ANALYZE phase in `.claude/skills/plan-authoring-cycle/SKILL.md`
- [ ] AMBIGUITY phase reads WORK.md and checks `operator_decisions` field
- [ ] If unresolved decisions exist, BLOCK and present AskUserQuestion with options
- [ ] If all decisions resolved (or none exist), populate Open Decisions section and proceed to ANALYZE
- [ ] Add tests for AMBIGUITY phase behavior

---

## History

### 2026-01-05 - Created (Session 175)
- Initial creation as part of INV-058 spawned work items

### 2026-01-05 - Populated (Session 177)
- Work item context and deliverables populated from INV-058 design

---

## References

- @docs/work/archive/INV-058/investigations/001-ambiguity-gating-for-plan-authoring.md (source design)
- @.claude/skills/plan-authoring-cycle/SKILL.md (target file)
- @.claude/templates/work_item.md (operator_decisions field from E2-272)
- @.claude/templates/implementation_plan.md (Open Decisions section from E2-273)
