---
template: work_item
id: E2-217
title: Observation Capture Gate in Close Cycle
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: medium
category: implementation
spawned_by: Session-133
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: implement
node_history:
- node: backlog
  entered: 2025-12-28 13:02:23
  exited: '2025-12-28T13:03:19.725422'
- node: implement
  entered: '2025-12-28T13:03:19.725422'
  exited: null
cycle_docs: {}
memory_refs:
- 79895
- 79896
- 79897
- 79898
- 79899
- 79900
- 79901
- 79902
- 79903
- 79904
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T15:13:17'
---
# WORK-E2-217: Observation Capture Gate in Close Cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Agents exhibit "Ceremonial completion" and "Optimistic confidence" anti-patterns (L1 invariants). Bugs, gaps, and "I noticed..." observations get glossed over in the rush to completion. Session 132 example: context estimator drifting +12-15pp was only caught by post-hoc self-reflection, not during closure.

**Root cause:** No structured capture point for anomalies. Agents complete work and move on without friction to surface issues.

**Solution:**
1. Create `observations.md` template in work directories
2. Add soft gate in close-work-cycle prompting for observation capture
3. Add **hard validation** that blocks closure if gate was skipped (not crossed)
4. Surface uncaptured observations in `/audit` and coldstart

---

## Current State

Work item in BACKLOG node. Ready for implementation - design approved by operator.

---

## Deliverables

### Phase 1: Template
- [x] Create `observations.md` template in `.claude/templates/`
- [x] Add scaffold support for observations file (scaffold.py, justfile)

### Phase 2: Capture Gate
- [x] Update close-work-cycle SKILL.md with CAPTURE phase observation prompt
- [x] Agent must explicitly populate observations.md or check "None observed"

### Phase 3: Hard Validation
- [x] Add validation in close-work-cycle that checks observations.md exists (observations.py)
- [x] Block closure if observations.md missing or has unchecked placeholders
- [x] Validate "None observed" is explicit choice, not default (validate_observations())
- [x] Just recipes: `just validate-observations`, `just scaffold-observations`, `just scan-observations`

### Phase 4: Surfacing
- [x] Update `/audit` skill to scan for observations across work items
- [ ] Update coldstart to mention outstanding observations (deferred - low priority)

---

## History

### 2025-12-28 - Created (Session 133)
- Operator insight: facilitate bug/gap capture at closure to prevent glossing
- Design: observations.md + soft gate + hard validation
- Rationale: L1 anti-patterns (Ceremonial completion, Optimistic confidence)

---

## References

- L1 Invariants: `.claude/config/invariants.md` (Ceremonial completion anti-pattern)
- Roadmap S126: "Glossed-bug extraction from transcripts" (Epoch 4 vision - this is lightweight precursor)
- close-work-cycle skill: `.claude/skills/close-work-cycle/SKILL.md`
