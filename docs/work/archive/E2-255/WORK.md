---
template: work_item
id: E2-255
title: CycleRunner Module - Phase Execution and Gates
status: complete
owner: Hephaestus
created: 2026-01-03
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: medium
effort: high
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by:
- E2-251
- E2-253
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-03 23:21:49
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-03
last_updated: '2026-01-03T23:24:04'
---
# WORK-E2-255: CycleRunner Module - Phase Execution and Gates

@docs/README.md
@docs/epistemic_state.md
@docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md

---

## Context

**Problem:** CycleRunner module doesn't exist. Skills are markdown files that Claude interprets - cycle execution is implicit in agent behavior.

**Scope (from INV-052 S17.7):**
- S2D: Cycle extensibility - **In markdown only**
- S2E: Cycle skill analysis - **Documentation only**
- S2F: Cycle definitions schema - **Config exists but not consumed programmatically**
- S2G: Cycle extension guide - **Documentation only**
- S10: Skills taxonomy - **Markdown skills**
- S11: Subagents - **Agent definitions exist**

**Current implementation:**
- 15 skills in `.claude/skills/*/SKILL.md`
- Cycle definitions in `.claude/haios/config/cycles.yaml`
- Phase execution via Claude interpreting skill markdown

---

## IMPORTANT: Recursive Adjustment Note

This work item requires **recursive scope tightening** during implementation:
1. Query memory for prior decisions on cycle/skill architecture
2. Determine if CycleRunner should orchestrate or just validate
3. Consider: skills work as markdown - is programmatic execution needed?
4. Observations module (observations.py) may belong here or in WorkEngine
5. May be lower priority if markdown-based skills work well

---

## Deliverables

- [ ] Create `cycle_runner.py` module
- [ ] Implement `run_cycle(cycle_id, work_context)` method
- [ ] Implement `validate_phase_gate()` method
- [ ] Integrate with GovernanceLayer for gate checks
- [ ] Integrate with WorkEngine for state updates
- [ ] Migrate observations.py functionality (or assign to WorkEngine)
- [ ] Tests for CycleRunner
- [ ] Verify runtime consumers exist (E2-250 DoD criterion)

---

## History

### 2026-01-03 - Created (Session 162)
- Part of Epoch 2.2 full migration plan
- Spawned from INV-052 Section 17 analysis
- Currently no module exists - skills are markdown

---

## References

- `docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md` - Module design (S17.7)
- `.claude/skills/*/SKILL.md` - Current skill implementations
- `.claude/haios/config/cycles.yaml` - Cycle definitions
- `.claude/lib/observations.py` - May migrate here
- `.claude/lib/node_cycle.py` - May migrate here
