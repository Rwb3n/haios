---
template: implementation_phase
phase: DO
maps_to_state: DO
version: '1.0'
input_contract:
- field: plan_validated
  type: boolean
  required: true
  description: PLAN phase complete
- field: file_manifest
  type: table
  required: true
  description: Files to modify listed
output_contract:
- field: tests_written
  type: boolean
  required: true
  description: Failing tests written first
- field: implementation_done
  type: boolean
  required: true
  description: All planned changes made
- field: design_matched
  type: boolean
  required: true
  description: Implementation matches Detailed Design
generated: '2026-02-04'
last_updated: '2026-02-04T23:56:41'
---
# DO Phase

Implement the design from the plan.

## Input Contract

- [ ] PLAN phase complete
- [ ] File manifest created (list of files to modify)

## Governed Activities

*From activity_matrix.yaml for DO state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read any file |
| file-write | allow | Create/modify files |
| file-edit | allow | Edit existing files |
| shell-execute | allow | Run commands |
| web-fetch | block | DO is black-box, no research |
| memory-search | block | Query memory during PLAN |
| user-query | block | Spec should be complete |

## Output Contract

- [ ] Failing tests written first (TDD)
- [ ] All planned changes made
- [ ] Implementation matches Detailed Design

## Template

```markdown
## File Manifest

| File | Action | Status |
|------|--------|--------|
| | | |

## TDD Progress

- [ ] Test written (RED)
- [ ] Code written (GREEN)
- [ ] Refactored (REFACTOR)
```
