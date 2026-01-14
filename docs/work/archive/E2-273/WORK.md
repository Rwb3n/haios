---
template: work_item
id: E2-273
title: Add Open Decisions Section to Implementation Plan Template
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
blocked_by: []
blocks:
- E2-271
enables:
- E2-274
- E2-275
related:
- INV-058
- E2-271
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-05 21:34:48
  exited: null
cycle_docs: {}
memory_refs:
- 80827
- 80828
- 80829
- 80830
- 80831
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-05
last_updated: '2026-01-05T22:45:19'
---
# WORK-E2-273: Add Open Decisions Section to Implementation Plan Template

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Implementation plans have no structured section to surface operator decisions from the work item. Agents author plans without documenting unresolved decisions, leading to plans built on assumptions.

**Root cause:** INV-058 Finding 1 - implementation_plan.md template has "Open Questions" but no "Open Decisions" section that links to work item's `operator_decisions` field.

**Source:** INV-058 investigation (Session 175) - Gate 2 of 4 in defense-in-depth strategy.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add "Open Decisions" section to `.claude/templates/implementation_plan.md`
- [ ] Section must include table with: Decision, Options, Chosen, Rationale columns
- [ ] Add comment explaining BLOCK behavior if unresolved
- [ ] Add test verifying section exists in template

---

## History

### 2026-01-05 - Created (Session 175)
- Initial creation

---

## References

- INV-058: Ambiguity Gating for Plan Authoring (source investigation)
- E2-272: Add operator_decisions Field to Work Item Template (prerequisite - COMPLETE)
- E2-274: Add AMBIGUITY Phase to plan-authoring-cycle (uses this section)
- E2-275: Add Decision Check to plan-validation-cycle (validates this section)
