---
template: work_item
id: E2-252
title: Complete GovernanceLayer Module - Scaffold Validate
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
blocked_by:
- E2-251
blocks: []
enables:
- E2-254
related:
- E2-240
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 23:21:49
  exited: null
cycle_docs:
  backlog: docs/work/active/E2-252/plans/PLAN.md
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/work/active/E2-252/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-17T15:31:58'
---
# WORK-E2-252: Complete GovernanceLayer Module - Scaffold Validate

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md

---

## Context

**Problem:** GovernanceLayer (E2-240) handles gate checks and transition validation but doesn't yet absorb scaffold and validate operations per INV-052 Section 17.

**Scope (from INV-052 S17.6):**
- S1A/S1B: Hooks - DONE (hooks work, layer validates)
- S16: Scaffold Templates - **Missing**
- Validation logic - **Missing**

**Justfile recipes still using old code:**
- `just validate` → `.claude/lib/validate.py`
- `just scaffold` → `.claude/lib/scaffold.py`

---

## IMPORTANT: Recursive Adjustment Note

This work item requires **recursive scope tightening** during implementation:
1. Query memory for prior decisions on scaffold/validate before designing
2. Determine if scaffold belongs in GovernanceLayer or ContextLoader (S16 vs S14)
3. Adjust deliverables if scope proves larger/smaller than estimated
4. Update related work items if dependencies change

---

## Deliverables

- [ ] Add `validate_template()` method to GovernanceLayer
- [ ] Add `scaffold_template()` method to GovernanceLayer (or defer to ContextLoader)
- [ ] Add CLI commands: `validate`, `scaffold`
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
- `.claude/lib/validate.py` - Current implementation to absorb
- `.claude/lib/scaffold.py` - Current implementation to absorb
- `docs/work/archive/E2-240/` - Prior GovernanceLayer work
