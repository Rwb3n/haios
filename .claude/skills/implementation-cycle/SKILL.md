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
```bash
just set-cycle implementation-cycle {PHASE} {work_id}
```

**On Complete:**
```bash
just clear-cycle
```
