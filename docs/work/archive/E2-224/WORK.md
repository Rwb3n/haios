---
template: work_item
id: E2-224
title: OBSERVE Phase Threshold-Triggered Triage
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: small
category: implementation
spawned_by: null
spawned_by_investigation: INV-048
blocked_by: []
blocks: []
enables: []
related:
- E2-221
- E2-222
- E2-217
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 17:50:43
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T17:51:18'
---
# WORK-E2-224: OBSERVE Phase Threshold-Triggered Triage

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Observations accumulate with `triage_status: pending` but no gate forces triage. Original INV-048 design placed threshold check in routing-gate, but S137 analysis revealed this causes context-switching anti-pattern.

**Root Cause:** Placing threshold check in routing-gate (CHAIN phase) interrupts agent mid-workflow, causing cognitive load and rushed triage.

**Solution:** Move threshold check to OBSERVE phase in close-work-cycle. Agent is already in reflection mode during OBSERVE, so inline triage maintains cognitive continuity.

---

## Current State

Work item in BACKLOG node. High priority - completes the observation feedback loop from E2-217.

---

## Deliverables

- [ ] Add step 3 to close-work-cycle OBSERVE phase: check total pending observations
- [ ] Add step 4: if threshold exceeded, invoke observation-triage-cycle inline
- [ ] Integrate with E2-222 threshold configuration
- [ ] Update close-work-cycle SKILL.md documentation

---

## History

### 2025-12-28 - Created (Session 137)
- Spawned from E2-221 revision after S137 anti-pattern analysis
- Threshold check moved from routing-gate to OBSERVE phase
- Anti-patterns: context-switching, bias toward completion

---

## References

- Investigation: INV-048 (Routing Gate Architecture) - original design
- Related: E2-221 (now pure routing, no thresholds)
- Related: E2-222 (threshold configuration)
- Related: E2-217 (Observation Capture Gate) - the capture mechanism
- Memory: 79890 (bias toward completion anti-pattern)
