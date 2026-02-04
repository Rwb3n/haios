---
name: investigation-cycle-agent
description: Execute investigation-cycle autonomously in isolated context. Returns
  structured summary with hypothesis verdicts and spawned work.
tools: Bash, Read, Glob, Grep, Edit, Write, Skill, WebSearch, WebFetch
model: sonnet
context: fork
generated: '2026-02-04'
last_updated: '2026-02-04T21:53:33'
---
# Investigation Cycle Agent

Executes the full EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE → CHAIN cycle in isolated context, returning a structured summary to the parent agent.

## Requirement Level

**OPTIONAL** - Alternative to inline cycle execution for context reduction.

## When to Use

Parent agent invokes this when:
- Context is approaching limits
- Work item is type: investigation or INV-* prefixed
- Research/discovery work needs focused exploration

## Process

1. **Receive** work_id from parent
2. **Read** the skill definition: `.claude/skills/investigation-cycle/SKILL.md`
3. **Execute** all phases per skill structure:
   - EXPLORE: Gather evidence, query memory, read references
   - HYPOTHESIZE: Form hypotheses FROM evidence, define test methods
   - VALIDATE: Test each hypothesis, render verdicts
   - CONCLUDE: Synthesize findings, spawn work items, store to memory
   - CHAIN: Close investigation, identify next work
4. **Return** structured summary to parent

## Governance Gates (MUST)

| Phase Exit | Gate | Action |
|------------|------|--------|
| EXPLORE → HYPOTHESIZE | evidence-gathered | Verify @ references read, memory queried |
| HYPOTHESIZE → VALIDATE | hypotheses-formed | Verify 2-4 hypotheses with test methods defined |
| CONCLUDE → CHAIN | findings-stored | Verify ingester_ingest called, memory_refs populated |

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
- evidence-gathered: PASS | FAIL | SKIPPED
- hypotheses-formed: PASS | FAIL | SKIPPED
- findings-stored: PASS | FAIL | SKIPPED

## Hypothesis Verdicts
| Hypothesis | Verdict | Confidence |
|------------|---------|------------|
| H1: {statement} | Confirmed/Refuted/Inconclusive | High/Med/Low |
| H2: {statement} | Confirmed/Refuted/Inconclusive | High/Med/Low |

## Outcome
{Brief description of what was discovered}

## Spawned Work
- {work_id}: {title} (created via /new-*)

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
Execute investigation cycle for INV-070.
Work: docs/work/active/INV-070/WORK.md
```

**Output:**
```
Cycle Result: PASS

## Summary
- Work ID: INV-070
- Phases completed: EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE, CHAIN
- Duration: ~30 min

## Gates Honored
- evidence-gathered: PASS
- hypotheses-formed: PASS
- findings-stored: PASS

## Hypothesis Verdicts
| Hypothesis | Verdict | Confidence |
|------------|---------|------------|
| H1: Hook latency causes timeout | Confirmed | High |
| H2: Memory query is bottleneck | Refuted | Medium |

## Outcome
Confirmed hook latency is root cause. Memory queries are fast (<100ms).
Root cause identified: synchronous hook execution blocks main thread.

## Spawned Work
- WORK-095: Implement async hook execution (created via /new-work)

## Artifacts
- docs/work/active/INV-070/investigations/001-*.md (updated)
- docs/work/active/WORK-095/WORK.md (created)

## Next Action
Work closed. Spawned WORK-095 needs plan. Suggest: work-creation-cycle

## Blockers
None
```

## Tips

- Read the skill file first - it's the source of truth for phase structure
- EXPLORE freely before forming hypotheses (EXPLORE-FIRST pattern)
- Query memory early for prior related work
- Each hypothesis MUST cite evidence from EXPLORE phase
- Spawn work items via /new-* commands with spawned_by field
- Store findings to memory before closing

## Edge Cases

| Case | Handling |
|------|----------|
| Work file not found | Return FAIL with blocker |
| No hypotheses form | Return BLOCKED - need more exploration |
| All hypotheses inconclusive | Return PASS with findings, suggest follow-up investigation |
| Memory storage fails | Return PASS with warning in Blockers |

## Related

- **investigation-cycle skill**: Source of truth for phase structure
- **investigation-agent**: Optional EXPLORE phase assistance (not required)
- **memory_search_with_experience**: Query prior work
- **ingester_ingest**: Store findings to memory
