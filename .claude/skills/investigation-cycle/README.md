# generated: 2025-12-22
# System Auto: last updated on: 2026-02-01T16:05:36
# Investigation Cycle Skill

Structured workflow for research and discovery tasks in HAIOS.

## Overview

The investigation-cycle skill guides agents through the **EXPLORE-HYPOTHESIZE-VALIDATE-CONCLUDE** workflow when conducting research, analyzing problems, or investigating system behavior.

## Usage

```
Skill(skill="investigation-cycle")
```

Or via the implement command with an investigation backlog ID:
```
/implement INV-XXX
```

## The Four Phases (EXPLORE-FIRST Pattern)

### 1. EXPLORE
- Gather evidence through unrestricted exploration
- Query memory for prior related work
- Document sources and findings freely

### 2. HYPOTHESIZE
- Form hypotheses FROM gathered evidence
- Each hypothesis must cite supporting evidence
- Define test method for each hypothesis

### 3. VALIDATE
- Test each hypothesis against evidence
- Render verdict: Confirmed / Refuted / Inconclusive
- Cite specific evidence for each verdict

### 4. CONCLUDE
- Synthesize findings
- Spawn follow-up work items (ADRs, plans, new investigations)
- Store learnings to memory
- Close the investigation

## Related Files

- `SKILL.md` - Full skill definition with exit criteria
- `.claude/templates/investigation/` - Fractured phase templates (preferred)
- `.claude/templates/investigation.md` - Monolithic template (deprecated)
- `.claude/commands/new-investigation.md` - Creation command

## Parallel Structure

| Investigation | Implementation |
|---------------|----------------|
| EXPLORE + HYPOTHESIZE | PLAN |
| VALIDATE | CHECK |
| CONCLUDE | DONE |

## History

- **Created:** Session 98 (2025-12-22, E2-111)
- **Updated:** Session 272 (2026-02-01, WORK-061) - EXPLORE-FIRST pattern
