# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T17:41:36
# Chapter: Chapter Acceptance

## Definition

**Chapter ID:** CH-009
**Arc:** pipeline
**Status:** Approved
**Depends:** CH-007 (Chapter Triage)
**Work Items:** None

---

## Problem

After completing chapter work items, no defined process to:
1. Verify implementation meets acceptance criteria
2. Resolve requirements variance (spec vs reality)
3. Mark chapter complete

Current state: Work items close, observations captured, but chapter status never updated.

---

## Agent Need

> "After completing a chapter's work items, I need to know how to verify acceptance and close the chapter."

---

## Requirements

### R1: Chapter Acceptance Checklist

After last work item completes, verify:
1. Acceptance criteria satisfied (does it work?)
2. Requirements variance resolved (spec matches reality)
3. Runtime integration exists (consumer uses it)

### R2: Requirements Variance Resolution

Observation triage adds outcome `requirements_variance`:
- Route to chapter spec update (not new work item)
- Fix spec to match working implementation

### R3: Chapter Status Transition

```
Planned → Approved → In Progress → Complete
```

When all work items complete AND acceptance verified → status: Complete

### R4: close-work-cycle Integration

After closing last chapter work item:
- Detect "last work item for chapter"
- Prompt for chapter acceptance
- Update chapter status

---

## Interface

**Trigger:** Last work item for chapter closes

**Process:**
1. close-work-cycle detects chapter context
2. Prompts: "All CH-XXX work items complete. Run acceptance?"
3. If yes: Verify criteria, fix variance, mark complete

**Output:** Chapter status → Complete

---

## Success Criteria

- [ ] chapter.md template has status field (already exists)
- [ ] observation-triage-cycle has `requirements_variance` outcome
- [ ] close-work-cycle prompts for chapter acceptance on last work item
- [ ] CH-002 closed using this process (validation)

---

## Non-Goals

- Automatic chapter reopening (scope extension is new work)
- Calibration cycles (absorbed into observation triage)
- Arc-level review (separate concern)
