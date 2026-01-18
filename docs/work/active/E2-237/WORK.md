---
template: work_item
id: E2-237
title: Cycle Definitions Config File
status: archived
owner: Hephaestus
created: 2025-12-30
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by: []
blocks:
- E2-239
enables:
- E2-239
related:
- E2-238
- E2-240
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 21:40:20
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2026-01-18T21:56:50'
---
# WORK-E2-237: Cycle Definitions Config File

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Cycle definitions are currently embedded in SKILL.md files as markdown prose. This makes it impossible to programmatically validate, extend, or orchestrate cycles consistently.

**Root cause:** Organic growth - skills were added incrementally without centralized schema.

**Solution:** Create `.claude/haios/config/cycle-definitions.yaml` with full schema for all 7 cycles per INV-052 SECTION-2F design.

---

## Current State

Design complete in INV-052/SECTION-2F-CYCLE-DEFINITIONS-SCHEMA.md. Ready for implementation.

---

## Deliverables

- [ ] Create `.claude/haios/config/` directory structure
- [ ] Create `cycle-definitions.yaml` with all 7 cycles (implementation, investigation, close-work, work-creation, checkpoint, observation-triage, plan-authoring)
- [ ] Validate schema matches SECTION-2F specification
- [ ] Add schema validation script or tests

---

## History

### 2025-12-30 - Created (Session 151)
- Spawned from INV-052 architecture redesign
- Design reference: SECTION-2F-CYCLE-DEFINITIONS-SCHEMA.md

---

## References

- docs/work/active/INV-052/SECTION-2F-CYCLE-DEFINITIONS-SCHEMA.md
- docs/work/active/INV-052/SECTIONS-INDEX.md
