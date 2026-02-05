---
template: validation_phase
phase: REPORT
maps_to_state: CHECK
version: '1.0'
input_contract:
- field: judge_complete
  type: boolean
  required: true
  description: JUDGE phase complete with verdict formed
- field: verdict_exists
  type: string
  required: true
  description: Overall verdict (PASS/FAIL/PARTIAL) determined
output_contract:
- field: report_written
  type: markdown
  required: true
  description: Validation report with findings summary
- field: recommendations_made
  type: list
  required: false
  description: Recommendations for remediation (if FAIL/PARTIAL)
generated: '2026-02-05'
last_updated: '2026-02-05T20:26:16'
---
# REPORT Phase

Document findings, verdict, and recommendations.

## Input Contract

- [ ] JUDGE phase complete with verdict formed
- [ ] Overall verdict determined

## Governed Activities

*From activity_matrix.yaml for CHECK state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read verdicts |
| file-write | allow | Write final report |
| memory-store | allow | Store validation learnings |

## Output Contract

- [ ] Validation report written with findings summary
- [ ] Recommendations made (if FAIL/PARTIAL)

## Template

```markdown
## Validation Report

**Work Item:** [ID]
**Verdict:** PASS / FAIL / PARTIAL
**Date:** [date]

## Findings Summary

[One paragraph summarizing what was validated and the outcome]

## Recommendations

- [Action item if FAIL/PARTIAL, or "None - validation passed"]
```
