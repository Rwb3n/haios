---
template: work_item
id: WORK-092
title: Fracture Triage Lifecycle Templates (CH-006)
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
acceptance_criteria:
- templates/triage/ directory exists with 4 phase templates
- SCAN.md, ASSESS.md, RANK.md, COMMIT.md created
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
memory_refs: []
extensions:
  epoch: E2.5
  implementation_type: CREATE_NEW
  fracture_target: triage
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-05T20:33:40.216380'
queue_position: backlog
cycle_phase: backlog
---
# WORK-092: Fracture Triage Lifecycle Templates (CH-006)

---

## Context

Triage lifecycle has no templates currently. Need to create per-phase templates from scratch.

**Current State:**
- No triage templates exist
- `templates/triage/` does not exist

**Target Structure:**
```
templates/triage/
├── SCAN.md     (~40 lines)
├── ASSESS.md   (~40 lines)
├── RANK.md     (~40 lines)
└── COMMIT.md   (~30 lines)
```

---

## Deliverables

- [ ] Create templates/triage/ directory
- [ ] Create SCAN.md with input/output contracts
- [ ] Create ASSESS.md with input/output contracts
- [ ] Create RANK.md with input/output contracts
- [ ] Create COMMIT.md with input/output contracts
- [ ] Verify each template ≤100 lines
- [ ] Unit test: load triage/RANK.md contains only RANK phase

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-006-TemplateFracturing (triage portion)
- Part of 4-way split: design, implementation, validation, triage

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @.claude/templates/investigation/ (reference pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)
