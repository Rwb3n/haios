---
template: work_item
id: INV-041
title: Autonomous Session Loop Gap Analysis
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7c-Governance
priority: high
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 14:22:09
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T14:39:47'
---
# WORK-INV-041: Autonomous Session Loop Gap Analysis

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Epoch 2 exit requires autonomous session loop: coldstart → pick work → execute → checkpoint → clear → coldstart. Currently agent waits for human to invoke commands at each step.

**Root Cause:** Skills and commands exist but lack:
1. Auto-routing after coldstart (agent should pick next work item)
2. Auto-chaining through cycles (investigation → implementation → close)
3. Auto-checkpoint before context full
4. Resume-from-checkpoint on coldstart

**Trigger:** S126 discussion clarifying true Epoch 2 exit criteria.

---

## Current State

Work item in BACKLOG node. Ready for investigation.

---

## Deliverables

- [ ] Map current session lifecycle (what exists, what's manual)
- [ ] Identify gaps for each phase: pick → execute → checkpoint → clear → resume
- [ ] Design auto-routing mechanism (how agent picks next work item)
- [ ] Design cycle-chaining mechanism (how cycles flow without prompting)
- [ ] Design context preservation mechanism (what survives clear)
- [ ] Spawn implementation work items for each gap

---

## History

### 2025-12-27 - Created (Session 126)
- Initial creation

---

## References

- [Related documents]
