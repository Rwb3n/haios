---
template: work_item
id: E2-164
title: "Coldstart L1 Context Review"
status: active
owner: Hephaestus
created: 2025-12-24
closed: null
milestone: M7b-WorkInfra
priority: medium
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
    entered: 2025-12-24T09:51:06
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-24
last_updated: 2025-12-24T10:34:24
---
# WORK-E2-164: Coldstart L1 Context Review

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Agent spent too long querying to learn synthesis is idempotent - core system knowledge that should be known immediately at session start. L1 context (essential system facts) isn't well-defined.

**Example failures:**
- Didn't know synthesis idempotency without querying
- Work file flow wasn't clear (created INV-027 without work file)
- Manual node_history updates (should know about just recipes or automation)

**Root cause:** Coldstart loads checkpoints/epistemic_state but not "core system facts" like idempotency, key architectural invariants, critical tooling patterns.

---

## Current State

Coldstart loads: CLAUDE.md, epistemic_state, 2 checkpoints, haios-status-slim, memory query. Missing: core system invariants/facts.

---

## Deliverables

- [ ] Define L1 context: What MUST be known immediately (idempotency, work file flow, key recipes)
- [ ] Create `.claude/REFS/CORE-FACTS.md` or similar for essential system knowledge
- [ ] Update coldstart to load/surface L1 context prominently
- [ ] Review: synthesis idempotency, work file flow, node automation, key just recipes

---

## History

### 2025-12-24 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
