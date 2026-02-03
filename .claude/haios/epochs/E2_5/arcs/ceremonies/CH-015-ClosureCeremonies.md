# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:32:52
# Chapter: Closure Ceremonies

## Definition

**Chapter ID:** CH-015
**Arc:** ceremonies
**Status:** Planned
**Implementation Type:** PARTIAL (skills exist, need ceremony contracts)
**Depends:** CH-011
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/skills/`

Closure skills exist:
- `close-work-cycle/SKILL.md` - VALIDATE→ARCHIVE→MEMORY→CHAIN phases
- `close-chapter-ceremony/SKILL.md` - VALIDATE→MARK→REPORT phases
- `close-arc-ceremony/SKILL.md` - VALIDATE→MARK→REPORT phases
- `close-epoch-ceremony/SKILL.md` - VALIDATE→ARCHIVE→TRANSITION phases

**What exists:**
- All 4 closure skills implemented
- DoD validation in each
- Event logging via governance-events.jsonl

**What doesn't exist:**
- Machine-readable contracts in frontmatter
- DoDResult type definition
- Consistent ceremony invocation pattern

**Composition pattern (per CH-012):**
close-work-cycle COMPOSES observation-capture and memory-commit as steps (not nested ceremonies).

---

## Problem

Skills exist but lack formal contracts. Need to add input_contract, output_contract, side_effects to frontmatter.

---

## Agent Need

> "I need consistent closure ceremonies at each hierarchy level so closing any entity follows the same governed pattern with appropriate DoD verification."

---

## Requirements

### R1: Four Closure Ceremonies

| Ceremony | Signature | DoD Verifies |
|----------|-----------|--------------|
| Close Work | `WorkItem → ClosedWorkItem` | Tests pass, artifact exists |
| Close Chapter | `Chapter → ClosedChapter` | All work complete, decisions implemented |
| Close Arc | `Arc → ClosedArc` | All chapters complete, no orphan decisions |
| Close Epoch | `Epoch → ClosedEpoch` | All arcs complete, exit criteria met |

### R2: Cascading DoD

Each level's DoD includes lower level completion:

```
Close Epoch requires:
  └── All arcs complete
      └── All chapters complete
          └── All work items complete
```

### R3: Closure Contracts

**Close Work:**
```yaml
input_contract:
  - field: work_id
    type: string
    required: true
output_contract:
  - field: archived_path
    type: path
side_effects:
  - "Update status to complete"
  - "Move to archive directory"
  - "Log WorkClosed event"
  - "Trigger memory commit"
```

**Close Chapter:**
```yaml
input_contract:
  - field: chapter_path
    type: path
    required: true
output_contract:
  - field: chapter_status
    type: string
    value: "Complete"
side_effects:
  - "Update chapter status"
  - "Log ChapterClosed event"
  - "Trigger Chapter Review ceremony"
```

---

## Interface

### Ceremony Skills

```
skills/
  close-work-ceremony.md
  close-chapter-ceremony.md
  close-arc-ceremony.md
  close-epoch-ceremony.md
```

### DoD Validation Functions

```python
def validate_work_dod(work_id: str) -> DoDResult:
    """Verify work item meets Definition of Done."""

def validate_chapter_dod(chapter_path: Path) -> DoDResult:
    """Verify chapter meets DoD (all work complete)."""

def validate_arc_dod(arc_path: Path) -> DoDResult:
    """Verify arc meets DoD (all chapters complete)."""

def validate_epoch_dod(epoch_path: Path) -> DoDResult:
    """Verify epoch meets DoD (all arcs complete, exit criteria)."""
```

### Invocation

```python
# Close work
ceremony_runner.invoke("close-work", work_id="WORK-001")

# Close chapter
ceremony_runner.invoke("close-chapter", chapter_path="arcs/lifecycles/CH-001.md")

# Close arc
ceremony_runner.invoke("close-arc", arc_path="arcs/lifecycles/")

# Close epoch
ceremony_runner.invoke("close-epoch", epoch_path="epochs/E2_5/")
```

---

## Success Criteria

- [ ] 4 closure ceremony skills created
- [ ] Each ceremony has input/output contract
- [ ] DoD validation functions for each level
- [ ] Cascading validation (chapter checks all work)
- [ ] Events logged for each closure
- [ ] Memory commit triggered on work closure
- [ ] Review ceremonies triggered appropriately
- [ ] Unit tests for DoD validation
- [ ] Integration test: work → chapter → arc cascade

---

## Non-Goals

- Reopen ceremonies (closed is terminal for now)
- Partial closure (all-or-nothing per entity)
- Async closure (synchronous only)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001, REQ-DOD-001, REQ-DOD-002)
- @.claude/skills/close-work-cycle.md (existing to refactor)
