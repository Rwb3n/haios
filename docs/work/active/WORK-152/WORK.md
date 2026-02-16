---
template: work_item
id: WORK-152
title: Plan Template Fracturing by Work Type
type: design
status: complete
owner: null
created: 2026-02-15
spawned_by: S378-observation
spawned_children: []
chapter: CH-047
arc: composability
closed: 2026-02-16
priority: medium
effort: medium
traces_to:
- REQ-REFERENCE-002
requirement_refs: []
source_files:
- .claude/templates/_legacy/implementation_plan.md
acceptance_criteria:
- Plan templates exist per work type (implementation, design, cleanup)
- Each template contains only sections relevant to its work type
- Type mapping routes work item types (feature/bug/chore/design) to plan template types
- scaffold_template auto-extracts TYPE from work item for transparent routing
- validate_template routes by subtype for type-specific section coverage
- Existing plan-authoring-cycle and plan-validation-cycle references updated
- Skip rationale frequency drops to <20% of sections per plan
- Tests for template selection routing (8 tests)
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-15 22:56:31
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85528
- 85529
- 85530
- 85531
extensions:
  epoch: E2.7
version: '2.0'
generated: 2026-02-15
last_updated: '2026-02-16T22:38:28.453946'
queue_history:
- position: ready
  entered: '2026-02-16T22:38:28.422585'
  exited: '2026-02-16T22:38:28.450914'
- position: working
  entered: '2026-02-16T22:38:28.450914'
  exited: null
---
# WORK-152: Plan Template Fracturing by Work Type

---

## Context

**Problem:** The implementation plan template is optimized for code implementation work. For `type: design` work items (ADRs, specs), ~60% of plan sections require skip rationales (TDD, code blocks, function signatures, call chains, backward compatibility). This creates overhead without value.

**Root cause:** Plan template is monolithic — one template for all work types. The template fracturing pattern already exists for lifecycle phases (`.claude/templates/{lifecycle}/{PHASE}.md`) but was not applied to plan templates.

**Evidence:** WORK-149 (Session 378) — ADR authoring required skip rationales for Tests First, Current/Desired State code blocks, Exact Code Change, Call Chain Context, Function Signatures, and Backward Compatibility test sections.

**Scope:** Fracture the plan template by work type, following the existing template fracturing pattern from E2.5.

---

## Deliverables

- [ ] Plan templates per work type: implementation, design, investigation, cleanup
- [ ] Template selection logic in scaffold.py (route by `type` field)
- [ ] plan-authoring-cycle updated to use type-specific template
- [ ] plan-validation-cycle updated to validate against correct template
- [ ] Tests for template selection routing

---

## History

### 2026-02-15 - Created (Session 378)
- Observation from WORK-149: plan template skew toward code implementation
- Queued for E2.7 Composability (template rationalization)

---

## References

- Memory: 85528-85531 (S378 plan template skew observation)
- @.claude/templates/_legacy/implementation_plan.md (current monolithic template)
- @docs/work/active/WORK-149/plans/PLAN.md (evidence of skip rationale overhead)
