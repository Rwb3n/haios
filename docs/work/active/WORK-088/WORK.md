---
template: work_item
id: WORK-088
title: Implement Phase Template Contracts (CH-005)
type: feature
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-005-PhaseTemplateContracts
arc: lifecycles
closed: '2026-02-04'
priority: medium
effort: medium
traces_to:
- REQ-TEMPLATE-001
requirement_refs: []
source_files:
- .claude/templates/investigation/EXPLORE.md
- .claude/haios/modules/cycle_runner.py
acceptance_criteria:
- All phase templates have input_contract in frontmatter
- All phase templates have output_contract in frontmatter
- Governance validates input contract on phase entry
- Governance validates output contract on phase exit
- Contracts are both machine-readable (YAML) and human-readable (markdown)
blocked_by:
- WORK-084
blocks:
- WORK-089
- WORK-090
- WORK-091
- WORK-092
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
  implementation_type: REFACTOR
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-04T22:35:53.698357'
queue_position: backlog
cycle_phase: backlog
---
# WORK-088: Implement Phase Template Contracts (CH-005)

---

## Context

Investigation phase templates already have contracts in human-readable markdown, but no machine-readable contracts in frontmatter for automated validation.

**Current State:**
```yaml
# From EXPLORE.md frontmatter
---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.0'
---
```

**What exists:**
- Investigation templates fractured with Input/Output Contract sections
- YAML frontmatter with `phase`, `maps_to_state`, `version`
- Human-readable checklist format for contracts

**What doesn't exist:**
- Machine-readable contracts in frontmatter (YAML schema)
- Governance validation of contract satisfaction
- Contracts for non-investigation templates

---

## Deliverables

- [ ] Define contract schema (input_contract, output_contract YAML structure)
- [ ] Add machine-readable contracts to investigation phase templates
- [ ] Implement validate_template_input(phase, work) function
- [ ] Implement validate_template_output(phase, work) function
- [ ] Integrate contract validation into CycleRunner phase entry/exit
- [ ] Unit tests for contract validation
- [ ] Integration test: missing input -> blocked entry

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-005-PhaseTemplateContracts
- Depends on WORK-084

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-005-PhaseTemplateContracts.md
- @.claude/templates/investigation/ (existing templates)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-001)
