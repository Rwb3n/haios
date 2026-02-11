---
template: work_item
id: WORK-123
title: Fix close-chapter-ceremony grep pattern mismatch
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-122
chapter: CH-015
arc: ceremonies
closed: '2026-02-11'
priority: high
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: done
node_history:
- node: backlog
  entered: 2026-02-11 21:10:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84910
- 84911
- 84912
- 84913
- 84914
- 84915
- 84916
- 84917
- 84918
extensions: {}
version: '2.0'
generated: 2026-02-11
last_updated: '2026-02-11T21:19:39.887849'
---
# WORK-123: Fix close-chapter-ceremony grep pattern mismatch

---

## Context

close-chapter-ceremony SKILL.md line 85 uses grep pattern `chapter: {arc}/{chapter_id}` to discover work items assigned to a chapter. Real WORK.md frontmatter uses `chapter: CH-015` (no arc prefix). The ceremony will fail to find any work items when invoked, causing false "no work items found" results during chapter closure validation. Discovered in S345 WORK-122 observations.

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

- [x] Fix grep pattern in close-chapter-ceremony SKILL.md: `chapter: {chapter_id}` (remove arc prefix)
- [x] Verify close-arc-ceremony SKILL.md for similar pattern issues
- [x] Test: verify chapter work item discovery matches real data format

---

## History

### 2026-02-11 - Completed (Session 346)
- Fixed 2 instances in close-chapter-ceremony SKILL.md (lines 75, 84): `{arc}/{chapter_id}` → `{chapter_id}`
- Verified close-arc-ceremony SKILL.md is clean (uses Glob on chapter files, not grep on chapter field)
- Tested: `grep "chapter: CH-015"` correctly finds WORK-122 and WORK-123

### 2026-02-11 - Created (Session 345)
- Spawned from WORK-122 observations: grep pattern mismatch discovered during DoD validation work

---

## References

- @.claude/skills/close-chapter-ceremony/SKILL.md (line 85: wrong pattern)
- @docs/work/active/WORK-122/observations.md (source observation)
