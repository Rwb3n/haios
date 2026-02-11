---
name: chapter-review
type: ceremony
description: "Review chapter scope after work completion to assess if adjustments needed."
category: feedback
stub: true
input_contract:
  - field: chapter_id
    type: string
    required: true
    description: "Chapter ID to review (e.g., CH-011)"
    pattern: "CH-\\d{3}"
  - field: completed_work_id
    type: string
    required: false
    description: "Work item that triggered this review"
    pattern: "WORK-\\d{3}"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether review completed"
  - field: scope_changed
    type: boolean
    guaranteed: on_success
    description: "Whether chapter scope was adjusted"
  - field: adjustments
    type: list
    guaranteed: on_success
    description: "List of scope adjustments made (empty if none)"
side_effects:
  - "Maybe update chapter scope"
generated: 2026-02-09
last_updated: "2026-02-09"
---
# Chapter Review Ceremony

Review a chapter's scope and progress after work item completion. Determines if the chapter needs scope adjustment based on completed work outcomes.

## When to Use

- After completing a work item within a chapter
- When observations suggest chapter scope drift
- Periodically during long-running chapters

**Invocation:** `Skill(skill="chapter-review")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `chapter_id` | MUST | Chapter ID to review (e.g., CH-011) |
| `completed_work_id` | SHOULD | Work item that triggered this review |

---

## Ceremony Steps

1. Read chapter file and extract objectives
2. List completed and remaining work items
3. Assess if completed work changed understanding of chapter scope
4. If scope change needed, propose adjustments to operator
5. Log ChapterReview ceremony event
6. Report review outcome to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether review completed |
| `scope_changed` | On success | Whether chapter scope was adjusted |
| `adjustments` | On success | List of scope adjustments made (empty if none) |

---

## Side Effects

- Maybe update chapter scope (exit criteria, work item list)

---

## References

- REQ-CEREMONY-002: Each ceremony has input/output contract
- L4/functional_requirements.md: Feedback ceremonies definition
- CH-011: CeremonyContracts
