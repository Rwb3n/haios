---
template: work_item
id: E2-016
title: Enhanced CLI Status + Synthesis Run
status: wontfix
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-26
milestone: M7d-Plumbing
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
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-26T16:41:28'
---
# WORK-E2-016: Enhanced CLI Status + Synthesis Run

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session 49 troubleshooting revealed table name assumptions. CLI status should be single source of truth.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add synthesis stats to `cli.py status` command (clusters, members, last run)
- [ ] Run synthesis with `--max-bridges 200` (double default) to connect E2-015 learnings

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

### 2025-12-26 - Closed as Won't Fix (Session 124)
- Investigation revealed `synthesis stats` command already exists
- Deliverable #1 (add synthesis stats) is redundant - use `python -m haios_etl.cli synthesis stats`
- Deliverable #2 (run synthesis) is operational, not code change
- See: INVESTIGATION-E2-016-enhanced-cli-status-design-investigation.md
- Memory refs: 79126-79129

---

## References

- [Related documents]
