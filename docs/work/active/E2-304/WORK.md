---
template: work_item
id: E2-304
title: Add Status-Aware ID Validation to Work Creation
type: implementation
status: active
owner: Hephaestus
created: 2026-01-26
spawned_by: INV-072
chapter: null
arc: workuniversal
closed: null
priority: high
effort: small
traces_to:
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/modules/work_engine.py
- .claude/lib/scaffold.py
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 21:38:22
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-26T21:39:02'
---
# E2-304: Add Status-Aware ID Validation to Work Creation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Work item creation (`just work`, `create_work()`) does not check if the specified ID already exists with a terminal status (complete/archived). This allows agents to accidentally overwrite completed work items.

**Root cause:** INV-072 investigation found that `create_work()` uses `exist_ok=True` for directory creation and no status validation exists in the creation path.

**Source:** INV-072 Finding 2, Design Outputs section

---

## Deliverables

- [ ] Add `_validate_id_available(id: str) -> bool` to work_engine.py
- [ ] Function checks if WORK.md exists AND status is complete/archived
- [ ] Raise error if ID exists with terminal status
- [ ] Add same check to scaffold.py `scaffold_template()` for work_item template
- [ ] Tests for validation logic (positive and negative cases)
- [ ] Runtime consumer: `create_work()` calls validation before creating

---

## History

### 2026-01-26 - Created (Session 246)
- Spawned from INV-072 (Spawn ID Collision investigation)
- High priority: prevents data loss from accidental overwrites

---

## References

- @docs/work/active/INV-072/investigations/001-spawn-id-collision-completed-work-items-reused.md (source investigation)
- @.claude/haios/modules/work_engine.py (primary implementation target)
- @.claude/lib/scaffold.py (secondary implementation target)
