---
template: work_item
id: E2-211
title: Add SQLite busy_timeout to DatabaseManager
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M8-Memory
priority: high
effort: low
category: implementation
spawned_by: null
spawned_by_investigation: INV-027
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 16:20:00
  exited: null
cycle_docs:
  backlog: docs/plans/PLAN-E2-211-add-sqlite-busytimeout-to-databasemanager.md
memory_refs: []
documents:
  investigations: []
  plans:
  - docs/plans/PLAN-E2-211-add-sqlite-busytimeout-to-databasemanager.md
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T16:45:50'
---
# WORK-E2-211: Add SQLite busy_timeout to DatabaseManager

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Concurrent access to haios_memory.db by ingester (MCP) and synthesis (CLI) causes crashes. When synthesis holds write lock during long transactions, ingester write attempts fail immediately because SQLite's default `busy_timeout` is 0ms.

**Root Cause:** No `PRAGMA busy_timeout` configured in `DatabaseManager.get_connection()`. SQLite defaults to 0ms wait, causing immediate `SQLITE_BUSY` errors instead of retrying.

**Source:** INV-027 investigation confirmed all 3 hypotheses with high confidence.

---

## Current State

Work item in BACKLOG node. Ready for implementation.

---

## Deliverables

- [ ] Add `PRAGMA busy_timeout=30000` in DatabaseManager.get_connection() after WAL mode
- [ ] Add test for concurrent access scenario
- [ ] Verify fix with manual test (run synthesis in background, call ingester_ingest)

---

## History

### 2025-12-27 - Created (Session 128)
- Spawned from INV-027 investigation
- Root cause: missing busy_timeout PRAGMA

---

## References

- INV-027: Ingester Synthesis Concurrent Access Crash investigation
- `.claude/lib/database.py:17-36` - target location for fix
- Memory concepts: 59590, 55504, 57730 (SQLite concurrency prior art)
