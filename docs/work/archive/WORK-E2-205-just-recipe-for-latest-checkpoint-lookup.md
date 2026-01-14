---
template: work_item
id: E2-205
title: Just recipe for latest checkpoint lookup
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: M7d-Plumbing
priority: medium
effort: low
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-26 15:54:44
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T16:02:36'
---
# WORK-E2-205: Just recipe for latest checkpoint lookup

@docs/README.md
@docs/epistemic_state.md

---

## Context

During coldstart, finding the most recent checkpoint requires either PowerShell or Python one-liners. PowerShell syntax (`$_.Name`) gets mangled when executed through bash due to variable interpolation (documented anti-pattern in epistemic_state.md). This friction point occurred in Session 124 coldstart and can be eliminated with a dedicated just recipe.

Root cause: No reusable recipe for "find most recent file matching pattern in directory".

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add `just checkpoint-latest` recipe to justfile (returns filename of most recent checkpoint)
- [ ] Recipe uses Python for cross-platform compatibility (avoids PowerShell variable escaping issues)
- [ ] Consider: generic `just latest <dir> <pattern>` recipe for reuse in other contexts

---

## History

### 2025-12-26 - Created (Session 124)
- Initial creation

---

## References

- [Related documents]
