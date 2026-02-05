---
template: triage_phase
phase: COMMIT
maps_to_state: DONE
version: '1.0'
input_contract:
- field: rank_complete
  type: boolean
  required: true
  description: RANK phase complete with ordered list
- field: ranked_list
  type: table
  required: true
  description: Items in priority order
output_contract:
- field: committed_items
  type: table
  required: true
  description: Items selected for action with queue assignments
- field: deferred_items
  type: table
  required: false
  description: Items explicitly deferred with reason
generated: '2026-02-05'
last_updated: '2026-02-05T20:27:08'
---
# COMMIT Phase

Select items for action and assign to queues.

## Input Contract

- [ ] RANK phase complete with ordered list
- [ ] Items in priority order

## Governed Activities

*From activity_matrix.yaml for DONE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read ranked list |
| file-write | allow | Update queue assignments |
| memory-store | allow | Store triage decisions |
| skill-invoke | allow | Create work items |

## Output Contract

- [ ] Items selected for action with queue assignments
- [ ] Deferred items documented with reason (if any)

## Template

```markdown
## Committed Items

| ID | Title | Queue | Action |
|----|-------|-------|--------|
| | | default/lifecycles/... | ready/active |

## Deferred Items

| ID | Title | Reason |
|----|-------|--------|
| | | |
```
