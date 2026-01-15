---
template: work_item
id: E2-289
title: Execute Hierarchy Rename Chapter to Arc
status: active
owner: Hephaestus
created: 2026-01-15
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-064
spawned_by_investigation: INV-064
blocked_by:
- ADR-042
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-15 19:44:46
  exited: null
cycle_docs: {}
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-15
last_updated: '2026-01-15T19:46:01'
---
# WORK-E2-289: Execute Hierarchy Rename Chapter to Arc

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Current hierarchy naming (Epoch→Chapter→Arc) inverts universal story semantics.

**Solution:** Per ADR-042, swap Chapter↔Arc naming to align with universal convention.

**Blocked by:** ADR-042 acceptance (operator must approve decision first)

---

## Current State

Work item in BACKLOG node. Blocked by ADR-042 approval.

---

## Deliverables

- [ ] Rename `chapters/` → `arcs/` directory
- [ ] Rename `CHAPTER.md` → `ARC.md` (6 files)
- [ ] Rename nested `arcs/` → `chapters/`
- [ ] Update `haios.yaml` config keys (active_chapters → active_arcs)
- [ ] Update architecture docs (EPOCH.md, S20, L4, etc.)
- [ ] Test coldstart loads correctly after rename

---

## History

### 2026-01-15 - Created (Session 191)
- Spawned by INV-064 investigation
- Blocked by ADR-042 acceptance

---

## References

- @docs/work/active/INV-064/investigations/001-work-hierarchy-rename-and-queue-architecture.md
- @docs/ADR/ADR-042-hierarchy-rename-chapter-to-arc.md
