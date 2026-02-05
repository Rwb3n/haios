---
template: triage_phase
phase: SCAN
maps_to_state: EXPLORE
version: '1.0'
input_contract:
- field: items_source
  type: markdown
  required: true
  description: Source of items to triage identified (queue, backlog, observations)
- field: scope_defined
  type: boolean
  required: true
  description: Triage scope and boundaries defined
output_contract:
- field: items_collected
  type: table
  required: true
  description: Items table with ID, title, and raw state
- field: item_count
  type: string
  required: true
  description: Total count of items scanned
generated: '2026-02-05'
last_updated: '2026-02-05T20:26:53'
---
# SCAN Phase

Collect and enumerate items for triage.

## Input Contract

- [ ] Source of items to triage identified
- [ ] Triage scope and boundaries defined

## Governed Activities

*From activity_matrix.yaml for EXPLORE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read work items, queues |
| file-search | allow | Find items by pattern |
| content-search | allow | Search for matching items |
| memory-search | allow | Query prior triage results |
| file-write | warn | Prefer notes over artifacts |

## Output Contract

- [ ] Items table populated with ID, title, and raw state
- [ ] Total count of items scanned

## Template

```markdown
## Items Collected

| ID | Title | Current State | Source |
|----|-------|---------------|--------|
| | | | |

**Total items scanned:** [N]
```
