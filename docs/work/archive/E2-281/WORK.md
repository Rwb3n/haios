---
template: work_item
id: E2-281
title: Checkpoint Loading Manifest Redesign
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
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-10 11:52:47
  exited: null
cycle_docs: {}
memory_refs:
- 81222
- 81223
- 81224
- 81225
- 81248
- 81249
- 81250
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-10
last_updated: '2026-01-10T11:55:22'
---
# WORK-E2-281: Checkpoint Loading Manifest Redesign

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Checkpoints are write-only activity logs (112 lines) that don't prevent architectural drift. Session 186 demonstrated that skills drifted from S20 principles despite checkpoints being created every session.

**Root cause:** Checkpoints capture what happened, not what should be loaded next session. They're logs, not manifests.

**Solution:** Redesign checkpoint as a ~20 line loading manifest with:
- `load_principles`: files coldstart MUST read
- `load_memory_refs`: concept IDs coldstart MUST query
- `pending`: work for next session
- `drift_observed`: principle violations flagged

---

## Deliverables

- [ ] New checkpoint template (~20 lines frontmatter, no body)
- [ ] `load_principles` field (list of files)
- [ ] `load_memory_refs` field (list of concept IDs)
- [ ] `pending` field (list of pending work)
- [ ] `drift_observed` field (list of violations)
- [ ] E2-282 implements the coldstart hook that reads this

---

## History

### 2026-01-10 - Created (Session 186)
- Spawned from Session 186 meta-observation: checkpoints didn't prevent E2.2 drift
- Design: checkpoint as loading manifest, not activity log

---

## References

- Memory 81222-81247 (checkpoint redesign concepts)
- Memory 81248-81266 (E2.2 drift diagnosis)
- S20-pressure-dynamics.md (the principles that were drifted from)
