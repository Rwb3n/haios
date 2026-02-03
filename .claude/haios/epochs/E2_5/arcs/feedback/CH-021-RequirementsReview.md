# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:34:28
# Chapter: Requirements Review

## Definition

**Chapter ID:** CH-021
**Arc:** feedback
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-020
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/haios/manifesto/L4/functional_requirements.md`

No requirements review ceremony exists:
- close-epoch-ceremony has VALIDATE→ARCHIVE→TRANSITION but no requirements review trigger
- L4/functional_requirements.md exists with Requirement ID Registry table
- Supersession Log exists (append-only pattern)

**What exists:**
- L4/functional_requirements.md with requirement tables
- Supersession Log section
- close-epoch-ceremony skill

**What doesn't exist:**
- requirements-review-ceremony skill
- RequirementsReviewed event type
- Automatic requirement ID generation

**ConfigLoader Compliance (per critique):**
L4 path should use ConfigLoader, not hardcoded:
```python
# Correct
l4_path = ConfigLoader.get_path("l4_requirements")
# Not
l4_path = ".claude/haios/manifesto/L4/functional_requirements.md"
```

---

## Human-Agent Boundary

Review REQUIRES human approval for any requirement changes:
- Agent proposes changes
- Human approves/rejects
- Only approved changes are applied

---

## Problem

Epochs close without triggering requirements review. System doesn't learn at L4 level.

---

## Agent Need

> "I need epoch completion to trigger a requirements review so learnings from entire epochs can reveal requirements we missed or need to evolve."

---

## Requirements

### R1: Epoch Completion Triggers Review (REQ-FEEDBACK-004)

close-epoch-ceremony MUST chain to requirements-review-ceremony:

```python
def close_epoch_ceremony(epoch_path: str):
    # ... closure steps ...

    # Trigger requirements review
    ceremony_runner.invoke("requirements-review",
        completed_epoch_path=epoch_path,
        l4_path=".claude/haios/manifesto/L4/functional_requirements.md"
    )
```

### R2: Requirements Review Contract

```yaml
name: requirements-review
category: feedback
input_contract:
  - field: completed_epoch_path
    type: path
    required: true
  - field: l4_path
    type: path
    required: true
output_contract:
  - field: review_outcome
    type: enum
    values: [no_change, requirements_added, requirements_superseded, gaps_identified]
  - field: updates
    type: list
    items: string
side_effects:
  - "May update L4 requirements document"
  - "May add new requirements"
  - "May mark requirements superseded"
  - "Log RequirementsReviewed event"
```

### R3: Review Question

Central question for requirements review:

> "Did this epoch reveal requirements we missed?"

Possible outcomes:
- No change needed
- Requirements added (new REQ-XXX entries)
- Requirements superseded (mark old, add new)
- Gaps identified (document for future epochs)

---

## Interface

### Requirements Review Ceremony Skill

```markdown
---
name: requirements-review
category: feedback
---

# Requirements Review Ceremony

## Purpose
Review L4 requirements based on completed epoch learnings.

## Input Contract
- completed_epoch_path: Epoch just closed
- l4_path: Path to L4 functional requirements

## Review Steps
1. Load L4 requirements document
2. Load completed epoch summary and learnings
3. Ask: "Did this epoch reveal requirements we missed?"
4. If yes: add requirements, supersede old, or document gaps
5. Log review outcome

## Output Contract
- review_outcome: no_change | requirements_added | requirements_superseded | gaps_identified
- updates: List of changes made
```

### L4 Document Updates

When requirements_added:
```markdown
## Requirement ID Registry (Master)

| ID | Domain | Description | Derives From | Implemented By |
|----|--------|-------------|--------------|----------------|
| REQ-PAUSE-001 | Lifecycle | Pause points per S27 breath model | L3.4, L3.5 | E2.5 lifecycles |
*Added from E2.5 requirements review*
```

### Supersession Handling

Per FP principles, requirements are never deleted:
```markdown
## Supersession Log (Append-Only)

| Session | Superseded | By | Reason |
|---------|------------|-----|--------|
| 295 | REQ-OLD-001 | REQ-NEW-001 | E2.5 revealed original was incomplete |
```

---

## Success Criteria

- [ ] Requirements Review ceremony skill created
- [ ] close-epoch-ceremony triggers requirements-review
- [ ] Review asks central question
- [ ] L4 document can be updated from review
- [ ] New requirements can be added
- [ ] Supersession follows FP pattern
- [ ] RequirementsReviewed event logged
- [ ] Unit tests for review outcomes
- [ ] Integration test: close epoch → requirements review → new requirement

---

## Non-Goals

- Automatic requirement generation (human judgment required)
- L3 principle changes (requirements only)
- Breaking backward compatibility (append-only)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FEEDBACK-004, document to update)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-020-EpochReview.md (prior level)
