# generated: 2026-02-09
# Queue Prioritize Ceremony Skill

Moves work items from `backlog` to `ready` with rationale. Batch capable.

## Overview

This is a **Ceremony Skill** that governs the selection of backlog items for upcoming work. Requires rationale for audit trail. Supports batch operations.

## Usage

```
Skill(skill="queue-prioritize")
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with input/output contracts |
| `README.md` | This documentation |

## Related

- CH-010: Queue Ceremonies specification
- queue_ceremonies.py: Python module with ceremony execution logic
- queue-unpark, queue-intake, queue-commit: Sibling ceremony skills
