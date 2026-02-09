# generated: 2026-02-09
# Queue Commit Ceremony Skill

Moves work item from `ready` to `working`, signaling active work session.

## Overview

This is a **Ceremony Skill** that governs the start of active work on a ready item. Typically invoked after survey-cycle selects an item.

## Usage

```
Skill(skill="queue-commit")
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with input/output contracts |
| `README.md` | This documentation |

## Related

- CH-010: Queue Ceremonies specification
- CH-008: Release IS close-work-cycle (no separate Release skill)
- queue_ceremonies.py: Python module with ceremony execution logic
- survey-cycle: Selects work item, may invoke Commit
- queue-unpark, queue-intake, queue-prioritize: Sibling ceremony skills
