---
template: work_item
id: INV-050
title: Anti-Pattern Checker Agent Design
status: complete
owner: Hephaestus
created: 2025-12-29
closed: 2025-12-29
milestone: M8-SkillArch
priority: high
effort: medium
category: investigation
spawned_by: Session-143
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-29 11:05:15
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-29
last_updated: '2025-12-29T11:05:49'
---
# WORK-INV-050: Anti-Pattern Checker Agent Design

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session 143 revealed that I (the agent) incorrectly claimed "Epoch 2 exit criteria are essentially met" without evidence. I conflated "infrastructure exists" with "behavior achieved" - classic Optimistic Confidence anti-pattern.

**Root Cause:** No mechanical check challenges summary claims before acceptance. I self-assessed my own work and was lenient. The 6 L1 anti-patterns from invariants.md aren't applied as verification lenses.

**Trigger:** Operator challenged my assessment: "why do you assess it that way?" - forcing me to recognize I had no evidence for my claims.

**Insight:** We need "Structured Mistrust" made mechanical - an agent that applies anti-pattern lenses to claims before they're accepted.

---

## Current State

Work item in BACKLOG node. High priority - addresses fundamental agent reliability issue.

---

## Deliverables

- [ ] Design anti-pattern-checker agent specification
- [ ] Define trigger points (when to invoke: milestone claims, epoch assessments, session summaries)
- [ ] Define the 6 anti-pattern verification lenses (from invariants.md L1)
- [ ] Define evidence requirements for each lens
- [ ] Prototype agent in `.claude/agents/anti-pattern-checker.md`
- [ ] Integration recommendation (checkpoint-cycle, manual invocation, or both)
- [ ] Test on 3 historical claims from Session 143

---

## History

### 2025-12-29 - Created (Session 143)
- Spawned from operator challenge during roadmap review
- Agent incorrectly claimed Epoch 2 criteria "essentially met"
- Identified root cause: Optimistic Confidence anti-pattern, no evidence verification

---

## References

- `.claude/config/invariants.md` - L1 anti-patterns (6 patterns)
- ADR-033 - Work Item Lifecycle DoD (evidence-based verification model)
- Session 143 checkpoint - contains the incorrect claim and correction
