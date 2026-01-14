---
template: implementation_plan
status: complete
date: 2025-12-10
backlog_id: E2-023
title: "Close Command Implementation"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-10
# System Auto: last updated on: 2025-12-10 23:45:40
# Implementation Plan: Close Command Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement `/close <backlog_id>` command that validates Definition of Done (DoD) per ADR-033, updates work item status across all associated documents, stores completion summary to memory, and refreshes the work item tree.

---

## Problem Statement

Closing work loops is manual. When completing a work item, the agent must:
1. Update backlog.md entry status
2. Update all associated plan statuses
3. Store completion reasoning to memory
4. Run UpdateHaiosStatus.ps1

This is error-prone. Steps get missed. `/close` automates this sequence with DoD validation.

---

## Methodology: AODEV TDD

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
              |          |
              v          v
           (Tests)   (Implementation)
```

Each phase writes tests BEFORE implementation. Red-Green-Refactor.

---

## Proposed Changes

### 1. Create `/close` Command (`.claude/commands/close.md`)
- [ ] Parse `<backlog_id>` argument
- [ ] Read work_items from haios-status.json
- [ ] Validate DoD criteria (prompt-based)
- [ ] Document update sequence

### 2. DoD Validation Logic
- [ ] Check associated plans have status: complete
- [ ] Prompt user to confirm: tests pass, WHY captured, docs current
- [ ] If validation fails, report what's missing

### 3. Closure Actions
- [ ] Update backlog.md entry status to `complete`
- [ ] Update associated plan files to status: `complete`
- [ ] Call `ingester_ingest` with closure summary
- [ ] Run UpdateHaiosStatus.ps1
- [ ] Report closure with memory concept IDs

---

## Verification

- [ ] Command parses backlog_id correctly
- [ ] DoD validation catches incomplete plans
- [ ] Backlog status updates correctly
- [ ] Memory storage succeeds
- [ ] haios-status.json refreshes

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backlog.md format varies | Medium | Use regex that handles variations |
| Work item not in haios-status.json | Medium | Prompt user to run UpdateHaiosStatus first |
| Memory MCP unavailable | Low | Continue closure, warn about memory skip |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 58 | 2025-12-10 | - | in_progress | Initial implementation |

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] All traced files complete

---

## References

- ADR-033: Work Item Lifecycle Governance (DoD definition)
- ADR-031: Workspace Awareness (work_items tree)
- E2-031: Work Item Lifecycle Implementation (parent work item)
- Session 57 checkpoint: E2-023 specification

---
