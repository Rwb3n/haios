---
template: work_item
id: WORK-156
title: "Implement Checkpoint Pending Staleness Detection"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-16
spawned_by: WORK-136
spawned_children: []
chapter: CH-051
arc: infrastructure
closed: null
priority: medium
effort: small
traces_to: [REQ-CEREMONY-001]
requirement_refs: []
source_files:
  - ".claude/haios/lib/session_loader.py"
  - ".claude/haios/lib/work_loader.py"
  - ".claude/haios/lib/coldstart_orchestrator.py"
acceptance_criteria:
  - "Stale WORK-ID pending items are annotated as [RESOLVED] at coldstart"
  - "Free-text pending items show age marker (pending since session N)"
  - "WorkLoader sort bug fixed (max by session number, not lexicographic)"
  - "All existing tests pass, new tests cover staleness detection"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-16T21:20:05
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-16
last_updated: 2026-02-16T21:20:05
---
# WORK-156: Implement Checkpoint Pending Staleness Detection

---

## Context

Investigation WORK-136 confirmed that checkpoint pending items become stale across sessions. 58% of pending items contain WORK-IDs that can be auto-resolved via WorkEngine status lookup. 42% are free-text items needing age markers.

**Three changes needed:**
1. SessionLoader: Add `validate_pending_items()` to annotate WORK-ID items as [RESOLVED] when their status is terminal
2. SessionLoader: Add age marker for free-text items showing originating session number
3. WorkLoader: Fix `_get_pending_from_checkpoint()` sort bug (lexicographic → session-number extraction, matching session_loader fix)

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

- [ ] `validate_pending_items()` in SessionLoader annotates stale WORK-ID items
- [ ] Free-text pending items surfaced with age marker (session number)
- [ ] WorkLoader `_get_pending_from_checkpoint()` sort bug fixed
- [ ] Tests for staleness detection (WORK-ID resolved, WORK-ID active, free-text, mixed)
- [ ] Tests for WorkLoader sort fix

---

## History

### 2026-02-16 - Created (Session 387)
- Initial creation

---

## References

- @docs/work/active/WORK-136/WORK.md (parent investigation)
- `.claude/haios/lib/session_loader.py` (primary change target)
- `.claude/haios/lib/work_loader.py` (sort bug fix)
- Memory: 84986 (stale pending waste), 84983 (pending staleness), 85621 (scope note)
