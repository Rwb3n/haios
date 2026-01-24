# generated: 2025-12-25
# System Auto: last updated on: 2026-01-24T21:21:02
# Plan Validation Cycle Skill (Bridge)

Validates implementation plan readiness before entering DO phase.

## Overview

This is a **Validation Skill** (bridge) that acts as a quality gate between plan-authoring-cycle and implementation-cycle.

## Phases

| Phase | Purpose |
|-------|---------|
| CHECK | Verify required sections exist |
| SPEC_ALIGN | Verify plan matches referenced specs |
| VALIDATE | Check section content quality |
| APPROVE | Confirm plan is ready |

> **Note (Session 233):** L4_ALIGN removed (was non-functional). SPEC_ALIGN provides requirements traceability via plan's References section.

## Usage

**Manual:**
```
Skill(skill="plan-validation-cycle")
```

**From implementation-cycle:** Optional quality gate before DO phase.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with phase contracts |
| `README.md` | This documentation |

## Quality Checks

- Goal: Single sentence, measurable
- Effort: Real numbers from file analysis
- Tests: Concrete assertions
- Design: File paths and code snippets
- Steps: Actionable checklist items

## Requirements Traceability

SPEC_ALIGN phase provides requirements traceability by:
1. Reading plan's `## References` section
2. Reading each referenced specification
3. Comparing plan's Detailed Design against spec interface
4. Blocking on mismatch (prevents "assume over verify" anti-pattern)

**L4 Requirements:** Now in `L4/` directory (Session 233 consolidation):
- `L4/functional_requirements.md` - Module function specs (for module work)
- `L4/technical_requirements.md` - How-to-enable patterns

## Related

- plan-authoring-cycle: Populates plan sections
- implementation-cycle: Uses validated plans
- close-work-cycle: Parallel validation pattern
