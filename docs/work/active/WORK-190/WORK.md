---
template: work_item
id: WORK-190
title: "backlog_id_uniqueness Gate False Positive on WORK-1XX IDs"
type: bug
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-189
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-005
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- "backlog_id_uniqueness gate does not fire false positives for WORK-1XX IDs against legacy E2-1XX plan files"
- "Gate regex correctly distinguishes WORK-XXX from E2-XXX ID formats"
- "Existing tests still pass"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T15:20:16
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T15:20:16
---
# WORK-190: backlog_id_uniqueness Gate False Positive on WORK-1XX IDs

---

## Context

The `backlog_id_uniqueness` gate in PreToolUse fires false positives when creating WORK-1XX items. The gate regex partially matches against legacy E2-1XX plan files (e.g., WORK-189 triggers "BLOCKED: Duplicate backlog_id. E2-141 already exists"). This erodes trust in governance gates and requires manual override.

Evidence: governance-events.jsonl — GateViolation at 2026-02-22T15:07:57. Also reported in S422 (mem:87457).

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

- [ ] Gate regex fixed to distinguish WORK-XXX from E2-XXX ID formats
- [ ] No false positives on WORK-1XX IDs
- [ ] Existing tests pass

---

## History

### 2026-02-22 - Created (Session 423)
- Extracted from WORK-189 retro-cycle (BUG-1)
- Known issue since S422 (mem:87457)

---

## References

- @docs/work/active/WORK-189/WORK.md (source retro extraction)
- Memory: 87457 (S422 initial report), 87508-87511 (S423 retro-extract)
