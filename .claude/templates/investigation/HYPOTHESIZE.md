---
template: investigation_phase
phase: HYPOTHESIZE
maps_to_state: DESIGN
version: '1.1'
input_contract:
- field: explore_complete
  type: boolean
  required: true
  description: EXPLORE phase complete
- field: evidence_documented
  type: table
  required: true
  description: Evidence documented with sources
output_contract:
- field: hypotheses_table
  type: table
  required: true
  description: Hypotheses table with confidence and test method
- field: scope_defined
  type: markdown
  required: true
  description: In Scope / Out of Scope sections populated
- field: falsification_criteria
  type: markdown
  required: true
  description: Each hypothesis has clear falsification criteria
generated: '2026-02-04'
last_updated: '2026-02-04T22:28:55'
---
# HYPOTHESIZE Phase

Form hypotheses from evidence.

## Input Contract

- [ ] EXPLORE phase complete
- [ ] Evidence documented with sources

## Governed Activities

*From activity_matrix.yaml for DESIGN state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read specs and evidence |
| file-write | allow | Write hypotheses |
| file-edit | allow | Refine hypotheses |
| user-query | allow | Clarify with operator |
| memory-search | allow | Query prior patterns |

## Output Contract

- [ ] Hypotheses table with confidence and test method
- [ ] Scope defined (In Scope / Out of Scope)
- [ ] Each hypothesis has clear falsification criteria

## Template

```markdown
## Hypotheses

| # | Hypothesis | Confidence | Test Method |
|---|------------|------------|-------------|
| H1 | | High/Med/Low | |
| H2 | | High/Med/Low | |

## Scope

### In Scope
-

### Out of Scope
-
```
