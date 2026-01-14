---
template: work_item
id: E2-160
title: Work File Prerequisite Gate
status: complete
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-24
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
current_node: implement
node_history:
- node: implement
  entered: 2025-12-24 09:42:00
  exited: null
- node: implement
  entered: 2025-12-24 09:42:00
  exited: null
- node: implement
  entered: 2025-12-24 09:42:00
  exited: null
- node: implement
  entered: 2025-12-24 09:42:00
  exited: null
cycle_docs:
  investigation: docs/investigations/INVESTIGATION-E2-160-work-file-prerequisite-gate-design.md
  plan: docs/plans/PLAN-E2-160-work-file-prerequisite-gate.md
memory_refs: []
documents:
  investigations:
  - INVESTIGATION-E2-160-work-file-prerequisite-gate-design.md
  plans:
  - PLAN-E2-160-work-file-prerequisite-gate.md
  checkpoints: []
version: '1.0'
generated: 2025-12-24
last_updated: '2025-12-27T12:31:39'
---
# WORK-E2-160: Work File Prerequisite Gate

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** `/new-investigation` and `/new-plan` can create orphaned documents without a work file to track them. This bypasses the M6 work file architecture (scaffold-on-entry, exit gates, node tracking).

**Root cause:** No L3 gate checks if work file exists before allowing document creation.

**Discovery:** Session 109 - Created INV-027 investigation directly without work file. The scaffold-on-entry/exit-gates hooks never fired because there was no work file with `current_node` to change.

---

## Current State

L2 (prompted) only - documentation says "use /new-work first" but nothing enforces it.

---

## Deliverables

### Phase 1: Work File Prerequisite
- [ ] PreToolUse gate: Block `/new-investigation {id}` if no `docs/work/active/WORK-{id}-*.md` exists
- [ ] PreToolUse gate: Block `/new-plan {id}` if no work file exists
- [ ] User-friendly error message suggesting `/new-work {id} "title"` first

### Phase 2: Plan-First Enforcement (Session 113 addition)
- [ ] PreToolUse gate: Block `current_node: implement` if no `docs/plans/PLAN-{id}*.md` exists
- [ ] Gate on work file Edit that changes node to `implement` without plan
- [ ] Error message: "Plan required. Run `/new-plan {id} title` first."

### Tests & Docs
- [ ] Tests for work file prerequisite gate
- [ ] Tests for plan-first gate
- [ ] Update `/new-investigation` and `/new-plan` commands to document requirement

---

## History

### 2025-12-24 - Reopened + Extended (Session 113)
- Reopened: Was ceremonially closed with all deliverables unchecked
- Added Phase 2: Plan-First Enforcement gate
- Discovered when implementing M7a-Recipes without plans - nothing blocked it
- Principle: "Everything spawns a work file, everything goes through the system. No matter how trivial."

### 2025-12-24 - Created (Session 109)
- Spawned from INV-027 orphan document discovery
- L3 enforcement to close M6 gap

---

## References

- INV-027: Discovered the gap when creating investigation without work file
- E2-154: Scaffold-on-entry (depends on work file existing)
- E2-155: Exit gates (depends on work file existing)
- INV-020: Enforcement spectrum (L3 gates are effective)
