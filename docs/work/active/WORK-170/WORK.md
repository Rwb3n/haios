---
template: work_item
id: WORK-170
title: "Checkpoint Field Auto-Population"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-160
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
  - REQ-CEREMONY-002
requirement_refs: []
source_files:
  - .claude/hooks/hooks/post_tool_use.py
  - .claude/haios/lib/session_end_actions.py
acceptance_criteria:
  - "Checkpoint scaffold auto-populates session_number, date, work_id, plan_ref"
  - "Auto-population works when invoked from PostToolUse hook after /new-checkpoint"
  - "Fields that cannot be auto-detected remain as placeholders (no errors)"
  - "Tests verify population with mock haios-status-slim.json and session file"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-19T00:17:34
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.8
  parent: WORK-160
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T00:20:00
---
# WORK-170: Checkpoint Field Auto-Population

---

## Context

When running `/new-checkpoint`, the agent must manually look up the session number (from `.claude/session`), the current work_id (from haios-status-slim.json), the date, and the plan reference — then fill them into the checkpoint frontmatter. This is pure mechanical work that costs agent tokens with zero judgment required.

This work item automates the population of standard checkpoint fields. A new `lib/checkpoint_auto.py` module provides `populate_checkpoint_fields()` which reads from existing infrastructure (session file, haios-status-slim.json, work directory) and fills in standard fields. Called from PostToolUse when a checkpoint file is created.

**Pattern:** Same fail-permissive pattern as `session_end_actions.py`. Uses `_default_project_root()` for path derivation. Fields that cannot be resolved are left as template placeholders.

---

## Deliverables

- [ ] New file `lib/checkpoint_auto.py` with `populate_checkpoint_fields()` function
- [ ] PostToolUse integration: auto-populate on checkpoint file creation
- [ ] Handles: session_number, date, work_id, plan_ref
- [ ] Graceful degradation for unresolvable fields
- [ ] Tests in `tests/test_checkpoint_auto.py`

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
