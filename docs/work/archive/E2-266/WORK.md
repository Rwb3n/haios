---
template: work_item
id: E2-266
title: AgentUX Gap Prompts in Observation Template
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-04'
milestone: null
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
  entered: 2026-01-04 21:00:41
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T21:01:17'
---
# WORK-E2-266: AgentUX Gap Prompts in Observation Template

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The observation template's "Gaps Noticed" section doesn't specifically prompt for **AgentUX gaps** - friction points agents encounter while working. The "None observed" checkbox makes it too easy to skip reflection.

**Root cause:** Template designed for general gaps, not specifically for agent experience issues. Process doesn't guide agents to surface workflow friction.

**Source:** S170 discussion - operator noted that AgentUX gaps (like verbose `just scaffold checkpoint`) should be surfaced during observation capture.

---

## Current State

Work item in BACKLOG node. Template enhancement.

---

## Deliverables

- [ ] Add "AgentUX Gaps" subsection to observation template under Gaps Noticed
- [ ] Add trigger phrases: "friction", "verbose", "too many steps", "should be easier"
- [ ] Consider: Should AgentUX gaps auto-spawn E2-xxx work items?

---

## History

### 2026-01-04 - Created (Session 170)
- Spawned from operator feedback during S170 checkpoint
- Observation process gap identified

---

## References

- `.claude/templates/observations.md` - Target template
- E2-217: Observation Gate implementation
- S170 checkpoint discussion
