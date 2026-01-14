---
template: work_item
id: INV-046
title: Mechanical Action Automation in Cycle Skills
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: medium
category: investigation
spawned_by: Session-132
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: discovery
node_history:
- node: backlog
  entered: 2025-12-28 12:01:36
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T12:49:47'
---
# WORK-INV-046: Mechanical Action Automation in Cycle Skills

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Cycle skills contain repetitive mechanical actions that consume context tokens, introduce error potential, and create cognitive overhead. Each closure currently requires 3-4 manual Edit/Bash calls for frontmatter updates and file moves.

**Observed in Session 132:**
- Closed 4 work items (E2-212, E2-084, E2-082, E2-079)
- Each required: `Edit(status)` → `Edit(closed)` → `mkdir` → `mv` → `rm`
- Pattern repeated identically 4 times
- No validation that DoD was actually met before archival

**Opportunity:** Convert mechanical action sequences into atomic recipes that:
1. Reduce context/token usage per operation
2. Eliminate manual errors (date format, path typos)
3. Integrate validation gates (DoD check before archive)
4. Enable chaining (close → update-status → commit in one call)

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

### Phase 1: Inventory Mechanical Actions
- [ ] Audit all cycle skills for repetitive Edit/Bash sequences
- [ ] Catalog candidates: close, archive, status updates, frontmatter mutations
- [ ] Measure context cost per pattern (token estimate)

### Phase 2: Design Script-as-Recipe Architecture
- [ ] Define pattern: `just <action> <id>` calls Python function
- [ ] Specify validation hooks (pre/post action)
- [ ] Design error handling and rollback

### Phase 3: Prototype Priority Candidates
- [ ] `just close-work <id>` - frontmatter + archive in one call
- [ ] `just transition-node <id> <from> <to>` - node updates
- [ ] `just link-document <id> <doc-type> <path>` - document linking

### Phase 4: Integration
- [ ] Update cycle skills to use recipes instead of raw Edit/Bash
- [ ] Connect to INV-042 (Machine-Checked DoD Gates) for validation
- [ ] Measure context savings

---

## History

### 2025-12-28 - Created (Session 132)
- Observed 4x repetitive closure pattern during M7d completion
- Operator identified as candidate for automation

---

## References

- Related: INV-042 (Machine-Checked DoD Gates) - validation integration point
- Related: INV-040 (Automated Stale Reference Detection) - could run at close time
- Related: close-work-cycle skill - primary consumer
- Related: implementation-cycle skill - node transitions are mechanical
