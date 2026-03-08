---
template: work_item
id: WORK-281
title: 'Agent Pattern: Use git log/show Instead of git stash for Pre-Existing Failure
  Verification'
type: implementation
status: complete
owner: Hephaestus
created: 2026-03-07
spawned_by: WORK-272
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-03-08'
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- CLAUDE.md
acceptance_criteria:
- 'Document in CLAUDE.md or MEMORY.md: never use git stash to verify pre-existing
  failures'
- 'Document alternative: git log to check when test last passed, or git show HEAD:path
  to compare'
- 'Optionally: add PreToolUse hook warning when Bash command contains ''git stash'''
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-03-07 20:49:53
  exited: '2026-03-08T13:31:52.973529'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-03-07
last_updated: '2026-03-08T13:31:52.978013'
queue_history:
- position: done
  entered: '2026-03-08T13:31:52.973529'
  exited: null
---
# WORK-281: Agent Pattern: Use git log/show Instead of git stash for Pre-Existing Failure Verification

---

## Context

S478 WORK-272 retro identified that using `git stash` to verify pre-existing test failures is dangerous — stash pop can fail on files modified by MCP tools (session-log.jsonl), and `git stash drop` permanently destroys work. Safe alternatives: `git log` to check when test last passed, or `git show HEAD:path` to read committed version without touching working tree.

Evidence: S478 WORK-272 retro WCBB-2, mem:89851, enrichment convergence_count=10.

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
