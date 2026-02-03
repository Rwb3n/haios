# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:34:15
# Chapter: Epoch Review

## Definition

**Chapter ID:** CH-020
**Arc:** feedback
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-019
**Work Items:** None

---

## Current State (Verified)

No epoch review ceremony exists:
- close-arc-ceremony has VALIDATE→MARK→REPORT but no epoch review trigger
- EPOCH.md files exist with exit criteria but no Update Log section
- No `get_epoch_for_arc()` function

**What exists:**
- EPOCH.md with Exit Criteria checklist
- close-arc-ceremony skill

**What doesn't exist:**
- epoch-review-ceremony skill
- EpochReviewed event type
- `get_epoch_for_arc()` function
- Parseable exit criteria format (currently markdown checkboxes)

---

## Human-Agent Boundary

Review pauses for human input on central question: "Did this arc change our understanding of epoch goals?"

---

## Problem

Arcs close without triggering epoch review. No mechanism for arc learnings to flow upward to epoch goals.

---

## Agent Need

> "I need arc completion to trigger an epoch review so learnings from arcs can update our understanding of epoch goals or identify gaps."

---

## Requirements

### R1: Arc Completion Triggers Review (REQ-FEEDBACK-003)

close-arc-ceremony MUST chain to epoch-review-ceremony:

```python
def close_arc_ceremony(arc_path: str):
    # ... closure steps ...

    # Trigger epoch review
    epoch_path = get_epoch_for_arc(arc_path)
    ceremony_runner.invoke("epoch-review",
        completed_arc_path=arc_path,
        epoch_path=epoch_path
    )
```

### R2: Epoch Review Contract

```yaml
name: epoch-review
category: feedback
input_contract:
  - field: completed_arc_path
    type: path
    required: true
  - field: epoch_path
    type: path
    required: true
output_contract:
  - field: review_outcome
    type: enum
    values: [no_change, goals_clarified, new_arc_needed, exit_criteria_updated]
  - field: updates
    type: list
    items: string
side_effects:
  - "May update epoch document"
  - "May create new arc"
  - "May update exit criteria"
  - "Log EpochReviewed event"
```

### R3: Review Question

Central question for epoch review:

> "Did this arc change our understanding of epoch goals?"

Possible outcomes:
- No change needed
- Goals clarified (update epoch purpose)
- New arc needed (create arc directory)
- Exit criteria updated (refine completion definition)
- Epoch complete (all arcs done, exit criteria met)

---

## Interface

### Epoch Review Ceremony Skill

```markdown
---
name: epoch-review
category: feedback
---

# Epoch Review Ceremony

## Purpose
Review epoch goals based on completed arc learnings.

## Input Contract
- completed_arc_path: Arc just closed
- epoch_path: Path to epoch this arc belongs to

## Review Steps
1. Load epoch document
2. Load completed arc summary
3. Ask: "Did this arc change our understanding of epoch goals?"
4. If yes: clarify goals, add arc, or update exit criteria
5. Log review outcome

## Output Contract
- review_outcome: no_change | goals_clarified | new_arc_needed | exit_criteria_updated
- updates: List of changes made
```

### Epoch Document Updates

When goals_clarified:
```markdown
## What We Learned (Updated)

### From lifecycles arc
- Pause semantics more important than originally scoped
- Batch mode enables new workflows not anticipated

### Exit Criteria Updates
- [x] Original: CycleRunner returns output
- [ ] Added: Pause points validated across all lifecycles
```

---

## Success Criteria

- [ ] Epoch Review ceremony skill created
- [ ] close-arc-ceremony triggers epoch-review
- [ ] Review asks central question
- [ ] Epoch document can be updated from review
- [ ] New arcs can be created
- [ ] Exit criteria can be updated
- [ ] EpochReviewed event logged
- [ ] Unit tests for review outcomes
- [ ] Integration test: close arc → epoch review → goals update

---

## Non-Goals

- Automatic goal detection (human judgment required)
- Epoch restructuring (goal updates only)
- Triggering requirements review (that's CH-021)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FEEDBACK-003)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-019-ArcReview.md (prior level)
