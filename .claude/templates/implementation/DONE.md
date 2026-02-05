---
template: implementation_phase
phase: DONE
maps_to_state: DONE
version: '1.0'
input_contract:
- field: check_complete
  type: boolean
  required: true
  description: CHECK phase complete
- field: dod_passed
  type: boolean
  required: true
  description: DoD criteria verified
output_contract:
- field: why_captured
  type: boolean
  required: true
  description: Learnings stored to memory
- field: plan_complete
  type: boolean
  required: true
  description: Plan status set to complete
- field: docs_updated
  type: boolean
  required: true
  description: READMEs updated
generated: '2026-02-04'
last_updated: '2026-02-04T23:57:03'
---
# DONE Phase

Complete implementation and prepare for closure.

## Input Contract

- [ ] CHECK phase complete
- [ ] DoD criteria verified

## Governed Activities

*From activity_matrix.yaml for DONE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read any file |
| file-write | allow | Update docs, status |
| file-edit | allow | Edit docs, status |
| shell-execute | warn | Prefer read-only |
| memory-store | allow | Capture learnings |
| shell-background | block | Not allowed in DONE |
| notebook-edit | block | Not allowed in DONE |

## Output Contract

- [ ] WHY captured (learnings stored to memory)
- [ ] Plan status set to complete
- [ ] READMEs updated

## Template

```markdown
## WHY Capture

**Learnings:**
- [Key insight 1]
- [Key insight 2]

**Memory refs:** [concept IDs from ingester_ingest]

## Status Updates

- [ ] Plan status: complete
- [ ] WORK.md deliverables: all checked
- [ ] README.md: updated
```
