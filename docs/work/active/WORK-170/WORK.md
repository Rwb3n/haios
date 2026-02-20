---
template: work_item
id: WORK-170
title: Checkpoint Field Auto-Population
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-160
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-20'
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/post_tool_use.py
- .claude/haios/lib/session_end_actions.py
acceptance_criteria:
- Checkpoint scaffold auto-populates session_number, date, work_id, plan_ref
- Auto-population works when invoked from PostToolUse hook after /new-checkpoint
- Fields that cannot be auto-detected remain as placeholders (no errors)
- Tests verify population with mock haios-status-slim.json and session file
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: PLAN
node_history:
- node: backlog
  entered: 2026-02-19 00:17:34
  exited: '2026-02-20T20:54:50.984362'
artifacts: []
cycle_docs: {}
memory_refs:
- 86964
- 86965
- 86966
- 86967
extensions:
  epoch: E2.8
  parent: WORK-160
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-20T20:54:50.987384'
queue_history:
- position: ready
  entered: '2026-02-20T20:26:57.766279'
  exited: '2026-02-20T20:27:09.532596'
- position: working
  entered: '2026-02-20T20:27:09.532596'
  exited: '2026-02-20T20:54:50.984362'
- position: done
  entered: '2026-02-20T20:54:50.984362'
  exited: null
---
# WORK-170: Checkpoint Field Auto-Population

---

## Context

When running `/new-checkpoint`, the agent must manually look up the session number (from `.claude/session`), the current work_id (from haios-status-slim.json), the date, and the plan reference — then fill them into the checkpoint frontmatter. This is pure mechanical work that costs agent tokens with zero judgment required.

This work item automates the population of standard checkpoint fields. A new `lib/checkpoint_auto.py` module provides `populate_checkpoint_fields()` which reads from existing infrastructure (session file, haios-status-slim.json, work directory) and fills in standard fields. Called from PostToolUse when a checkpoint file is created.

**Pattern:** Same fail-permissive pattern as `session_end_actions.py`. Uses `_default_project_root()` for path derivation. Fields that cannot be resolved are left as template placeholders.

**Field resolution strategies:**
- `session_number`: Read last line of `.claude/session` (existing pattern in `session_end_actions.py`)
- `date`: `datetime.now().strftime("%Y-%m-%d")`
- `work_id`: Read `session_state.work_id` from `haios-status-slim.json`; if null, leave placeholder
- `plan_ref`: Glob `docs/work/active/{work_id}/plans/PLAN.md`; if exists, use relative path; if not found, leave placeholder
- `prior_session`: `session_number - 1` (simple derivation)

---

## Deliverables

- [ ] New file `lib/checkpoint_auto.py` with `populate_checkpoint_fields()` function
- [ ] PostToolUse integration: auto-populate on checkpoint file Write to `docs/checkpoints/`
- [ ] Handles: session, prior_session, date, work_id, plan_ref
- [ ] Template update: add `work_id` and `plan_ref` placeholders to `checkpoint.md`
- [ ] Graceful degradation for unresolvable fields (null work_id, missing plan, missing session file)
- [ ] Tests in `tests/test_checkpoint_auto.py` (including null work_id case)

---

## History

### 2026-02-19 - Created (Session 399)
- Spawned from WORK-160 decomposition
- Independent — no dependencies on other decomposed items

---

## References

- @docs/work/active/WORK-160/WORK.md (parent)
- @.claude/hooks/hooks/post_tool_use.py (target integration point)
- @.claude/haios/lib/session_end_actions.py (pattern template — read_session_number)
