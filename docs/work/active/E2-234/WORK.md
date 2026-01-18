---
template: work_item
id: E2-234
title: Auto Session-Start in Coldstart
status: dismissed
owner: Hephaestus
created: 2025-12-30
closed: '2026-01-17'
milestone: M7b-WorkInfra
priority: high
effort: low
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 20:18:39
  exited: null
cycle_docs: {}
memory_refs:
- 81445
- 81446
- 81447
- 81448
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2026-01-18T21:56:50'
---
# WORK-E2-234: Auto Session-Start in Coldstart

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Coldstart.md instructs agent to "run `just session-start N`" but doesn't automate it. Agent must manually compute N = current_session + 1 and run the command. This leads to missed session-start events and inconsistent session tracking.

**Root cause:** Session-start is documented as a manual step rather than an automated action in the coldstart workflow.

**Source:** INV-052 Issue 2 (Session-Start Not Automated)

---

## Current State

COMPLETE. Coldstart.md Step 8 implements automated session-start. Verified working in Session 200.

---

## Deliverables

- [x] Update `.claude/commands/coldstart.md` to include automated session-start
- [x] Add step after "Read haios-status-slim.json" to run `just session-start N` where N = current_session + 1
- [x] Test coldstart with new automation

---

## History

### 2025-12-30 - Created (Session 150)
- Initial creation

### 2026-01-17 - Completed (Session 200)
- Verified coldstart.md Step 8 implements automated session-start
- Tested: Session 200 started successfully via `just session-start 200`
- Note: Implementation predates work item closure - likely added during coldstart refactoring

---

## References

- [Related documents]
