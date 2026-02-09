# generated: 2026-02-09
# Queue Unpark/Park Ceremony Skill

Governs transitions between `parked` and `backlog` queue positions (scope decisions).

## Overview

This is a **Ceremony Skill** that manages scope-level decisions for work items. Unpark brings items into scope; Park defers them out of scope.

## Usage

```
Skill(skill="queue-unpark")
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with input/output contracts |
| `README.md` | This documentation |

## Related

- CH-010: Queue Ceremonies specification
- queue_ceremonies.py: Python module with ceremony execution logic
- queue-intake, queue-prioritize, queue-commit: Sibling ceremony skills
