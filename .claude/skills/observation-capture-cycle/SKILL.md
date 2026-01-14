---
name: observation-capture-cycle
description: 3 questions for genuine reflection before work closure. Hard gate on
  non-empty.
recipes:
- scaffold-observations
generated: 2026-01-10
last_updated: '2026-01-12T01:28:41'
---
# Observation Capture

Capture observations before closing work. Invoked by `/close` command.

## Questions

Answer these 3 questions about the work just completed:

1. **What surprised you?**
   - Unexpected behaviors, bugs encountered
   - Things easier or harder than anticipated
   - Assumptions that proved wrong

2. **What's missing?**
   - Gaps in tooling, docs, or infrastructure noticed
   - Features that would have helped
   - AgentUX friction points

3. **What should we remember?**
   - Learnings for future work
   - Patterns worth reusing
   - Warnings for similar tasks

## Gate

**MUST** provide:
- At least one substantive answer, OR
- Explicit "None observed" with brief justification

Empty responses BLOCK closure.

## Output

Write answers to `docs/work/active/{id}/observations.md` using simplified template.
