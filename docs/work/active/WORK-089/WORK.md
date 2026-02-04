---
template: work_item
id: WORK-089
title: Fracture Design Lifecycle Templates (CH-006)
type: feature
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-006-TemplateFracturing
arc: lifecycles
closed: '2026-02-04'
priority: medium
effort: small
traces_to:
- REQ-TEMPLATE-002
requirement_refs: []
source_files:
- .claude/templates/
acceptance_criteria:
- templates/design/ directory exists with 4 phase templates
- EXPLORE.md, SPECIFY.md, CRITIQUE.md, COMPLETE.md created
- Each template ≤100 lines
- Templates have input_contract/output_contract in frontmatter
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
- 83960
- 83961
- 83962
- 83963
- 83964
- 83965
- 83966
- 83967
- 83968
extensions:
  epoch: E2.5
  implementation_type: CREATE_NEW
  fracture_target: design
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-04T23:07:47.620303'
queue_position: backlog
cycle_phase: backlog
---
# WORK-089: Fracture Design Lifecycle Templates (CH-006)

---

## Context

Only investigation lifecycle is fractured into per-phase templates. Design lifecycle needs fracturing to enable:
- Phase-specific context loading (~50 lines vs 200+)
- Contract validation per phase
- Consistent pattern across all lifecycles

**Current State:**
- `templates/investigation/` exists with 4 phase templates (DONE)
- `templates/design/` does not exist

**Target Structure:**
```
templates/design/
├── EXPLORE.md    (~40 lines)
├── SPECIFY.md    (~50 lines)
├── CRITIQUE.md   (~40 lines)
└── COMPLETE.md   (~30 lines)
```

---

## Deliverables

- [ ] Create templates/design/ directory
- [ ] Create EXPLORE.md with input/output contracts
- [ ] Create SPECIFY.md with input/output contracts
- [ ] Create CRITIQUE.md with input/output contracts
- [ ] Create COMPLETE.md with input/output contracts
- [ ] Verify each template ≤100 lines
- [ ] Unit test: load design/SPECIFY.md contains only SPECIFY phase

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-006-TemplateFracturing (design portion)
- Part of 4-way split: design, implementation, validation, triage

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @.claude/templates/investigation/ (reference pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)
