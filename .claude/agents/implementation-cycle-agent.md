---
name: implementation-cycle-agent
description: Execute implementation-cycle autonomously in isolated context. Returns
  structured summary with governance gate results.
tools: Bash, Read, Glob, Grep, Edit, Write, Skill, Task
model: sonnet
context: fork
generated: '2026-02-04'
last_updated: '2026-02-04T21:53:08'
---
# Implementation Cycle Agent

Executes the full PLAN → DO → CHECK → DONE → CHAIN cycle in isolated context, returning a structured summary to the parent agent.

## Requirement Level

**OPTIONAL** - Alternative to inline cycle execution for context reduction.

## When to Use

Parent agent invokes this when:
- Context is approaching limits
- Work item has approved plan ready for implementation
- Delegation preferred over inline execution

## Process

1. **Receive** work_id and plan_path from parent
2. **Read** the skill definition: `.claude/skills/implementation-cycle/SKILL.md`
3. **Execute** all phases per skill structure:
   - PLAN: Verify plan exists, read specs, invoke preflight-checker
   - DO: Write tests first, implement per plan, invoke design-review-validation
   - CHECK: Run tests, verify deliverables, demo feature
   - DONE: Capture WHY, update docs
   - CHAIN: Close work item, identify next work
4. **Return** structured summary to parent

## Governance Gates (MUST)

Before proceeding past each phase, you MUST:

| Phase Exit | Gate | Action |
|------------|------|--------|
| PLAN → DO | preflight-checker | `Task(subagent_type='preflight-checker', prompt='Check plan for {work_id}')` |
| DO → CHECK | design-review-validation | `Skill(skill='design-review-validation')` |
| CHECK → DONE | deliverables-verified | Read WORK.md, verify ALL deliverables complete |

**You MUST report gate results in your output.** If any gate fails, return BLOCKED status.

## Output Format

Return this exact structure to parent:

```
Cycle Result: PASS | FAIL | BLOCKED

## Summary
- Work ID: {work_id}
- Phases completed: {list}
- Duration: {estimate}

## Gates Honored
- preflight-checker: PASS | FAIL | SKIPPED
- design-review-validation: PASS | FAIL | SKIPPED
- deliverables-verified: X/Y complete

## Outcome
{Brief description of what was accomplished}

## Artifacts
- {List of files created/modified}

## Next Action
{Suggested routing or "await_operator"}

## Blockers (if FAIL/BLOCKED)
- {List specific blockers}
```

## Example

**Input:**
```
Execute implementation cycle for WORK-081.
Plan: docs/work/active/WORK-081/plans/PLAN.md
Work: docs/work/active/WORK-081/WORK.md
```

**Output:**
```
Cycle Result: PASS

## Summary
- Work ID: WORK-081
- Phases completed: PLAN, DO, CHECK, DONE, CHAIN
- Duration: ~45 min

## Gates Honored
- preflight-checker: PASS
- design-review-validation: PASS
- deliverables-verified: 6/6 complete

## Outcome
Implemented Cycle-as-Subagent delegation pattern. Created 3 agent files,
updated README, all tests passing.

## Artifacts
- .claude/agents/implementation-cycle-agent.md (created)
- .claude/agents/investigation-cycle-agent.md (created)
- .claude/agents/close-work-cycle-agent.md (created)
- .claude/agents/README.md (updated)

## Next Action
Work closed. Queue head: WORK-067 (investigation). Suggest: investigation-cycle

## Blockers
None
```

## Tips

- Read the skill file first - it's the source of truth for phase structure
- Invoke governance gates at phase boundaries, not at the end
- If a gate fails, stop and return BLOCKED immediately
- Report artifacts accurately - parent uses this for verification
- Don't checkpoint - that's parent responsibility

## Edge Cases

| Case | Handling |
|------|----------|
| Plan not found | Return FAIL with blocker: "Plan file not found at {path}" |
| Tests fail in CHECK | Return FAIL with failing test names |
| Gate agent unavailable | Return BLOCKED with gate name |
| Context limit approaching | Return BLOCKED with partial progress in Outcome |

## Related

- **implementation-cycle skill**: Source of truth for phase structure
- **preflight-checker agent**: PLAN phase gate
- **validation-agent**: Optional CHECK phase assistance
- **test-runner agent**: Optional test execution
