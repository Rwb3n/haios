---
template: implementation_plan
status: complete
date: 2025-12-11
backlog_id: E2-009
title: "Lifecycle Sequence Enforcement"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
completed_session: 63
completion_note: "UserPromptSubmit hook enhanced with lifecycle enforcement - detects plan-creation intent, checks prerequisites, injects guidance"
---
# generated: 2025-12-11
# System Auto: last updated on: 2025-12-11 23:53:53
# Implementation Plan: Lifecycle Sequence Enforcement

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Enforce the canonical work lifecycle (ADR-034) by guiding agents through the proper sequence:
```
BACKLOG -> DISCOVERY -> DESIGN -> PLAN -> IMPLEMENT -> VERIFY -> CLOSE
```

When an agent attempts to skip phases (e.g., jumping straight to implementation), the system prompts them to complete prerequisite phases first.

---

## Problem Statement

**Current state:** Agents can create PLAN-* files without any prior analysis (INVESTIGATION-*) or design (ADR-*). This leads to:
- Plans based on assumptions rather than investigation
- Rework when assumptions prove wrong
- No documented "WHY" for decisions

**Desired state:** The governance system gently enforces lifecycle sequence:
1. Detect implementation intent (creating PLAN-*, writing code)
2. Check if prerequisite phases exist (INVESTIGATION-* or ADR-* for the work item)
3. If missing, prompt agent to complete discovery/design first
4. Allow override for trivial work (operator discretion)

**Blocking dependency resolved:** INV-006 complete, ADR-034 accepted - lifecycle phases now defined.

---

## Methodology

**Soft enforcement via UserPromptSubmit hook** - inject guidance when lifecycle sequence is violated, but don't hard-block.

---

## Proposed Changes

### 1. UserPromptSubmit Hook Enhancement
- [x] Detect plan-creation intent (keywords: "create plan", "new plan", "/new-plan", "implement", "add feature")
- [x] Query haios-status.json for active work item context
- [x] Check if INVESTIGATION-* or ADR-* exists for the work item
- [x] If missing prerequisite, inject reminder:
  ```
  Lifecycle Reminder: No discovery/design document found for this work item.
  Consider creating an INVESTIGATION-* to analyze the problem first.
  Use /new-investigation <backlog_id> <title> to start discovery.
  Override: Include "skip discovery" in your message to proceed without.
  ```

### 2. New Command: /new-investigation (E2-032 - Session 62)
- [x] Create `.claude/commands/new-investigation.md`
- [x] Rename template `handoff_investigation.md` -> `investigation.md`
- [x] Scaffold INVESTIGATION-<backlog_id>-<title>.md files
- [x] Default location: `docs/investigations/` (new directory)

### 3. PreToolUse Enhancement (Optional - DEFERRED)
- [ ] When Write/Edit targets `docs/plans/PLAN-*.md`:
  - Check if corresponding INVESTIGATION-* exists
  - If not, warn but allow (soft enforcement)
- **Note:** UserPromptSubmit soft enforcement is sufficient for now

### 4. Template and Directory Updates (E2-032 - Session 62)
- [x] Create `docs/investigations/` directory
- [x] Create `investigation` template (from `handoff_investigation`)
- [x] Deprecate `handoff` and `handoff_investigation` templates
- [ ] Archive `docs/handoff/HANDOFF_TYPES.md` (deferred - not blocking)

---

## Lifecycle Enforcement Matrix

| Phase | Required Before | Document Type | Check |
|-------|-----------------|---------------|-------|
| DISCOVERY | BACKLOG exists | INVESTIGATION-* | Work item in backlog.md |
| DESIGN | DISCOVERY (for non-trivial) | ADR-* | INVESTIGATION-* exists OR operator override |
| PLAN | DISCOVERY or DESIGN | PLAN-* | INVESTIGATION-* or ADR-* exists |
| IMPLEMENT | PLAN (for significant work) | (code) | PLAN-* exists OR trivial change |
| VERIFY | IMPLEMENT | REPORT-* | Code exists |
| CLOSE | VERIFY | (/close) | All DoD criteria met |

---

## Verification

- [x] UserPromptSubmit hook detects plan-creation intent
- [x] Hook checks for prerequisite documents
- [x] Missing prerequisite injects guidance message
- [x] "skip discovery" override works
- [x] /new-investigation command works (E2-032)
- [x] Investigation template scaffolds correctly (E2-032)
- [x] Documentation updated (CLAUDE.md, ADR-034 implementation checklist)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positives (every message triggers) | High | Precise keyword detection, require work item context |
| Annoyance from over-prompting | Medium | Soft enforcement, easy override, remember overrides per session |
| haios-status.json stale | Low | Check file timestamps, warn if stale |
| Performance (hook adds latency) | Low | Simple file checks, no LLM calls in hook |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 61 | 2025-12-11 | - | plan_created | ADR-034 unblocked E2-009 |
| 63 | 2025-12-11 | - | complete | Hook enhanced with lifecycle enforcement |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (hook logic tested manually)
- [x] WHY captured (reasoning stored to memory)
- [x] Documentation current (CLAUDE.md, hooks README)
- [x] All traced files complete

---

## Dependencies

- **E2-032** - ADR-034 Implementation (MUST complete first)
  - Provides `/new-investigation` command
  - Provides `investigation` template
  - Provides `docs/investigations/` directory

---

## References

- **ADR-034** - Document Ontology and Work Lifecycle (defines phases)
- **ADR-033** - Work Item Lifecycle Governance (DoD)
- **INV-006** - Document Ontology Audit (investigation that led here)
- **E2-032** - ADR-034 Implementation (prerequisite)
- **Session 61** - Plan creation

---
