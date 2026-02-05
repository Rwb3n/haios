---
id: obs-313-01
session: 313
date: 2026-02-05
dimension: architecture
triage_status: pending
potential_action: investigation
parked_for: E2.6
discovered_during: WORK-091
generated: '2026-02-05'
last_updated: '2026-02-05T08:30:09'
---
# Observation: Ceremonies Are Static, Need Dynamic Composition

## What Was Observed

During WORK-091 (Fracture Validation Templates), discovered that:

1. Template fracturing work (CH-006) exposed tooling gaps (just recipes, hooks, scaffold module)
2. No ceremony exists for "architectural blocker discovered mid-implementation"
3. Agent had to improvise workflow: pause, discuss, manually propose steps
4. Ceremonies are hardcoded as skills, not composable from primitives

## Why It Matters

**Current State:**
- 20 ceremonies defined in L4/functional_requirements.md
- Each ceremony = one skill file
- Adding new ceremony = write new skill
- No trigger registry ("when X, consider ceremony Y")
- No composition mechanism ("ceremony = these activities in order")

**Impact:**
- Agent recognizes patterns but can't act on them systematically
- Operator decisions aren't captured in structured way
- Next agent has no context about what triggered what
- System can't learn new ceremonies from experience

## Aspired State

```yaml
# triggers.yaml - declarative trigger definitions
triggers:
  architectural_blocker_discovered:
    when:
      - during: [implementation-cycle/DO, implementation-cycle/PLAN]
      - condition: "ecosystem gap affecting >1 work item"
    then:
      - ceremony: pause_and_scope

# ceremonies.yaml - composable ceremony definitions
ceremonies:
  pause_and_scope:
    activities:
      - primitive: state_save
      - primitive: user_query
      - primitive: spawn_work
      - primitive: link_work
```

## Recommendation

Park for E2.6 investigation:
- **Question:** Can ceremonies be config-driven instead of skill-driven?
- **Explores:** triggers.yaml, ceremonies.yaml, activity primitives
- **Output:** Architecture proposal or "not worth complexity" decision

## Evidence

- Session 313 transcript: Manual improvisation of "pause and scope" workflow
- No matching ceremony in L4 functional_requirements.md
- REQ-ACTIVITY-001 describes composition but doesn't implement it
- REQ-CEREMONY-001 defines ceremonies as side-effect boundaries but static

## Links

- spawned_by: WORK-091
- related_requirement: REQ-ACTIVITY-001, REQ-CEREMONY-001
- epoch_context: E2.5 Independent Lifecycles
