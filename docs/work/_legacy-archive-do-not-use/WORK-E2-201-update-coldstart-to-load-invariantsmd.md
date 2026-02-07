---
template: work_item
id: E2-201
title: Update Coldstart to Load invariants.md
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-037
spawned_by_investigation: INV-037
blocked_by:
- E2-200
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-26 10:50:16
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T11:29:07'
---
# WORK-E2-201: Update Coldstart to Load invariants.md

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** INV-037 confirmed coldstart loads 55% L3 (session-specific) content but only 35% L1 (invariants). Missing core philosophical context (Certainty Ratchet, Three Pillars, etc.).

**Root cause:** Coldstart file list was not designed with context level architecture in mind.

---

## Current State

Work item in BACKLOG node. Blocked by E2-200 (invariants.md must exist first).

---

## Deliverables

- [ ] Update `.claude/commands/coldstart.md` to load `.claude/config/invariants.md` as step 3 (L1)
- [ ] Reduce checkpoint loading from 2 to 1 (reduce L3 token cost)
- [ ] Reorder load sequence per INV-037 design: L1 → L2 → L3
- [ ] Update summary output to reference new balance (40% L1, 20% L2, 40% L3)

---

## History

### 2025-12-26 - Created (Session 121)
- Spawned from INV-037 H3 finding (L1/L2/L3 imbalance confirmed)
- Blocked by E2-200

---

## References

- INV-037: Context Level Architecture and Source Optimization
- E2-200: Create invariants.md (blocker)
- E2-164: Coldstart L1 Context Review (related, may be superseded)
