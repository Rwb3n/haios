---
template: work_item
id: E2-223
title: Integrate Routing-Gate into Cycle Skills
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: small
category: implementation
spawned_by: null
spawned_by_investigation: INV-048
blocked_by:
- E2-221
blocks: []
enables: []
related:
- E2-221
- E2-222
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 17:25:32
  exited: null
cycle_docs: {}
memory_refs:
- 79985
- 79986
- 79987
- 79988
- 79989
documents:
  investigations: []
  plans:
  - plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T20:08:51'
---
# WORK-E2-223: Integrate Routing-Gate into Cycle Skills

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Three cycle skills (implementation, investigation, close-work) have duplicated routing tables that need to be replaced with routing-gate skill invocation.

**Root Cause:** INV-048 designed the extraction, E2-221 implements the skill, this item integrates it.

---

## Current State

Work item in BACKLOG node. Blocked by E2-221 (routing-gate must exist first).

---

## Deliverables

- [ ] Update implementation-cycle CHAIN phase to invoke routing-gate
- [ ] Update investigation-cycle CHAIN phase to invoke routing-gate
- [ ] Update close-work-cycle CHAIN phase to invoke routing-gate
- [ ] Verify all three skills route correctly after integration

---

## History

### 2025-12-28 - Created (Session 137)
- Spawned from INV-048: Routing Gate Architecture
- Blocked by E2-221 (skill must be created first)

---

## References

- Spawned by: INV-048 (Routing Gate Architecture with Observation Triage Threshold)
- Blocked by: E2-221 (routing-gate skill)
- Related: E2-222 (threshold configuration)
