---
template: work_item
id: WORK-071
title: Pre-Decomposition Review Gate Design
type: design
status: active
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-055
chapter: flow/CH-011
arc: feedback
closed: null
priority: medium
effort: medium
traces_to:
- REQ-TRACE-005
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by:
- WORK-069
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 23:06:07
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83024
- 83025
- 83026
extensions:
  epoch: E2.5
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-03T20:52:10'
---
# WORK-071: Pre-Decomposition Review Gate Design

---

## Context

**Spawned from:** WORK-055 (Multi-Level Governance Investigation)

**Problem:** When an arc is decomposed into chapters, there's no verification that the decomposition is complete. Chapters get scaffolded and worked independently without verifying the set of chapters covers all epoch decisions.

**Layer Placement:** This is a **CEREMONIES** layer concern - the ceremony that verifies decomposition completeness before chapter work begins.

**Five-Layer Context:**
```
PRINCIPLES       - L0-L3
WAYS OF WORKING  - Universal flow, Chapter flow
CEREMONIES       - decompose-arc-ceremony ← THIS
ACTIVITIES       - Governed primitives
ASSETS           - ARC.md chapter table, chapter files
```

**Ceremony Pattern:**
```
DECOMPOSE (create chapter table) → CRITIQUE (verify coverage) → PROCEED (begin chapter work)
```

This is the entry ceremony for chapter-level work, analogous to how critique-gate is the entry ceremony for DO phase.

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

- [ ] **decompose-arc-ceremony Skill** - Skill that verifies decomposition completeness
- [ ] **Coverage Check** - Verify all epoch decisions for arc have chapter assignment
- [ ] **Scope Check** - Verify sum of chapter scopes covers arc theme
- [ ] **Arc-Level Critique** - Invoke critique on decomposition before chapter work
- [ ] **CH-011 Chapter File** - Document the pre-decomposition ceremony

**Ceremony Flow:**

```
1. DECOMPOSE: Create chapter table in ARC.md
2. ASSIGN: For each epoch decision targeting this arc, assign to chapter(s)
3. CRITIQUE: Run arc-level completeness check
   - All epoch decisions for this arc have chapter assignment?
   - Sum of chapter scopes covers arc theme?
   - No gaps in coverage?
4. PROCEED: Only when critique passes, begin chapter work
```

---

## History

### 2026-02-01 - Created (Session 279)
- Spawned from WORK-055
- Assigned to flow arc as CH-011 (Pre-Decomposition Ceremony)
- Framed as CEREMONIES layer concern per Five-Layer Hierarchy
- Blocked by WORK-069 (needs decision traceability schema first)

---

## References

- @docs/work/active/WORK-055/WORK.md (source investigation)
- @docs/work/active/WORK-069/WORK.md (blocking dependency)
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md (parent arc)
- @.claude/haios/epochs/E2_4/arcs/flow/CH-006-chapter-flow.md (chapter flow context)
