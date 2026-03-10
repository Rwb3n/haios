---
name: implementation-cycle
type: lifecycle
description: HAIOS Implementation Cycle for structured work item implementation. Use
  when starting implementation of a plan. Guides PLAN->DO->CHECK->DONE workflow with
  phase-specific tooling.
recipes:
- node
generated: 2025-12-22
last_updated: '2026-02-22T11:00:00'
---
# Implementation Cycle

This skill defines the PLAN-DO-CHECK-DONE cycle for structured implementation of work items. It composes existing primitives (Skills, Commands, Subagents, Justfile) into a coherent workflow.

## When to Use

**SHOULD** invoke this skill when:
- Starting implementation of a backlog item
- Resuming work on an in-progress item
- Unsure of next step in implementation workflow

**Invocation:** `Skill(skill="implementation-cycle")`

---

## The Cycle

```
PLAN --> DO --> CHECK --> DONE --> CHAIN
  ^       ^       |                  |
  |       +-------+ (if tests fail)  [route next]
  +-- (if no plan)                   |
                              /-------------\
                        type=investigation  has plan?   else
                        OR INV-* prefix        |          |
                               |          implement  work-creation
                          investigation    -cycle     -cycle
                             -cycle
```

## Phase Contracts

Each phase's full behavioral contract is in its own file (ADR-048 progressive disclosure):

| Phase | File | Content |
|-------|------|---------|
| PLAN | `phases/PLAN.md` | Entry gate (critique), plan authoring, exit gates (critique loop, plan-validation, preflight) |
| DO | `phases/DO.md` | Dispatch protocol, TDD enforcement, design-review exit gate |
| CHECK | `phases/CHECK.md` | Test suite, deliverables verification, DoD criteria |
| DONE | `phases/DONE.md` | WHY capture, plan status, documentation |
| CHAIN | `phases/CHAIN.md` | Close work, routing decision table, next cycle invocation |

## Reference

- `reference/decisions.md` — Key design decisions, rationale, related ADRs
- `reference/composition.md` — Composition map, quick reference, TDD cycle, governance events

---

**On Entry (any phase):**
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="{PHASE}", work_id="{work_id}")
```

**Direct DO-Phase Entry (Build-Session):**

When survey-cycle routes here after detecting an approved plan (plan `status: approved` + `cycle_phase: PLAN` + checkpoint `pending`):
1. `mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")`
2. Read `docs/work/active/{work_id}/plans/PLAN.md` (the handoff artifact from plan-session)
3. Execute DO phase per `phases/DO.md` — skip PLAN phase

> PLAN was completed in session N. DO begins in session N+1 with clean context.
> See `phases/PLAN.md` Session Yield and `survey-cycle/SKILL.md` Build-Session Detection for the full protocol.

**On Complete:**
```
mcp__haios-operations__cycle_clear()
```
