---
template: investigation_phase
phase: VALIDATE
maps_to_state: CHECK
version: '1.1'
input_contract:
- field: hypothesize_complete
  type: boolean
  required: true
  description: HYPOTHESIZE phase complete
- field: hypotheses_with_tests
  type: table
  required: true
  description: Hypotheses defined with test methods
output_contract:
- field: hypothesis_verdicts
  type: table
  required: true
  description: Verdict for each hypothesis (Confirmed/Refuted/Inconclusive)
- field: key_evidence
  type: markdown
  required: true
  description: Key evidence cited with file:line or concept ID
- field: confidence_level
  type: string
  required: true
  description: Confidence level documented
generated: '2026-02-04'
last_updated: '2026-02-04T22:29:08'
---
# VALIDATE Phase

Test hypotheses against evidence.

## Input Contract

- [ ] HYPOTHESIZE phase complete
- [ ] Hypotheses defined with test methods

## Governed Activities

*From activity_matrix.yaml for CHECK state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read evidence |
| shell-execute | allow | Run verification commands |
| memory-search | allow | Query for patterns |
| file-write | warn | Verdicts only |

## Output Contract

- [ ] Verdict for each hypothesis (Confirmed/Refuted/Inconclusive)
- [ ] Key evidence cited with file:line or concept ID
- [ ] Confidence level documented

## Template

```markdown
## Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | Confirmed/Refuted/Inconclusive | | High/Med/Low |
| H2 | | | |

## Detailed Findings

### [Finding Title]

**Evidence:**
[file:line or concept ID]

**Analysis:**
[What this means]
```
