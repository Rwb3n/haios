---
template: work_item
id: E2-019
title: "Concept Type Normalization"
status: archived
owner: Hephaestus
created: 2025-12-23
closed: null
milestone: M8-Memory
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
    entered: 2025-12-23T19:06:12
    exited: null
cycle_docs: {}
memory_refs: [64641, 64642, 64643, 64644, 64645, 64646, 64647, 64648, 64649, 64650, 64651, 64652]
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-23
last_updated: 2025-12-23T18:04:04
---
# WORK-E2-019: Concept Type Normalization

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** 110+ distinct concept types, many duplicates/variants.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add synthesis stats to `cli.py status` command (clusters, members, last run)
- [ ] Run synthesis with `--max-bridges 200` (double default) to connect E2-015 learnings
- [ ] Identify which concepts lack embeddings (by type, content length, creation date)
- [ ] Run embedding completion script
- [ ] Verify 100% coverage
- [ ] Add entity embedding generation to ETL pipeline
- [ ] Generate embeddings for existing entities
- [ ] Verify entity retrieval works
- [ ] Define canonical type set (Greek Triad + LangExtract core types)
- [ ] Create migration to normalize existing concepts
- [ ] Update extraction to use canonical types

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
