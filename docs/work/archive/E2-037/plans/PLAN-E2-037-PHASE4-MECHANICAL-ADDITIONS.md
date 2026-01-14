---
template: implementation_plan
status: draft
date: 2025-12-13
backlog_id: E2-037
title: "Phase 4 Mechanical Additions"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 22:03:28
# Implementation Plan: Phase 4 Mechanical Additions

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Add mechanical (hook-based) enforcement to complement semantic (RFC 2119) guidance. Where hooks CAN detect governance-relevant events, add automation for defense-in-depth.

---

## Problem Statement

Phase 1-2 provide semantic guidance (CLAUDE.md rules + UserPromptSubmit reminders). But some governance events ARE hook-detectable:

1. **PostToolUse:** Can validate governed documents match templates
2. **Stop:** Can prompt for checkpoint creation before session end
3. **PreToolUse:** Already blocks direct SQL, raw writes to governed paths

Phase 4 evaluates which mechanical additions provide value without causing friction.

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

### 1. PostToolUse: Governed Document Validation

**Current State (verified Session 67):**
- PostToolUse.ps1 (lines 240-288) ALREADY validates: templates, directives, plans, reports, checkpoints
- ValidateTemplateHook.ps1 DUPLICATES this coverage (same directories + guides, .claude/mcp/)
- MISSING: `docs/ADR/`, `docs/investigations/`, `docs/handoff/`

**Proposed Changes:**
- [ ] Consolidate: Remove duplicate inline validation in PostToolUse.ps1 (defer to ValidateTemplateHook)
- [ ] Extend ValidateTemplateHook to cover: `docs/ADR/`, `docs/investigations/`, `docs/handoff/`
- [ ] Add frontmatter field checks (template, status, date, backlog_id where required)
- [ ] Tests: Test-GovernedDocValidation.ps1

**Design Decision:** Consolidate validation into ValidateTemplateHook. PostToolUse focuses on timestamps only.

### 2. Stop Hook: Checkpoint Prompt

**Current State (verified Session 67):**
- Stop.ps1 runs reasoning_extraction.py on session end
- Has stop_hook_active loop prevention
- Timeout: 10 seconds for Python extraction
- Does NOT have checkpoint prompt logic

**Proposed Changes:**
- [ ] Add checkpoint existence check (glob `docs/checkpoints/*-SESSION-*.md` for current date)
- [ ] Add significant work detection (check transcript for Edit/Write tool calls > threshold)
- [ ] Output reminder: "Consider creating checkpoint with /new-checkpoint"
- [ ] Tests: Test-StopCheckpointPrompt.ps1

**Design Decision:** Informational only. Don't block session end. Run BEFORE reasoning extraction.

### 3. Hybrid Value Evaluation

Document which mechanical additions complement vs conflict with semantic guidance.

- [ ] Create evaluation criteria matrix
- [ ] Test each addition over 3 sessions
- [ ] Document friction points
- [ ] Recommend keep/remove for each

---

## Verification

- [ ] PostToolUse validation tests pass
- [ ] Stop checkpoint prompt tests pass
- [ ] No performance regression (hooks <100ms)
- [ ] User friction acceptable (measured in Phase 3 tracking)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Duplicate validation noise | Medium | Coordinate with existing ValidateTemplateHook |
| Stop prompt annoyance | Low | Only prompt if significant work detected |
| Mechanical conflicts with semantic | Medium | Phase 3 compliance data informs decisions |
| Hook performance regression | Low | Regex-only checks, no external calls |

---

## Dependencies

- **INVESTIGATION-E2-037-phase3-compliance-tracking.md:** Phase 3 data informs which mechanical additions are valuable
- **ValidateTemplateHook.ps1:** Existing validation to EXTEND (add ADR, investigations, handoff paths)
- **PostToolUse.ps1:** Remove duplicate validation (lines 240-288), keep timestamps only
- **Stop.ps1:** Existing ReasoningBank extraction to EXTEND with checkpoint prompt

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 67 | 2025-12-13 | - | draft | Plan created |
| 67 | 2025-12-13 | - | verified | Grounded against current mechanisms |
| 68 | 2025-12-13 | - | blocked | E2-021 implemented; Phase 3 data collection in progress |

**Session 67 Verification Findings:**
- Task 1: Discovered duplicate validation (PostToolUse + ValidateTemplateHook). Plan updated to consolidate.
- Task 2: Stop.ps1 has infrastructure for extension. No checkpoint logic exists.
- Missing coverage identified: docs/ADR/, docs/investigations/, docs/handoff/

**Session 68 Context:**
- E2-021 partial implementation added memory_refs validation to PreToolUse.ps1 (WARN not BLOCK)
- This demonstrates the "soft governance" pattern: inform rather than enforce
- Phase 3 compliance tracking shows Session 68 as baseline (no triggers expected during pure implementation)
- Hypothesis validation: pure implementation sessions should NOT trigger governance reminders (confirmed)

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] All traced files complete

**Note:** This phase is OPTIONAL per ADR-035. Implementation depends on Phase 3 findings.

---

## References

- ADR-035: RFC 2119 Governance Signaling (accepted)
- PLAN-E2-037-RFC2119-GOVERNANCE-SIGNALING.md (Phase 1-2 complete)
- PLAN-E2-021-MEMORY-REFERENCE-GOVERNANCE.md (Session 68 - demonstrates soft governance pattern)
- INVESTIGATION-E2-037-phase3-compliance-tracking.md (in progress - Session 68 baseline added)
- INVESTIGATION-E2-037-governance-framework-constellation.md (Session 68 update)
- .claude/hooks/PostToolUse.ps1 (current implementation)
- .claude/hooks/Stop.ps1 (current implementation)
- .claude/hooks/PreToolUse.ps1 (E2-021 memory_refs warning added Session 68)

---
