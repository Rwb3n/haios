# generated: 2026-02-09
# Queue Intake Ceremony Skill

Logs creation of new work items at the `backlog` queue position.

## Overview

This is a **Ceremony Skill** that wraps work-creation-cycle with queue ceremony event logging. It does not replace work-creation-cycle; it adds audit trail on top.

## Usage

```
Skill(skill="queue-intake")
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with input/output contracts |
| `README.md` | This documentation |

## Related

- CH-010: Queue Ceremonies specification
- queue_ceremonies.py: Python module with ceremony execution logic
- work-creation-cycle: Creates the actual work item
- queue-unpark, queue-prioritize, queue-commit: Sibling ceremony skills
