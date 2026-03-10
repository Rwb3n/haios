---
name: survey-cycle
type: lifecycle
description: HAIOS Survey Cycle for structured session-level work selection. Use after
  coldstart context loading. Guides GATHER->ASSESS->OPTIONS->CHOOSE->ROUTE workflow
  with volumous exploration before tight commitment.
recipes: []
generated: 2026-01-11
last_updated: '2026-01-28T22:44:56'
---
# Survey Cycle

Select work after coldstart. Invoked automatically or via `Skill(skill="survey-cycle")`.

## Logic

1. **Continue prior work?**
   - Check checkpoint `pending` field
   - If work in_progress from prior session:
     - **Build-Session Fast-Path:** If plan `status: approved` AND `cycle_phase: PLAN` AND
       work item is in checkpoint `pending` field → route to `implementation-cycle` at DO phase
       (skip PLAN — build-session). See Build-Session Detection below.
     - Otherwise → continue at current phase normally

2. **Otherwise, present options**
   - Run `mcp__haios-operations__queue_list(queue_name="{queue_name}")` for ordered items (default: "default")
   - Alternatively: `mcp__haios-operations__queue_ready()` for flat unordered list (backward compat)
   - Select top 3 from queue head
   - Present via `AskUserQuestion` (or auto-select if autonomous)

**After queue selection:**
```bash
just set-queue {queue_name}
```

3. **Route**
   - Read work item WORK.md to get `type` field
   - Use routing decision table (WORK-030: type field is authoritative):
     - `type: investigation` → `investigation-cycle`
     - Has plan (file exists at `docs/work/active/{id}/plans/PLAN.md`) → `implementation-cycle`
     - Otherwise → `work-creation-cycle`

**Build-Session Detection (approved-plan fast-path — invoked from step 1):**

When the checkpoint `pending` field contains a work item ID, check for the approved-plan state:
1. Read `docs/work/active/{id}/plans/PLAN.md` frontmatter — check `status: approved`
2. Read `docs/work/active/{id}/WORK.md` frontmatter — check `cycle_phase: PLAN`
3. Confirm work item is in checkpoint `pending` field (third condition — prevents false-positive
   on stale approved plans re-entering PLAN phase, since `pending` is only set by plan-session yield)
4. If ALL THREE conditions true: route to implementation-cycle and set phase to DO:
   ```
   mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")
   ```
5. Read the approved plan from disk before executing DO steps.
   (If any condition is false, enter PLAN phase normally — fail-safe.)

> **Rationale (WORK-289):** Avoids re-running PLAN phase (~15% context wasted per mem:89507) when plan
> was authored in a dedicated plan-session. Three-condition check (plan status + cycle_phase + pending)
> prevents false-positive fast-path. Pending field is only set by plan-session yield, not PLAN entry.

## Gate

**MUST** select exactly one work item OR explicitly report "await_operator".

## Output

Invoke the appropriate cycle skill:
- `Skill(skill="investigation-cycle")`
- `Skill(skill="implementation-cycle")`
- `Skill(skill="work-creation-cycle")`

Or report: "No unblocked work. Awaiting operator direction."
