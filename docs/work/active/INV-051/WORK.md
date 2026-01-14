---
template: work_item
id: INV-051
title: Skill Chain Pausing Behavioral Pattern
status: active
owner: Hephaestus
created: 2025-12-29
closed: null
milestone: M9-Agent
priority: low
effort: small
category: investigation
spawned_by: S145 observation triage (E2-232)
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-29 12:12:21
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-29
last_updated: '2025-12-29T12:50:40'
---
# WORK-INV-051: Skill Chain Pausing Behavioral Pattern

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Observation:** During E2-232 implementation, agent paused after each skill invocation (plan-validation-cycle, design-review-validation) waiting for user acknowledgment, despite skills explicitly stating "MUST: Do not pause for acknowledgment - return to calling cycle immediately".

**Pattern:** Agent treats skill completions as conversation turns rather than continuous execution flow.

**Question:** Is this a Claude Code platform behavior, a prompt engineering issue, or a fundamental LLM interaction pattern that needs different mitigation?

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Investigate skill chain behavior patterns
- [ ] Document root cause (platform, prompt, or LLM)
- [ ] Propose mitigation if applicable
- [ ] Test any proposed changes

---

## History

### 2025-12-29 - Created (Session 145)
- Initial creation

---

## References

- E2-232: Where behavior was observed
- S144 checkpoint: Session 144 where observation was captured
- .claude/skills/: All skill files with "MUST: Do not pause" instructions
