---
template: work_item
id: WORK-178
title: "CHECK Phase Subagent Delegation"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-177
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: low
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
- .claude/skills/design-review-validation/SKILL.md
acceptance_criteria:
- "Design-review-validation runs as sonnet subagent during DO phase exit"
- "Deliverables verification runs as haiku subagent during CHECK phase"
- "Main context token savings measurable (fewer inline Read calls during CHECK)"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-19T23:15:57
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T23:15:57
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
