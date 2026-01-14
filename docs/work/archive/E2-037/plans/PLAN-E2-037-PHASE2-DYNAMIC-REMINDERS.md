---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-037
title: "RFC 2119 Phase 2 - Dynamic Reminders"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 21:02:34
# Implementation Plan: RFC 2119 Phase 2 - Dynamic Reminders

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Add dynamic RFC 2119 governance reminders to UserPromptSubmit hook. When the hook detects trigger keywords in user messages, inject contextual MUST/SHOULD guidance.

---

## Problem Statement

Phase 1 added static governance triggers to CLAUDE.md. However:
- Claude may not re-read CLAUDE.md mid-session
- Long sessions may cause agents to "forget" the rules
- Trigger situations are detectable from user messages

**Solution:** UserPromptSubmit hook detects trigger keywords and injects reminders at prompt time.

---

## Current UserPromptSubmit Structure

```
Part 1: Date/Time Context (lines 32-39)
Part 2: Memory Context Injection (lines 41-89)
Part 3: Lifecycle Sequence Enforcement (lines 91-167) - E2-009
Part 4: [NEW] RFC 2119 Governance Reminders
```

---

## Methodology: AODEV TDD

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
              |          |
              v          v
           (Tests)   (Implementation)
```

Tests defined for keyword detection and reminder injection.

---

## Proposed Changes

### 1. UserPromptSubmit.ps1 - Part 4: Governance Reminders

Add new section after Part 3 (line ~167):

```powershell
# === PART 4: RFC 2119 Governance Reminders (E2-037, Session 66) ===
# Detect trigger keywords and inject MUST/SHOULD guidance
```

**Trigger Detection Rules:**

| Trigger Pattern | Reminder | Tier |
|-----------------|----------|------|
| `bug`, `issue`, `gap`, `problem`, `broken`, `wrong`, `error` + `found`/`discovered`/`noticed` | MUST /new-investigation | MUST |
| `sql`, `query`, `database`, `select`, `table` | MUST schema-verifier | MUST |
| `close`, `done`, `complete`, `finish` + backlog ID | MUST /close | MUST |
| `decision`, `decided`, `chose`, `architecture` | SHOULD /new-adr | SHOULD |
| `checkpoint`, `session end`, `wrapping up` | SHOULD /new-checkpoint | SHOULD |

**Design Decisions:**

- **DD-037-P2-01:** Only trigger on MUST rules initially. SHOULD rules may be too noisy.
- **DD-037-P2-02:** Combine keyword pairs to reduce false positives (e.g., "bug" alone is too broad, "found bug" is specific).
- **DD-037-P2-03:** Add override: "skip reminder" in message bypasses injection.
- **DD-037-P2-04:** Output format matches Part 3 style for consistency.
- **DD-037-P2-05:** Use E2-036 corrected regex: `E2-[A-Z]*-?\d{3}` (supports E2-FIX-XXX).

**Pre-requisite Fix (discovered during verification):**
- Part 3 (line 108) uses outdated regex `(E2-\d+|INV-\d+|TD-\d+)`
- Must update to `(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})` for E2-FIX-XXX support
- Fix as part of Phase 2 implementation

### 2. Fix Part 3 Regex (E2-036 alignment)

- [x] Update line 108: `(E2-\d+|INV-\d+|TD-\d+)` -> `(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})` (Session 67)

### 3. Test File - .claude/hooks/tests/Test-GovernanceReminders.ps1

- [x] Test: Discovery keywords trigger investigation reminder
- [x] Test: SQL keywords trigger schema-verifier reminder
- [x] Test: Close keywords trigger /close reminder
- [x] Test: Override "skip reminder" bypasses detection
- [x] Test: Single keyword without context does NOT trigger
- [x] Test: E2-FIX-XXX format detected correctly
- [x] All 25 tests passing (Session 67)

### 4. Documentation Updates

- [x] Update hooks README with Part 4 description (Session 67)
- [x] CLAUDE.md already has governance_reminders in haios-status.json hook features

---

## Implementation Pseudocode

```powershell
# === PART 4: RFC 2119 Governance Reminders (E2-037) ===
if ($userPrompt -and -not ($userPrompt -match "skip reminder")) {

    # MUST: Discovery -> /new-investigation
    $discoveryTrigger = $userPrompt -match "(bug|issue|gap|problem|broken|wrong|error).*(found|discovered|noticed|identified)" -or
                        $userPrompt -match "(found|discovered|noticed|identified).*(bug|issue|gap|problem|broken|wrong|error)"
    if ($discoveryTrigger) {
        Write-Output ""
        Write-Output "--- RFC 2119 Governance (MUST) ---"
        Write-Output "Discovery detected. MUST use /new-investigation to document before fixing."
        Write-Output "Command: /new-investigation <backlog_id> <title>"
        Write-Output "Override: Include 'skip reminder' in your message."
        Write-Output "--- End Governance Reminder ---"
    }

    # MUST: SQL -> schema-verifier
    $sqlTrigger = $userPrompt -match "(run|execute|write).*(sql|query)" -or
                  $userPrompt -match "(select|insert|update|delete)\s+from"
    if ($sqlTrigger) {
        Write-Output ""
        Write-Output "--- RFC 2119 Governance (MUST) ---"
        Write-Output "SQL intent detected. MUST use schema-verifier subagent first."
        Write-Output "Command: Task(prompt='...', subagent_type='schema-verifier')"
        Write-Output "Override: Include 'skip reminder' in your message."
        Write-Output "--- End Governance Reminder ---"
    }

    # MUST: Close -> /close (E2-036 corrected regex)
    $closeTrigger = $userPrompt -match "(close|complete|finish|done).*(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})"
    if ($closeTrigger) {
        $backlogMatch = [regex]::Match($userPrompt, "(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})")
        if ($backlogMatch.Success) {
            Write-Output ""
            Write-Output "--- RFC 2119 Governance (MUST) ---"
            Write-Output "Work item closure detected. MUST use /close to validate DoD."
            Write-Output "Command: /close $($backlogMatch.Value)"
            Write-Output "Override: Include 'skip reminder' in your message."
            Write-Output "--- End Governance Reminder ---"
        }
    }
}
```

---

## Verification

- [x] All 25 tests pass (Session 67)
- [x] False positive rate acceptable (keyword pairs reduce false positives)
- [x] Override works correctly ("skip reminder" bypass)
- [x] Output format consistent with Part 3
- [x] No performance regression (regex only, no external calls)
- [x] Part 3 regex fixed (E2-FIX-XXX support)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positives (noise) | Medium | Require keyword pairs, not singles |
| User annoyance | Medium | Provide clear override mechanism |
| Performance regression | Low | Regex is fast; no external calls |
| Conflict with Part 3 | Low | Separate concerns, different triggers |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 66 | 2025-12-13 | Session 66 | complete | Plan created, approved |
| 67 | 2025-12-13 | Session 67 | complete | Phase 2 implementation complete |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (25/25)
- [x] WHY captured (stored below)
- [x] Documentation current (hooks README updated)
- [x] All traced files complete

---

## References

- ADR-035: RFC 2119 Governance Signaling (accepted)
- PLAN-E2-037-RFC2119-GOVERNANCE-SIGNALING.md (Phase 1 complete)
- .claude/hooks/UserPromptSubmit.ps1 (current implementation)
- docs/checkpoints/2025-12-13-02-SESSION-65-rfc2119-governance-signaling.md

---
