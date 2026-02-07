---
template: work_item
id: E2-204
title: Add L1/L2/L3 Context Level Definitions
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
  entered: 2025-12-26 14:23:46
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T14:56:36'
---
# WORK-E2-204: Add L1/L2/L3 Context Level Definitions

@docs/README.md
@docs/epistemic_state.md

---

## Context

INV-039 identified that L1/L2/L3 terms are used in coldstart.md but never formally defined. INV-037 designed the framework but definitions only exist in the investigation file, not in operational docs. Need to add formal definitions to invariants.md.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add "Context Levels" section to invariants.md with L1/L2/L3 definitions
- [ ] L1 = Invariants (evergreen, rarely changes)
- [ ] L2 = Operational (session-applicable, may evolve)
- [ ] L3 = Session-specific (checkpoints, memory queries)
- [ ] Keep invariants.md at or under 100 lines

---

## History

### 2025-12-26 - Created (Session 122)
- Initial creation
- Spawned from INV-039 (Information Architecture Policy Audit)

---

## References

- INV-039: Information Architecture Policy Audit (spawned this)
- INV-037: Context Level Architecture (original framework design)
- invariants.md: Target location for definitions
