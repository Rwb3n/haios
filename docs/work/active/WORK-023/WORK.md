---
template: work_item
id: WORK-023
title: scan_incomplete_work false positives - ignores status field
type: bug
status: complete
owner: Hephaestus
created: 2026-01-26
spawned_by: null
chapter: null
arc: configuration
closed: '2026-01-26'
priority: high
effort: small
traces_to:
- REQ-CONTEXT-001
requirement_refs: []
source_files:
- .claude/haios/lib/governance_events.py
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 23:22:33
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82509
- 82510
- 82512
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-26T23:50:52'
---
# WORK-023: scan_incomplete_work false positives - ignores status field

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** `scan_incomplete_work()` in `governance_events.py:191-241` reports ALL work items with `exited: null` in node_history as "stuck", ignoring the `status` field. This causes coldstart to show 80+ false positives.

**Evidence:**
- E2-236 has `status: complete` but coldstart says "stuck in backlog"
- E2-295 has `status: archived` but coldstart says "stuck in complete"
- Every work item has `exited: null` on its current node by design

**Root cause:** The function checks `exited: null` (which node is current) but doesn't filter by `status` (is work done).

---

## Deliverables

- [x] Fix `scan_incomplete_work()` to filter out `status: complete` and `status: archived`
- [x] Verify coldstart no longer reports completed work as "stuck"
- [x] Add test coverage for the fix

---

## History

### 2026-01-26 - Created (Session 247)
- Discovered during E2-306 coldstart
- Root cause identified: missing status filter

---

## References

- @.claude/haios/lib/governance_events.py (lines 191-241)
- @docs/work/active/E2-236/WORK.md (example false positive)
