---
name: observation-capture-cycle
description: 4 questions for genuine reflection before work closure. Hard gate on
  non-empty.
recipes:
- scaffold-observations
generated: 2026-01-10
last_updated: '2026-01-25T21:53:12'
---
# Observation Capture

Capture observations before closing work. Invoked by `/close` command.

## Questions

Answer these 4 questions about the work just completed:

1. **What surprised you?**
   - Unexpected behaviors, bugs encountered
   - Things easier or harder than anticipated
   - Assumptions that proved wrong
   - Principles revealed through the work
   - Operator insights that shifted understanding

2. **What's missing?**
   - Gaps in tooling, docs, or infrastructure
   - Features that would have helped
   - AgentUX friction points
   - Schema or architectural concepts not yet codified
   - Patterns that should exist but don't

3. **What should we remember?**
   - Learnings for future work
   - Patterns worth reusing or naming
   - Warnings for similar tasks
   - Decisions that should become ADRs
   - Principles worth adding to L3/L4

4. **What drift did you notice?**
   - Reality vs documented behavior
   - Code vs spec misalignment
   - Principles violated or bent
   - Patterns that have evolved past their docs

## Gate

**MUST** provide:
- At least one substantive answer, OR
- Explicit "None observed" with brief justification

Empty responses BLOCK closure.

## Output

### Step 1: Scaffold the file

```bash
just scaffold-observations {id}
```

### Step 2: Write FULL answers (MUST - Session 240 Learning)

**CRITICAL:** Copy your FULL answers to the file, not compressed summaries.

| WRONG | RIGHT |
|-------|-------|
| "Scope narrower than expected" | "Scope was narrower than expected. The investigation (WORK-013) predicted 12 files. Actual: 11 files (4 Python + 6 skills + 1 command). work_item.py was optional because it's untracked and portal_manager.py is the active code path." |
| Bullet point | Full paragraph with WHY |

**Include for each observation:**
- What happened (the fact)
- Why it matters (the implication)
- Specific references (file names, line numbers, work IDs)

**Rationale:** Observations without WHY get lost. Future sessions can't act on "scope narrower" without knowing which files and why.

### Step 3: Store to memory

For observations worth preserving long-term, store via ingester:

```
ingester_ingest(
  content="<full observation with context>",
  source_path="observation:{work_id}",
  content_type_hint="doxa"
)
```

Add returned concept IDs to the work item's `memory_refs` field.
