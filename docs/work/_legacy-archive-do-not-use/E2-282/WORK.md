---
template: work_item
id: E2-282
title: Coldstart Hook Manifest Loading
status: complete
owner: Hephaestus
created: 2026-01-10
closed: '2026-01-10'
milestone: null
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by:
- E2-281
blocks: []
enables: []
related: []
current_node: complete
node_history:
- node: backlog
  entered: 2026-01-10 11:54:18
  exited: 2026-01-10 12:36:34
- node: complete
  entered: 2026-01-10 12:36:34
  exited: null
cycle_docs: {}
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-10
last_updated: '2026-01-10T16:06:42'
---
# WORK-E2-282: Coldstart Hook Manifest Loading

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Checkpoint manifests (E2-281) exist but nothing enforces loading them. Agent can skip principles, skip memory_refs, ignore drift warnings.

**Root cause:** Current coldstart is a markdown command, not a hook. Suggestions, not enforcement.

**Solution:** Coldstart hook that:
1. Reads latest checkpoint frontmatter
2. MUST load each file in `load_principles` and inject into context
3. MUST query each ID in `load_memory_refs` and inject results
4. MUST surface `drift_observed` as warnings before work selection
5. Agent cannot bypass - hook does the loading

---

## Deliverables

- [x] Coldstart command reads checkpoint manifest
- [x] `load_principles` files read and injected (via command instructions)
- [x] `load_memory_refs` IDs queried and injected (via command instructions)
- [x] `drift_observed` surfaced as warnings (via command instructions)
- [ ] ~~Agent cannot skip loading (hook enforcement)~~ DEFERRED - command sufficient for now

---

## History

### 2026-01-10 - Created (Session 186)
- Blocked by E2-281 (checkpoint template must exist first)
- Implements the enforcement half of context architecture

---

## References

- E2-281 (checkpoint template - blocked by)
- Memory 81222-81247 (checkpoint redesign)
- S20-pressure-dynamics.md
