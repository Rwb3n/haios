---
template: work_item
id: WORK-113
title: Ceremony Contract Validation and Governance
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-09
spawned_by: null
chapter: ceremonies/CH-011
arc: ceremonies
closed: '2026-02-10'
priority: high
effort: medium
traces_to:
- REQ-CEREMONY-002
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/lib/ceremony_contracts.py
- tests/test_ceremony_validation.py
- .claude/haios/config/haios.yaml
acceptance_criteria:
- validate_ceremony_input() function implemented in lib/
- validate_ceremony_output() function implemented in lib/
- Governance gate blocks ceremony start if input contract fails (configurable warn/block)
- Unit tests for contract validation (input valid, input invalid, output valid, output
  invalid)
- OutputField.guaranteed validated against {always, on_success, on_failure} (WORK-112
  critique A5)
- ContractField.type validated against canonical vocabulary {string, boolean, list,
  path, integer} (WORK-112 critique A6)
- 'Registry ceremony_count self-verifying: assert declared == actual (WORK-112 critique
  A10)'
blocked_by:
- WORK-111
- WORK-112
blocks: []
enables: []
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-09 22:19:48
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84295
- 84296
- 84297
- 84298
- 84299
- 84300
- 84301
- 84302
- 84303
extensions:
  epoch: E2.5
version: '2.0'
generated: 2026-02-09
last_updated: '2026-02-10T00:11:17.521902'
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

- [x] `validate_ceremony_input(contract, inputs)` in `.claude/haios/lib/ceremony_contracts.py`
- [x] `validate_ceremony_output(contract, outputs)` in `.claude/haios/lib/ceremony_contracts.py`
- [x] Governance enforcement via `enforce_ceremony_contract()` (warn/block configurable in haios.yaml)
- [x] Unit tests in `tests/test_ceremony_validation.py` (17 tests)
- [x] haios.yaml toggle: `toggles.ceremony_contract_enforcement: warn|block`

---

## History

### 2026-02-10 - Implemented (Session 334)
- Plan authored and approved with 17 TDD tests
- Critique agent (REVISE verdict): addressed A5 (governance gate), A3 (missing success warning), A8 (documented coupling)
- Implementation: validate_ceremony_input, validate_ceremony_output, enforce_ceremony_contract, vocabulary __post_init__ validators
- 139/139 tests passed (17 new + 122 existing), zero regressions

### 2026-02-09 - Created (Session 332)
- Spawned from ceremonies arc survey (CH-011 decomposition)
- 3 of 3 work items for CH-011: schema → retrofit → validation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md (R3: Contract Validation)
- @.claude/haios/lib/queue_ceremonies.py (reference: existing ceremony module pattern)
- @docs/work/active/WORK-111/WORK.md (schema dependency)
- @docs/work/active/WORK-112/WORK.md (retrofit dependency)
