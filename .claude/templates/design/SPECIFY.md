---
template: design_phase
phase: SPECIFY
maps_to_state: DESIGN
version: '1.0'
input_contract:
- field: explore_complete
  type: boolean
  required: true
  description: EXPLORE phase complete
- field: requirements_documented
  type: table
  required: true
  description: Requirements gathered with sources
output_contract:
- field: specification_draft
  type: markdown
  required: true
  description: Specification sections populated
- field: interface_defined
  type: markdown
  required: true
  description: Inputs/outputs defined
- field: success_criteria
  type: list
  required: true
  description: Measurable success criteria
generated: '2026-02-04'
last_updated: '2026-02-04T23:02:20'
---
# SPECIFY Phase

Write specification from gathered requirements.

## Input Contract

- [ ] EXPLORE phase complete
- [ ] Requirements documented with sources

## Governed Activities

*From activity_matrix.yaml for DESIGN state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read requirements |
| file-write | allow | Write specification |
| file-edit | allow | Refine specification |
| user-query | allow | Clarify with operator |
| memory-search | allow | Query prior patterns |

## Output Contract

- [ ] Specification draft sections populated
- [ ] Interface defined (inputs/outputs)
- [ ] Measurable success criteria documented

## Template

```markdown
## Specification

### Purpose

[One paragraph describing what this spec achieves]

### Interface

**Inputs:**
-

**Outputs:**
-

### Success Criteria

- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
```
