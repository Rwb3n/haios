---
template: work_item
id: WORK-091
title: Fracture Validation Lifecycle Templates (CH-006)
type: feature
status: active
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-006-TemplateFracturing
arc: lifecycles
closed: null
priority: medium
effort: small
traces_to:
- REQ-TEMPLATE-002
requirement_refs: []
source_files:
- .claude/templates/
acceptance_criteria:
- templates/validation/ directory exists with 3 phase templates
- VERIFY.md, JUDGE.md, REPORT.md created
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
  fracture_target: validation
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T19:43:41'
---
# WORK-091: Fracture Validation Lifecycle Templates (CH-006)

---

## Context

Validation lifecycle has no templates currently. Need to create per-phase templates from scratch.

**Current State:**
- No validation templates exist
- `templates/validation/` does not exist

**Target Structure:**
```
templates/validation/
├── VERIFY.md   (~40 lines)
├── JUDGE.md    (~40 lines)
└── REPORT.md   (~30 lines)
```

---

## Deliverables

- [ ] Create templates/validation/ directory
- [ ] Create VERIFY.md with input/output contracts
- [ ] Create JUDGE.md with input/output contracts
- [ ] Create REPORT.md with input/output contracts
- [ ] Verify each template ≤100 lines
- [ ] Unit test: load validation/JUDGE.md contains only JUDGE phase

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-006-TemplateFracturing (validation portion)
- Part of 4-way split: design, implementation, validation, triage

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @.claude/templates/investigation/ (reference pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)
