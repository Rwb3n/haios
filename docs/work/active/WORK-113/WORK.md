---
template: work_item
id: WORK-113
title: "Ceremony Contract Validation and Governance"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-09
spawned_by: null
chapter: ceremonies/CH-011
arc: ceremonies
closed: null
priority: high
effort: medium
traces_to: [REQ-CEREMONY-002, REQ-CEREMONY-001]
requirement_refs: []
source_files: []
acceptance_criteria:
  - "validate_ceremony_input() function implemented in lib/"
  - "validate_ceremony_output() function implemented in lib/"
  - "Governance gate blocks ceremony start if input contract fails (configurable warn/block)"
  - "Unit tests for contract validation (input valid, input invalid, output valid, output invalid)"
  - "OutputField.guaranteed validated against {always, on_success, on_failure} (WORK-112 critique A5)"
  - "ContractField.type validated against canonical vocabulary {string, boolean, list, path, integer} (WORK-112 critique A6)"
  - "Registry ceremony_count self-verifying: assert declared == actual (WORK-112 critique A10)"
blocked_by: [WORK-111, WORK-112]
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-09T22:19:48
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
version: "2.0"
generated: 2026-02-09
last_updated: 2026-02-09T22:19:48
---
# WORK-113: Ceremony Contract Validation and Governance

---

## Context

After WORK-111 (schema) and WORK-112 (retrofit), all 19 ceremonies have YAML contracts. This work item implements the validation functions and governance integration that makes contracts enforceable rather than just documentation.

**Deliverables:**
1. Python validation functions that parse ceremony YAML frontmatter and validate inputs/outputs
2. Governance gate integration (PreToolUse hook or CeremonyRunner wrapper) that checks contracts
3. Unit tests covering valid/invalid cases

**Design constraint:** Enforcement mode must be configurable (warn vs block) via haios.yaml toggles, matching the existing governance toggle pattern.

---

## Deliverables

- [ ] `validate_ceremony_input(ceremony, inputs)` in `.claude/haios/lib/ceremony_contracts.py`
- [ ] `validate_ceremony_output(ceremony, outputs)` in `.claude/haios/lib/ceremony_contracts.py`
- [ ] Governance enforcement (warn/block configurable in haios.yaml)
- [ ] Unit tests in `tests/test_ceremony_contracts.py`
- [ ] haios.yaml toggle: `toggles.ceremony_contract_enforcement: warn|block`

---

## History

### 2026-02-09 - Created (Session 332)
- Spawned from ceremonies arc survey (CH-011 decomposition)
- 3 of 3 work items for CH-011: schema → retrofit → validation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md (R3: Contract Validation)
- @.claude/haios/lib/queue_ceremonies.py (reference: existing ceremony module pattern)
- @docs/work/active/WORK-111/WORK.md (schema dependency)
- @docs/work/active/WORK-112/WORK.md (retrofit dependency)
