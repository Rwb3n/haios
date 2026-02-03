# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:31:19
# Chapter: Ceremony Contracts

## Definition

**Chapter ID:** CH-011
**Arc:** ceremonies
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** None
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/skills/close-work-cycle/SKILL.md`, `.claude/skills/close-chapter-ceremony/SKILL.md`

Existing ceremony-like skills have YAML frontmatter but not formal contracts:

```yaml
# From close-work-cycle/SKILL.md
---
name: close-work-cycle
description: HAIOS Close Work Cycle for structured work item closure.
recipes:
- close-work
- update-status
---
```

**What exists:**
- Skills with `name`, `description`, `recipes` in frontmatter
- Human-readable phase documentation
- Some entry/exit criteria in markdown

**What doesn't exist:**
- `input_contract` in frontmatter (machine-readable)
- `output_contract` in frontmatter (machine-readable)
- `side_effects` in frontmatter
- Validation functions for contract enforcement
- CeremonyRunner (vs existing CycleRunner)

---

## Problem

Skills have YAML frontmatter but lack machine-readable contracts. No `input_contract`, `output_contract`, or `side_effects` fields for automated validation.

---

## Agent Need

> "I need each ceremony to have explicit input/output contracts so I know exactly what to provide and what to expect, making ceremonies predictable and testable."

---

## Requirements

### R1: Contract Structure (REQ-CEREMONY-002)

Every ceremony skill must include:

```yaml
---
name: ceremony-name
category: queue|session|closure|feedback|memory|spawn
---

## Input Contract
- field1: type, required/optional, description
- field2: type, required/optional, description

## Output Contract
- result1: type, description
- result2: type, description

## Side Effects
- effect1: description
- effect2: description
```

### R2: Contract Schema

Machine-readable contract in frontmatter:

```yaml
---
name: close-work
category: closure
input_contract:
  - field: work_id
    type: string
    required: true
    pattern: "WORK-\\d{3}"
  - field: completion_evidence
    type: list
    required: true
output_contract:
  - field: closed_work_id
    type: string
  - field: archived_path
    type: path
side_effects:
  - "Updates WORK.md status to complete"
  - "Logs ClosureEvent to governance-events.jsonl"
  - "Triggers memory commit"
---
```

### R3: Contract Validation

Governance validates contracts:
- Input contract satisfied before ceremony starts
- Output contract satisfied before ceremony completes
- Side effects logged

---

## Interface

### Ceremony Skill Template

```markdown
---
name: {ceremony-name}
category: {category}
input_contract: [...]
output_contract: [...]
side_effects: [...]
---

# {Ceremony Name} Ceremony

## Purpose
{Why this ceremony exists}

## Input Contract
{Human-readable input requirements}

## Ceremony Steps
1. {Step 1}
2. {Step 2}
...

## Output Contract
{Human-readable output guarantees}

## Side Effects
{What state changes occur}
```

### Validation Functions

```python
def validate_ceremony_input(ceremony: str, inputs: Dict) -> ValidationResult:
    """Check inputs satisfy ceremony's input contract."""

def validate_ceremony_output(ceremony: str, outputs: Dict) -> ValidationResult:
    """Check outputs satisfy ceremony's output contract."""
```

---

## Success Criteria

- [ ] Contract schema defined (YAML structure)
- [ ] All 19 ceremonies have input_contract in frontmatter
- [ ] All 19 ceremonies have output_contract in frontmatter
- [ ] All 19 ceremonies have side_effects documented
- [ ] Validation functions implemented
- [ ] Governance blocks ceremony start if input contract fails
- [ ] Unit tests for contract validation

---

## Non-Goals

- Implementing all ceremonies (other chapters handle specific categories)
- Runtime type checking (schema validation only)
- Contract versioning (future work)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-002)
- @.claude/skills/ (existing ceremony skills to update)
