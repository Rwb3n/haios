---
template: work_item
id: E2-254
title: ContextLoader Module - Bootstrap and Session
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: medium
effort: high
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by:
- E2-251
- E2-252
- E2-253
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 23:21:49
  exited: null
cycle_docs:
  backlog: docs/work/active/E2-254/plans/PLAN.md
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
  planss:
  - docs/work/active/E2-254/plans/PLAN.md
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T23:23:43'
---
# WORK-E2-254: ContextLoader Module - Bootstrap and Session

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md

---

## Context

**Problem:** ContextLoader module doesn't exist. Coldstart is a markdown command that Claude interprets - not modularized code.

**Scope (from INV-052 S17.3):**
- S5: Session number computation - **Not modularized**
- S14: Bootstrap architecture (L0-L3 hierarchy) - **In markdown only**
- S15: Information architecture (token budgets) - **Not modularized**
- S2A: Session lifecycle - **In coldstart.md only**

**Current implementation:**
- `.claude/commands/coldstart.md` - Markdown instructions
- Session number: computed ad-hoc from haios-status.json

---

## IMPORTANT: Recursive Adjustment Note

This work item requires **recursive scope tightening** during implementation:
1. Query memory for prior decisions on coldstart architecture
2. Determine if ContextLoader should be Python module or enhanced markdown
3. Consider: is programmatic bootstrap needed, or is markdown sufficient?
4. Adjust deliverables based on actual grounding requirements
5. May be lower priority if markdown-based coldstart works well

---

## Deliverables

- [ ] Create `context_loader.py` module
- [ ] Implement `load_grounded_context()` method
- [ ] Implement `compute_session_number()` method
- [ ] Integrate with MemoryBridge for strategy retrieval
- [ ] Integrate with WorkEngine for ready items
- [ ] Tests for ContextLoader
- [ ] Migrate coldstart to invoke ContextLoader (or document decision not to)
- [ ] Verify runtime consumers exist (E2-250 DoD criterion)

---

## History

### 2026-01-03 - Created (Session 162)
- Part of Epoch 2.2 full migration plan
- Spawned from INV-052 Section 17 analysis
- Currently no module exists - coldstart is markdown

---

## References

- `docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md` - Module design (S17.3)
- `.claude/commands/coldstart.md` - Current implementation
- `.claude/haios/manifesto/L0-telos.md` through `L4-implementation.md` - Context to load
