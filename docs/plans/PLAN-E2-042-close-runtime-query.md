---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-042
title: "Close Runtime Query"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 23:39:02
# Implementation Plan: Close Runtime Query

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Update /close command to query associated documents at runtime via grep instead of reading pre-computed `work_items` from haios-status.json.

---

## Problem Statement

The /close command (`.claude/commands/close.md`) currently:
1. Reads haios-status.json
2. Looks up `work_items[backlog_id]` to find associated plans, checkpoints, etc.

This depends on stale pre-computed data. Per ADR-036, we should query at runtime:
```bash
grep -r "backlog_id: E2-041" docs/ --include="*.md"
```

This enables E2-041 to remove work_items entirely.

---

## Proposed Changes

### 1. Update close.md Step 1 (Document Lookup)
- [ ] Replace haios-status.json read with runtime grep
- [ ] Query pattern: `grep -r "backlog_id: {ID}" docs/ --include="*.md"`
- [ ] Parse results to categorize by document type (plan, checkpoint, etc.)
- [ ] Remove fallback to UpdateHaiosStatus.ps1 (no longer needed)

### 2. Query Implementation
- [ ] Use Grep tool (not bash grep) for consistency
- [ ] Pattern: `backlog_id:\s*{ID}` or `backlog_ids:.*{ID}`
- [ ] Search paths: docs/plans/, docs/checkpoints/, docs/reports/, docs/ADR/

### 3. Result Parsing
- [ ] Identify document type from path or frontmatter template field
- [ ] Extract status from frontmatter for plan completion checks
- [ ] Group results by type for DoD validation

---

## Verification

- [ ] /close E2-xxx finds all associated documents
- [ ] /close works without haios-status.json work_items section
- [ ] DoD validation still checks plan statuses correctly
- [ ] Performance acceptable (grep should be <1s)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Grep misses documents | High | Test with known backlog IDs |
| Performance slow | Low | Grep is fast; limit to docs/ |
| Frontmatter variations | Medium | Support both `backlog_id:` and `backlog_ids:` |

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
- E2-041: haios-status Work Items Removal (unblocked by this)

---
