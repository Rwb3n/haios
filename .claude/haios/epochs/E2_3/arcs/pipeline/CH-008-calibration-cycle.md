# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T10:34:15
# Chapter: Calibration Cycle

## Definition

**Chapter ID:** CH-008
**Arc:** pipeline
**Status:** Planned
**Depends:** CH-007 (Chapter Triage)
**Work Items:** None

---

## Problem

No feedback loop between design and execution.

Current state:
```
Design → Execute → Done
```

Learnings from implementation don't flow back to design. Same mistakes repeat.

---

## Agent Need

> "After implementing a chapter's work items, I need to review what worked, what didn't, and update the design accordingly."

---

## Requirements

### R1: Chapter Calibration Section

Every chapter has a Calibration section:

```markdown
## Calibration

**Status:** Not Started | In Progress | Complete

### Pre-Triage Questions
- [Questions surfaced before creating work items]

### Post-Implementation Learnings
- [What worked]
- [What was unclear]
- [What should change]

### Amendments
- [Changes made to this chapter]
- [Changes proposed to CH-007 triage process]
```

### R2: Calibration Trigger

Calibration runs after all work items for a chapter are closed.

```
Chapter status: In Progress → Complete (work done) → Calibrated
```

### R3: Comparison Check

Calibration compares:
- Requirements (R1, R2, ...) → Were they clear?
- Work items created → Did mapping make sense?
- Deliverables → Did they satisfy requirements?

### R4: Feedback to Triage Process

If calibration reveals process issues, propose amendments to CH-007 (Chapter Triage).

```
Calibration output:
- Chapter-specific learnings (stay in chapter)
- Process learnings (propagate to CH-007)
```

### R5: Memory Storage

Key learnings stored to memory with:
- `source_path`: chapter file
- `content_type`: techne (how-to knowledge)

---

## Interface

**Input:** Completed chapter (all work items closed)

**Process:**
1. Read chapter requirements
2. Read linked work items and their outcomes
3. Prompt: What worked? What was unclear?
4. Update chapter Calibration section
5. If process issues, propose CH-007 amendments
6. Store learnings to memory

**Output:** Updated chapter with Calibration complete

---

## Success Criteria

- [ ] Chapter template includes Calibration section
- [ ] Calibration runs after chapter work complete
- [ ] Learnings stored to memory
- [ ] Process feedback flows to CH-007

---

## Non-Goals

- Automatic calibration (agent judgment required)
- Per-work-item calibration (chapter level only)
- Blocking chapter close on calibration (advisory, not gate)

---

## Validation

This chapter is speculative. Validate need after first triage (CH-002 Session Simplify).

If CH-002 triage + implementation reveals:
- No feedback needed → Deprecate this chapter
- Template change sufficient → Implement R1 only
- Full cycle needed → Implement all requirements
