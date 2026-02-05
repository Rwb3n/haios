---
template: implementation_phase
phase: PLAN
maps_to_state: PLAN
version: '1.0'
input_contract:
- field: work_context
  type: markdown
  required: true
  description: Work item exists with approved plan
- field: plan_exists
  type: boolean
  required: true
  description: Plan file present in plans/ directory
output_contract:
- field: specs_verified
  type: boolean
  required: true
  description: Referenced specifications read and verified
- field: tests_defined
  type: boolean
  required: true
  description: Tests First section has concrete tests
- field: design_documented
  type: boolean
  required: true
  description: Detailed Design section complete
generated: '2026-02-04'
last_updated: '2026-02-04T23:56:30'
---
# PLAN Phase

Verify plan exists and is ready for implementation.

## Input Contract

- [ ] Work item exists with approved plan
- [ ] Plan file present in plans/ directory

## Governed Activities

*From activity_matrix.yaml for PLAN state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read plan, specs, requirements |
| file-search | allow | Find related files |
| memory-search | allow | Query prior implementations |
| file-write | allow | Update plan if needed |
| shell-execute | warn | Prefer read-only commands |

## Output Contract

- [ ] Referenced specifications read and verified
- [ ] Tests First section has concrete tests
- [ ] Detailed Design section complete

## Template

```markdown
## PLAN Phase Verification

**Plan file:** [path]
**Status:** [draft|approved]

### Spec Verification

| Spec | Read | Matches Plan |
|------|------|--------------|
| | | |

### Tests Defined

- [ ] Test 1: [description]
- [ ] Test 2: [description]
```
