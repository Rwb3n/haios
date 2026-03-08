---
template: work_item
id: WORK-280
title: Git Stash Safety — session-log.jsonl Conflict Causes Permanent Work Loss
type: investigation
status: active
owner: Hephaestus
created: 2026-03-07
spawned_by: WORK-272
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/session-log.jsonl
acceptance_criteria:
- Investigate why git stash pop fails when session-log.jsonl is modified by MCP session_start
  tool
- Determine if session-log.jsonl should be gitignored (ephemeral session data) or
  if stash should be avoided entirely
- Document safe alternatives to git stash for verifying pre-existing test failures
  (git log, git show HEAD:path)
- Findings doc with recommendation
blocked_by: []
blocks: []
enables: []
queue_position: ready
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-03-07 20:49:52
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-03-07
last_updated: '2026-03-08T16:23:24.360117'
queue_history:
- position: ready
  entered: '2026-03-08T16:23:24.356865'
  exited: null
---
# WORK-280: Git Stash Safety — session-log.jsonl Conflict Causes Permanent Work Loss

---

## Context

During S478 WORK-272 implementation, `git stash` was used to verify a pre-existing test failure. `git stash pop` failed because `.claude/haios/session-log.jsonl` had been modified by the MCP `session_start` tool after the stash was created. The subsequent `git stash drop` permanently destroyed all uncommitted work (6 file edits). The agent had to re-apply all changes from memory/plan, wasting ~10 minutes of context.

Evidence: S478 WORK-272 retro WCBB-1, mem:89850, enrichment convergence_count=10.

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
