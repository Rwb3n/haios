---
template: work_item
id: WORK-114
title: "Wire Ceremony Contract Enforcement into Runtime"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-10
spawned_by: null
chapter: ceremonies/CH-012
arc: ceremonies
closed: null
priority: high
effort: medium
traces_to:
- REQ-CEREMONY-001
- REQ-CEREMONY-002
requirement_refs: []  # DEPRECATED: use traces_to instead
source_files: []
acceptance_criteria:
- enforce_ceremony_contract() called at ceremony start in runtime path (PreToolUse hook or CycleRunner)
- Validation errors surface to agent via hook output (warn mode) or block ceremony (block mode)
- Existing ceremony tests pass with no regressions
- Integration test demonstrating contract enforcement at runtime
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-10T00:25:05
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-10
last_updated: 2026-02-10T00:25:05
---
# WORK-114: Wire Ceremony Contract Enforcement into Runtime

---

## Context

WORK-113 (Session 334) implemented `enforce_ceremony_contract()` in `lib/ceremony_contracts.py` with configurable warn/block modes via `haios.yaml` toggle `toggles.ceremony_contract_enforcement`. However, this function is currently only called by tests — no runtime code path invokes it. Ceremonies can start without their input contracts being validated.

The function needs to be wired into the runtime ceremony entry point. Two candidate integration points exist:
1. **PreToolUse hook** — intercept `Skill` tool calls for ceremony skills, parse inputs, validate
2. **CycleRunner / ceremony dispatch** — call `enforce_ceremony_contract()` when `just set-cycle` runs for a ceremony

This is the first work item for CH-012 (SideEffectBoundaries), scoped narrowly to contract enforcement wiring. The full `ceremony_context()` context manager is a separate, future work item.

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

- [ ] Runtime call-site for `enforce_ceremony_contract()` at ceremony entry point
- [ ] Contract validation errors surfaced to agent (warn mode: log + continue; block mode: halt)
- [ ] Integration test: ceremony with invalid inputs triggers enforcement
- [ ] Integration test: ceremony with valid inputs passes enforcement
- [ ] Zero regressions on existing ceremony tests (139+)

---

## History

### 2026-02-10 - Created (Session 335)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md
- @.claude/haios/lib/ceremony_contracts.py (enforce_ceremony_contract function)
- @.claude/haios/config/haios.yaml (toggles.ceremony_contract_enforcement)
- @docs/work/active/WORK-113/WORK.md (validation implementation dependency)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001, REQ-CEREMONY-002)
