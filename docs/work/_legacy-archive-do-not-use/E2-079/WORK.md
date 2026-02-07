---
template: work_item
id: E2-079
title: CLAUDE.md De-bloat (Progressive Static Context)
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-28
milestone: M7d-Plumbing
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
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
last_updated: '2025-12-28T11:57:45'
---
# WORK-E2-079: CLAUDE.md De-bloat (Progressive Static Context)

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** CLAUDE.md has grown large (~500+ lines). Much content is reference material that could live elsewhere, loaded on-demand.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [x] Audit CLAUDE.md sections by usage frequency - done, split into L0/L1/L2
- [x] Identify content that can move to on-demand references - moved to .claude/config/
- [x] Create reference directory - `.claude/config/` with north-star.md, invariants.md, roadmap.md
- [x] Slim CLAUDE.md to essentials - **161 lines** (target was 150, from 500+)
- [x] Update coldstart to surface refs availability - loads L0/L1/L2 at session start
- [x] Verify agent can still access reference content - coldstart.md lines 18-25

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
