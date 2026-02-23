---
template: work_item
id: WORK-205
title: Survey-Cycle Auto-Prioritize for Backlog Items
type: implementation
status: active
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-179
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/skills/survey-cycle/SKILL.md
acceptance_criteria:
- When operator selects a backlog-position item in survey-cycle, both prioritize (backlog->ready)
  and commit (ready->working) transitions execute automatically
- Operator still sees queue transition confirmation in output
- No regression for items already at ready position (single commit transition)
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-23 13:38:48
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 87793
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T13:40:34.667389'
queue_history:
- position: parked
  entered: '2026-02-23T13:40:34.663971'
  exited: null
---
# WORK-205: Survey-Cycle Auto-Prioritize for Backlog Items

---

## Context

During WORK-179 investigation (S431), queue commit for a backlog-position item required 2 manual justfile invocations: `just queue-prioritize` (backlog→ready) then `just queue-commit` (ready→working). The queue state machine enforces backlog→ready→working as separate transitions (CH-009), but when the operator has already selected a work item via survey-cycle, the intermediate "ready" state adds no decision value — it's mechanical friction.

Survey-cycle should detect when the selected item is at backlog position and auto-chain both transitions, reducing 2 tool calls to 0 manual intervention.

Evidence: WORK-179 retro WCBB-1, retro-extract FEATURE-2 (mem:87793).

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

- [ ] Survey-cycle skill updated with auto-prioritize logic for backlog items
- [ ] Queue transition output still visible to operator
- [ ] No regression for ready-position items (single commit only)

---

## History

### 2026-02-23 - Created (Session 431)
- Spawned from WORK-179 retro-cycle EXTRACT FEATURE-2
- Observed friction: 2 manual justfile calls for backlog→working transition

---

## References

- @.claude/skills/survey-cycle/SKILL.md (target for change)
- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition)
- @docs/work/active/WORK-179/WORK.md (parent investigation)
- Memory: 87793 (retro-extract FEATURE-2)
