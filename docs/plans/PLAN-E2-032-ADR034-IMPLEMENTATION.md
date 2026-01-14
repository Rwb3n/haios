---
template: implementation_plan
status: complete
date: 2025-12-11
backlog_id: E2-032
completed_session: 62
completion_note: "All deliverables implemented - investigation template, command, directory, deprecations, validator, CLAUDE.md"
title: "ADR-034 Implementation (Ontology Cleanup)"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-11
# System Auto: last updated on: 2025-12-11 23:18:36
# Implementation Plan: ADR-034 Implementation (Ontology Cleanup)

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement ADR-034's ontology decisions:
1. Rename `handoff_investigation` template to `investigation`
2. Create `/new-investigation` command
3. Create `docs/investigations/` directory
4. Deprecate handoff-related artifacts

---

## Problem Statement

ADR-034 (accepted Session 61) defined canonical lifecycle phases and deprecated "handoff" as obsolete. The implementation artifacts (templates, commands, directories) still reflect the old ontology.

**Discovery:** INV-006 (Session 60-61) - Document Ontology Audit
**Design:** ADR-034 (Session 61) - Canonical Prefixes with Aliases

This plan executes the design decisions.

---

## Proposed Changes

### 1. Template Rename
- [ ] Copy `.claude/templates/handoff_investigation.md` to `.claude/templates/investigation.md`
- [ ] Update template frontmatter: `template: investigation`
- [ ] Update `.claude/templates/README.md` to list `investigation` and mark `handoff_investigation` deprecated
- [ ] Keep `handoff_investigation.md` for backward compatibility (add deprecation warning at top)

### 2. New Command: /new-investigation
- [ ] Create `.claude/commands/new-investigation.md`
- [ ] Scaffold: `INVESTIGATION-<backlog_id>-<title>.md`
- [ ] Output directory: `docs/investigations/`
- [ ] Variables: BACKLOG_ID, TITLE, DATE

### 3. Directory Structure
- [ ] Create `docs/investigations/` directory
- [ ] Create `docs/investigations/README.md` explaining purpose

### 4. Deprecations
- [ ] Move `docs/handoff/HANDOFF_TYPES.md` to `docs/archive/`
- [ ] Add deprecation notice to `.claude/templates/handoff.md`
- [ ] Add deprecation notice to `.claude/commands/new-handoff.md`

### 5. Validator Updates
- [ ] Update `ValidateTemplate.ps1` to accept `investigation` as valid template type
- [ ] Add alias mapping: `handoff_investigation` -> `investigation`

### 6. Documentation
- [ ] Update CLAUDE.md "Epoch 2 Governance System" section with canonical prefixes
- [ ] Update CLAUDE.md "Slash Commands" to include `/new-investigation`

---

## Verification

- [ ] `investigation` template exists and scaffolds correctly
- [ ] `/new-investigation E2-TEST Test` creates `docs/investigations/INVESTIGATION-E2-TEST-test.md`
- [ ] ValidateTemplate.ps1 accepts `template: investigation`
- [ ] Deprecated templates show warning
- [ ] CLAUDE.md reflects new ontology

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing handoff docs break | Low | Keep old templates, just deprecate |
| Commands reference old paths | Medium | Update commands before deprecating |
| Validator rejects new template | Low | Test ValidateTemplate.ps1 first |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 61 | 2025-12-11 | - | plan_created | ADR-034 accepted, plan drafted |

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (validation works)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current (CLAUDE.md updated)
- [ ] All traced files complete

---

## References

- **INV-006** - Document Ontology Audit (discovery phase)
- **ADR-034** - Document Ontology and Work Lifecycle (design phase)
- **Session 61** - Plan creation
- **Blocks:** E2-009 (Lifecycle Sequence Enforcement)

---
