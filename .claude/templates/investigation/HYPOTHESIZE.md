---
template: investigation_phase
phase: HYPOTHESIZE
maps_to_state: DESIGN
version: '1.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:25:31'
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
