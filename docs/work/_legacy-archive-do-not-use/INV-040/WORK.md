---
template: work_item
id: INV-040
title: Automated Stale Reference Detection
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-29
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
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 11:15:40
  exited: null
cycle_docs: {}
memory_refs:
- 80230
- 80231
- 80232
- 80233
- 80234
- 80235
- 80236
- 80237
- 80238
documents:
  investigations:
  - investigations/001-automated-stale-reference-detection.md
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-29T10:57:50'
---
# WORK-INV-040: Automated Stale Reference Detection

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** E2-212 was prematurely closed with Phase 4.3 (Consumer Verification) incomplete. The plan's MUST requirement "Verify zero stale references" was not enforced, resulting in 10+ files with outdated path patterns.

**Root cause:** Consumer verification is a manual grep check in the plan. The close workflow trusts the operator/agent to complete it but has no automated gate.

**Evidence:** Session 132 discovered stale `docs/plans/PLAN-{id}-*.md` references in skills, agents, and commands after E2-212 was marked complete.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Document current stale reference patterns (what to detect)
- [ ] Evaluate detection mechanisms (grep in close workflow, pre-commit hook, CI)
- [ ] Prototype automated detection script
- [ ] Recommend integration point (close-work-cycle, just commit-close, or separate audit)
- [ ] Define blocking vs warning behavior

---

## History

### 2025-12-28 - Created (Session 132)
- Spawned from E2-212 closure gap analysis
- Observed pattern: migrations change path patterns but consumers lag

---

## References

- Spawned by: E2-212 (Work Directory Structure Migration)
- Related: E2-152 (Work-Item Tooling Cutover) - has similar consumer verification need
- Related: ADR-033 (Work Item Lifecycle) - DoD requires traced files complete
