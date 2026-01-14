---
template: implementation_plan
status: complete
date: 2025-12-08
backlog_id: PLAN-ADR-031-IMPLEMENTATION
title: "ADR-031 Operational Self-Awareness Implementation"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-08
# System Auto: last updated on: 2025-12-09 18:49:21
# Implementation Plan: ADR-031 Operational Self-Awareness Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement ADR-031 Operational Self-Awareness: extend `UpdateHaiosStatus.ps1` to parse document content for outstanding items, add `workspace` section to `haios-status.json`, and create `/workspace` command for operational visibility.

**Success Criteria:**
- System knows what checkpoints have pending items
- System knows what handoffs are waiting for pickup
- System knows what plans are approved but not started
- `/coldstart` composes `/haios` + `/workspace` naturally

---

## Problem Statement

HAIOS has governance infrastructure (hooks, commands, templates) but cannot answer:
1. What work is outstanding?
2. What's blocked?
3. What's forgotten?
4. What's the operational rhythm?

The system governs document creation but doesn't understand document state.

**ADR:** docs/ADR/ADR-031-workspace-awareness.md (APPROVED Session 47)

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

## Phase 3: Extend haios-status.json Schema

### 3.1 OBSERVE - Define Expected Behavior
- [ ] Document workspace section schema (JSON structure)
- [ ] Document outstanding item detection heuristics
- [ ] Document staleness thresholds

### 3.2 ANALYZE - Write Failing Tests
- [ ] Test: `Get-OutstandingItems` returns pending checkboxes from checkpoint files
- [ ] Test: `Get-StaleItems` detects handoffs older than N days
- [ ] Test: `Get-WorkspaceSummary` aggregates counts correctly
- [ ] Test: Schema validates against expected structure

### 3.3 DECIDE - Design Decisions
- DD-031-01: Outstanding item = unchecked `- [ ]` in "Pending Work" section
- DD-031-02: Stale threshold = 3 days for handoffs, 7 days for plans
- DD-031-03: Approved-not-started = `status: approved` with no corresponding checkpoint

### 3.4 EXECUTE - Implement
- [ ] Add `Get-OutstandingItems` function to UpdateHaiosStatus.ps1
- [ ] Add `Get-StaleItems` function to UpdateHaiosStatus.ps1
- [ ] Add `Get-WorkspaceSummary` function to UpdateHaiosStatus.ps1
- [ ] Add `workspace` section to status output structure

### 3.5 VERIFY - All Tests Pass
- [ ] Run test script: `.claude/hooks/tests/Test-UpdateHaiosStatus.ps1`
- [ ] Verify haios-status.json has workspace section
- [ ] Manual verification: content matches file reality

---

## Phase 4: Create /workspace Command

### 4.1 OBSERVE - Define Expected Behavior
- [ ] Command outputs structured workspace status
- [ ] Shows outstanding items prominently
- [ ] Shows stale items with age
- [ ] Provides recommendations

### 4.2 ANALYZE - Write Failing Tests
- [ ] Test: Command file exists at `.claude/commands/workspace.md`
- [ ] Test: Command reads from haios-status.json workspace section
- [ ] Test: Output format matches specification

### 4.3 DECIDE - Design Decisions
- DD-031-04: Format = markdown with sections (Outstanding, Stale, Recommendations)
- DD-031-05: Recommendations = prioritized list based on age and status

### 4.4 EXECUTE - Implement
- [ ] Create `.claude/commands/workspace.md`
- [ ] Implement PowerShell one-liner to extract workspace section
- [ ] Format output with sections

### 4.5 VERIFY - All Tests Pass
- [ ] `/workspace` command produces expected output
- [ ] Output is readable and actionable

---

## Phase 5: Integrate with /coldstart

### 5.1 OBSERVE - Define Expected Behavior
- [ ] `/coldstart` = `/haios` logic + `/workspace` logic + memory query
- [ ] Outstanding items surfaced at session start
- [ ] Composable architecture

### 5.2 ANALYZE - Write Failing Tests
- [ ] Test: coldstart.md includes workspace status section
- [ ] Test: Outstanding items appear in coldstart output

### 5.3 DECIDE - Design Decisions
- DD-031-06: Composition via inline expansion (not subcommand call)
- DD-031-07: Outstanding items appear BEFORE memory query (priority)

### 5.4 EXECUTE - Implement
- [ ] Modify `.claude/commands/coldstart.md` to include workspace section
- [ ] Add "Outstanding Work" section after system status

### 5.5 VERIFY - All Tests Pass
- [ ] `/coldstart` shows workspace status
- [ ] User sees outstanding items at session start

---

## Workspace Schema (Target State)

```json
{
  "workspace": {
    "outstanding": {
      "checkpoints": [
        {"path": "...", "pending_items": ["Item 1", "Item 2"]}
      ],
      "handoffs": [
        {"path": "...", "status": "pending", "age_days": 2}
      ],
      "plans": [
        {"path": "...", "status": "approved", "not_started": true}
      ]
    },
    "stale": {
      "items": [
        {"path": "...", "type": "handoff", "age_days": 5}
      ]
    },
    "summary": {
      "pending_handoffs": 3,
      "incomplete_checkpoints": 1,
      "stale_items": 2,
      "approved_not_started": 4
    }
  }
}
```

---

## Outstanding Item Heuristics

| Document Type | Outstanding Pattern | Detection |
|---------------|---------------------|-----------|
| Checkpoint | Unchecked boxes in "Pending Work" | `- [ ]` after "## Pending" |
| Handoff | Status not "done" or "resolved" | `status: pending/open` |
| Plan | Approved but no execution checkpoint | `status: approved` + no session ref |
| ADR | Proposed but not decided | `status: proposed` > 3 days |

---

## Verification Checklist

- [ ] All Phase 3 tests pass
- [ ] All Phase 4 tests pass
- [ ] All Phase 5 tests pass
- [ ] haios-status.json includes workspace section
- [ ] /workspace command works
- [ ] /coldstart includes workspace status
- [ ] Documentation updated (epistemic_state.md)
- [ ] Backlog E2-013 marked complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PowerShell test framework complexity | Medium | Use simple assertion pattern, not full Pester |
| Heuristics produce false positives | Low | Tune thresholds based on real data |
| UpdateHaiosStatus.ps1 grows too large | Low | Modular functions, consider splitting later |

---

## References

- [ADR-031: Operational Self-Awareness](../ADR/ADR-031-workspace-awareness.md)
- [Session 46 Checkpoint](../checkpoints/2025-12-08-02-SESSION-46-adr031-operational-self-awareness.md)
- [E2-013 Backlog Item](../pm/backlog.md#e2-013)
- [UpdateHaiosStatus.ps1](../../.claude/hooks/UpdateHaiosStatus.ps1)
- Memory Concepts: 64608 (vision alignment), 37910/37935/10452 (hook framework)

---


<!-- VALIDATION ERRORS (2025-12-08 21:05:06):
  - ERROR: Invalid status 'completed' for implementation_plan template. Allowed: draft, approved, rejected
-->
