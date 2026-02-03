# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:34:05
# Chapter: Arc Review

## Definition

**Chapter ID:** CH-019
**Arc:** feedback
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-018
**Work Items:** None

---

## Current State (Verified)

No arc review ceremony exists:
- close-chapter-ceremony has VALIDATE→MARK→REPORT but no arc review trigger
- ARC.md files exist (5 in E2.5) but have no Update Log section
- No `get_arc_for_chapter()` function

**What exists:**
- ARC.md files with chapters table
- close-chapter-ceremony skill

**What doesn't exist:**
- arc-review-ceremony skill
- ArcReviewed event type
- `get_arc_for_chapter()` function
- "arc_complete" outcome in close-chapter contract

---

## Human-Agent Boundary

Review pauses for human input on central question: "Did this chapter reveal new work needed in this arc?"

---

## Problem

Chapters close without triggering arc review. No mechanism for chapter learnings to flow upward.

---

## Agent Need

> "I need chapter completion to trigger an arc review so learnings from chapters can reveal new work needed in the arc or adjust arc direction."

---

## Requirements

### R1: Chapter Completion Triggers Review (REQ-FEEDBACK-002)

close-chapter-ceremony MUST chain to arc-review-ceremony:

```python
def close_chapter_ceremony(chapter_path: str):
    # ... closure steps ...

    # Trigger arc review
    arc_path = get_arc_for_chapter(chapter_path)
    ceremony_runner.invoke("arc-review",
        completed_chapter_path=chapter_path,
        arc_path=arc_path
    )
```

### R2: Arc Review Contract

```yaml
name: arc-review
category: feedback
input_contract:
  - field: completed_chapter_path
    type: path
    required: true
  - field: arc_path
    type: path
    required: true
output_contract:
  - field: review_outcome
    type: enum
    values: [no_change, direction_adjusted, new_chapter_needed]
  - field: updates
    type: list
    items: string
side_effects:
  - "May update arc document"
  - "May create new chapter"
  - "Log ArcReviewed event"
```

### R3: Review Question

Central question for arc review:

> "Did this chapter reveal new work needed in this arc?"

Possible outcomes:
- No change needed
- Direction adjusted (update arc theme/scope)
- New chapter needed (create chapter file)
- Arc complete (all chapters done)

---

## Interface

### Arc Review Ceremony Skill

```markdown
---
name: arc-review
category: feedback
---

# Arc Review Ceremony

## Purpose
Review arc direction based on completed chapter learnings.

## Input Contract
- completed_chapter_path: Chapter just closed
- arc_path: Path to arc this chapter belongs to

## Review Steps
1. Load arc document
2. Load completed chapter summary
3. Ask: "Did this chapter reveal new work needed in this arc?"
4. If yes: adjust arc or create new chapter
5. Log review outcome

## Output Contract
- review_outcome: no_change | direction_adjusted | new_chapter_needed
- updates: List of changes made
```

### Arc Document Updates

When direction_adjusted:
```markdown
## Direction Updates

### Update 1 (from CH-004 review)
- Added: Need for explicit error handling patterns
- Rationale: CallerChaining chapter revealed edge cases not originally scoped
```

---

## Success Criteria

- [ ] Arc Review ceremony skill created
- [ ] close-chapter-ceremony triggers arc-review
- [ ] Review asks central question
- [ ] Arc document can be updated from review
- [ ] New chapters can be created
- [ ] ArcReviewed event logged
- [ ] Unit tests for review outcomes
- [ ] Integration test: close chapter → arc review → direction update

---

## Non-Goals

- Automatic direction detection (human judgment required)
- Arc restructuring (direction updates only)
- Triggering epoch review (that's CH-020)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FEEDBACK-002)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-018-ChapterReview.md (prior level)
