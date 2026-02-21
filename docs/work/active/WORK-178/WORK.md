---
template: work_item
id: WORK-178
title: CHECK Phase Subagent Delegation
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-177
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-21'
priority: low
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
- .claude/skills/design-review-validation/SKILL.md
acceptance_criteria:
- Design-review-validation runs as sonnet subagent during DO phase exit
- Deliverables verification runs as haiku subagent during CHECK phase
- Design-review-validation and deliverables verification in SKILL.md are wrapped in
  Task() subagent calls, not inline Skill() or direct Read sequences
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-19 23:15:57
  exited: '2026-02-21T15:50:05.643265'
artifacts: []
cycle_docs: {}
memory_refs:
- 87218
- 87219
- 87220
- 87221
- 87222
- 87223
- 87224
- 87225
- 87226
extensions: {}
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-21T15:50:05.646990'
queue_history:
- position: ready
  entered: '2026-02-21T14:57:44.069543'
  exited: '2026-02-21T14:57:54.934721'
- position: working
  entered: '2026-02-21T14:57:54.934721'
  exited: '2026-02-21T15:50:05.643265'
- position: done
  entered: '2026-02-21T15:50:05.643265'
  exited: null
---
# WORK-178: CHECK Phase Subagent Delegation

---

## Context

During WORK-177 (S407), design-review-validation and deliverables verification ran inline in the main agent context, consuming tokens for structural checks that don't require main-agent judgment. This fits E2.8 Arc 1 (call) theme: "agents spend tokens on work, not bookkeeping."

Proposal: Delegate design-review-validation to sonnet subagent (requires judgment — comparing plan design to implementation) and deliverables verification to haiku subagent (structural check — read WORK.md deliverables, confirm each exists).

Scoped pytest (fast, <1s) stays inline. Full-suite regression already delegates to test-runner (haiku).

---

## Deliverables

- [ ] Design-review-validation delegated to sonnet subagent in implementation-cycle SKILL.md
- [ ] Deliverables verification delegated to haiku subagent in implementation-cycle SKILL.md
- [ ] implementation-cycle SKILL.md updated with subagent invocation patterns
- [ ] Existing CHECK phase behavior preserved (no regression)

---

## History

### 2026-02-19 - Created (Session 407)
- Spawned from WORK-177 retro: CHECK phase activities should be subagents

---

## References

- @.claude/skills/implementation-cycle/SKILL.md (CHECK phase)
- @.claude/skills/design-review-validation/SKILL.md (bridge skill)
- @docs/work/active/WORK-177/WORK.md (parent)
