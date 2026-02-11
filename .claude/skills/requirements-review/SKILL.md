---
name: requirements-review
type: ceremony
description: "Review L4 requirements after epoch completion to assess if updates needed."
category: feedback
stub: true
input_contract:
  - field: epoch_id
    type: string
    required: true
    description: "Completed epoch ID that triggers requirements review"
  - field: l4_path
    type: path
    required: false
    description: "Path to L4 requirements (auto-detected from config)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether review completed"
  - field: requirements_changed
    type: boolean
    guaranteed: on_success
    description: "Whether L4 requirements were updated"
  - field: adjustments
    type: list
    guaranteed: on_success
    description: "List of requirement adjustments made (empty if none)"
side_effects:
  - "Maybe update requirements"
generated: 2026-02-09
last_updated: "2026-02-09"
---
# Requirements Review Ceremony

Review L4 requirements after epoch completion. Determines if requirements need updating based on learnings from the completed epoch.

## When to Use

- After completing an epoch
- When significant architectural learnings emerge
- Before planning a new epoch

**Invocation:** `Skill(skill="requirements-review")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `epoch_id` | MUST | Completed epoch ID that triggers requirements review |
| `l4_path` | SHOULD | Path to L4 requirements (auto-detected from config) |

---

## Ceremony Steps

1. Read L4 functional and technical requirements
2. Load epoch summary and key learnings from memory
3. Identify requirements that may need updating based on epoch outcomes
4. If changes needed, propose requirement updates to operator
5. Log RequirementsReview ceremony event
6. Report review outcome to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether review completed |
| `requirements_changed` | On success | Whether L4 requirements were updated |
| `adjustments` | On success | List of requirement adjustments made (empty if none) |

---

## Side Effects

- Maybe update L4 requirements (functional_requirements.md, technical_requirements.md)

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- L4/functional_requirements.md: The requirements being reviewed
- L4/technical_requirements.md: The requirements being reviewed
- CH-011: CeremonyContracts
