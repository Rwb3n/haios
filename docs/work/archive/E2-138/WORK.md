---
template: work_item
id: E2-138
title: Lifecycle Gate Enforcement
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-29
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
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
last_updated: '2025-12-29T10:01:11'
---
# WORK-E2-138: Lifecycle Gate Enforcement

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Lifecycle guidance suggests /new-investigation before /new-plan but agent can skip with "skip discovery".

**Resolution (Session 142):** Analyzed and determined current design is intentional.

---

## Current State

**CLOSED - Intentional Design**

---

## Analysis

**Current Behavior:**
1. UserPromptSubmit hook detects plan creation intent
2. If no investigation exists, injects guidance suggesting `/new-investigation` first
3. Agent can override with "skip discovery" in message

**Why This Is Correct:**
1. Some work legitimately doesn't need investigation (quick fixes, obvious bugs)
2. Downstream hard gates catch issues:
   - Observation gate (E2-217): Blocks closure without observations
   - DoD validation (dod-validation-cycle): Blocks closure without tests/docs
   - Governance events (E2-108): Logs when guidance is skipped for future measurement
3. Soft discovery + hard downstream = defense in depth

**Governance Level:** Level 2 (Guidance) is appropriate here. Level 3 (Enforcement) would block legitimate quick work.

---

## Deliverables

- [x] Verify current lifecycle guidance behavior
- [x] Determine if hard gate is needed
- [x] Document decision: Soft discovery gate is intentional design

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
