---
template: work_item
id: E2-161
title: "Auto-link Documents to Work File"
status: active
owner: Hephaestus
created: 2025-12-24
closed: null
milestone: M7b-WorkInfra
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
    entered: 2025-12-24T09:41:53
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-24
last_updated: 2025-12-24T13:40:05
---
# WORK-E2-161: Auto-link Documents to Work File

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** When `/new-investigation` or `/new-plan` creates a document, the work file's `cycle_docs` and `documents` fields must be manually updated.

**Solution:** PostToolUse hook detects scaffold completion and auto-updates the work file.

---

## Current State

Work item in BACKLOG node. Blocked by E2-160 (prerequisite gate first).

---

## Deliverables

- [ ] PostToolUse handler: detect scaffold_template output for investigation/plan
- [ ] Auto-update work file: add path to `cycle_docs.<type>`
- [ ] Auto-update work file: add filename to `documents.<type>s[]`
- [ ] Tests for auto-linking logic

---

## History

### 2025-12-24 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
