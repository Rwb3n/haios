---
template: work_item
id: INV-071
title: Work Item Triage Strategy for E2.3 Migration
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-25
spawned_by: null
chapter: null
arc: migration
closed: '2026-01-25'
priority: medium
effort: medium
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-25 00:09:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 81610
- 81606
- 81614
- 81612
- 82347
- 82348
- 82349
- 82350
- 82351
- 82352
- 82353
- 82354
extensions: {}
version: '2.0'
generated: 2026-01-25
last_updated: '2026-01-25T00:25:26'
---
# INV-071: Work Item Triage Strategy for E2.3 Migration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** 72 active work items exist in `docs/work/active/`, created during E2.0-E2.2 epochs. Current epoch is E2.3 (The Pipeline). These items were created under prior missions and may not align with E2.3's doc-to-product pipeline focus.

**Root cause:** Epoch transitions don't automatically reframe or archive prior work. Items accumulate without explicit triage.

**Evidence from memory:**
- 81610: "Epoch transitions need explicit migration periods with triage work items"
- 81606: "Work items created under E2 don't automatically fit E2.3 mission"
- 81614: "Create triage work item -> MANIFEST.md with rationale -> update statuses"

**Scope:** Design triage criteria and process for 72 active items. Determine which items are pipeline-relevant, which should archive, which need reframing.

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

- [x] Triage criteria document - ALREADY EXISTS: `.claude/haios/epochs/E2_3/arcs/migration/MANIFEST.md` (Session 208)
- [x] MIGRATION-MANIFEST.md - ALREADY EXISTS: 59 items categorized with rationale
- [x] Batch processing approach - ALREADY DONE: Session 208 processed all items
- [x] Queue update strategy - VERIFIED: 11/14 transfer items in queue, 3 legitimately closed since S208

---

## History

### 2026-01-25 - Created (Session 234)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md (parent arc)
- @.claude/haios/epochs/E2_3/EPOCH.md (E2.3 mission)
- @.claude/haios/epochs/E2/EPOCH.md (prior epoch for context)
