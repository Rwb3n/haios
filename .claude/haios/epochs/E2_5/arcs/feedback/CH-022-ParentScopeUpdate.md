# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:34:42
# Chapter: Parent Scope Update

## Definition

**Chapter ID:** CH-022
**Arc:** feedback
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-018, CH-019, CH-020, CH-021
**Work Items:** None

---

## Current State (Verified)

No parent scope update mechanism exists:
- Chapter/Arc/Epoch files don't have "Update Log" sections
- No `update_chapter_scope()` or similar functions
- Updates are manual via Edit tool

**What exists:**
- Parent documents (Chapter.md, ARC.md, EPOCH.md, L4/*)
- Edit tool for modifications

**What doesn't exist:**
- Update Log section in parent document templates
- `update_chapter_scope()`, `update_arc_direction()`, etc. functions
- Update type schema (add_section, clarify, mark_complete, add_item)
- DocumentUpdated event type

**Pre-requisite (per critique):**
All parent documents need "Update Log" section added before this can work:
```markdown
## Update Log

| Date | Source | Type | Change | Rationale |
|------|--------|------|--------|-----------|
```

---

## Problem

No mechanism to apply updates from reviews. Updates identified but require manual editing.

---

## Agent Need

> "I need review ceremonies to actually update parent documents when appropriate, not just identify that updates are needed."

---

## Requirements

### R1: Reviews MAY Update Parent Scope (REQ-FEEDBACK-005)

Review ceremonies have permission to modify parent documents:

```python
# In chapter-review-ceremony
if review_outcome == "scope_updated":
    update_chapter_document(chapter_path, updates)
```

### R2: Update Types Per Level

| Review Level | Parent Document | Allowed Updates |
|--------------|-----------------|-----------------|
| Chapter Review | Chapter.md | Scope, work items list |
| Arc Review | ARC.md | Direction, chapters list |
| Epoch Review | EPOCH.md | Goals, exit criteria, arcs list |
| Requirements Review | functional_requirements.md | Requirements table, supersession log |

### R3: Update Audit Trail

All updates must be traceable:

```markdown
## Update Log

| Date | Source | Change | Reviewer |
|------|--------|--------|----------|
| 2026-02-03 | WORK-001 review | Added batch mode consideration | Hephaestus |
```

### R4: Update Constraints

Reviews can:
- Add content (new sections, new items)
- Clarify existing content (refine descriptions)
- Mark items complete (check boxes)

Reviews cannot:
- Delete content (append-only)
- Change fundamental structure
- Remove requirements (supersede only)

---

## Interface

### Document Update Functions

```python
def update_chapter_scope(chapter_path: Path, updates: List[Update]) -> None:
    """Apply updates to chapter document."""

def update_arc_direction(arc_path: Path, updates: List[Update]) -> None:
    """Apply updates to arc document."""

def update_epoch_goals(epoch_path: Path, updates: List[Update]) -> None:
    """Apply updates to epoch document."""

def update_requirements(l4_path: Path, updates: List[Update]) -> None:
    """Apply updates to L4 requirements."""
```

### Update Schema

```python
@dataclass
class Update:
    type: str       # add_section, clarify, mark_complete, add_item
    location: str   # Where in document
    content: str    # What to add/change
    source: str     # WORK-XXX that triggered this
    rationale: str  # Why this update
```

### Ceremony Integration

```python
# In review ceremony
def execute_review(review_type: str, inputs: Dict) -> ReviewResult:
    # ... review logic ...

    if updates_needed:
        for update in updates:
            apply_update(parent_document, update)
            log_update(update)

    return ReviewResult(
        outcome=outcome,
        updates_applied=updates
    )
```

### Update Log Format

Each parent document gets Update Log section:

```markdown
## Update Log

| Date | Source | Type | Change | Rationale |
|------|--------|------|--------|-----------|
| 2026-02-03 | WORK-001 | add_item | Added CH-007 to chapters | Queue discovery |
| 2026-02-03 | CH-004 | clarify | Refined chaining semantics | Implementation learning |
```

---

## Success Criteria

- [ ] Update functions for each document level
- [ ] Updates applied automatically during review
- [ ] Update Log section in all parent documents
- [ ] Updates traceable to source work/chapter/arc
- [ ] Append-only constraint enforced
- [ ] DocumentUpdated events logged
- [ ] Unit tests for update application
- [ ] Integration test: review → update → verify log

---

## Non-Goals

- Automatic update suggestions (human reviews, system applies)
- Complex merge logic (simple append/clarify only)
- Undo/revert (append-only design)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FEEDBACK-005)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-018-ChapterReview.md (uses this)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-019-ArcReview.md (uses this)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-020-EpochReview.md (uses this)
- @.claude/haios/epochs/E2_5/arcs/feedback/CH-021-RequirementsReview.md (uses this)
