---
name: survey-cycle
description: HAIOS Survey Cycle for structured session-level work selection. Use after
  coldstart context loading. Guides GATHER->ASSESS->OPTIONS->CHOOSE->ROUTE workflow
  with volumous exploration before tight commitment.
recipes:
- ready
generated: 2026-01-11
last_updated: '2026-01-12T01:27:33'
---
# Survey Cycle

Select work after coldstart. Invoked automatically or via `Skill(skill="survey-cycle")`.

## Logic

1. **Continue prior work?**
   - Check checkpoint `pending` field
   - If work in_progress from prior session, continue it

2. **Otherwise, present options**
   - Run `just ready` for unblocked items
   - Select top 3 by priority + chapter alignment
   - Present via `AskUserQuestion` (or auto-select if autonomous)

3. **Route**
   - Use routing decision table:
     - `INV-*` prefix → `investigation-cycle`
     - Has plan → `implementation-cycle`
     - Otherwise → `work-creation-cycle`

## Gate

**MUST** select exactly one work item OR explicitly report "await_operator".

## Output

Invoke the appropriate cycle skill:
- `Skill(skill="investigation-cycle")`
- `Skill(skill="implementation-cycle")`
- `Skill(skill="work-creation-cycle")`

Or report: "No unblocked work. Awaiting operator direction."
