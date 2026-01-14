---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-044
title: "Close Auto-Archive"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 23:44:07
# Implementation Plan: Close Auto-Archive

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Update /close command to automatically archive completed items to docs/pm/archive/backlog-complete.md, keeping backlog.md always clean.

---

## Problem Statement

After E2-043 migrates existing completed items, new completions will accumulate again. Per INV-009 and ADR-036:
- /close already edits backlog.md (updates status to complete)
- Adding "move to archive" is incremental complexity
- Immediate archival = always-clean active backlog
- No arbitrary schedule (quarterly, monthly) needed

---

## Prerequisites

**BLOCKED BY:** E2-043 (archive file must exist first)

The archive file docs/pm/archive/backlog-complete.md must be created by E2-043 before this enhancement.

**Note:** The directory `docs/pm/archive/` already exists. E2-043 only needs to create the target file.

---

## Proposed Changes

### 1. Update close.md Step 3a (Execute Closure)
Current behavior:
- Updates status line in backlog.md to `complete`

New behavior:
- Extract the entire item section (header through next header or EOF)
- Append to docs/pm/archive/backlog-complete.md
- Remove from backlog.md

### 2. Implementation Steps
- [ ] After DoD validation passes, locate item section in backlog.md
- [ ] Extract section content (preserve all fields)
- [ ] Append to archive file with timestamp comment
- [ ] Remove section from backlog.md
- [ ] Continue with memory storage and status refresh

### 3. Archive Entry Format
```markdown
<!-- Archived: 2025-12-13 via /close -->
### [COMPLETE] E2-xxx: Title
- **Status:** complete
- **Completed:** {date}
... (rest of item)
```

---

## Verification

- [ ] /close E2-xxx removes item from backlog.md
- [ ] /close E2-xxx adds item to archive with timestamp
- [ ] Item content preserved exactly (no data loss)
- [ ] Memory closure summary still works
- [ ] haios-status.json refresh still works

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Section boundary errors | High | Reuse regex from E2-043 |
| Archive file corruption | Medium | Append-only writes |
| User wants to undo close | Low | Item still in archive, can restore manually |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] All traced files complete

---

## References

- ADR-036: PM Data Architecture
- INV-009: Backlog Archival Governance
- E2-043: Backlog Archival Migration (prerequisite)
- E2-042: Close Runtime Query (related /close enhancement)

---
