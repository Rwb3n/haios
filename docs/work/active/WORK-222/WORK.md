---
template: work_item
id: WORK-222
title: StatusPropagator Exit Criteria Validation
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-25
spawned_by: WORK-220
spawned_children:
- WORK-239
- WORK-240
chapter: CH-066
arc: call
closed: '2026-03-06'
priority: medium
effort: small
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/lib/status_propagator.py
acceptance_criteria:
- 'Root cause documented: StatusPropagator marks chapter complete based on work item
  count, not exit criteria'
- 'Design proposal: how to validate exit criteria checkboxes before chapter completion'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-25 12:10:11
  exited: '2026-03-06T22:12:30.301447'
artifacts: []
cycle_docs: {}
memory_refs:
- 89199
- 89200
- 89201
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-03-06T22:12:30.303456'
queue_history:
- position: ready
  entered: '2026-03-06T22:06:34.873161'
  exited: '2026-03-06T22:06:38.170218'
- position: working
  entered: '2026-03-06T22:06:38.170218'
  exited: '2026-03-06T22:12:30.301447'
- position: done
  entered: '2026-03-06T22:12:30.301447'
  exited: null
---
# WORK-222: StatusPropagator Exit Criteria Validation

---

## Context

When WORK-220 closed, StatusPropagator marked CH-066 as chapter_completed because all 3 work items were done. But CH-066 has 3 unchecked exit criteria (scaffold tools, recipe retirement, Tier 3 only). The propagator uses a count-based predicate (all work items status=complete) without evaluating the chapter's markdown exit criteria checkboxes. This allows premature chapter closure when work items are complete but chapter goals are not met.

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

- [ ] Root cause analysis of StatusPropagator count-based vs criteria-based completion
- [ ] Design proposal for exit criteria validation (checkbox parsing or structured frontmatter)

---

## History

### 2026-02-25 - Created (Session 451)
- Initial creation

---

## References

- @.claude/haios/lib/status_propagator.py (propagation logic)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md (premature closure example)
- Memory: 88752-88771 (WORK-220 retro findings identifying this gap)
