---
template: work_item
id: WORK-090
title: Fracture Implementation Lifecycle Templates (CH-006)
type: feature
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-006-TemplateFracturing
arc: lifecycles
closed: '2026-02-05'
priority: medium
effort: small
traces_to:
- REQ-TEMPLATE-002
requirement_refs: []
source_files:
- .claude/templates/
- .claude/templates/implementation_plan.md
acceptance_criteria:
- templates/implementation/ directory exists with 4 phase templates
- PLAN.md, DO.md, CHECK.md, DONE.md created
- Each template ≤100 lines
- Templates have input_contract/output_contract in frontmatter
- Legacy implementation_plan.md archived
blocked_by:
- WORK-088
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 19:30:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83971
extensions:
  epoch: E2.5
  implementation_type: REFACTOR
  fracture_target: implementation
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-05T00:01:21.097007'
queue_position: backlog
cycle_phase: backlog
---
# WORK-090: Fracture Implementation Lifecycle Templates (CH-006)

---

## Context

Implementation lifecycle currently uses monolithic `implementation_plan.md` template. Needs fracturing to per-phase templates.

**Current State:**
- `templates/implementation_plan.md` exists (MONOLITHIC - needs fracturing)
- `templates/implementation/` does not exist

**Target Structure:**
```
templates/implementation/
├── PLAN.md    (~40 lines)
├── DO.md      (~50 lines)
├── CHECK.md   (~40 lines)
└── DONE.md    (~30 lines)
```

---

## Deliverables

- [ ] Create templates/implementation/ directory
- [ ] Create PLAN.md with input/output contracts
- [ ] Create DO.md with input/output contracts
- [ ] Create CHECK.md with input/output contracts
- [ ] Create DONE.md with input/output contracts
- [ ] Move implementation_plan.md to templates/_legacy/
- [ ] Verify each template ≤100 lines
- [ ] Unit test: load implementation/DO.md contains only DO phase

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-006-TemplateFracturing (implementation portion)
- Part of 4-way split: design, implementation, validation, triage

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @.claude/templates/investigation/ (reference pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)
