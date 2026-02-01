---
template: investigation_phase
phase: VALIDATE
maps_to_state: CHECK
version: '1.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:25:43'
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
