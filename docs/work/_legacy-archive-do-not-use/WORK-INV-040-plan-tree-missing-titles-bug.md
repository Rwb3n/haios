---
template: work_item
id: INV-040
title: Plan Tree Missing Titles Bug
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: null
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
  entered: 2025-12-26 15:14:04
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T15:20:19'
---
# WORK-INV-040: Plan Tree Missing Titles Bug

@docs/README.md
@docs/epistemic_state.md

---

## Context

`just tree` and `just ready` outputs show work item IDs but titles are missing/empty for many items. Example:
```
[x] E2-109:                          <-- EMPTY TITLE
[x] E2-132:                          <-- EMPTY TITLE
```

The `plan_tree.py` script is failing to extract the `title:` field from YAML frontmatter for some work items. This affects operational visibility - cannot see what work items are about.

---

## Current State

Work item in BACKLOG node. Awaiting investigation.

---

## Deliverables

- [ ] Diagnose root cause of missing titles in plan_tree.py output
- [ ] Fix parsing logic to correctly extract titles from all work files
- [ ] Verify fix with `just tree` showing all titles populated

---

## History

### 2025-12-26 - Created (Session 123)
- Initial creation
- Bug observed during M7d milestone review

---

## References

- scripts/plan_tree.py - Script with parsing bug
- Memory 78861: Related status.py parsing issue with milestone discovery
- Memory 77347: Script parses backlog.md headers
