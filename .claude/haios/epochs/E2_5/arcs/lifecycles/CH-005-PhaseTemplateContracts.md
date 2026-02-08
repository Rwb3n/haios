# generated: 2026-02-03
# System Auto: last updated on: 2026-02-05T22:33:46
# Chapter: Phase Template Contracts

## Definition

**Chapter ID:** CH-005
**Arc:** lifecycles
**Status:** Complete
**Completed:** 2026-02-04 (Session 308)
**Implementation Type:** REFACTOR (partial - contracts exist, validation doesn't)
**Depends:** CH-001
**Work Items:** WORK-088

---

## Current State (Verified)

**Source:** `.claude/templates/investigation/EXPLORE.md`

Investigation phase templates already have contracts:

```yaml
# From EXPLORE.md frontmatter
---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.0'
---
```

```markdown
# From EXPLORE.md body
## Input Contract
- [ ] Work item exists with Context and Objective defined
- [ ] Prior Work Query section ready to populate

## Output Contract
- [ ] Evidence Collection table populated with file:line sources
- [ ] Memory Evidence table populated with concept IDs
- [ ] Prior Work Query completed
```

**What exists:**
- Investigation templates fractured with Input/Output Contract sections
- YAML frontmatter with `phase`, `maps_to_state`, `version`
- Human-readable checklist format for contracts
- Governed Activities table mapping to activity_matrix.yaml

**What doesn't exist:**
- Machine-readable contracts in frontmatter (YAML schema)
- Governance validation of contract satisfaction
- Contracts for non-investigation templates (implementation, design, etc.)

---

## Problem

Contracts exist in investigation templates but are human-readable only (markdown checklists). No programmatic validation of input/output contracts by governance.

---

## Agent Need

> "I need each phase template to have explicit input and output contracts so I know exactly what I need to have before starting a phase and what I must produce to complete it."

---

## Requirements

### R1: Input/Output Contracts (REQ-TEMPLATE-001)

Every phase template must include:

```markdown
## Input Contract
- [required field 1]: description
- [required field 2]: description

## Output Contract
- [produced field 1]: description
- [produced field 2]: description
```

### R2: Contract Validation

Governance validates:
- Input contract satisfied before phase entry
- Output contract satisfied before phase exit

### R3: Contract Schema

Contracts should be machine-readable (YAML in template frontmatter):

```yaml
---
phase: SPECIFY
lifecycle: design
input_contract:
  - field: requirements
    type: markdown
    required: true
  - field: exploration_notes
    type: markdown
    required: false
output_contract:
  - field: specification
    type: markdown
    required: true
  - field: open_decisions
    type: list
    required: true
---
```

---

## Interface

### Template Structure

Each phase template follows pattern:

```markdown
---
phase: {PHASE_NAME}
lifecycle: {LIFECYCLE}
input_contract: [...]
output_contract: [...]
---

# {Phase Name} Phase

## Input Contract

{Human-readable input requirements}

## Phase Work

{What to do in this phase}

## Output Contract

{Human-readable output requirements}

## Checklist

- [ ] Input contract items present
- [ ] Phase work completed
- [ ] Output contract items produced
```

### Governance Integration

```python
# Phase entry validation
def can_enter_phase(work_id: str, phase: str) -> GateResult:
    template = load_template(phase)
    work = work_engine.get_work(work_id)
    for item in template.input_contract:
        if item.required and not has_field(work, item.field):
            return GateResult(blocked=True, reason=f"Missing: {item.field}")
    return GateResult(allowed=True)
```

---

## Success Criteria

- [ ] All phase templates have input_contract in frontmatter
- [ ] All phase templates have output_contract in frontmatter
- [ ] Governance validates input contract on phase entry
- [ ] Governance validates output contract on phase exit
- [ ] Contracts are both machine-readable (YAML) and human-readable (markdown)
- [ ] Unit tests for contract validation
- [ ] Integration test: missing input → blocked entry

---

## Non-Goals

- Fracturing templates into smaller files (see CH-006)
- Defining all contract fields (that's per-lifecycle work)
- Runtime type checking of contract values (schema validation only)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-001)
- @.claude/templates/ (existing template directory)
