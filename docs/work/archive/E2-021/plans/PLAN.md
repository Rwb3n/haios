---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-021
title: "Memory Reference Governance"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 21:56:05
# Implementation Plan: Memory Reference Governance

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement memory reference governance for backlog items and investigations. Create a closed learning loop where:
1. Investigations MUST produce memory references (via `ingester_ingest`)
2. Backlog items SHOULD link to those memory references
3. Future work can query memory for context on pending items

**Scope (Partial - Session 68):** Deliverables 1-3 only. Deliverable 4 (`/new-backlog-item` command) deferred to E2-029.

---

## Problem Statement

Backlog items inconsistently link to memory concepts. No closed learning loop exists between:
- Discovery work (investigations) that produce insights
- Memory storage of those insights
- Backlog items that should reference the insights
- Future sessions that query memory for context

**Evidence (Session 50):** E2-021 created with memory concepts 64653-64669, but pattern not enforced.

**Root Cause:** No governance mechanism ensures memory linkage. Manual process is skipped under time pressure.

---

## Methodology: AODEV TDD

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
              |          |
              v          v
           (Tests)   (Implementation)
```

This plan uses light TDD - validation tests for hook changes.

---

## Proposed Changes

### 1. CLAUDE.md Governance Triggers (Memory-Specific Rules)

Add memory-specific MUST/SHOULD/MAY rules to the existing governance triggers table.

**Tier 1 (MUST):**
| Trigger | Action | Rationale |
|---------|--------|-----------|
| Complete investigation | **MUST** store findings via `ingester_ingest` | Capture WHY, not just WHAT |
| Close work item | **MUST** have WHY captured in memory | DoD requirement (ADR-033) |

**Tier 2 (SHOULD):**
| Trigger | Action | Rationale |
|---------|--------|-----------|
| Create backlog item from investigation | **SHOULD** include `memory_refs` | Link to source insights |
| Session insights worth preserving | **SHOULD** use `ingester_ingest` | Compound learning |

- [x] Add memory triggers to Tier 1 table
- [x] Add memory triggers to Tier 2 table
- [x] Add memory_refs documentation to backlog section

### 2. ValidateTemplate.ps1 - Add memory_refs Field

Add `memory_refs` as an OptionalField for backlog_item template.

- [x] Add `memory_refs` to OptionalFields array (line 83)
- [x] No validation logic needed (optional field, any format)

### 3. PreToolUse.ps1 - Memory Reference Validation (Warn Only)

Add soft validation when editing backlog.md - warn if memory_refs missing for investigation-spawned items.

**Design Decision:** WARN only, not BLOCK. Reasons:
1. Investigations may be in-progress (no memory refs yet)
2. Not all backlog items come from investigations
3. Hard enforcement would be ceremony-heavy

- [x] Detect backlog.md edits
- [x] Parse frontmatter for `spawned_by` field
- [x] If spawned_by contains INV-* and no memory_refs, emit warning
- [x] Test: Edit backlog.md with/without memory_refs (5 tests pass)

### 4. DEFERRED: /new-backlog-item Command

This is E2-029. Not in scope for this plan.

---

## Verification

- [x] Governance triggers table updated in CLAUDE.md
- [x] ValidateTemplate.ps1 accepts memory_refs field
- [x] PreToolUse.ps1 warns on missing memory_refs for INV-* spawned items
- [x] No test regressions (33 existing tests pass, 5 new tests pass)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Warning fatigue | Low | Only warn for investigation-spawned items |
| Memory refs format inconsistent | Low | Document expected format, don't validate |
| Backlog.md parsing complexity | Medium | Simple regex, not full YAML parse |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 68 | 2025-12-13 | TBD | complete | Partial implementation (3/4 deliverables) |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (38 total: 5 new + 33 existing)
- [x] WHY captured (Concepts 71223-71235)
- [x] Documentation current (CLAUDE.md updated)
- [x] All traced files complete (partial - deliverable 4 deferred to E2-029)

---

## References

- ADR-033: Work Item Lifecycle (DoD includes WHY capture)
- ADR-035: RFC 2119 Governance Signaling
- E2-037: RFC 2119 Governance Signaling System (framework)
- E2-029: /new-backlog-item Command (deferred deliverable 4)
- Memory Concepts (Session 50): 64653-64669
- Memory Concepts (Session 68 closure): 71223-71235

---
