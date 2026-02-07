---
template: work_item
id: E2-233
title: Checkpoint Anti-Pattern Verification Integration
status: complete
owner: Hephaestus
created: 2025-12-29
closed: 2025-12-29
milestone: M8-SkillArch
priority: medium
effort: medium
category: implementation
spawned_by: S145 observation triage (E2-232, INV-050)
spawned_by_investigation: INV-050
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-29 12:10:55
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-29
last_updated: '2025-12-29T12:11:56'
---
# WORK-E2-233: Checkpoint Anti-Pattern Verification Integration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The anti-pattern-checker agent (E2-232) was designed in INV-050 to mechanically verify session claims against L1 anti-patterns from invariants.md. However, it requires manual invocation. The agent should be automatically invoked during checkpoint-cycle to verify claims before summary finalization.

**Root Cause:** checkpoint-cycle currently has FILL → CAPTURE phases but no VERIFY phase that would invoke the anti-pattern-checker agent before the summary is considered complete.

**Impact:** Without automatic verification, agent may make optimistic claims in checkpoint summaries that are not verified against known anti-patterns (Assume over verify, Optimistic confidence, Pattern-match solutions, etc.).

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add VERIFY phase to checkpoint-cycle skill between FILL and CAPTURE
- [ ] VERIFY phase invokes anti-pattern-checker agent on checkpoint content
- [ ] If verification finds issues, report them before finalizing
- [ ] Update checkpoint-cycle documentation
- [ ] Tests for VERIFY phase integration

---

## History

### 2025-12-29 - Created (Session 145)
- Initial creation

---

## References

- E2-232: Anti-pattern-checker agent implementation
- INV-050: Anti-pattern checker design investigation
- .claude/skills/checkpoint-cycle.md: Current checkpoint-cycle skill
- .claude/agents/anti-pattern-checker.md: Agent to integrate
