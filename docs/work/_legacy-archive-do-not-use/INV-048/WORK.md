---
template: work_item
id: INV-048
title: Routing Gate Architecture with Observation Triage Threshold
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 17:10:51
  exited: null
cycle_docs: {}
memory_refs:
- 79945
- 79946
- 79947
- 79948
- 79949
- 79950
- 79951
documents:
  investigations:
  - investigations/001-routing-gate-architecture-with-observation-triage-threshold.md
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T17:29:04'
---
# WORK-INV-048: Routing Gate Architecture with Observation Triage Threshold

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Routing logic is embedded in each cycle's CHAIN phase. Observations accumulate with `triage_status: pending` but no gate forces triage - they become write-only.

**Gap:** No threshold enforcement. Could close 50 work items, accumulate 150 observations, never triage them. Feedback loop breaks silently.

**Opportunity:** Extract routing into modular `routing-gate` skill that checks system health thresholds before routing to next work. Use observation triage threshold as test case.

---

## Current State

Work item in BACKLOG node. High priority for M7c-Governance.

---

## Deliverables

- [x] Map current routing logic across all cycle CHAIN phases
- [x] Define routing-gate contract (inputs: current work, system state; outputs: next action)
- [x] Design threshold mechanism (configurable via YAML or haios-status)
- [x] Prototype observation triage threshold check
- [x] Identify enforcement point (PreToolUse vs coldstart vs cycle CHAIN)
- [x] Design escape hatch for urgent work

---

## History

### 2025-12-28 - Created (Session 136)
- Spawned from S136 epistemic discussion on observation feedback loop gap
- Observation gates capture but don't force processing
- Routing extraction enables modular health checks

---

## References

- Related: E2-218 (Observation Triage Cycle) - the cycle that would be triggered
- Related: observation-triage-cycle skill
- Related: close-work-cycle CHAIN phase (current routing location)
- Enables: Self-enforcing governance (system checks itself)
