---
template: work_item
id: WORK-227
title: Investigation CONCLUDE Spawn Completeness Enforcement
type: implementation
status: active
owner: Hephaestus
created: '2026-02-25'
spawned_by: WORK-221
spawned_children: []
chapter: CH-066
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-LIFECYCLE-004
requirement_refs: []
source_files:
- .claude/templates/investigation/CONCLUDE.md
- .claude/commands/close.md
- .claude/skills/investigation-cycle/SKILL.md
acceptance_criteria:
- "CONCLUDE template has Work Disposition table requiring each finding-recommended item to have disposition (spawned/deferred with rationale)"
- "Close command Step 1.5b validates spawned work completeness against findings, not just non-empty check"
- "Investigation-cycle CONCLUDE exit criteria include completeness qualifier for spawned work"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: '2026-02-25T16:26:23.365897'
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-25
last_updated: '2026-02-25T16:26:23.365897'
queue_history:
- position: backlog
  entered: '2026-02-25T16:26:23.365897'
  exited: null
---
# WORK-227: Investigation CONCLUDE Spawn Completeness Enforcement

---

## Context

WORK-221 investigation found that investigation-cycle CONCLUDE phase uses binary presence checks for spawned work ("did spawning happen?") rather than completeness checks ("did all recommended work get spawned or explicitly deferred?"). Three enforcement points lack cross-reference validation:

1. CONCLUDE template output contract: `spawned_work: required: false` — correct for zero-spawn, missing partial-spawn handling
2. Close command Step 1.5b: checks spawned section is non-empty, no findings cross-reference
3. Investigation-cycle CONCLUDE exit criteria: "Spawned work items created" without completeness qualifier

Concrete example: WORK-218 identified 5+ phases of work, CONCLUDE spawned only 2 (WORK-219, WORK-220). Phases 2-5 were eventually created via implementation chaining (WORK-220 spawned them), but this recovery was implicit, not guaranteed.

---

## Deliverables

- [ ] CONCLUDE.md template updated with "Work Disposition" table
- [ ] close.md Step 1.5b updated with cross-reference validation
- [ ] investigation-cycle/SKILL.md CONCLUDE exit criteria updated with completeness qualifier

---

## References

- @docs/work/active/WORK-221/WORK.md (parent investigation)
- @.claude/templates/investigation/CONCLUDE.md (template to update)
- @.claude/commands/close.md (close command to update)
- @.claude/skills/investigation-cycle/SKILL.md (skill to update)
