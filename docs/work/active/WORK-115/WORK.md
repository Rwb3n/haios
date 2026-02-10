---
template: work_item
id: WORK-115
title: Implement Ceremony Context Manager (CH-012)
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-10
spawned_by: null
chapter: CH-012
arc: ceremonies
closed: '2026-02-10'
priority: high
effort: medium
traces_to:
- REQ-CEREMONY-001
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/haios/modules/governance_layer.py
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- ceremony_context() context manager implemented with start/end event logging
- in_ceremony_context() check function returns bool
- WorkEngine state-changing methods guard on ceremony context
- Config toggle ceremony_context_enforcement (warn/block) in haios.yaml
- Composition model supported (steps within ceremony, no nesting)
- Unit tests for boundary enforcement (warn + block modes)
blocked_by:
- WORK-114
blocks: []
enables: []
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-10 20:22:34
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84767
extensions: {}
version: '2.0'
generated: 2026-02-10
last_updated: '2026-02-10T20:46:28.781483'
---
# WORK-115: Implement Ceremony Context Manager (CH-012)

---

## Context

State-changing methods in WorkEngine (close, update_work, create_work, archive) execute without ceremony context verification. Any code path can mutate work item state without governance logging or contract enforcement. CH-011 (WORK-114) implemented ceremony contract definitions and PreToolUse enforcement, but with empty inputs — the contracts are validated at skill-invoke time but have no structured inputs to validate against. This work item implements the `ceremony_context()` context manager that provides the side-effect boundary: all state changes must occur within a ceremony context, ceremony start/end events are logged, and the context provides structured inputs to the contract system built in CH-011. Two enforcement modes (warn/block) allow gradual migration. Composition (steps within a ceremony) is supported; nesting (ceremony within ceremony) is forbidden.

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

- [ ] `ceremony_context()` context manager in governance_layer.py with CeremonyStart/CeremonyEnd event logging
- [ ] `in_ceremony_context()` check function (thread-local or context-var based)
- [ ] `CeremonyContext` object with `execute_step()` and `log_side_effect()` methods
- [ ] WorkEngine state-changing methods (update_work, close, create_work, archive) guarded by ceremony context check
- [ ] `ceremony_context_enforcement` config toggle in haios.yaml (warn/block modes)
- [ ] Nesting detection: raise error if ceremony_context opened within existing context
- [ ] Unit tests: ceremony_context start/end logging, in_ceremony_context true/false, warn mode logs warning, block mode raises error, nesting forbidden
- [ ] Integration test: WorkEngine.close() outside ceremony context triggers warn/block

---

## History

### 2026-02-10 - Created (Session 336)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md
- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001, REQ-CEREMONY-002)
- @docs/work/active/WORK-114/WORK.md (predecessor: contract enforcement wiring)
