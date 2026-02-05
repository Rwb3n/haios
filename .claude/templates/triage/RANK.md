---
template: triage_phase
phase: RANK
maps_to_state: DESIGN
version: '1.0'
input_contract:
- field: assess_complete
  type: boolean
  required: true
  description: ASSESS phase complete with scores assigned
- field: items_assessed
  type: table
  required: true
  description: Items with priority, effort, and impact scores
output_contract:
- field: ranked_list
  type: table
  required: true
  description: Items in priority order with rank justification
- field: ranking_rationale
  type: markdown
  required: true
  description: Rationale for ranking decisions
generated: '2026-02-05'
last_updated: '2026-02-05T20:27:03'
---
# RANK Phase

Order items by priority using assessment scores.

## Input Contract

- [ ] ASSESS phase complete with scores assigned
- [ ] Items have priority, effort, and impact scores

## Governed Activities

*From activity_matrix.yaml for DESIGN state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read assessments |
| file-write | allow | Write ranked list |
| memory-search | allow | Prior ranking patterns |

## Output Contract

- [ ] Items in priority order with rank justification
- [ ] Ranking rationale documented

## Template

```markdown
## Ranked Items

| Rank | ID | Title | Priority | Effort | Rationale |
|------|----|-------|----------|--------|-----------|
| 1 | | | | | |
| 2 | | | | | |

## Ranking Rationale

[Explain ordering decisions, trade-offs considered]
```
