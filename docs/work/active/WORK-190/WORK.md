---
template: work_item
id: WORK-190
title: backlog_id_uniqueness Gate False Positive on WORK-1XX IDs
type: bug
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-189
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-GOVERN-001
requirement_refs: []
source_files:
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- backlog_id_uniqueness gate does not fire false positives for WORK-1XX IDs against
  legacy E2-1XX plan files
- Gate regex correctly distinguishes WORK-XXX from E2-XXX ID formats
- Existing tests still pass
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 15:20:16
  exited: '2026-02-22T16:05:12.040194'
artifacts: []
cycle_docs: {}
memory_refs:
- 87542
- 87543
- 87544
- 87545
- 87546
- 87547
- 87548
- 87549
- 87550
- 87551
- 87552
- 87578
- 87579
extensions: {}
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T16:05:12.043480'
queue_history:
- position: ready
  entered: '2026-02-22T15:46:34.768791'
  exited: '2026-02-22T15:46:52.475167'
- position: working
  entered: '2026-02-22T15:46:52.475167'
  exited: '2026-02-22T16:05:12.040194'
- position: done
  entered: '2026-02-22T16:05:12.040194'
  exited: null
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

- [x] Gate regex fixed to distinguish WORK-XXX from E2-XXX ID formats
- [x] No false positives on WORK-1XX IDs
- [x] Existing tests pass

---

## History

### 2026-02-22 - Completed (Session 424)
- Root cause: _check_backlog_id_uniqueness extracted backlog_id from entire file content, not just YAML frontmatter
- Fix: Added _extract_frontmatter() helper, gate now searches only frontmatter between --- delimiters
- 3 new tests, 7 total pass. Full suite: 1609 passed, 0 regressions.
- Critique caught: traces_to misalignment (corrected REQ-OBSERVE-005 -> REQ-GOVERN-001), chapter manifest gap (added to CH-059)

### 2026-02-22 - Created (Session 423)
- Extracted from WORK-189 retro-cycle (BUG-1)
- Known issue since S422 (mem:87457)

---

## References

- @docs/work/active/WORK-189/WORK.md (source retro extraction)
- Memory: 87457 (S422 initial report), 87508-87511 (S423 retro-extract)
