---
template: work_item
id: E2-024
title: Dependency Integrity Validator
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-28
milestone: M7c-Governance
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
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs:
- 64736
- 64737
- 64738
- 64739
- 64740
- 64741
- 64742
- 64743
- 64744
- 64745
- 64746
- 64747
- 64748
- 64749
- 64750
- 64751
documents:
  investigations: []
  plans:
  - docs/work/active/E2-024/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-28T21:21:52'
---
# WORK-E2-024: Dependency Integrity Validator

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Governance mechanisms reference other artifacts (hooks -> subagents -> skills -> commands). No validation these exist.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Create `validate_dependencies()` function in `.claude/lib/` - checks hooks/subagents/skills/commands references exist
- [ ] Validate hook references (hooks that invoke subagents, skills, or commands)
- [ ] Validate skill references (skills that invoke other skills or commands)
- [ ] Validate command references (commands that invoke skills)
- [ ] Integration with `/status` command - surface broken references
- [ ] Add dependency validation to `just update-status` or as standalone `just validate-deps`

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
