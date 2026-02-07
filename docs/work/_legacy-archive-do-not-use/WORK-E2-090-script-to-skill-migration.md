---
template: work_item
id: E2-090
title: Script-to-Skill Migration
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-24
milestone: M7a-Recipes
priority: medium
effort: medium
category: implementation
spawned_by: Session 81
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: check
node_history:
- node: check
  entered: '2025-12-24T20:08:45.221863'
  exited: null
- node: check
  entered: '2025-12-24T20:08:45.221863'
  exited: null
- node: check
  entered: '2025-12-24T20:08:45.221863'
  exited: null
- node: check
  entered: '2025-12-24T20:08:45.221863'
  exited: null
cycle_docs: {}
memory_refs: null
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: 2025-12-24T20:10:44
---
# WORK-E2-090: Script-to-Skill Migration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Scripts created during E2-084 (plan_tree.py) violate INV-011 architecture. Commands should invoke skills, skills should call just recipes.
---

## Current State

Session 114: Scope refined after recipe audit. Original scope too broad - most recipes already exist.

---

## Deliverables (Scope Refined Session 114)

**Recipe Consolidation:**
- [ ] `/audit` skill - chains audit-sync, audit-gaps, audit-stale
- [ ] `/tree` command - user-facing milestone visibility (wraps just tree)
- [ ] `/ready` command - user-facing "what to work on" (wraps just ready)
- [ ] Verify PostToolUse cascade could use `just cascade` (optimization check)

**Descoped (already exist as just recipes, no command needed):**
- ~~`just cascade`~~ - internal plumbing
- ~~`just events*`~~ - operational debugging
- ~~`just session-*`~~ - auto-invoked
- ~~`just orphans`~~ - already in audit recipes

**Architectural Pattern (Memory 71341):**
```
/tree command → just tree recipe
     ↓              ↓
   prompt       execution
```

**Related:** INV-011 (Command-Skill Architecture Gap)

---

## History

### 2025-12-24 - Updated (Session 111)
- Added `just orphans` / `/workspace` enhancement candidate
- Pattern discovered when PowerShell command failed; Python > just > skill > command chain identified

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
