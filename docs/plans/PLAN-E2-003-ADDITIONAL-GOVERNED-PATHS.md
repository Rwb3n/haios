---
template: implementation_plan
status: complete
date: 2025-12-09
backlog_id: E2-003
title: "Additional Governed Paths"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-09
# System Auto: last updated on: 2025-12-09 21:29:38
# Implementation Plan: Additional Governed Paths

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Extend governance enforcement to ADR, TRD, and README files. When agent tries to create these files via raw Write/Edit, hook blocks and suggests appropriate command.

**Success Criteria:**
- `/new-adr` command exists and scaffolds ADRs with template
- PreToolUse blocks raw writes to `docs/ADR/*.md`
- Pattern reusable for TRD, README if needed

---

## Problem Statement

**Demonstrated Gap (Session 45):** ADR-031 was written without governance - no template, no scaffolding, manual frontmatter. This contradicts the governance philosophy established for checkpoints, plans, handoffs.

**Current Governed Paths:**
- `docs/checkpoints/*.md` -> `/new-checkpoint`
- `docs/plans/PLAN-*.md` -> `/new-plan`
- `docs/handoff/*.md` -> `/new-handoff`
- `docs/reports/*.md` -> `/new-report`

**Missing:**
- `docs/ADR/*.md` -> `/new-adr` (needed)
- `docs/specs/*.md` -> `/new-trd` (future consideration)

---

## Proposed Changes

### 1. Create `/new-adr` Command
- [ ] Create `.claude/commands/new-adr.md`
- [ ] Arguments: `<adr-number> <title>` (e.g., `/new-adr 033 "Work Loop Closure"`)
- [ ] Scaffold via `ScaffoldTemplate.ps1` with `architecture_decision_record` template
- [ ] Output: `docs/ADR/ADR-<number>-<slug>.md`

### 2. Create ADR Template (if not exists)
- [ ] Verify `.claude/templates/architecture_decision_record.md` exists
- [ ] If missing, create with standard ADR structure (Context, Decision, Status, Consequences)

### 3. Update PreToolUse.ps1
- [ ] Add `docs/ADR/` to governed paths
- [ ] Pattern: `ADR-*.md`
- [ ] Block message: "Use `/new-adr <number> <title>` command instead"

### 4. Update CLAUDE.md
- [ ] Add `/new-adr` to Slash Commands table
- [ ] Add `docs/ADR/` to governed paths list

---

## Verification

- [ ] `/new-adr 999 Test` creates `docs/ADR/ADR-999-test.md` with template
- [ ] Raw `Write` to `docs/ADR/ADR-999-foo.md` is blocked by hook
- [ ] Created ADR passes `/validate` check
- [ ] CLAUDE.md documents the new command

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADR number collision | Low | Check if file exists before scaffold |
| Template not found | Medium | Verify template exists in pre-check |
| Existing ADRs without frontmatter | Low | Only block NEW file creation, not edits |

---

## Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-003-01 | ADR number is explicit argument | Unlike plans (linked to backlog), ADRs have sequential numbering convention |
| DD-003-02 | Block new files only, allow edits | Existing ADRs may not have frontmatter; don't break editing |
| DD-003-03 | Defer TRD/README governance | Start with ADR, expand pattern if successful |

---

## References

- Backlog: E2-003 (Additional Governed Paths)
- Trigger: Session 45 - ADR-031 written without governance
- Pattern: PreToolUse.ps1 existing governance logic
- Template: `.claude/templates/architecture_decision_record.md`

---
