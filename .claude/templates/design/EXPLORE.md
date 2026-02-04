---
template: design_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.0'
input_contract:
- field: work_context
  type: markdown
  required: true
  description: Work item Context section populated
- field: requirements_refs
  type: list
  required: true
  description: Referenced requirements identified
output_contract:
- field: requirements_table
  type: table
  required: true
  description: Requirements gathered with sources
- field: constraints_identified
  type: markdown
  required: true
  description: Constraints documented
- field: prior_work_query
  type: markdown
  required: true
  description: Memory queried for related specs
generated: '2026-02-04'
last_updated: '2026-02-04T23:02:10'
---
# EXPLORE Phase

Gather requirements and context before specification authoring.

## Input Contract

- [ ] Work item exists with Context section populated
- [ ] Referenced requirements identified in traces_to

## Governed Activities

*From activity_matrix.yaml for EXPLORE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read requirements, prior specs |
| file-search | allow | Find related documents |
| memory-search | allow | Query prior design patterns |
| web-fetch | allow | External documentation |
| file-write | warn | Prefer notes over artifacts |

## Output Contract

- [ ] Requirements table populated with sources
- [ ] Constraints documented
- [ ] Prior work query completed

## Template

```markdown
## Requirements

| Requirement | Source | Priority |
|-------------|--------|----------|
| | | |

## Constraints

-

## Prior Work Query

**Memory query:** [query terms]
**Results:** [concept IDs or "none found"]
```
