---
template: work_item
id: INV-045
title: Memory Retrieval UX and Trigger Design
status: archived
owner: Hephaestus
created: 2025-12-28
closed: null
milestone: M8-Memory
priority: medium
effort: medium
category: investigation
spawned_by: Session-132
spawned_by_investigation: null
blocked_by: []
blocks: []
enables:
- INV-023
related:
- INV-023
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 11:36:20
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2026-01-18T21:56:50'
---
# WORK-INV-045: Memory Retrieval UX and Trigger Design

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Memory retrieval is underutilized during active work. Agent has memory tools available but defaults to immediate file context over retrieved context.

**Observed Patterns (Session 132 self-reflection):**

1. **Friction in query loop** - Memory adds interpretation step that feels like overhead when "in flow"
2. **Results require synthesis** - 10 results with mixed relevance scores; unclear what's actionable
3. **Unclear trigger points** - "SHOULD check memory before complex tasks" is too vague; every task feels either "not complex enough" or "I already know what to do"
4. **No feedback loop** - No signal when memory helps; no penalty when skipped; incentive structure is neutral
5. **Retrieval quality uncertainty** - 0.65 vs 0.85 scores mixed; don't trust ranking enough to always act on top results

**Root cause:** No clear mental model for *when* memory changes decisions. Treated as optional → skipped → habit never forms.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Document current memory query trigger points (coldstart, memory-agent skill)
- [ ] Identify decision points where memory SHOULD be queried (before impl, before close, etc.)
- [ ] Prototype explicit trigger injection (e.g., "Before implementing {id}, query memory")
- [ ] Evaluate result filtering (only 0.75+ scores, only actionable types)
- [ ] Design "memory changed my plan" logging for feedback loop
- [ ] Propose integration with ReasoningBank (INV-023) for strategy injection

---

## History

### 2025-12-28 - Created (Session 132)
- Spawned from operator question: "why is memory being pushed to the wayside?"
- Agent self-reflection identified 5 friction patterns
- Core insight: neutral incentive structure → skip memory → no habit formation

---

## References

- Related: INV-023 (ReasoningBank Feedback Loop Architecture) - upstream strategy extraction
- Enables: INV-023 - this investigation provides UX layer for ReasoningBank consumption
- Memory 79160: Synthesis about event logging and query refinement
- Session 132: E2-212 closure gap - memory *might* have surfaced consumer verification need
