---
id: CH-065
name: Bug Batch E2.8
arc: infrastructure
epoch: E2.8
status: In Progress
work_items:
- id: WORK-166
  title: Bug Batch E2.8
  status: Complete
  type: implementation
- id: WORK-175
  title: Fix plan_tree.py --ready Blocked_by Filter
  status: Active
  type: implementation
- id: WORK-181
  title: Investigate Test Failure Root Causes
  status: Complete
  type: investigation
- id: WORK-183
  title: Fix 13 Pre-Existing Test Failures
  status: Active
  type: implementation
exit_criteria:
- text: Checkpoint same-session sort bug fixed (session_loader.py:120) (S395)
  checked: true
- text: Queue state machine backlog->done transition added (S395)
  checked: true
- text: All confirmed E2.7 triage bugs resolved or explicitly deferred (S395)
  checked: true
- text: Zero test regressions (S395)
  checked: true
dependencies: []
---
# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: BugBatch-E28

## Chapter Definition

**Chapter ID:** CH-065
**Arc:** infrastructure
**Epoch:** E2.8
**Name:** Bug Batch E2.8
**Status:** In Progress

---

## Purpose

Batch fix confirmed bugs from E2.7 triage and S393 operator report. Clean foundation for the UX arcs. Follows the validated batch bug pattern (mem:84963): grouping 4+ small fixes in one session is efficient.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-166 | Bug Batch E2.8 | Complete | implementation |
| WORK-175 | Fix plan_tree.py --ready Blocked_by Filter | Active | implementation |
| WORK-181 | Investigate Test Failure Root Causes | Complete | investigation |
| WORK-183 | Fix 13 Pre-Existing Test Failures | Active | implementation |

---

## Exit Criteria

- [x] Checkpoint same-session sort bug fixed (session_loader.py:120) (S395)
- [x] Queue state machine backlog->done transition added (S395)
- [x] All confirmed E2.7 triage bugs resolved or explicitly deferred (S395)
- [x] Zero test regressions (S395)

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No dependencies — runs in parallel with UX arcs |

---

## References

- @.claude/haios/epochs/E2_8/arcs/infrastructure/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @docs/work/active/WORK-166/WORK.md (work item)
- Memory: 84963 (batch pattern), 85712, 85557, 85795, 85573, 85132 (E2.7 triage bugs)
