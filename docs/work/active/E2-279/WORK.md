---
template: work_item
id: E2-279
title: WorkEngine Decomposition
status: complete
owner: Hephaestus
created: 2026-01-08
closed: '2026-01-09'
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-061
spawned_by_investigation: INV-061
blocked_by: []
blocks: []
enables: []
related: []
current_node: plan
node_history:
- node: backlog
  entered: 2026-01-08 20:03:04
  exited: 2026-01-08 23:50:00
- node: plan
  entered: 2026-01-08 23:50:00
  exited: null
cycle_docs:
  plan: docs/work/active/E2-279/plans/PLAN.md
memory_refs:
- 81184
- 81185
- 81186
- 81187
- 81188
- 81189
- 81190
- 81191
- 81192
- 72314
- 81194
- 81195
- 81196
- 81197
- 81198
- 81199
- 81200
- 81201
- 81202
- 81203
- 81204
- 81205
- 81206
- 81207
- 81208
- 81209
- 81210
operator_decisions: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-279/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-08
last_updated: '2026-01-08T23:50:44'
---
# WORK-E2-279: WorkEngine Decomposition

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** WorkEngine is 1195 lines with too many responsibilities (CRUD, cascade, portal, spawn, backfill). This violates svelte governance criteria (max 300 lines per module).

**Root cause:** Organic growth during Epoch 2 added capabilities without decomposition.

**Solution:** Decompose into 5 atomic modules per INV-061 findings.

---

## Deliverables

- [ ] Extract CascadeEngine (~290 lines) from WorkEngine
- [ ] Extract PortalManager (~200 lines) from WorkEngine
- [ ] Extract SpawnTree (~100 lines) from WorkEngine
- [ ] Extract BackfillEngine (~160 lines) from WorkEngine
- [ ] Refactor WorkEngine core to ~300 lines
- [ ] Update consumers (just recipes) to use new modules
- [ ] Tests pass

---

## History

### 2026-01-08 - Created (Session 183)
- Spawned from INV-061 (Svelte Governance Architecture)
- Per H2 findings: decomposition is feasible

---

## References

@docs/work/active/INV-061/WORK.md
@.claude/haios/modules/work_engine.py
