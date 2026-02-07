---
template: work_item
id: E2-284
title: Observation-Capture Simplify to 3 Questions
status: complete
owner: Hephaestus
created: 2026-01-10
closed: '2026-01-10'
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
  entered: 2026-01-10 11:54:34
  exited: null
cycle_docs: {}
memory_refs:
- 81268
- 81269
- 81270
- 81271
- 81272
- 81273
- 81274
- 81275
- 81276
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-10
last_updated: '2026-01-10T16:56:07'
---
# WORK-E2-284: Observation-Capture Simplify to 3 Questions

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** observation-capture-cycle is 134 lines with 3 phases (RECALL→NOTICE→COMMIT). S20 says "observations.md (4 sections, 100 lines) should be 3 questions, hard gate."

**Evidence:** The cycle forces reflection but through procedural phases. The template itself (observations.md) has the structure - the cycle is overhead.

**Solution:** 3 questions, hard gate:
1. What surprised you?
2. What's missing?
3. What should we remember?

Gate: non-empty answers or explicit "none observed"

---

## Deliverables

- [x] Simplify observation-capture to 3 questions
- [x] Hard gate (binary pass/fail)
- [x] Remove RECALL→NOTICE→COMMIT phases
- [x] observations.md template also simplified

---

## History

### 2026-01-10 - Created (Session 186)
- Spawned from Session 186 meta-observation
- S20 explicitly calls out "3 questions, hard gate" as target

---

## References

- Memory 81211-81221 (skills as procedural theater)
- S20-pressure-dynamics.md line 98 ("3 questions, hard gate")
- Current: .claude/skills/observation-capture-cycle/SKILL.md
