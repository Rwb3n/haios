---
template: work_item
id: WORK-034
title: Upstream Status Propagation on Work Closure
type: implementation
status: complete
owner: Hephaestus
created: 2026-01-29
spawned_by: null
chapter: CH-045
arc: engine-functions
closed: '2026-02-16'
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
  entered: 2026-01-29 22:39:18
  exited: '2026-02-16T20:51:41.490677'
artifacts: []
cycle_docs: {}
memory_refs:
- 85686
- 85687
- 85688
- 85689
- 85690
- 85703
extensions:
  epoch: E2.7
version: '2.0'
generated: 2026-01-29
last_updated: '2026-02-16T20:51:41.493256'
queue_history:
- position: ready
  entered: '2026-02-16T20:11:40.887066'
  exited: '2026-02-16T20:11:47.112631'
- position: working
  entered: '2026-02-16T20:11:47.112631'
  exited: '2026-02-16T20:51:41.490677'
- position: done
  entered: '2026-02-16T20:51:41.490677'
  exited: null
queue_position: done
cycle_phase: done
---
# WORK-034: Upstream Status Propagation on Work Closure

@docs/README.md
@docs/epistemic_state.md

---

## Context

When a work item completes a chapter, there's no automatic propagation to update:
- Chapter status in ARC.md (Planned → Complete)
- Arc status if all chapters complete
- Epoch exit criteria if arc completes
- L4 requirement satisfaction tracking

Currently this is done manually (as we did this session for Pipeline CH-001/CH-002/CH-003). This is error-prone and causes drift between actual state and documented state.

The traceability chain is: `Work Item → Chapter → Arc → Epoch → L4 Requirement`

When work closes, the close-work-cycle should propagate status upstream.

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

- [ ] `StatusPropagator` module in `lib/status_propagator.py`
- [ ] Parse work item `chapter` and `arc` fields to find upstream docs
- [ ] Update Chapter status in ARC.md when work completes chapter
- [ ] Check if all chapters in arc are complete → log arc completion event
- [ ] Log StatusPropagation event to governance-events.jsonl (flag for upstream review)
- [ ] Integration with close-work-cycle ARCHIVE phase
- [ ] Tests: propagation scenarios (chapter complete, arc complete, partial)

---

## History

### 2026-01-29 - Created (Session 247)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_3/arcs/workuniversal/ARC.md
- @.claude/skills/close-work-cycle/SKILL.md
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
- REQ-TRACE-005 (Traceability chain)
