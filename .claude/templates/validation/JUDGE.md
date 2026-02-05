---
template: validation_phase
phase: JUDGE
maps_to_state: CHECK
version: '1.0'
input_contract:
- field: verify_complete
  type: boolean
  required: true
  description: VERIFY phase complete with evidence gathered
- field: evidence_exists
  type: table
  required: true
  description: Evidence table populated from VERIFY phase
output_contract:
- field: criteria_evaluated
  type: table
  required: true
  description: Each criterion evaluated with pass/fail verdict
- field: verdict_formed
  type: string
  required: true
  description: Overall verdict (PASS/FAIL/PARTIAL)
- field: gaps_identified
  type: list
  required: false
  description: Gaps or issues found during evaluation
generated: '2026-02-05'
last_updated: '2026-02-05T20:26:10'
---
# JUDGE Phase

Evaluate evidence against criteria to form a verdict.

## Input Contract

- [ ] VERIFY phase complete with evidence gathered
- [ ] Evidence table populated

## Governed Activities

*From activity_matrix.yaml for CHECK state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read evidence and specs |
| shell-execute | allow | Run additional verification |
| memory-search | allow | Check for known issues |
| file-write | warn | Verdicts only |

## Output Contract

- [ ] Each criterion evaluated with pass/fail verdict
- [ ] Overall verdict formed (PASS/FAIL/PARTIAL)
- [ ] Gaps or issues identified (if any)

## Template

```markdown
## Criteria Evaluation

| Criterion | Evidence | Verdict | Notes |
|-----------|----------|---------|-------|
| | | PASS/FAIL | |

## Overall Verdict

**Verdict:** PASS / FAIL / PARTIAL
**Confidence:** High / Medium / Low
**Rationale:** [Why this verdict]

## Gaps Identified

- [Gap or issue found]
```
