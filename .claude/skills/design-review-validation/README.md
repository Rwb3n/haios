# generated: 2025-12-25
# System Auto: last updated on: 2026-01-03T14:49:49
# Design Review Validation Skill (Bridge)

Validates implementation alignment with Detailed Design during DO phase.

## Overview

This is a **Validation Skill** (bridge) that acts as a quality gate between implementation and verification phases.

## Phases

| Phase | Purpose |
|-------|---------|
| COMPARE | Read design and implementation |
| VERIFY | Check alignment on key points |
| APPROVE | Confirm or document deviations |

## Usage

**Manual (standalone):**
```
Skill(skill="design-review-validation")
```

**From implementation-cycle (WORK-178):** Required exit gate — invoked as sonnet subagent:
```
Task(subagent_type='design-review-validation-agent', model='sonnet', prompt='...')
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with phase contracts |
| `README.md` | This documentation |

## Comparison Points

- File paths match plan
- Function signatures match (names, params, returns)
- Logic flow matches design
- Key design decisions followed

## Related

- plan-validation-cycle: Pre-DO validation (plan completeness)
- close-work-cycle: Post-DO validation (DoD check)
- dod-validation-cycle: Parallel pattern for DoD
