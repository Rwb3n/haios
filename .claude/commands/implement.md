---
allowed-tools: Read, Glob, Write, Edit, Bash, Skill, Task, SlashCommand
description: Implement a backlog item using the PLAN-DO-CHECK-DONE cycle
argument-hint: <backlog_id>
generated: '2025-12-28'
last_updated: '2025-12-28T10:49:10'
---
# Implement Work Item

**Arguments:** $ARGUMENTS

Parse the backlog_id from arguments (e.g., `E2-092`, `INV-012`).

## Workflow

1. **Invoke Skill:** `Skill(skill="implementation-cycle")`
2. **Pass Context:** The skill will guide through PLAN-DO-CHECK-DONE
3. **Track State:** Update plan status as phases complete

## Phase Entry Points

| Phase | Entry Condition |
|-------|-----------------|
| PLAN | Plan exists at `docs/work/active/{backlog_id}/plans/PLAN.md` (or legacy `docs/plans/PLAN-{backlog_id}-*.md`) |
| DO | Plan status is `approved` and design is complete |
| CHECK | Implementation complete, ready for verification |
| DONE | All tests pass, ready for closure |

## Quick Start

After invoking this command:
1. I will read the plan file for {backlog_id}
2. Determine current phase based on plan status
3. Execute phase-specific actions from the skill
4. Report progress and next steps
