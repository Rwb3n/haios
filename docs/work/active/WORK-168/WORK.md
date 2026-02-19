---
template: work_item
id: WORK-168
title: Cycle Phase Auto-Advancement
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-160
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-19'
priority: high
effort: small
traces_to:
- REQ-CEREMONY-005
- REQ-OBSERVE-001
requirement_refs: []
source_files:
- .claude/hooks/hooks/post_tool_use.py
- .claude/haios/lib/session_end_actions.py
- .claude/haios/modules/cycle_runner.py
acceptance_criteria:
- PostToolUse hook detects lifecycle skill completion and updates session_state in
  haios-status-slim.json
- session_state.current_phase and session_state.active_cycle updated correctly
- Governance event logged for each phase transition via log_phase_transition
- 'Fail-permissive: errors in auto-advancement never break the hook chain'
- just set-cycle continues to work as a manual override
- Tests verify phase advancement for implementation-cycle and investigation-cycle
blocked_by: []
blocks:
- WORK-171
enables:
- WORK-171
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-19 00:17:34
  exited: '2026-02-19T19:50:15.198591'
artifacts: []
cycle_docs: {}
memory_refs:
- 85390
- 86726
- 86727
- 86748
- 86749
- 86750
- 86752
- 86753
- 86754
- 86755
- 86756
- 86788
extensions:
  epoch: E2.8
  parent: WORK-160
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-19T19:50:15.202608'
queue_history:
- position: ready
  entered: '2026-02-19T19:01:26.810146'
  exited: '2026-02-19T19:01:26.837309'
- position: working
  entered: '2026-02-19T19:01:26.837309'
  exited: '2026-02-19T19:50:15.198591'
- position: done
  entered: '2026-02-19T19:50:15.198591'
  exited: null
---
# WORK-168: Cycle Phase Auto-Advancement

---

## Context

Currently, cycle phase advancement requires the agent to execute `just set-cycle <cycle> <phase> <work_id>` explicitly — a manual step instructed by ceremony SKILL.md files. This costs agent tokens (reading the instruction + executing the Bash command) and is easily forgotten, leading to stale session_state in haios-status-slim.json.

This work item automates cycle phase advancement via the PostToolUse hook. When a lifecycle skill invocation completes, the hook detects the skill name, maps it to the next phase using existing CYCLE_PHASES from cycle_runner.py, and updates session_state in haios-status-slim.json automatically.

**Pattern:** Follows `session_end_actions.py` — new `lib/cycle_state.py` with fail-permissive functions. PostToolUse adds a "Part 8" handler that calls the lib function when `tool_name == "Skill"`.

**Existing infrastructure:**
- `just set-cycle` (justfile:308) — writes session_state to haios-status-slim.json
- `session_end_actions.clear_cycle_state()` — clears all 6 session_state fields
- `post_tool_use._log_cycle_transition()` — already detects phase changes in plan files
- `cycle_runner.CYCLE_PHASES` — defines phase ordering per cycle

---

## Deliverables

- [ ] New file `lib/cycle_state.py` with `advance_cycle_phase()` function
- [ ] PostToolUse hook Part 8: auto-advance on lifecycle skill completion
- [ ] Governance event logged via existing `log_phase_transition()`
- [ ] Tests in `tests/test_cycle_state.py` for phase advancement logic
- [ ] `just set-cycle` continues to work unchanged (manual override)

---

## History

### 2026-02-19 - Created (Session 399)
- Spawned from WORK-160 decomposition
- Independent of tier detection — blocks WORK-171 (Phase Migration)

---

## References

- @docs/work/active/WORK-160/WORK.md (parent)
- @.claude/hooks/hooks/post_tool_use.py (target for Part 8)
- @.claude/haios/lib/session_end_actions.py (pattern template)
- @.claude/haios/modules/cycle_runner.py (CYCLE_PHASES dict)
- Memory: 85390 (104% problem)
