---
template: investigation_phase
phase: EXPLORE
maps_to_state: EXPLORE
version: '1.1'
input_contract:
- field: work_context
  type: markdown
  required: true
  description: Work item Context section populated
- field: objective
  type: markdown
  required: true
  description: Work item Objective defined
output_contract:
- field: evidence_table
  type: table
  required: true
  description: Evidence Collection table with file:line sources
- field: memory_evidence
  type: table
  required: true
  description: Memory Evidence table with concept IDs
- field: prior_work_query
  type: markdown
  required: true
  description: Prior Work Query completed
generated: '2026-02-04'
last_updated: '2026-02-04T22:28:42'
---
# EXPLORE Phase

Evidence gathering before hypothesis formation.

## Input Contract

- [ ] Work item exists with Context and Objective defined
- [ ] Prior Work Query section ready to populate

## Governed Activities

*From activity_matrix.yaml for EXPLORE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read any file |
| file-search | allow | Glob patterns |
| content-search | allow | Grep patterns |
| web-fetch | allow | External docs |
| web-search | allow | Web queries |
| memory-search | allow | Query prior work |
| file-write | warn | Prefer notes over artifacts |

## Output Contract

- [ ] Evidence Collection table populated with file:line sources
- [ ] Memory Evidence table populated with concept IDs
- [ ] Prior Work Query completed

## Template

```markdown
## Evidence Collection

| Finding | Source (file:line) | Notes |
|---------|-------------------|-------|
| | | |

## Memory Evidence

| Concept ID | Summary | Relevance |
|------------|---------|-----------|
| | | |
```
