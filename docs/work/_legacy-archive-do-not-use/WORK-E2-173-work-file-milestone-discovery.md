---
template: work_item
id: E2-173
title: Work File Milestone Discovery
status: complete
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-24
milestone: M7d-Plumbing
priority: high
effort: low
category: implementation
spawned_by: INV-029
spawned_by_investigation: INV-029
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-24 20:52:30
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-24
last_updated: '2025-12-24T21:29:09'
---
# WORK-E2-173: Work File Milestone Discovery

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Vitals show stale "M4-Research (50%)" despite M7a-Recipes being 100% complete.

**Root Cause:** `status.py:_discover_milestones_from_backlog()` only scans `backlog.md` for `**Milestone:**` patterns. M7 sub-milestones (M7a-M7e) exist only in work file YAML frontmatter (`milestone:` field), which status.py doesn't read.

**Source:** INV-029 investigation (Session 115)

---

## Current State

Work item in BACKLOG node. Ready for immediate implementation.

---

## Deliverables

- [ ] Add `_discover_milestones_from_work_files()` function to `.claude/lib/status.py`
- [ ] Scan `docs/work/{active,blocked,archive}/*.md` for `milestone:` YAML field
- [ ] Merge work file milestones with backlog milestones (work files take precedence)
- [ ] Update `_load_existing_milestones()` to call both discovery functions
- [ ] Add tests to `tests/test_lib_status.py`
- [ ] Verify vitals show M7a-Recipes progress after fix

---

## History

### 2025-12-24 - Created (Session 114)
- Initial creation

---

## References

- [Related documents]
