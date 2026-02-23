---
template: work_item
id: WORK-208
title: Design Lifecycle Cycle Skill
type: feature
status: open
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-102
spawned_children: []
chapter: CH-064
arc: discover
closed: null
priority: low
effort: medium
traces_to:
- REQ-FLOW-003
requirement_refs: []
source_files:
- .claude/skills/ (new design-cycle skill)
- .claude/haios/modules/cycle_runner.py
acceptance_criteria:
- design-cycle skill exists with EXPLORE->SPECIFY->CRITIQUE->COMPLETE phases
- Governed phase transitions with governance events for design lifecycle
- 'Proportional scaling: effort=small uses inline (current), effort=medium+ uses governed
  skill'
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-23 18:04:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T18:06:03.412523'
queue_history:
- position: parked
  entered: '2026-02-23T18:06:03.410534'
  exited: null
---
# WORK-208: Design Lifecycle Cycle Skill

---

## Context

Retro extract from WORK-102 (S435). WORK-102 executed the design lifecycle (EXPLORE->SPECIFY->CRITIQUE->COMPLETE) inline without a dedicated cycle skill. This worked for effort=small but has no governed phase transitions, no governance events for phase entry/exit, and no automated scaling. REQ-FLOW-003 defines the design lifecycle but no tooling exists. Only needed when medium+ effort design work appears — small items continue inline.

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

- [ ] design-cycle SKILL.md with 4-phase ceremony contract
- [ ] CycleRunner support for design lifecycle
- [ ] Proportional scaling: inline for small, governed for medium+

---

## History

### 2026-02-23 - Created (Session 435)
- Initial creation

---

## References

- @docs/work/active/WORK-102/WORK.md (parent retro extract)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FLOW-003)
- Memory: 87988 (retro-extract FEATURE-1)
