---
template: work_item
id: WORK-085
title: Implement Pause Semantics (CH-002)
type: feature
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-002-PauseSemantics
arc: lifecycles
closed: '2026-02-03'
priority: high
effort: small
traces_to:
- REQ-LIFECYCLE-002
requirement_refs: []
source_files:
- .claude/haios/modules/work_engine.py
- .claude/skills/close-work-cycle/SKILL.md
acceptance_criteria:
- WorkEngine.is_at_pause_point() implemented
- Pause phases defined for all 5 lifecycles
- close-work-cycle accepts pause point closure
- No warnings/errors when closing at pause
blocked_by:
- WORK-084
blocks:
- WORK-087
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 19:30:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
  implementation_type: REFACTOR
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T19:42:38'
---
# WORK-085: Implement Pause Semantics (CH-002)

---

## Context

Per S27 Breath Model, pause points are valid completion states:
```
EXPLORE [inhale] -> SYNTHESIZE [exhale] -> [pause: safe to stop]
```

While close-work-cycle allows `await_operator`, there's no programmatic way to recognize pause points.

**Gap to address:**
- No PAUSE_PHASES constant mapping lifecycles to their pause phases
- WorkEngine lacks `is_at_pause_point()` method
- S27 phase names don't match lifecycle phases

---

## Deliverables

- [ ] Define PAUSE_PHASES constant mapping each lifecycle to its pause phase(s)
- [ ] Implement WorkEngine.is_at_pause_point(work_id) method
- [ ] Update close-work-cycle to accept pause point closure without warning
- [ ] Unit tests for pause recognition per lifecycle
- [ ] Integration test: Investigation CONCLUDE -> close without spawn -> success

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-002-PauseSemantics
- Depends on WORK-084 for lifecycle signatures

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-002-PauseSemantics.md
- @.claude/haios/epochs/E2_4/architecture/S27-breath-model.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-002)
