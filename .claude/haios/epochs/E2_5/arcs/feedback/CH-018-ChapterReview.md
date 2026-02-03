# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:33:54
# Chapter: Chapter Review

## Definition

**Chapter ID:** CH-018
**Arc:** feedback
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** Ceremonies:CH-015
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/skills/close-work-cycle/SKILL.md`, `.claude/haios/epochs/E2_5/arcs/*/CH-*.md`

No chapter review ceremony exists:
- close-work-cycle has CHAIN phase but doesn't trigger chapter review
- Chapter files exist (27 in E2.5) but have no Update Log section
- No `get_chapter_for_work()` function

**What exists:**
- Chapter files with Status field
- Work items with `chapter` field in frontmatter (traces to chapter)
- close-work-cycle CHAIN phase routes to next work

**What doesn't exist:**
- chapter-review-ceremony skill
- ChapterReviewed event type
- Update Log section in chapter template
- `get_chapter_for_work()` function

---

## Human-Agent Boundary

**CLARIFICATION (per critique):**

| Action | Actor | Pause Required |
|--------|-------|----------------|
| Trigger review | Agent (automatic on close) | No |
| Gather review inputs | Agent | No |
| Answer central question | **Human** | **Yes - pause for input** |
| Apply updates | Agent | No |

The ceremony PAUSES to ask the human: "Did this work change our understanding of chapter scope?"

---

## Problem

Work closes without triggering chapter review. No mechanism for work learnings to flow upward to chapter scope.

---

## Agent Need

> "I need work completion to trigger a chapter review so learnings from implementation can update chapter scope, revealing new work or adjusting direction."

---

## Requirements

### R1: Work Completion Triggers Review (REQ-FEEDBACK-001)

close-work-ceremony MUST chain to chapter-review-ceremony:

```python
def close_work_ceremony(work_id: str):
    # ... closure steps ...

    # Trigger chapter review
    chapter_path = get_chapter_for_work(work_id)
    ceremony_runner.invoke("chapter-review",
        completed_work_id=work_id,
        chapter_path=chapter_path
    )
```

### R2: Chapter Review Contract

```yaml
name: chapter-review
category: feedback
input_contract:
  - field: completed_work_id
    type: string
    required: true
  - field: chapter_path
    type: path
    required: true
output_contract:
  - field: review_outcome
    type: enum
    values: [no_change, scope_updated, new_work_identified]
  - field: updates
    type: list
    items: string
side_effects:
  - "May update chapter document"
  - "May add new work items to chapter"
  - "Log ChapterReviewed event"
```

### R3: Review Question

Central question for chapter review:

> "Did this work change our understanding of chapter scope?"

Possible outcomes:
- No change needed
- Scope clarification (update chapter description)
- New work identified (add to chapter)
- Chapter complete (all planned work done)

---

## Interface

### Chapter Review Ceremony Skill

```markdown
---
name: chapter-review
category: feedback
---

# Chapter Review Ceremony

## Purpose
Review chapter scope based on completed work learnings.

## Input Contract
- completed_work_id: Work item just closed
- chapter_path: Path to chapter this work belongs to

## Review Steps
1. Load chapter document
2. Load completed work observations
3. Ask: "Did this work change our understanding of chapter scope?"
4. If yes: update chapter or identify new work
5. Log review outcome

## Output Contract
- review_outcome: no_change | scope_updated | new_work_identified
- updates: List of changes made
```

### Integration with close-work-ceremony

```python
# In close-work-ceremony, after work archived
ceremony_runner.invoke("chapter-review",
    completed_work_id=work_id,
    chapter_path=work.traces_to_chapter
)
```

### Chapter Document Updates

When scope_updated:
```markdown
## Scope Updates

### Update 1 (from WORK-001 review)
- Added: consideration for batch mode
- Rationale: WORK-001 revealed need for concurrent item handling
```

---

## Success Criteria

- [ ] Chapter Review ceremony skill created
- [ ] close-work-ceremony triggers chapter-review
- [ ] Review asks central question
- [ ] Chapter document can be updated from review
- [ ] New work can be identified and created
- [ ] ChapterReviewed event logged
- [ ] Unit tests for review outcomes
- [ ] Integration test: close work → chapter review → scope update

---

## Non-Goals

- Automatic scope detection (human judgment required)
- Chapter restructuring (scope updates only)
- Triggering arc review (that's CH-019)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FEEDBACK-001)
- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-015-ClosureCeremonies.md (triggers this)
