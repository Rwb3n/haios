---
template: work_item
id: INV-064
title: Work Hierarchy Rename and Queue Architecture
status: active
owner: Hephaestus
created: 2026-01-15
closed: null
milestone: null
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
  entered: 2026-01-15 19:34:10
  exited: null
cycle_docs: {}
memory_refs:
- 81366
- 81367
- 81368
- 81369
- 81370
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-15
last_updated: '2026-01-15T19:36:15'
---
# WORK-INV-064: Work Hierarchy Rename and Queue Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Current hierarchy naming (Epoch→Chapter→Arc→Work Item) conflicts with universal story semantics. In storytelling, an "arc" spans multiple "chapters" - we have it backwards. Additionally, no work queue architecture exists to structure execution across the hierarchy.

**Root Cause:** Session 179 chose names based on pressure patterns ([volumous]/[tight]) rather than narrative convention. The metaphor "Arc = Scene/sequence" was imprecise.

**Impact:**
- Cognitive dissonance when reasoning about hierarchy
- Work items float disconnected from structure
- No batching, ordering, or async execution support

---

## Current State

Investigation in HYPOTHESIZE phase. Context and hypotheses defined.

---

## Deliverables

- [ ] ADR for hierarchy rename decision (Chapter↔Arc swap)
- [ ] Work queue architecture design
- [ ] Migration impact assessment
- [ ] HAIOS init spec draft (showing hierarchy + queues)

---

## History

### 2026-01-15 - Created (Session 191)
- Operator design discussion identified semantic mismatch
- Investigation scaffolded with hypotheses
- Prior work from Session 179 queried (memory 80910-80916)

---

## References

- Memory 80910-80916 (Session 179 hierarchy decision)
- @.claude/haios/epochs/E2/EPOCH.md
- @.claude/haios/epochs/E2/chapters/
