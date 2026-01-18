---
template: work_item
id: WORK-002
title: E2.3 Triage - Strategic triage of E2 arcs and work items
status: active
owner: Hephaestus
created: 2026-01-18
closed: null
milestone: null
priority: high
effort: medium
category: strategic
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-18 21:25:58
  exited: null
cycle_docs: {}
memory_refs: []
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-18
last_updated: '2026-01-18T21:28:00'
---
# WORK-WORK-002: E2.3 Triage - Strategic triage of E2 arcs and work items

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session 206 reframed HAIOS as a doc-to-product pipeline, not PM infrastructure. This created Epoch 2.3 with new arcs (Provenance, Pipeline, WorkUniversal, Migration, Observations). However, E2.2 has 6 arcs (Chariot, Breath, Form, Ground, Tongue, WorkInfra) and 57 active work items that need disposition before E2.3 work can proceed cleanly.

**Root cause:** Epoch transition without triage creates ambiguity about what transfers forward vs. archives. Work items reference E2-specific milestones and arcs that may no longer exist in E2.3 context.

**Scope:**
- 6 E2 arcs to triage (chariot, breath, form, ground, tongue, workinfra)
- 57 active work items in `docs/work/active/`
- Architecture docs (S1-S26) to classify as pipeline-relevant vs. HAIOS-specific

**Triage Categories (from Migration arc):**
| Category | Action | Example |
|----------|--------|---------|
| Pipeline-relevant | Transfer to E2.3 | S26, S20, Ground arc |
| Reusable-infra | Keep, reference | Memory system, hooks |
| HAIOS-specific | Archive with summary | E2-235, INV-054 |
| Obsolete | Archive, no action | Completed work |

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

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
-->

- [ ] Arc triage manifest: Disposition for each E2 arc (chariot, breath, form, ground, tongue, workinfra)
- [ ] Work item triage: Each of 57 active items marked as transfer/archive/dismiss
- [ ] Architecture doc classification: S1-S26 categorized as pipeline-relevant or HAIOS-specific
- [ ] Queue cleanup: `just queue default` reflects only transferred items
- [ ] Migration manifest: Document all decisions with rationale in `epochs/E2_3/arcs/migration/MANIFEST.md`

---

## History

### 2026-01-18 - Created (Session 207)
- Initial creation
- Work-creation-cycle VERIFY/POPULATE/READY complete
- Context and deliverables populated

---

## References

- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md (Migration arc definition)
- @.claude/haios/epochs/E2/EPOCH.md (Source epoch)
- @docs/checkpoints/2026-01-18-05-SESSION-206-e23-epoch-creation-and-strategic-review.md (Strategic review)
