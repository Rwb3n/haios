---
template: work_item
id: WORK-186
title: Parked Item Discoverability in Coldstart and Survey
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: null
spawned_children: []
chapter: null
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-CONFIG-001
- L3.3
requirement_refs: []
source_files:
- .claude/haios/lib/coldstart_orchestrator.py
- .claude/skills/survey-cycle/SKILL.md
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- Coldstart WORK phase output includes parked item count and summary
- Survey-cycle OPTIONS phase optionally surfaces parked items for unpark consideration
- Parked items remain excluded from queue/ready lists (existing REQ-QUEUE-005 behavior
  preserved)
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 09:19:03
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 87339
- 87340
- 87341
- 87342
extensions: {}
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T09:20:00.409303'
queue_history:
- position: parked
  entered: '2026-02-22T09:20:00.406297'
  exited: null
---
# WORK-186: Parked Item Discoverability in Coldstart and Survey

---

## Context

Parked work items are invisible during normal session flow. WorkEngine.get_parked() exists and correctly returns parked items (e.g., WORK-182, WORK-184), but neither coldstart_orchestrator.py nor survey-cycle/SKILL.md queries or displays them.

When items are parked via queue-unpark, they effectively disappear until someone explicitly asks. This means scope decisions lack periodic review triggers — parked items may become stale or forgotten across epoch transitions.

**Root cause:** coldstart WORK phase only calls get_ready() and get_queue(). Survey-cycle only presents ready/queue items. Neither mentions parked.

**Fix:** Add a "Parked (N)" summary line to coldstart WORK phase output. Optionally surface in survey-cycle so the operator can consider unparking during work selection.

Discovered during S419 external audit review — auditor findings triggered investigation into discoverability gaps.

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

- [ ] coldstart_orchestrator.py WORK phase includes parked item count and titles
- [ ] survey-cycle SKILL.md OPTIONS phase surfaces parked items as optional unpark candidates
- [ ] Tests verify parked items appear in coldstart output

---

## History

### 2026-02-22 - Created (Session 419)
- Initial creation

---

## References

- .claude/haios/lib/coldstart_orchestrator.py (WORK phase loader)
- .claude/skills/survey-cycle/SKILL.md (work selection)
- .claude/skills/queue-unpark/SKILL.md (park/unpark ceremony)
- .claude/haios/modules/work_engine.py:765 (get_parked method)
