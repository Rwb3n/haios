---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-037
title: "RFC 2119 Governance Signaling Implementation"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 21:12:15
# Implementation Plan: RFC 2119 Governance Signaling Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement RFC 2119 governance signaling system to bridge the gap between work events (discoveries, decisions) and artifact creation (investigations, ADRs, plans).

---

## Problem Statement

Session 65 discovered the "Two-Track Problem":
- **Work Track** (ephemeral): discover -> design -> plan -> implement -> verify
- **Artifact Track** (persistent): INVESTIGATION -> ADR -> PLAN -> CHECKPOINT -> REPORT

No automatic bridge exists. Work events in Claude's reasoning don't trigger artifact spawning. Hooks can't see semantic events (discoveries happen in thought, not file operations).

**Solution:** RFC 2119 signals (MUST/SHOULD/MAY) guide Claude toward proper commands/skills/agents at semantically appropriate moments.

---

## Methodology: AODEV TDD

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
              |          |
              v          v
           (Tests)   (Implementation)
```

Note: Phase 1 is documentation-only (CLAUDE.md update). No code tests needed.
Phases 2+ involve hook changes - tests will be defined then.

---

## Proposed Changes

### Phase 1: Static Rules (CLAUDE.md) - Session 66 - COMPLETE
- [x] Add "Governance Triggers" section to CLAUDE.md (lines 234-263)
- [x] Define MUST tier rules (4 rules)
- [x] Define SHOULD tier rules (4 rules)
- [x] Define MAY tier rules (2 rules)
- [x] Reference ADR-035

### Phase 2: Dynamic Reminders (UserPromptSubmit) - Session 67 - COMPLETE
- [x] Enhance UserPromptSubmit to detect trigger keywords (Part 4, lines 170-217)
- [x] Inject contextual reminders (discovery, SQL, close triggers)
- [x] Measure false positive rate (keyword pairs reduce false positives)
- [x] Define tests for keyword detection (25 tests in Test-GovernanceReminders.ps1)
- [x] Part 3 regex fixed for E2-FIX-XXX support
- [x] See: PLAN-E2-037-PHASE2-DYNAMIC-REMINDERS.md (complete)

### Phase 3: Compliance Tracking - Session 67 - SCAFFOLDED
- [ ] Track signal compliance over 5 sessions
- [ ] Identify ignored signals and patterns
- [ ] Iterate on trigger definitions
- [x] **Investigation created:** INVESTIGATION-E2-037-phase3-compliance-tracking.md
- Status: Pending data collection (Sessions 68-72)

### Phase 4: Mechanical Additions (Optional) - Session 67 - SCAFFOLDED
- [ ] PostToolUse validation for governed documents
- [ ] Stop hook checkpoint prompt
- [ ] Evaluate hybrid value
- [x] **Plan created:** PLAN-E2-037-PHASE4-MECHANICAL-ADDITIONS.md (draft)
- Status: Blocked on Phase 3 findings

---

## RFC 2119 Signal Tiers (from ADR-035)

### Tier 1: MUST (Absolute Requirements)

| Trigger | Action | Rationale |
|---------|--------|-----------|
| Discover bug/gap/issue | `/new-investigation` | Document before fixing |
| Any SQL query needed | `schema-verifier` subagent | Verify schema first |
| Close work item | `/close <id>` | Validate DoD |
| Create governed document | `/new-*` command | Use templates |

### Tier 2: SHOULD (Strong Recommendations)

| Trigger | Action | Rationale |
|---------|--------|-----------|
| Make architectural decision | `/new-adr` | Document significant choices |
| Session work complete | `/new-checkpoint` | Capture progress |
| Verification complete | `/new-report` | Document results |
| Complex memory retrieval | `memory-agent` skill | Better context |

### Tier 3: MAY (Optional)

| Trigger | Action | Rationale |
|---------|--------|-----------|
| Exploring codebase | `Explore` subagent | Faster than manual grep |
| Quick status check | `/status` | Quick health check |

---

## Verification

- [x] CLAUDE.md contains governance triggers section (lines 234-263)
- [x] Rules match ADR-035 signal tiers
- [x] No syntax errors in CLAUDE.md
- [x] Dynamic reminders active in UserPromptSubmit.ps1 (Part 4)
- [x] 25 tests passing for Phase 2 keyword detection

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude ignores SHOULD/MAY | Medium | Start with MUST enforcement, expand gradually |
| False positives in keyword detection | Medium | Phase 2 pilot with logging before enforcement |
| Rules become stale | Low | Review every 10 sessions, iterate on triggers |
| Context bloat from signals | Low | Signals are text, not tool calls - minimal overhead |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 66 | 2025-12-13 | Session 66 | complete | Phase 1 COMPLETE |
| 67 | 2025-12-13 | Session 67 | complete | Phase 2 COMPLETE |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (25/25 for Phase 2)
- [x] WHY captured: Concepts 70957-70963 (Phase 1), 71216-71217 (Phase 2)
- [x] Documentation current (CLAUDE.md + hooks README)
- [x] All traced files complete

**Note:** Phases 3-4 are future enhancements, not blocking completion.

---

## References

**ADR:**
- ADR-035: RFC 2119 Governance Signaling (accepted Session 66)

**Plans:**
- PLAN-E2-037-RFC2119-GOVERNANCE-SIGNALING.md (this file - Phase 1+2 complete)
- PLAN-E2-037-PHASE2-DYNAMIC-REMINDERS.md (complete)
- PLAN-E2-037-PHASE4-MECHANICAL-ADDITIONS.md (draft, blocked on Phase 3)

**Investigations:**
- INVESTIGATION-E2-037-governance-framework-constellation.md (Session 66)
- INVESTIGATION-E2-037-phase3-compliance-tracking.md (pending data)

**Implementation:**
- CLAUDE.md lines 234-263 (governance triggers section)
- .claude/hooks/UserPromptSubmit.ps1 Part 4 (dynamic reminders)
- .claude/hooks/tests/Test-GovernanceReminders.ps1 (25 tests)

**Memory:**
- Concepts 70904-70939 (ontology), 70954-70956 (constellation)
- Concepts 70957-70963 (Phase 1 WHY), 71216-71217 (Phase 2 WHY)

---
