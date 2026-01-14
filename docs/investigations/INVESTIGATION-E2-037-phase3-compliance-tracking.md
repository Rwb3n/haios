---
template: investigation
status: complete
date: 2025-12-13
backlog_id: E2-037-phase3
title: "Investigation: Phase 3 Compliance Tracking"
author: Hephaestus
lifecycle_phase: conclude
version: "1.1"
session: 65
closed_session: 102
closure_note: "SUPERSEDED by INV-020. Core question (do agents follow MUST/SHOULD/MAY?) answered by INV-020: L2 suggestions ignored ~20%, only L3/L4 enforcement works. Hook migration to Python made Phase 2 tracking moot."
generated: 2025-12-23
last_updated: 2025-12-23T11:02:28
---
# Investigation: Phase 3 Compliance Tracking

@docs/README.md
@docs/epistemic_state.md

---

## Context

E2-037 Phase 1 and Phase 2 are complete:
- **Phase 1 (Session 66):** Static rules added to CLAUDE.md (lines 234-263)
- **Phase 2 (Session 67):** Dynamic reminders in UserPromptSubmit.ps1 (Part 4)

Phase 3 is about measuring whether these signals are effective. Do agents actually follow MUST/SHOULD/MAY guidance? Which signals get ignored? What patterns emerge?

---

## Objective

1. Measure RFC 2119 signal compliance over 5+ sessions
2. Identify which signals are followed vs ignored
3. Determine if false positive rate is acceptable
4. Recommend trigger refinements based on observed patterns

---

## Scope

### In Scope
- Discovery trigger compliance (bug/issue + /new-investigation)
- SQL trigger compliance (query intent + schema-verifier)
- Close trigger compliance (close + backlog ID + /close)
- Override usage patterns ("skip reminder")
- Checkpoint and handoff review for governance signals

### Out of Scope
- SHOULD tier tracking (not yet implemented in hooks)
- MAY tier tracking (optional, no enforcement)
- Automated compliance scoring (future enhancement)

---

## Hypotheses

1. **H1:** MUST triggers will have >80% compliance rate (agents follow most reminders)
2. **H2:** SQL trigger will have highest compliance (already enforced by PreToolUse)
3. **H3:** Discovery trigger may have lower compliance (semantic detection is harder)
4. **H4:** Override usage will be <10% (escape hatch rarely needed)

---

## Investigation Steps

1. [ ] Wait for 5 sessions with Phase 2 active
2. [ ] Review session transcripts for trigger events
3. [ ] Count: trigger fired, command used, override used, ignored
4. [ ] Calculate compliance rates per trigger type
5. [ ] Identify false positive patterns (triggers that shouldn't fire)
6. [ ] Document ignored signals and reasons

---

## Findings

**Status:** Pending - requires 5 sessions with Phase 2 active

### Session Tracking Table

| Session | Discovery Triggers | SQL Triggers | Close Triggers | Overrides | Notes |
|---------|-------------------|--------------|----------------|-----------|-------|
| 67 | - | - | - | - | Phase 2 implemented |
| 68 | 0 fired, N/A | 0 fired, N/A | 0 fired, N/A | 0 | Implementation session (E2-021). No discovery/SQL/close events. |
| 69 | | | | | |
| 70 | | | | | |
| 71 | | | | | |

**Session 68 Analysis:**
- No discovery triggers expected - planned implementation work, not debugging
- No SQL triggers expected - worked with hooks/scripts, not database queries
- No close triggers expected - E2-021 partial completion, not full closure
- First clean baseline session: triggers should NOT fire during pure implementation work

---

## Spawned Work Items

- [ ] None yet - depends on findings

Potential future items:
- E2-038: Trigger refinement based on compliance data
- E2-039: SHOULD tier hook implementation
- E2-040: Automated compliance dashboard

---

## Expected Deliverables

- [ ] Compliance rates per trigger type
- [ ] False positive analysis
- [ ] Trigger refinement recommendations
- [ ] Memory storage (concepts)

---

## References

- ADR-035: RFC 2119 Governance Signaling (accepted)
- PLAN-E2-037-RFC2119-GOVERNANCE-SIGNALING.md (complete)
- PLAN-E2-037-PHASE2-DYNAMIC-REMINDERS.md (complete)
- PLAN-E2-021-MEMORY-REFERENCE-GOVERNANCE.md (Session 68 - E2-021 partial)
- .claude/hooks/UserPromptSubmit.ps1 (Part 4)
- .claude/hooks/tests/Test-GovernanceReminders.ps1 (25 tests)
- .claude/hooks/tests/Test-MemoryRefsValidation.ps1 (5 tests - Session 68)

---
