---
template: design_phase
phase: COMPLETE
maps_to_state: DONE
version: '1.0'
input_contract:
- field: critique_complete
  type: boolean
  required: true
  description: CRITIQUE phase complete
- field: verdict_proceed
  type: boolean
  required: true
  description: Critique verdict is PROCEED
output_contract:
- field: specification_finalized
  type: boolean
  required: true
  description: Status set to approved
- field: memory_stored
  type: list
  required: true
  description: Spec decisions stored via ingester_ingest
- field: handoff_ready
  type: boolean
  required: true
  description: Specification ready for implementation
generated: '2026-02-04'
last_updated: '2026-02-04T23:02:40'
---
# COMPLETE Phase

Finalize specification and prepare for handoff.

## Input Contract

- [ ] CRITIQUE phase complete
- [ ] Critique verdict is PROCEED

## Governed Activities

*From activity_matrix.yaml for DONE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read final spec |
| file-write | allow | Finalize documents |
| memory-store | allow | Ingest learnings |
| skill-invoke | allow | Spawn work items |

## Output Contract

- [ ] Specification status set to approved
- [ ] Decisions stored via `ingester_ingest`
- [ ] Specification ready for implementation handoff

## Template

```markdown
## Finalization

- [ ] Specification status: approved
- [ ] Memory stored (concept IDs): [list]
- [ ] Handoff ready: Yes/No

## Spawned Work

| ID | Title | Type |
|----|-------|------|
| | | implementation |
```
