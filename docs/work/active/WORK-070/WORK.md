---
template: work_item
id: WORK-070
title: Multi-Level DoD Cascade Design
type: design
status: active
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-055
chapter: flow/CH-010
arc: flow
closed: null
priority: high
effort: medium
traces_to:
- REQ-TRACE-003
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by:
- WORK-069
blocks:
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
- 83021
- 83022
- 83023
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-02T00:56:30'
---
# WORK-070: Multi-Level DoD Cascade Design

---

## Context

**Spawned from:** WORK-055 (Multi-Level Governance Investigation)

**Problem:** DoD exists only at work item level (ADR-033). No Chapter DoD, Arc DoD, or Epoch DoD verifies that the sum of completed work achieves the stated objectives.

**Layer Placement:** This is a **CEREMONIES** layer concern - defining the ceremonies that verify completeness at each hierarchy level.

**Five-Layer Context:**
```
PRINCIPLES       - L0-L3
WAYS OF WORKING  - Universal flow
CEREMONIES       - close-chapter, close-arc, close-epoch ceremonies ← THIS
ACTIVITIES       - Governed primitives
ASSETS           - Chapter files, ARC.md, EPOCH.md (verified by these ceremonies)
```

**Ceremony Pattern:**
```
CEREMONY (entry gate) → BLACK-BOX EXECUTION → CEREMONY (exit gate)
```

Each level gets entry/exit ceremonies with DoD criteria.

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

- [ ] **Chapter DoD Ceremony** - `close-chapter-ceremony` skill with criteria
- [ ] **Arc DoD Ceremony** - `close-arc-ceremony` skill with criteria
- [ ] **Epoch DoD Ceremony** - `close-epoch-ceremony` skill with criteria
- [ ] **DoD Cascade Schema** - Work → Chapter → Arc → Epoch verification chain
- [ ] **CH-010 Chapter File** - Document the multi-level DoD ceremonies

**DoD Criteria per Level:**

| Level | DoD Criteria |
|-------|--------------|
| Work Item | Tests pass, runtime consumer, WHY captured (ADR-033) |
| Chapter | All work complete + exit criteria + implements_decisions verified |
| Arc | All chapters complete + no unassigned epoch decisions |
| Epoch | All arcs complete + all decisions implemented |

---

## History

### 2026-02-01 - Created (Session 279)
- Spawned from WORK-055
- Assigned to flow arc as CH-010 (Multi-Level DoD Ceremonies)
- Framed as CEREMONIES layer concern per Five-Layer Hierarchy
- Blocked by WORK-069 (needs decision traceability schema first)

---

## References

- @docs/work/active/WORK-055/WORK.md (source investigation)
- @docs/work/active/WORK-069/WORK.md (blocking dependency)
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md (parent arc)
- @docs/ADR/ADR-033-work-item-lifecycle.md (work item DoD)
