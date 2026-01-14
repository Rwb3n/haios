---
template: work_item
id: E2-179
title: Scaffold Recipe Optional Frontmatter Args
status: active
owner: Hephaestus
created: 2025-12-25
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-033
spawned_by_investigation: INV-033
blocked_by: []
blocks: []
enables: []
related:
- E2-176
- E2-177
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-25 08:58:01
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T08:58:33'
---
# WORK-E2-179: Scaffold Recipe Optional Frontmatter Args

@docs/README.md
@docs/epistemic_state.md

---

## Context

The `just` scaffolding recipes (e.g., `just work`, `just inv`, `just plan`) only accept `backlog_id` and `title` as arguments. Key frontmatter fields like `spawned_by`, `milestone`, `priority`, and `related` must be manually edited after scaffolding.

This creates friction when spawning work items from investigations or other work items - the `spawned_by` linkage must be added manually.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Update `scaffold_template()` in `.claude/lib/scaffold.py` to accept optional kwargs for frontmatter fields
- [ ] Update `just work` recipe to accept optional `--spawned-by` arg
- [ ] Update `just inv` recipe to accept optional `--spawned-by` arg
- [ ] Update `just plan` recipe to accept optional `--spawned-by` arg
- [ ] Consider other optional args: `--milestone`, `--priority`, `--related`
- [ ] Update `.claude/lib/README.md` with new parameter documentation

---

## History

### 2025-12-25 - Created (Session 116)
- Spawned from INV-033 observation that spawned_by must be manually added after scaffolding

---

## References

- INV-033: Skill as Node Entry Gate Formalization (spawned this)
- `.claude/lib/scaffold.py`: Current scaffolding implementation
- `justfile`: Recipe definitions
