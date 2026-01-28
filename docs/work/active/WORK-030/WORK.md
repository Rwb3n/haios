---
template: work_item
id: WORK-030
title: Universal WORK-XXX ID Format Enforcement
type: implementation
status: complete
owner: Hephaestus
created: 2026-01-28
spawned_by: WORK-028
chapter: null
arc: null
closed: '2026-01-28'
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
  entered: 2026-01-28 22:39:54
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-28
last_updated: '2026-01-28T22:47:45'
---
# WORK-030: Universal WORK-XXX ID Format Enforcement

@docs/README.md
@docs/epistemic_state.md

---

## Context

Work item IDs are inconsistent: E2-XXX (epoch), INV-XXX (investigation), WORK-XXX (universal), and arbitrary strings all accepted. This causes:
- Confusion about which format to use
- Special-case logic for INV-* prefix in routing
- Spawning errors when IDs collide across formats

**Decision:** All new work uses WORK-XXX format. The `type` field determines behavior (investigation, implementation, etc.), not the ID prefix.

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

- [x] Remove INV-* prefix logic from routing.py
- [x] Remove INV-* prefix logic from status.py
- [x] Remove INV-* prefix logic from work_item.py
- [x] Update /new-work to document WORK-XXX policy
- [x] Update /new-investigation to use WORK-XXX + type: investigation
- [x] Update CLAUDE.md with ID policy
- [x] Update survey-cycle routing table
- [x] Update close-work-cycle routing table
- [x] Tests pass (routing logic, work_engine)

---

## History

### 2026-01-28 - Created (Session 247)
- Initial creation

---

## References

- [Related documents]
