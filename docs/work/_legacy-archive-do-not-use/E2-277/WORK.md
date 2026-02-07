---
template: work_item
id: E2-277
title: Implement Portal System in Work Items
status: complete
owner: Hephaestus
created: 2026-01-06
closed: '2026-01-06'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
epoch: E2
chapter: C3-WorkInfra
arc: ARC-002-portal-system
blocked_by: []
blocks: []
enables:
- E2-280
related:
- E2-271
- INV-052
current_node: implement
node_history:
- node: backlog
  entered: 2026-01-06 19:54:29
  exited: '2026-01-06T20:19:23.983184'
- node: plan
  entered: '2026-01-06T20:19:23.983184'
  exited: '2026-01-06T23:08:05.609077'
- node: implement
  entered: '2026-01-06T23:08:05.609077'
  exited: null
cycle_docs: {}
memory_refs:
- 80910
- 80911
- 80912
- 80999
- 81000
- 81001
- 81002
- 81003
- 81004
- 81005
- 81006
- 81007
- 81008
- 81009
- 81010
- 81011
- 81012
- 81013
- 81014
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-06
last_updated: '2026-01-06T20:19:12'
---
# WORK-E2-277: Implement Portal System in Work Items

@docs/README.md
@docs/epistemic_state.md

---

## REQUIRED READING (MUST load before planning)

| Document | Location | Why |
|----------|----------|-----|
| **Work Item Directory** | `.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md` | **PRIMARY** - Portal system design |
| **Epoch Definition** | `.claude/haios/epochs/E2/EPOCH.md` | Epoch architecture |
| **Modular Architecture** | `.claude/haios/epochs/E2/architecture/S17-modular-architecture.md` | WorkEngine owns portals |

---

## Context

**Problem:** INV-052 Section 2C designed portal system (`references/REFS.md`) but it was never implemented. Work items exist as isolated files with no traversable links to parent investigations, ADRs, or memory.

**Impact:** ground-cycle cannot traverse provenance because portals don't exist.

**Solution:** Implement portal system per S2C design.

---

## Current State

Work item in BACKLOG node. Blocked by E2-276 (ground-cycle design must specify portal interface).

---

## Deliverables

- [ ] Create `references/REFS.md` in work item template
- [ ] Define portal types: spawned_from, blocks, related, adr, memory, external
- [ ] WorkEngine creates/maintains portals on work item creation
- [ ] WorkEngine updates portals on status changes
- [ ] ground-cycle can traverse portals

---

## History

### 2026-01-06 - Created (Session 177)
- Spawned from Session 177 synthesis
- Part of ARC-002-portal-system
- Portal design from INV-052 Section 2C

---

## References

- @.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md (portal design)
- @.claude/haios/epochs/E2/EPOCH.md
- @docs/work/archive/INV-052/SECTION-2C-WORK-ITEM-DIRECTORY.md (original)
