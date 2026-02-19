---
template: work_item
id: WORK-172
title: "Block EnterPlanMode via PreToolUse Hook"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: high
effort: trivial
traces_to:
  - REQ-CEREMONY-001
requirement_refs: []
source_files:
  - .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
  - "PreToolUse hook denies tool_name=='EnterPlanMode' with redirect message to /new-plan"
  - "Governance event logged (GateViolation) when EnterPlanMode is blocked"
  - "Test verifies EnterPlanMode is blocked"
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
  - 86604
  - 86656
  - 86682
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T20:14:06
---
# WORK-172: Block EnterPlanMode via PreToolUse Hook

---

## Context

EnterPlanMode writes to ungoverned path `C:\Users\ruben\.claude\plans\` with no frontmatter, no backlog_id, no memory_refs, no critique gate, no plan-authoring-cycle chain. HAIOS uses `/new-plan` -> plan-authoring-cycle -> `docs/work/active/{id}/plans/PLAN.md`. 15+ convergent retro entries (S399, S403) identify this as the strongest signal in E2.8.

Currently blocked only by MEMORY.md operator directive — no hook enforcement exists. S399 saw EnterPlanMode called and approved without any hook intervention.

**Fix:** Add `tool_name == "EnterPlanMode"` check to PreToolUse hook, returning deny with redirect message.

---

## Deliverables

- [ ] PreToolUse hook check for EnterPlanMode added to pre_tool_use.py
- [ ] Deny response with message: "HAIOS uses governed plans. Use /new-plan {backlog_id} instead."
- [ ] GateViolation governance event logged
- [ ] Test in tests/ verifying the block

---

## History

### 2026-02-19 - Created (Session 403)
- From E2.8 retro triage: 15+ convergent entries (mem:86604, 86656, 86682)
- Strongest signal in E2.8 retro extractions

---

## References

- @.claude/hooks/hooks/pre_tool_use.py (target file)
- Memory: 86604, 86656, 86682 (EnterPlanMode block entries)
