---
template: work_item
id: E2-276
title: Design ground-cycle Skill
status: complete
owner: Hephaestus
created: 2026-01-06
closed: '2026-01-06'
milestone: M7b-WorkInfra
priority: critical
effort: medium
category: design
spawned_by: null
spawned_by_investigation: null
epoch: E2
chapter: C3-WorkInfra
arc: ARC-001-ground-cycle
blocked_by: []
blocks:
- E2-277
- E2-278
- E2-279
enables:
- E2-280
related:
- E2-271
- INV-052
current_node: implement
node_history:
- node: backlog
  entered: 2026-01-06 19:53:33
  exited: '2026-01-06T20:10:26.946566'
- node: plan
  entered: '2026-01-06T20:10:26.946566'
  exited: '2026-01-06T20:58:40.413775'
- node: implement
  entered: '2026-01-06T20:58:40.413775'
  exited: null
cycle_docs: {}
memory_refs:
- 80858
- 80859
- 80860
- 80918
- 80919
- 80910
- 80911
- 80936
- 80937
- 80938
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-06
last_updated: '2026-01-06T19:54:21'
---
# WORK-E2-276: Design ground-cycle Skill

@docs/README.md
@docs/epistemic_state.md

---

## REQUIRED READING (MUST load before planning)

| Document | Location | Why |
|----------|----------|-----|
| **Epoch Definition** | `.claude/haios/epochs/E2/EPOCH.md` | Epoch-level architecture |
| **Modular Architecture** | `.claude/haios/epochs/E2/architecture/S17-modular-architecture.md` | Module interfaces |
| **Work Item Directory** | `.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md` | Portal system design |
| **Arc Definition** | `.claude/haios/epochs/E2/chapters/workinfra/arcs/ARC-001-ground-cycle/ARC.md` | Arc context and design |
| **Memory: ground-cycle discovery** | Query concepts 80858-80874 | Problem statement |
| **Memory: hierarchy design** | Query concepts 80910-80917 | Final hierarchy |

---

## Context

**Problem:** Agents author plans without knowing architectural context. E2-271 referenced `.claude/lib/` when Epoch 2.2 specifies `.claude/haios/modules/`.

**Root cause:** No mechanism traverses provenance chain to load source investigation's architecture before planning.

**Solution:** ground-cycle - a standalone cycle that loads architectural context before any cognitive work.

---

## Current State

Work item in BACKLOG node. Priority: CRITICAL. This is the foundational piece for fixing context loss.

---

## Deliverables

- [ ] ground-cycle skill definition (`.claude/skills/ground-cycle/SKILL.md`)
- [ ] 4 phases defined: PROVENANCE, ARCHITECTURE, MEMORY, CONTEXT MAP
- [ ] Interface specification (inputs, outputs)
- [ ] Integration points with calling cycles (plan-authoring, investigation, implementation)
- [ ] Exit criteria for each phase

---

## Design Constraints (from REQUIRED READING)

1. **Module boundaries (S17):** ground-cycle likely owned by CycleRunner
2. **Portal traversal (S2C):** Must read `references/REFS.md` when implemented
3. **Token budgets (S15):** GroundedContext must fit within L4 budget
4. **Epoch architecture:** Output must include epoch/chapter/arc references

---

## History

### 2026-01-06 - Created (Session 177)
- Spawned from Session 177 ground-cycle discovery
- Part of ARC-001-ground-cycle
- Memory refs: 80858-80874 (discovery), 80910-80917 (hierarchy)

---

## References

- @.claude/haios/epochs/E2/chapters/workinfra/arcs/ARC-001-ground-cycle/ARC.md
- @.claude/haios/epochs/E2/EPOCH.md
- @.claude/haios/epochs/E2/architecture/S17-modular-architecture.md
- @.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md
