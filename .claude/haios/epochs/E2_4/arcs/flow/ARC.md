# generated: 2026-01-30
# System Auto: last updated on: 2026-02-01T23:34:42
# Arc: Flow

## Arc Definition

**Arc ID:** flow
**Epoch:** E2.4 (The Activity Layer)
**Name:** Universal Flow with Gates
**Status:** Planned
**Pressure:** [volumous] - thematic exploration

---

## Theme

Implement the universal flow with critique hard gates.

**Universal Flow:**
```
EXPLORE → DESIGN → PLAN → DO → CHECK → DONE
```

**Investigation Variant:**
```
EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
```

---

## Gate Pattern

**Critique as Hard Gate:**

```
DESIGN/PLAN → critique-invoke → critique-read → REVISE?
  - If Yes → revise → loop back
  - If No (PROCEED) → advance to next state
```

**Transition Gates:**

| Transition | Gate |
|------------|------|
| EXPLORE → DESIGN/HYPOTHESIZE | Findings captured |
| DESIGN → PLAN | Critique = PROCEED |
| PLAN → DO | Critique = PROCEED |
| DO → CHECK | Artifacts exist |
| CHECK → DONE | Verdict = pass |

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | FlowStateMachine | Planned | Implement state transitions with gates |
| CH-002 | CritiqueGate | Planned | Critique loop until PROCEED |
| CH-003 | InvestigationFlow | Planned | EXPLORE-FIRST variant implementation |
| CH-004 | ImplementationFlow | Planned | Full 6-phase flow implementation |
| CH-005 | FlowRouter | Planned | Route work type to correct flow |
| CH-006 | [ChapterFlow](CH-006-chapter-flow.md) | Planned | Bulk spawn, chapter scaffold, implementation spawn |
| CH-007 | [BatchOperations](CH-007-batch-operations.md) | Planned | Ceremony for bulk create without cycle trigger |
| CH-008 | [EpochTransition](CH-008-epoch-transition.md) | Planned | Ceremony for epoch transitions (/new-epoch) |
| CH-009 | DecisionTraceability | Planned | Ceremony for decision-to-chapter assignment (WORK-069) |
| CH-010 | MultiLevelDoD | Planned | Ceremonies for chapter/arc/epoch DoD cascade (WORK-070) |
| CH-011 | PreDecomposition | Planned | Ceremony for arc decomposition review (WORK-071) |

---

## Key Principle

> "Robust DESIGN allows simulation before DO."

DESIGN isn't optional overhead. It's the counter to completion incentive.

---

## Exit Criteria

- [ ] State machine implemented
- [ ] Critique hard gate enforced
- [ ] Investigation uses EXPLORE-FIRST
- [ ] DO phase is black-box

---

## Memory Refs

Session 265 universal flow decision: 82717-82720
Session 265 critique gate decision: 82711-82716

---

## References

- @.claude/haios/epochs/E2_4/EPOCH.md
- @.claude/agents/critique-agent.md
- @docs/work/active/WORK-037/ (EXPLORE-FIRST design)
