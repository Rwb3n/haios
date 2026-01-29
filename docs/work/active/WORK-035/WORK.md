---
template: work_item
id: WORK-035
title: E2 Legacy Queue Triage
type: cleanup
status: active
owner: Hephaestus
created: 2026-01-29
spawned_by: null
chapter: CH-003
arc: migration
closed: null
priority: medium
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
  entered: 2026-01-29 22:39:20
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-29
last_updated: '2026-01-29T22:41:14'
---
# WORK-035: E2 Legacy Queue Triage

@docs/README.md
@docs/epistemic_state.md

---

## Context

The work queue contains items from E2.0-E2.2 that may not align with E2.3 objectives:

| Item | Origin | E2.3 Alignment |
|------|--------|----------------|
| INV-017 Observability Gap | E2 | Infrastructure, not pipeline |
| INV-068 Cycle Delegation | E2 | Architecture, not pipeline |
| INV-069 PostToolUse Timestamp | E2 | Hooks, not pipeline |
| E2-249 Agent UX Test | E2 | DoD testing, not pipeline |

These items clutter the queue and dilute focus on E2.3 exit criteria. Need to decide: reframe for E2.3, archive, or explicitly defer.

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

- [ ] Review each E2-era item in queue (INV-017, INV-068, INV-069, E2-249, etc.)
- [ ] For each item, decide: Reframe (align to E2.3 arc), Archive (complete or obsolete), Defer (explicit backlog)
- [ ] Archive items that are complete or superseded
- [ ] Reframe items that support E2.3 exit criteria
- [ ] Update queue to reflect E2.3-aligned priorities
- [ ] Document triage decisions with rationale

---

## History

### 2026-01-29 - Created (Session 247)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md
- @.claude/haios/epochs/E2_3/EPOCH.md (exit criteria)
- @.claude/haios/epochs/E2/EPOCH.md (prior epoch)
