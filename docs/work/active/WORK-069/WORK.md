---
template: work_item
id: WORK-069
title: Decision Traceability Schema Design
type: design
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-055
chapter: flow/CH-009
arc: flow
closed: '2026-02-02'
priority: high
effort: medium
traces_to:
- REQ-TRACE-005
requirement_refs: []
source_files: []
acceptance_criteria:
- EPOCH.md decisions have assigned_to field with arc/chapter mappings
- Chapter files have implements_decisions field listing decision IDs
- Validation warns on decisions without assigned_to
- CH-009 chapter file documents the decision traceability ceremony
blocked_by: []
blocks:
- WORK-070
- WORK-071
- WORK-075
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 23:06:07
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83018
- 83019
- 83020
- 83119
- 83120
- 83121
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-02T08:25:32'
---
# WORK-069: Decision Traceability Schema Design

---

## Context

**Spawned from:** WORK-055 (Multi-Level Governance Investigation)

**Problem:** Epoch decisions have no structured traceability to chapters. Decisions are prose in EPOCH.md with no `assigned_to` field. This allows decisions to exist without explicit chapter ownership, causing decomposition leakage.

**Layer Placement:** This is a **CEREMONIES** layer concern - the schema enables the ceremony that verifies decision coverage before decomposition.

**Five-Layer Context:**
```
PRINCIPLES       - L0-L3
WAYS OF WORKING  - Universal flow
CEREMONIES       - Decision assignment ceremony ← THIS
ACTIVITIES       - Governed primitives
ASSETS           - EPOCH.md, chapter files (modified by this schema)
```

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] **EPOCH.md Decision Schema** - Add `assigned_to: [{arc, chapters}]` field to decisions
- [ ] **Chapter implements_decisions Field** - Add `implements_decisions: [D1, D3]` to chapter files
- [ ] **Validation Rule** - Decision without `assigned_to` triggers warning
- [ ] **Validation Integration** - Wire validation into audit skill or work-creation-cycle
- [ ] **CH-009 Chapter File** - Document the decision traceability ceremony

---

## History

### 2026-02-02 - Populated (Session 283)
- work-creation-cycle POPULATE phase
- Added acceptance_criteria to frontmatter
- Added "Validation Integration" deliverable (gap from WORK-055 Design Outputs)
- Validated traces_to: REQ-TRACE-005 exists in registry

### 2026-02-01 - Created (Session 279)
- Spawned from WORK-055
- Assigned to flow arc as CH-009 (Decision Traceability Ceremony)
- Framed as CEREMONIES layer concern per Five-Layer Hierarchy

---

## References

- @docs/work/active/WORK-055/WORK.md (source investigation)
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md (parent arc)
- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 8 - Multi-Level Governance)
