---
template: work_item
id: E2-251
title: Complete WorkEngine Module - Cascade Spawn Backfill
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by: []
blocks:
- E2-252
- E2-253
enables:
- E2-254
- E2-255
related:
- E2-250
- E2-242
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 23:21:49
  exited: null
cycle_docs:
  backlog: docs/work/active/E2-251/plans/PLAN.md
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-251/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T23:22:31'
---
# WORK-E2-251: Complete WorkEngine Module - Cascade Spawn Backfill

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md

---

## Context

**Problem:** WorkEngine (E2-242/E2-250) handles node transitions but doesn't yet absorb cascade, spawn, and backfill operations per INV-052 Section 17.

**Scope (from INV-052 S17.4):**
- S2B: Work item lifecycle (DAG, node_history) - DONE
- S2C: Work item directory - DONE
- S3: State storage - DONE
- **Missing:** cascade.py, spawn.py, backfill.py functionality

**Justfile recipes still using old code:**
- `just cascade` → `.claude/lib/cascade.py`
- `just spawn-tree` → `.claude/lib/spawn.py`
- `just backfill` → `.claude/lib/backfill.py`

---

## IMPORTANT: Recursive Adjustment Note

This work item requires **recursive scope tightening** during implementation:
1. Query memory for prior decisions on cascade/spawn/backfill before designing
2. Verify each function's actual usage before migrating (may be unused)
3. Adjust deliverables if scope proves larger/smaller than estimated
4. Update related work items (E2-252+) if dependencies change

---

## Deliverables

- [ ] Add `cascade()` method to WorkEngine
- [ ] Add `spawn_tree()` method to WorkEngine
- [ ] Add `backfill()` method to WorkEngine
- [ ] Add CLI commands: `cascade`, `spawn-tree`, `backfill`
- [ ] Update justfile recipes to use cli.py
- [ ] Tests for new methods
- [ ] Verify runtime consumers exist (E2-250 DoD criterion)

---

## History

### 2026-01-03 - Created (Session 162)
- Part of Epoch 2.2 full migration plan
- Spawned from INV-052 Section 17 analysis

---

## References

- `docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md` - Module design
- `.claude/lib/cascade.py` - Current implementation to absorb
- `.claude/lib/spawn.py` - Current implementation to absorb
- `.claude/lib/backfill.py` - Current implementation to absorb
- `docs/work/archive/E2-250/` - Prior WorkEngine integration
