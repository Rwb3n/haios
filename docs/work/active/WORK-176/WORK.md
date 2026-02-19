---
template: work_item
id: WORK-176
title: "Plan-Authoring-Cycle Subagent Delegation"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-CEREMONY-002
  - REQ-CEREMONY-005
requirement_refs: []
source_files:
  - .claude/skills/plan-authoring-cycle/SKILL.md
  - .claude/skills/implementation-cycle/SKILL.md
acceptance_criteria:
  - "Plan authoring delegated to sonnet subagent instead of inline main context"
  - "Main context token savings measurable (~40% reduction for plan phase)"
  - "Plan quality maintained (same sections, same validation gates)"
  - "implementation-cycle PLAN phase updated to invoke subagent"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-19T20:14:06
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 86707
  - 86708
  - 86709
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T20:14:06
---
# WORK-176: Plan-Authoring-Cycle Subagent Delegation

---

## Context

Plan authoring currently runs inline in the main context, consuming ~40% of tokens for structural work (mem:86709). Pattern observed in S398 (WORK-101) and S400 (WORK-167). This is mechanical — the plan-authoring-cycle reads source files, fills in template sections, and produces a structured document. It requires context (specs, source files) but not main-context judgment.

Delegating to a sonnet subagent preserves plan quality while freeing main context for the DO phase. Matches the E2.8 principle: agents spend tokens on work, not bookkeeping.

**Fix:** Convert plan-authoring-cycle invocation from inline skill to Task(subagent_type=...) call. Subagent reads specs, populates plan, returns completed plan for critique.

---

## Deliverables

- [ ] Plan-authoring subagent configuration or Task invocation pattern
- [ ] implementation-cycle PLAN phase updated to delegate
- [ ] Plan quality validation (same sections, same gates)
- [ ] Token savings measurement (before/after comparison)

---

## History

### 2026-02-19 - Created (Session 403)
- From E2.8 retro triage: observed in S398, S400 (mem:86707-86709)

---

## References

- @.claude/skills/plan-authoring-cycle/SKILL.md (target)
- @.claude/skills/implementation-cycle/SKILL.md (consumer)
- Memory: 86707, 86708, 86709
