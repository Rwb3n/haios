---
template: work_item
id: E2-165
title: Checkpoint Skill with Git Commit
status: complete
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-25
milestone: M7d-Plumbing
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-24 10:27:31
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-24
last_updated: '2025-12-25T21:27:39'
---
# WORK-E2-165: Checkpoint Skill with Git Commit

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** `/new-checkpoint` is a command (static text expansion). Cannot include procedural steps like git commit.

**Solution:** Convert to skill with workflow: scaffold → guide content → `just commit-session {N}`.

---

## Current State

Command only. No git integration. Manual commits required.

---

## Deliverables

- [ ] Create `.claude/skills/checkpoint/` skill directory
- [ ] Skill phases: SCAFFOLD → FILL → CAPTURE → COMMIT
- [ ] Final step calls `just commit-session {N}` (E2-167 complete)
- [ ] Remove @ references from checkpoint template (merged from E2-132, per INV-E2-116)
- [ ] Add "Spawned Work Items" section to template (merged from E2-035)
- [ ] Prompt for discovered issues during checkpoint creation (merged from E2-035)

---

## History

### 2025-12-24 - Created (Session 105)
- Initial creation

### 2025-12-25 - Updated (Session 120, INV-036)
- E2-167 blocker resolved (git recipes complete)
- Merged E2-132 scope (remove @ references from template)
- Merged E2-035 scope (spawned items prompt)

---

## References

- [Related documents]
