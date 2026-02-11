---
name: epoch-review
type: ceremony
description: "Review epoch goals after arc completion to assess if adjustments needed."
category: feedback
stub: true
input_contract:
  - field: epoch_id
    type: string
    required: true
    description: "Epoch ID to review (e.g., E2.5)"
  - field: completed_arc_id
    type: string
    required: false
    description: "Arc that triggered this review"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether review completed"
  - field: goals_changed
    type: boolean
    guaranteed: on_success
    description: "Whether epoch goals were adjusted"
  - field: adjustments
    type: list
    guaranteed: on_success
    description: "List of goal adjustments made (empty if none)"
side_effects:
  - "Maybe update epoch goals"
generated: 2026-02-09
last_updated: "2026-02-09"
---
# Epoch Review Ceremony

Review an epoch's goals and progress after arc completion. Determines if the epoch needs goal adjustment based on completed arc outcomes.

## When to Use

- After completing an arc within an epoch
- When observations suggest epoch goal drift
- Before planning new arcs in the epoch

**Invocation:** `Skill(skill="epoch-review")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `epoch_id` | MUST | Epoch ID to review (e.g., E2.5) |
| `completed_arc_id` | SHOULD | Arc that triggered this review |

---

## Ceremony Steps

1. Read EPOCH.md and extract goals and success criteria
2. List completed and remaining arcs
3. Assess if completed arc changed understanding of epoch goals
4. If goal change needed, propose adjustments to operator
5. Log EpochReview ceremony event
6. Report review outcome to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether review completed |
| `goals_changed` | On success | Whether epoch goals were adjusted |
| `adjustments` | On success | List of goal adjustments made (empty if none) |

---

## Side Effects

- Maybe update epoch goals (success criteria, arc list)

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- L4/functional_requirements.md: Feedback ceremonies definition
- CH-011: CeremonyContracts
