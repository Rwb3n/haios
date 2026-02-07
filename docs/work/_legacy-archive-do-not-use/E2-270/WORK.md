---
template: work_item
id: E2-270
title: Command PowerShell Elimination
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-05'
milestone: M7b-WorkInfra
priority: medium
effort: small
category: implementation
spawned_by: null
spawned_by_investigation: INV-057
blocked_by: []
blocks: []
enables: []
related:
- INV-057
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 22:28:56
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T22:30:18'
---
# WORK-E2-270: Command PowerShell Elimination

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Commands `validate.md` and `new-handoff.md` invoke PowerShell directly, breaking cross-platform portability.

**Root cause:** E2-120 migrated hooks to Python but commands still contain raw PowerShell invocations.

**Source:** INV-057 investigation (Session 172)

---

## Current State

Work item in BACKLOG node. Ready for implementation.

---

## Deliverables

- [ ] Replace PowerShell in `validate.md` with `just validate` recipe
- [ ] Replace PowerShell in `new-handoff.md` with `just scaffold` recipe
- [ ] Update `README.md` to remove .ps1 script references
- [ ] Update `status.md` to use Python module instead of deprecated haios_etl

---

## History

### 2026-01-04 - Created (Session 172)
- Spawned from INV-057 investigation
- Fixes portability issues in 4 command files

---

## References

- INV-057: Commands Skills Templates Portability investigation
- E2-120: PowerShell Elimination (completed hook migration)
