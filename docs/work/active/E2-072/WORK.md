---
template: work_item
id: E2-072
title: Critique Subagent (Assumption Surfacing)
status: active
owner: Hephaestus
created: 2025-12-23
closed: null
milestone: Epoch3-FORESIGHT
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
spawned_by_investigation: null
arc: pipeline
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
last_updated: '2026-01-25T00:36:25'
---
# WORK-E2-072: Critique Subagent (Assumption Surfacing)

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Design decisions contain implicit assumptions. Main agent has cognitive bias (sunk cost, confirmation). Isolated critique agent can provide unbiased analysis.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

> **Note (Session 212):** Deliverables cleaned up from legacy corruption (Session 142 bug). Original had 50+ unrelated items copy-pasted from backfill process.

- [ ] Create `.claude/agents/critic.md` subagent definition
- [ ] Define critique framework (Assumption Surfacing as default)
- [ ] Create `/critique <artifact>` command or skill invocation
- [ ] Test on 3 existing designs, validate improvement

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

### 2026-01-19 - Deliverables Cleaned (Session 212)
- Fixed legacy deliverables corruption (Session 142 bug pattern)
- Applied memory strategy (concept 80224): trust Context/title over corrupted Deliverables
- Reduced from 50+ unrelated items to 4 correct deliverables matching title

---

## References

- [Related documents]
