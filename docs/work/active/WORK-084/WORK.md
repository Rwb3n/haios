---
template: work_item
id: WORK-084
title: Implement Lifecycle Signatures (CH-001)
type: feature
status: active
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-001-LifecycleSignature
arc: lifecycles
closed: null
priority: high
effort: medium
traces_to:
- REQ-LIFECYCLE-001
requirement_refs: []
source_files:
- .claude/haios/modules/cycle_runner.py
acceptance_criteria:
- CycleRunner.run() returns typed LifecycleOutput object
- No auto-chaining to next lifecycle
- Each lifecycle has documented Input -> Output signature
- Unit tests verify pure function behavior
blocked_by: []
blocks:
- WORK-085
- WORK-086
- WORK-087
- WORK-088
- WORK-089
enables:
- WORK-093
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
last_updated: '2026-02-03T19:42:27'
---
# WORK-084: Implement Lifecycle Signatures (CH-001)

---

## Context

CycleRunner exists as a stateless phase gate validator (E2-255). Current API validates gates but doesn't return typed outputs. Skills complete via markdown interpretation with implicit chaining in CHAIN phases.

**Gap to address:**
- No typed return objects (Findings, Specification, etc.)
- CHAIN phases in skills prompt for next lifecycle (soft auto-chain)
- No explicit pure function signature

**Current State (from CH-001):**
```python
# Actual current methods (cycle_runner.py:113-148)
def get_cycle_phases(cycle_id: str) -> List[str]
def check_phase_entry(cycle_id: str, phase: str, work_id: str) -> GateResult
def check_phase_exit(cycle_id: str, phase: str, work_id: str) -> GateResult
```

---

## Deliverables

- [ ] Define LifecycleOutput base dataclass with outcome, work_id, timestamp, status
- [ ] Define 5 output types: Findings, Specification, Artifact, Verdict, PriorityList
- [ ] Add CycleRunner.run(work_id, lifecycle) -> LifecycleOutput method
- [ ] Document Input -> Output signatures for all 5 lifecycles
- [ ] Unit tests verifying pure function behavior (no side effects)
- [ ] Integration test: Design completes, returns Specification, no implementation spawned

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-001-LifecycleSignature
- Foundation work item for lifecycles arc

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-001-LifecycleSignature.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-001)
- @.claude/haios/modules/cycle_runner.py
