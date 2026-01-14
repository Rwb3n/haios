---
template: work_item
id: E2-232
title: Implement Anti-Pattern Checker Agent
status: complete
owner: Hephaestus
created: 2025-12-29
closed: 2025-12-29
milestone: M8-SkillArch
priority: high
effort: medium
category: implementation
spawned_by: INV-050
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-29 11:13:14
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-29
last_updated: '2025-12-29T11:13:48'
---
# WORK-E2-232: Implement Anti-Pattern Checker Agent

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session 143 exposed Optimistic Confidence anti-pattern - agent claimed "Epoch 2 criteria met" without evidence. No mechanical check challenges claims before acceptance.

**Solution:** INV-050 designed an anti-pattern-checker agent that applies the 6 L1 anti-patterns as verification lenses to claims.

---

## Current State

Work item in BACKLOG node. Design complete from INV-050.

---

## Deliverables

- [ ] Create `.claude/agents/anti-pattern-checker.md` agent definition
- [ ] Define 6 verification lenses (from invariants.md L1 anti-patterns)
- [ ] Implement structured output format (JSON with pass/fail per lens)
- [ ] Add Edge Cases table (incomplete claims, no evidence, partial evidence)
- [ ] Add Examples section showing input/output
- [ ] Test on Session 143's incorrect claim as example

---

## History

### 2025-12-29 - Created (Session 143)
- Spawned from INV-050 investigation
- Design spec in investigation findings

---

## References

- Spawned by: INV-050 (Anti-Pattern Checker Agent Design)
- Design spec: `docs/work/active/INV-050/investigations/001-anti-pattern-checker-agent-design.md`
- Source patterns: `.claude/config/invariants.md:83-95`
- Architecture patterns: `.claude/agents/validation-agent.md`, `.claude/agents/preflight-checker.md`
