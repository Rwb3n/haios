---
template: work_item
id: E2-088
title: Epistemic State Slim-Down
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-26
milestone: M7d-Plumbing
priority: low
effort: small
category: implementation
spawned_by: Session 81
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-26T15:34:59'
---
# WORK-E2-088: Epistemic State Slim-Down

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** `docs/epistemic_state.md` has stale sections (Unknowns last updated Session 58, Mitigation duplicates CLAUDE.md). Only anti-patterns section provides unique value.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Rename `epistemic_state.md` -> `anti-patterns.md` (or keep name, retitle)
- [ ] Delete stale sections (Unknowns, Recently Surfaced, Mitigation Mechanisms)
- [ ] Update `/coldstart` to load renamed file
- [ ] Update CLAUDE.md references

**Current State:**
- Unknowns: last updated Session 58 (stale)
- Mitigation: duplicates CLAUDE.md governance section
- Anti-patterns: **only unique value** - actively maintained behavioral patterns

**Decision:** Keep anti-patterns, prune everything else. File becomes behavioral pattern reference, not catch-all.

**Related:** E2-079 (CLAUDE.md De-bloat) - similar context reduction effort

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
