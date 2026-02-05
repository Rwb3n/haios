---
template: triage_phase
phase: ASSESS
maps_to_state: EXPLORE
version: '1.0'
input_contract:
- field: scan_complete
  type: boolean
  required: true
  description: SCAN phase complete with items collected
- field: items_collected
  type: table
  required: true
  description: Items table from SCAN phase
output_contract:
- field: items_assessed
  type: table
  required: true
  description: Items with priority, effort, and impact scores
- field: assessment_criteria
  type: list
  required: true
  description: Criteria used for assessment documented
generated: '2026-02-05'
last_updated: '2026-02-05T20:26:58'
---
# ASSESS Phase

Evaluate each item against triage criteria.

## Input Contract

- [ ] SCAN phase complete with items collected
- [ ] Items table populated

## Governed Activities

*From activity_matrix.yaml for EXPLORE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read item details |
| file-search | allow | Check dependencies |
| memory-search | allow | Prior assessments |
| file-write | warn | Assessment notes only |

## Output Contract

- [ ] Items assessed with priority, effort, and impact scores
- [ ] Assessment criteria documented

## Template

```markdown
## Assessment Criteria

- [Criterion 1: e.g., blocks other work]
- [Criterion 2: e.g., effort level]

## Items Assessed

| ID | Title | Priority | Effort | Impact | Blocked By |
|----|-------|----------|--------|--------|------------|
| | | high/med/low | S/M/L | high/med/low | |
```
