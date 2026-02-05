---
template: validation_phase
phase: VERIFY
maps_to_state: CHECK
version: '1.0'
input_contract:
- field: artifact_exists
  type: boolean
  required: true
  description: Artifact to validate exists and is accessible
- field: spec_exists
  type: boolean
  required: true
  description: Specification or acceptance criteria available
output_contract:
- field: evidence_gathered
  type: table
  required: true
  description: Evidence table with source references
- field: artifact_inspected
  type: boolean
  required: true
  description: Artifact has been run/exercised/inspected
- field: criteria_identified
  type: list
  required: true
  description: List of criteria to evaluate against
generated: '2026-02-05'
last_updated: '2026-02-05T20:26:03'
---
# VERIFY Phase

Gather evidence by running tests, inspecting artifacts, and collecting data.

## Input Contract

- [ ] Artifact to validate exists and is accessible
- [ ] Specification or acceptance criteria available

## Governed Activities

*From activity_matrix.yaml for CHECK state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read artifacts and specs |
| shell-execute | allow | Run tests and verification commands |
| memory-search | allow | Query for known patterns |
| file-write | warn | Evidence notes only |

## Output Contract

- [ ] Evidence table populated with source references
- [ ] Artifact has been run/exercised/inspected
- [ ] List of criteria to evaluate against identified

## Template

```markdown
## Evidence Collection

| Evidence | Source | Method |
|----------|--------|--------|
| | | |

## Artifact Inspection

**Artifact:** [path or identifier]
**Method:** [how inspected - test run, manual review, demo]
**Result:** [raw observations]

## Criteria Checklist

- [ ] [Criterion from spec or acceptance criteria]
```
