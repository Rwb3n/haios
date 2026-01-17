---
template: work_item
id: INV-068
title: Cycle Delegation Architecture - Subagents for Cycle Execution
status: active
owner: Hephaestus
created: 2026-01-17
closed: null
milestone: null
priority: medium
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related:
- INV-062
- INV-065
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-17 15:07:16
  exited: null
cycle_docs: {}
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-17
last_updated: '2026-01-17T15:07:50'
---
# WORK-INV-068: Cycle Delegation Architecture - Subagents for Cycle Execution

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Main agent track (orchestrator) reaches context limits faster as governance strengthens. Coldstart, hooks, status injection, and inline cycle execution all consume context. The main track should focus on operator/supervisor routing, not execute full cycles inline.

**Root Cause:** Cycles (implementation-cycle, close-work-cycle, investigation-cycle) execute inline in the main conversation. Each phase consumes context. The orchestrator becomes a worker instead of delegating.

**Alignment:**
- L4 Epoch 4 vision: Orchestrator at L3-L4, Workers at L5-L7
- S25 SDK path: Custom tools execute cycles, harness controls flow
- S20 pressure dynamics: Main track [volumous] survey/route, subagents [tight] execution

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

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
-->

- [ ] Findings document with architectural options for cycle delegation
- [ ] Trade-off analysis: inline execution vs subagent delegation
- [ ] Spawned work items for implementation (if warranted)

---

## History

### 2026-01-17 - Created (Session 199)
- Initial creation

---

## References

- [Related documents]
