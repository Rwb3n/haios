---
template: work_item
id: INV-035
title: Skill Architecture Refactoring
status: complete
owner: Hephaestus
created: 2025-12-25
closed: 2025-12-25
milestone: M8-SkillArch
priority: medium
effort: medium
category: investigation
spawned_by: INV-035
spawned_by_investigation: INV-035
blocked_by: []
blocks: []
enables:
- E2-176
- E2-177
related:
- INV-033
- INV-011
- INV-022
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-25 09:21:06
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-25
last_updated: '2025-12-25T09:21:49'
---
# WORK-INV-035: Skill Architecture Refactoring

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 116 discussion revealed architectural inconsistencies in the skill/command/agent layering:

1. **Command-skill chaining inconsistent**: `/new-investigation` chains to skill, `/new-plan` doesn't
2. **No work-creation skill**: `/new-work` scaffolds but doesn't guide population
3. **Validation not formalized**: No bridge skills between phases (design→simulation→execution)
4. **Work item as fundamental unit**: Not enforced - can create investigations without work items

**Key Insights from Discussion:**
- Work Item = Virtual Session (contains all context, decisions, artifacts)
- Checkpoint = Context Compaction
- Validation skills should act as bridges between cycles
- Sub-agents useful for unbiased verification (async validation)

---

## Proposed Architecture

### Layered Skill Architecture

```
CYCLE SKILLS (orchestration):
├── work-creation-cycle (NEW)
├── plan-authoring-cycle (DESIGN) (NEW)
├── plan-validation-cycle (SIMULATION) (NEW) ← bridge
├── implementation-cycle (EXECUTION) ✓ exists
├── investigation-cycle ✓ exists
└── close-work-cycle (NEW)

VALIDATION SKILLS (bridges/gates):
├── preflight-validation
├── design-review
└── dod-validation

UTILITY SKILLS (composable):
├── memory-agent ✓ exists
├── schema-ref ✓ exists
└── audit ✓ exists

SUB-AGENTS (isolated contexts):
├── investigation-agent ✓ exists
├── validation-agent (NEW)
├── test-runner ✓ exists
└── async-validator (NEW)
```

### Validation as Bridge Pattern

```
DESIGN → SIMULATION → EXECUTION

plan-author-cycle → plan-validation-cycle → implementation-cycle
                          │
                   "Does agent know
                    what to do?"
```

---

## Current State

Work item in BACKLOG node. Awaiting investigation execution.

---

## Deliverables

Investigation phase:
- [ ] Document current skill/command/agent inventory
- [ ] Map gaps against proposed architecture
- [ ] Define skill contracts for new skills (work-creation, plan-authoring, close-work)
- [ ] Define validation bridge pattern formally
- [ ] Identify implementation sequence (dependencies)

Spawn phase:
- [ ] Spawn work items for each new skill/agent
- [ ] Update E2-176, E2-177 scope based on findings
- [ ] Create milestone for skill architecture refactoring

---

## History

### 2025-12-25 - Created (Session 116)
- Spawned from INV-033 and Session 116 architectural discussion
- Captured layered skill architecture vision
- Identified work-item-as-fundamental-unit paradigm

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- INV-011: Command-Skill Architecture Gap
- INV-022: Work Cycle DAG Unified Architecture
- Session 116 discussion: Skill architecture refactoring
