---
template: design_phase
phase: CRITIQUE
maps_to_state: CHECK
version: '1.0'
input_contract:
- field: specify_complete
  type: boolean
  required: true
  description: SPECIFY phase complete
- field: specification_exists
  type: markdown
  required: true
  description: Draft specification written
output_contract:
- field: assumptions_surfaced
  type: table
  required: true
  description: Assumptions table populated
- field: risks_identified
  type: markdown
  required: true
  description: Risks and mitigations documented
- field: critique_verdict
  type: string
  required: true
  description: PROCEED or REVISE
generated: '2026-02-04'
last_updated: '2026-02-04T23:02:29'
---
# CRITIQUE Phase

Validate assumptions and surface risks in specification.

## Input Contract

- [ ] SPECIFY phase complete
- [ ] Draft specification written

## Governed Activities

*From activity_matrix.yaml for CHECK state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read specification |
| shell-execute | allow | Run verification |
| memory-search | allow | Query for patterns |
| file-write | warn | Verdicts only |

## Output Contract

- [ ] Assumptions table populated
- [ ] Risks and mitigations documented
- [ ] Critique verdict: PROCEED or REVISE

## Template

```markdown
## Assumptions

| Assumption | Confidence | Mitigation |
|------------|------------|------------|
| | High/Med/Low | |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| | | |

## Verdict

**Decision:** [PROCEED / REVISE]
**Rationale:** [Why this verdict]
```
