---
template: work_item
id: E2-203
title: Reconcile Anti-Pattern Duplication
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-039
spawned_by_investigation: INV-039
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-26 14:23:45
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T14:51:14'
---
# WORK-E2-203: Reconcile Anti-Pattern Duplication

@docs/README.md
@docs/epistemic_state.md

---

## Context

INV-039 identified anti-pattern duplication between invariants.md (6 patterns) and epistemic_state.md (8 patterns). The 6 L1 patterns are duplicated, causing authoritative source confusion. epistemic_state.md should reference invariants.md for L1 patterns and only list the 2 implementation-specific ones (PowerShell, Static Registration).

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Update epistemic_state.md anti-pattern table to reference invariants.md for L1 patterns
- [ ] Keep only PowerShell-bash and Static Registration patterns in epistemic_state.md
- [ ] Verify no content loss (all patterns documented somewhere)

---

## History

### 2025-12-26 - Created (Session 122)
- Initial creation
- Spawned from INV-039 (Information Architecture Policy Audit)

---

## References

- INV-039: Information Architecture Policy Audit (spawned this)
- invariants.md: L1 anti-patterns (authoritative)
- epistemic_state.md: Current duplicated content
