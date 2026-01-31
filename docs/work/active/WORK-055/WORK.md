---
template: work_item
id: WORK-055
title: Multi-Level Governance - Decomposition Leakage Pattern
type: investigation
status: active
owner: null
created: 2026-01-31
spawned_by: obs-268-1
chapter: null
arc: null
closed: null
priority: high
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-31 18:07:09
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-31
last_updated: '2026-01-31T18:07:55'
---
# WORK-055: Multi-Level Governance - Decomposition Leakage Pattern

---

## Context

Spawned from observation `obs-268-1` during WORK-040 closure review.

**Problem:** We have governance for leaf nodes (work items) but not branch nodes (chapters, arcs, epochs). Decomposition happens without verification that the decomposition is complete.

**Symptoms:**
1. Epoch decisions don't trace to chapters - decisions can fall through cracks
2. No batch critique at arc level - only per-plan critique exists
3. DoD only at work item level - no Chapter/Arc/Epoch DoD
4. No pre-scaffold review - chapters worked independently without completeness check

**Example:** E2.4 Decision 4 (Critique as Hard Gate) wasn't explicitly assigned to CH-002 or CH-003. It could be missed.

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

- [ ] **Gap Analysis** - Document where multi-level governance is missing
- [ ] **Traceability Design** - How epoch decisions trace to chapters
- [ ] **Batch Critique Pattern** - Arc-level critique before chapter work
- [ ] **Multi-Level DoD** - DoD cascade: Work → Chapter → Arc → Epoch
- [ ] **Pre-Decomposition Gate** - Review decomposition completeness before work begins
- [ ] **Findings Document** - Investigation conclusions with recommendations

---

## History

### 2026-01-31 - Created (Session 268)
- Spawned from obs-268-1
- Operator identified decomposition leakage risk during WORK-040 review

---

## References

- @.claude/haios/epochs/E2_4/observations/obs-268-1.md (source observation)
- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 4 - example of untraced decision)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (chapter decomposition)
