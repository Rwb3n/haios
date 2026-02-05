---
template: implementation_phase
phase: CHECK
maps_to_state: CHECK
version: '1.0'
input_contract:
- field: do_complete
  type: boolean
  required: true
  description: DO phase complete
- field: tests_exist
  type: boolean
  required: true
  description: Tests written during DO
output_contract:
- field: tests_pass
  type: boolean
  required: true
  description: All tests pass
- field: deliverables_verified
  type: boolean
  required: true
  description: All WORK.md deliverables complete
- field: ground_truth_verified
  type: boolean
  required: true
  description: Ground Truth Verification complete
generated: '2026-02-04'
last_updated: '2026-02-04T23:56:51'
---
# CHECK Phase

Verify implementation meets quality bar.

## Input Contract

- [ ] DO phase complete
- [ ] Tests written during DO phase

## Governed Activities

*From activity_matrix.yaml for CHECK state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read any file |
| shell-execute | allow | Run tests, commands |
| file-write | warn | Writes should be verdict only |
| file-edit | warn | Edits should be verdict only |
| web-fetch | allow | Check docs if needed |
| memory-search | allow | Query for verification |

## Output Contract

- [ ] All tests pass
- [ ] All WORK.md deliverables verified complete
- [ ] Ground Truth Verification complete

## Template

```markdown
## Test Results

```bash
pytest tests/test_*.py -v
```

**Result:** [PASS/FAIL]

## Deliverables Check

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| | | |

## Ground Truth Verification

| File | Expected | Verified |
|------|----------|----------|
| | | |
```
