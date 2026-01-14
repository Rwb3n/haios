---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-041
title: "haios-status Work Items Removal"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 23:43:28
# Implementation Plan: haios-status Work Items Removal

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Remove the `work_items` section from haios-status.json, reducing file size by ~895 lines (66% reduction).

---

## Problem Statement

haios-status.json contains a `work_items` section that pre-computes document associations per backlog ID. This is:
1. **Stale:** Only refreshed when UpdateHaiosStatus.ps1 runs
2. **Redundant:** Data is queryable from document frontmatter via grep
3. **Bloated:** 895 lines of cached index data loaded every /coldstart

Per INV-008 and ADR-036, this is premature optimization that should be removed.

---

## Prerequisites

**BLOCKED BY:** E2-042 (Update /close to query at runtime)

The /close command currently reads work_items to find associated documents. E2-042 must complete first to replace this with runtime grep queries.

---

## Proposed Changes

### 1. UpdateHaiosStatus.ps1
- [ ] Remove `Build-WorkItemsSection` function
- [ ] Remove work_items from JSON output structure
- [ ] Remove lifecycle.live_files section (also redundant)
- [ ] Update tests if any exist

### 2. Documentation
- [ ] Update CLAUDE.md if work_items is referenced
- [ ] Update any commands that reference work_items structure

---

## Verification

- [ ] haios-status.json is ~120 lines (down from 1,365)
- [ ] /coldstart still works (doesn't depend on work_items)
- [ ] /haios still works
- [ ] /close still works (after E2-042)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Other code depends on work_items | Medium | Grep for "work_items" before removal |
| Performance regression in /close | Low | Grep is fast; acceptable trade-off |

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
- INV-008: haios-status.json Architecture Optimization
- E2-042: Close Runtime Query (prerequisite)

---
