---
template: work_item
id: E2-275
title: Add Decision Check to plan-validation-cycle
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
- E2-274
blocks:
- E2-271
enables: []
related:
- INV-058
- E2-271
current_node: plan
node_history:
- node: backlog
  entered: 2026-01-05 21:34:59
  exited: '2026-01-05T23:11:56.648069'
- node: plan
  entered: '2026-01-05T23:11:56.648069'
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-05
last_updated: '2026-01-05T23:19:31'
---
# WORK-E2-275: Add Decision Check to plan-validation-cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Even with Gates 1-3 in place (operator_decisions field, Open Decisions section, AMBIGUITY phase), a plan could still reach implementation with unresolved decisions if the plan-validation-cycle doesn't check for them.

**Root cause:** plan-validation-cycle's VALIDATE phase checks section completeness and quality but doesn't verify that the "Open Decisions" section has no `[BLOCKED]` entries. This is the final gate in the defense-in-depth strategy.

**Evidence from INV-058 Finding 3:**
- plan-validation-cycle VALIDATE phase (lines 88-116) checks quality but has no check for "Open Decisions resolved?"
- A plan can pass all quality checks while having unresolved operator decisions

---

## Current State

Work item in PLAN node. E2-272, E2-273, E2-274 complete as prerequisites.

---

## Deliverables

- [ ] Add check in VALIDATE phase for unresolved Open Decisions
- [ ] Check that "Open Decisions" table has no `[BLOCKED]` entries in Chosen column
- [ ] BLOCK if unresolved decisions exist with actionable message
- [ ] Add tests for the new check

---

## History

### 2026-01-05 - Created (Session 175)
- Initial creation as part of INV-058 spawned work items

### 2026-01-05 - Populated (Session 177)
- Work item context and deliverables populated from INV-058 design

---

## References

- @docs/work/archive/INV-058/investigations/001-ambiguity-gating-for-plan-authoring.md (source design)
- @.claude/skills/plan-validation-cycle/SKILL.md (target file)
- @.claude/templates/implementation_plan.md (Open Decisions section from E2-273)
