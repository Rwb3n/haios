---
template: work_item
id: E2-246
title: Consolidate Config Files MVP
status: complete
owner: Hephaestus
created: 2026-01-03
closed: 2026-01-03
milestone: M7b-WorkInfra
priority: medium
effort: low
category: implementation
spawned_by: null
spawned_by_investigation: INV-053
blocked_by: []
blocks:
- E2-240
enables:
- E2-240
- E2-241
- E2-242
related:
- INV-052
- INV-053
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 13:07:58
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T14:54:50'
---
# WORK-E2-246: Consolidate Config Files MVP

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** INV-052 proposed 7 YAML config files which is premature optimization. Current 3 files work fine.

**Root cause:** Over-engineering for organizational scaling we don't have yet. INV-053 identified consolidation opportunity.

**Goal:** Consolidate proposed 7 config files into 3 MVP files: haios.yaml, cycles.yaml, components.yaml.

---

## Current State

Work item in BACKLOG node. Should be done first (enables module implementations).

---

## Deliverables

- [ ] Create `.claude/haios/config/haios.yaml` (manifest + toggles + thresholds)
- [ ] Create `.claude/haios/config/cycles.yaml` (cycle definitions + gates + node bindings)
- [ ] Create `.claude/haios/config/components.yaml` (skill + agent + hook registries)
- [ ] Migrate existing config from `.claude/config/` to new location
- [ ] Update config loaders in modules
- [ ] Documentation of config schema

---

## History

### 2026-01-03 - Created (Session 158)
- Spawned from INV-053 (HAIOS Modular Architecture Review)
- NEW item (not in original INV-052 spawn list)
- Prerequisite for module implementations

---

## References

- INV-052: HAIOS Architecture Reference (proposed 7-file schema in S17.11)
- INV-053: HAIOS Modular Architecture Review (consolidation decision)
- docs/work/active/INV-052/SECTION-17.11-CONFIG-FILE-SCHEMAS.md (source schemas)
