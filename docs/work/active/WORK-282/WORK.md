---
template: work_item
id: WORK-282
title: "Auto-Sync ARC.md work_items on Work Item Creation"
type: implementation
status: active
owner: Hephaestus
created: 2026-03-07
spawned_by: WORK-272
spawned_children: []
chapter: CH-067
arc: infrastructure
closed: null
priority: low
effort: medium
traces_to:
- REQ-TRACE-003
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- .claude/haios/lib/arc_frontmatter.py
acceptance_criteria:
- "scaffold_work automatically adds work_id to ARC.md frontmatter work_items list when chapter/arc fields are set"
- "Uses arc_frontmatter.py update_chapter_in_frontmatter or new function to append to work_items list"
- "Prevents drift: CH-059 had 60 items but ARC.md listed only 2 (S478 WORK-272 WSY-1)"
- "Blocked by WORK-277 findings — may be superseded if frontmatter-based hierarchy replaces ARC.md lists"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-03-07T20:49:53
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-03-07
last_updated: 2026-03-07T20:49:53
---
# WORK-282: Auto-Sync ARC.md work_items on Work Item Creation

---

## Context

ARC.md chapter work_items lists are not automatically updated when new work items are created with a chapter assignment. S478 WORK-272 discovered CH-059 had 60 actual work items but ARC.md listed only 2, CH-061 listed 3 but had 6, and CH-067 listed 2 but had 13. This causes drift detectors and hierarchy consumers to operate on incomplete data.

Note: WORK-277 investigation may supersede this — if hierarchy is derived from WORK.md frontmatter (chapter field) rather than ARC.md lists, auto-sync becomes unnecessary.

Evidence: S478 WORK-272 retro WSY-1, WDN-1, WMI-1. Enrichment convergence_count=10, prior_work_ids=[WORK-277].

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

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## History

### 2026-03-07 - Created (Session 477)
- Initial creation

---

## References

- [Related documents]
