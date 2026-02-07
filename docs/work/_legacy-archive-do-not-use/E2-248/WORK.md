---
template: work_item
id: E2-248
title: GovernanceLayer Error Visibility
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: low
effort: low
category: implementation
spawned_by: null
spawned_by_investigation: INV-055
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 18:31:58
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T18:32:36'
---
# WORK-E2-248: GovernanceLayer Error Visibility

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** GovernanceLayer catches all exceptions silently (`.claude/haios/modules/governance_layer.py:187,211`), which violates the Agent UX Test "Can an agent recover from failure?" requirement.

**Root cause:** Exception handling uses bare `except Exception: pass` pattern with no logging or status indication.

**Goal:** Add logging/return value for handler exceptions so agents know when governance is degraded.

---

## Current State

Work item in BACKLOG node. Low priority - governance works, just silent on errors.

---

## Deliverables

- [ ] Add logging for caught exceptions in GovernanceLayer
- [ ] Return degraded status or warning in GateResult when handlers fail
- [ ] Tests for exception visibility
- [ ] Update README.md with new behavior

---

## History

### 2026-01-03 - Created (Session 161)
- Spawned from INV-055: Agent Usability Requirements Detailing
- Finding 1: GovernanceLayer Silent Failure

---

## References

- INV-055: Agent Usability Requirements Detailing (spawn source)
- L3-requirements.md: Agent Usability Requirements (lines 76-113)
