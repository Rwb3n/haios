---
template: work_item
id: WORK-042
title: CH-004 PreToolUseIntegration - Wire Governed Activities to Hook
type: implementation
status: complete
owner: Hephaestus
created: 2026-01-30
spawned_by: null
chapter: CH-004
arc: activities
closed: '2026-02-01'
priority: high
effort: medium
traces_to:
- REQ-ACTIVITY-001
- REQ-ACTIVITY-002
- REQ-GOVERN-001
- REQ-GOVERN-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
- .claude/haios/modules/governance_layer.py
- .claude/haios/config/activity_matrix.yaml
acceptance_criteria:
- PreToolUse hook calls GovernanceLayer.check_activity() for state-aware enforcement
- DO state blocks AskUserQuestion, memory-search, web-fetch, web-search
- Unknown primitive/state defaults to allow (fail-open)
- Activity matrix loaded from YAML config
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 21:50:40
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82798
- 82799
- 82800
- 82801
- 82802
- 82803
- 82814
- 82815
- 82816
- 82817
- 82818
- 82819
- 82820
- 82821
- 82827
- 82828
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-02-01T14:58:11'
---
# WORK-042: CH-004 PreToolUseIntegration - Wire Governed Activities to Hook

---

## Context

CH-001 ActivityMatrix defines 17 primitives across 6 states with 102 governance rules. CH-002 StateDefinitions formalizes state detection via phase-to-state mapping. CH-003 GovernanceRules defines the rule schema, `check_activity()` algorithm, and `activity_matrix.yaml` data structure.

**Problem:** The designed governance system exists only in documentation. The PreToolUse hook (`pre_tool_use.py`) has no state-awareness - it checks tool + path, not tool + state. To enforce the governed activities paradigm, we need to:

1. **Implement GovernanceLayer methods** - `get_activity_state()`, `map_tool_to_primitive()`, `check_activity()`
2. **Create activity_matrix.yaml** - Configuration file with rules per CH-003 data structure
3. **Wire into PreToolUse hook** - Add state-aware check early in the hook flow
4. **Add skill restriction logic** - DO-phase skill blocklist per CH-001

**Depends on:**
- CH-001 ActivityMatrix (primitives, states, rules matrix)
- CH-002 StateDefinitions (state detection algorithm, phase mapping)
- CH-003 GovernanceRules (rule schema, check algorithm, data structure)

**Completes:** Activities arc - final chapter enabling state-aware governance

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] **activity_matrix.yaml** - Configuration file at `.claude/haios/config/activity_matrix.yaml` with O(1) lookup structure per CH-003
- [x] **GovernanceLayer.get_activity_state()** - Returns current ActivityMatrix state from cycle/phase
- [x] **GovernanceLayer.map_tool_to_primitive()** - Maps tool_name + tool_input to primitive name
- [x] **GovernanceLayer.check_activity()** - Evaluates rule for (primitive, state, context), returns GateResult
- [x] **GovernanceLayer._check_skill_restriction()** - DO-phase skill allowlist/blocklist per CH-001
- [x] **PreToolUse integration** - Hook calls check_activity() early, handles allow/warn/block/redirect
- [x] **Unit tests** - Tests for all new GovernanceLayer methods in `tests/test_governance_layer.py`
- [x] **CH-004-PreToolUseIntegration.md** - Chapter file documenting the implementation

---

## History

### 2026-01-30 - Created (Session 247)
- Initial scaffold

### 2026-02-01 - Populated (Session 270)
- Added context linking to CH-001, CH-002, CH-003
- Defined 8 deliverables covering config, methods, integration, tests, documentation
- Linked to REQ-ACTIVITY-001, REQ-ACTIVITY-002, REQ-GOVERN-001, REQ-GOVERN-002
- Added memory_refs to Session 269 GovernanceRules decisions

### 2026-02-01 - Completed (Session 270)
- Created activity_matrix.yaml with 17 primitives × 6 states (102 rules)
- Implemented 5 GovernanceLayer methods: get_activity_state, map_tool_to_primitive, check_activity, _check_skill_restriction, _load_activity_matrix
- Integrated into PreToolUse hook via _check_governed_activity()
- Added `just get-cycle` recipe to justfile (critique found missing dependency)
- All 8 unit tests pass (40 governance tests total)
- Created CH-004-PreToolUseIntegration.md chapter file
- WHY captured to memory (82814-82821)

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md
- @.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md
- @.claude/haios/epochs/E2_4/arcs/activities/CH-003-GovernanceRules.md
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md
- @.claude/hooks/hooks/pre_tool_use.py
- @.claude/haios/modules/governance_layer.py
