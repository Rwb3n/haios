---
name: arc-review
description: "Review arc direction after chapter completion to assess if adjustments needed."
category: feedback
stub: true
input_contract:
  - field: arc_id
    type: string
    required: true
    description: "Arc ID to review (e.g., ceremonies)"
  - field: completed_chapter_id
    type: string
    required: false
    description: "Chapter that triggered this review"
    pattern: "CH-\\d{3}"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether review completed"
  - field: direction_changed
    type: boolean
    guaranteed: on_success
    description: "Whether arc direction was adjusted"
  - field: adjustments
    type: list
    guaranteed: on_success
    description: "List of direction adjustments made (empty if none)"
side_effects:
  - "Maybe update arc direction"
generated: 2026-02-09
last_updated: "2026-02-09"
---
# Arc Review Ceremony

Review an arc's direction and progress after chapter completion. Determines if the arc needs direction adjustment based on completed chapter outcomes.

## When to Use

- After completing a chapter within an arc
- When observations suggest arc direction drift
- Before planning new chapters in the arc

**Invocation:** `Skill(skill="arc-review")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `arc_id` | MUST | Arc ID to review (e.g., ceremonies) |
| `completed_chapter_id` | SHOULD | Chapter that triggered this review |

---

## Ceremony Steps

1. Read ARC.md and extract theme and objectives
2. List completed and remaining chapters
3. Assess if completed chapter changed understanding of arc direction
4. If direction change needed, propose adjustments to operator
5. Log ArcReview ceremony event
6. Report review outcome to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether review completed |
| `direction_changed` | On success | Whether arc direction was adjusted |
| `adjustments` | On success | List of direction adjustments made (empty if none) |

---

## Side Effects

- Maybe update arc direction (theme, chapter list, exit criteria)

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- L4/functional_requirements.md: Feedback ceremonies definition
- CH-011: CeremonyContracts
