---
template: work_item
id: INV-042
title: Machine-Checked DoD Gates
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: medium
category: investigation
spawned_by: E2-212
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: investigation-active
node_history:
- node: backlog
  entered: 2025-12-28 11:17:03
  exited: '2025-12-28T16:15:18.528841'
- node: investigation-active
  entered: '2025-12-28T16:15:18.528841'
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T11:27:43'
---
# WORK-INV-042: Machine-Checked DoD Gates

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Plan DoD criteria (Ground Truth Verification) are documented as checklists but enforced on the honor system. The agent or operator marks items complete without automated verification.

**Evidence from E2-212:**
- Plan Section "Ground Truth Verification" had `[ ]` checkboxes for each criterion
- Grep verification command was documented but never executed
- Work was marked complete with checkboxes still unchecked
- dod-validation-cycle skill validates DoD criteria but doesn't machine-check plan-specific verifications

**Current state:**
- ADR-033 defines DoD: Tests pass, WHY captured, Docs current, Traced files complete
- dod-validation-cycle checks these at close time
- BUT plan-specific criteria (like "grep returns 0 matches") are not automated

**Gap:** The plan's Ground Truth Verification table says "MUST read each file below and verify state" but there's no enforcement mechanism.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Catalog machine-checkable vs human-judgment DoD criteria
- [ ] Evaluate Ground Truth Verification automation (read files, run commands)
- [ ] Prototype plan-specific DoD parser
- [ ] Assess integration with dod-validation-cycle and close-work-cycle
- [ ] Define blockers vs warnings vs optional checks

---

## History

### 2025-12-28 - Created (Session 132)
- Spawned from E2-212 closure gap analysis
- Observed: Ground Truth Verification checkboxes were never validated

---

## References

- Spawned by: E2-212 (Work Directory Structure Migration)
- Related: INV-040 (Automated Stale Reference Detection) - specific example of checkable criterion
- Related: E2-189 (DoD Validation Cycle Skill) - current DoD gate implementation
- Related: ADR-033 (Work Item Lifecycle) - defines DoD criteria
