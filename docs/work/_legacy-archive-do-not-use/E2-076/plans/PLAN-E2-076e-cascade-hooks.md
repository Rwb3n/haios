---
template: implementation_plan
status: complete
date: 2025-12-14
backlog_id: E2-076e
title: "Cascade Hooks (Heartbeat Mechanism)"
author: Hephaestus
lifecycle_phase: plan
session: 75
parent_plan: E2-076
spawned_by: PLAN-E2-076
related: [E2-076, E2-076d, E2-080, E2-081, ADR-033]
absorbs: [E2-033]
enables: [E2-084]
execution_layer: E2-080
version: "1.1"
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-16 22:36:30
# Implementation Plan: Cascade Hooks (Heartbeat Mechanism)

@docs/README.md
@docs/epistemic_state.md
@docs/plans/PLAN-E2-076-dag-governance-architecture-adr.md

---

## Goal

Implement heartbeat cascade mechanism where document status changes (e.g., plan COMPLETE) automatically propagate effects to dependent nodes: unblocking items, updating milestone progress, and surfacing actionable messages.

---

## Current State vs Desired State

### Current State

```powershell
# .claude/hooks/PostToolUse.ps1:240-288
# Current: Timestamp + Template Validation only
# Template validation runs but doesn't track status changes
if ($shouldValidate -and $extension -eq ".md") {
    # ... validation logic ...
}
# No cascade awareness
```

**Behavior:** PostToolUse adds timestamps and validates templates. Status changes are invisible to the system.

**Result:**
- Items remain "blocked" even after blocker completes
- Milestone progress not updated automatically
- Agent must manually track dependencies
- No "heartbeat" - graph is static

### Desired State

```powershell
# PostToolUse enhanced with cascade detection
# After template validation, check for status transitions
if ($statusChanged -and $newStatus -eq "complete") {
    # Find items with blocked_by: this-item
    # Surface: "E2-076 complete. Unblocked: E2-077"
    # Update milestone progress
    # Trigger haios-status refresh
}
```

**Behavior:** Status changes propagate through dependency graph

**Result:**
- Automatic unblock detection
- Milestone progress auto-updates
- Agent receives actionable cascade messages
- Graph is dynamic - heartbeat pulses on state change

---

## Core Concepts

### Heartbeat Trigger Events

| Event | Source | Cascade Actions |
|-------|--------|-----------------|
| Plan COMPLETE | `status: complete` in plan frontmatter | Unblock dependents, update milestone |
| Investigation COMPLETE | `status: complete` in investigation | Unblock plans waiting for discovery |
| ADR ACCEPTED | `status: accepted` in ADR | Unblock items waiting for design |
| Work Item CLOSED | `/close` command | Update related documents, milestone |

### Five Cascade Types (from E2-076 Section 2b + Session 80)

| Cascade Type | Edge | Trigger | Action |
|--------------|------|---------|--------|
| **Unblock** | `blocked_by` | Blocker completes | Mark dependent as READY, surface message |
| **Related** | `related` | Related item completes | Surface awareness: "may need review" |
| **Milestone** | `milestone` | Item in milestone completes | Recalculate %, surface delta |
| **Substantive** | Content reference | Item completes | Detect if docs need update, spawn work item |
| **Review Prompt** | `blocked_by` | Item unblocked | ALWAYS prompt plan review; extra urgency if stale (3+ sessions) |

### Mechanical vs Substantive Updates

| Update Type | Characteristics | Action |
|-------------|-----------------|--------|
| **Mechanical** | Status, dates, counts, frontmatter | Auto-update via hook |
| **Substantive** | Body content, new sections, rewrites | Spawn update work item (E2-UPDATE-xxx) |

**Detection heuristic:**
- Frontmatter-only reference → Mechanical (auto-update)
- Body content reference → Substantive (spawn work item)
- CLAUDE.md, README.md → Almost always substantive

### Cascade Message Format (Enhanced - Session 80)

```
--- Cascade (Heartbeat) ---
PLAN-E2-076d status: complete

[UNBLOCK]
  - E2-076e is now READY (was blocked_by: E2-076d)

[REVIEW PROMPT]  <-- NEW (Session 80)
  - E2-076e last updated: Session 75 (5 sessions ago)
  - SHOULD review plan against recent work before starting
  - Recent completions to consider: E2-076d, E2-081

[RELATED]
  - E2-069 may need review (related to E2-076d)

[MILESTONE]
  - M2-Governance: 78% -> 80% (+2%)

[SUBSTANTIVE]
  - CLAUDE.md references E2-076d -> Consider update
  - Spawned: E2-UPDATE-001 (CLAUDE.md governance section)

Action: E2-076e is next in sequence.
--- End Cascade ---
```

---

## Tests First (TDD)

> Note: PowerShell hooks verified via manual execution + unit test script.

### Test 1: Detect Status Change to Complete
```powershell
# Test: File with status: complete triggers cascade check
# Input: Plan file with status: complete in frontmatter
# Expected: Cascade detection function returns $true
```

### Test 2: Find Blocked Items
```powershell
# Test: Given completed item ID, find items with blocked_by reference
# Input: "E2-076d" completed
# Mock: haios-status.json with E2-076e.blocked_by = "E2-076d"
# Expected: Returns ["E2-076e"]
```

### Test 3: Cascade Message Output
```powershell
# Test: Cascade produces formatted message
# Expected: Output contains "--- Cascade (Heartbeat) ---"
# Expected: Output contains "Unblocked:"
```

### Test 4: No Cascade for Non-Complete Status
```powershell
# Test: status: draft does not trigger cascade
# Expected: No cascade message output
```

### Test 5: Milestone Progress Update
```powershell
# Test: Completing item updates milestone percentage
# Expected: haios-status.json milestone.progress incremented
```

---

## Detailed Design

### Architecture

```
PostToolUse.ps1
    |
    v
[Timestamp + Validation] (existing)
    |
    v
[Cascade Detection] (new)
    |
    +-- Is this a governed document? (.md in plans/checkpoints/etc)
    |       |
    |       +-- YES: Parse frontmatter
    |       |       |
    |       |       +-- status: complete/accepted?
    |       |               |
    |       |               +-- YES: Call CascadeHook.ps1
    |       |               +-- NO: Exit
    |       +-- NO: Exit
    |
    v
[Exit]

CascadeHook.ps1
    |
    +-- Input: file_path, backlog_id, new_status
    |
    +-- [Load haios-status.json]
    |
    +-- [1. UNBLOCK CASCADE]
    |       +-- Find items with blocked_by containing this-id
    |       +-- For each candidate:
    |       |       +-- Get ALL blockers from blocked_by array
    |       |       +-- Check if ALL blockers are complete
    |       |       +-- Only if ALL complete: "E2-xxx is now READY"
    |       |       +-- If partial: "E2-xxx still blocked by [remaining]"
    |       +-- Add to effects
    |
    +-- [2. RELATED CASCADE]
    |       +-- Find items with related: this-id
    |       +-- Add to effects: "E2-yyy may need review"
    |
    +-- [3. MILESTONE CASCADE]
    |       +-- Get milestone from frontmatter
    |       +-- Read milestone definition from haios-status.json
    |       +-- Calculate: complete_count / total_count
    |       +-- Add to effects: "M2: 78% -> 80%"
    |
    +-- [4. SUBSTANTIVE CASCADE]
    |       +-- Scan for docs referencing this-id in body
    |       +-- CLAUDE.md? README.md? -> Flag as substantive
    |       +-- Add to effects: "Consider update" or "Spawned: E2-UPDATE-xxx"
    |
    +-- [5. REFRESH STATUS] (NEW - required for freshness)
    |       +-- Call UpdateHaiosStatus.ps1
    |       +-- Regenerates haios-status.json with new state
    |       +-- Regenerates haios-status-slim.json for Vitals
    |
    +-- [Format cascade message with all effects]
    |
    +-- [Output to stdout]
```

### Function Signatures

```powershell
# CascadeHook.ps1

function Get-UnblockedItems {
    param(
        [string]$CompletedId,
        [PSObject]$HaiosStatus
    )
    # Returns: array of item IDs that have blocked_by: $CompletedId
}

function Get-RelatedItems {
    param(
        [string]$CompletedId,
        [PSObject]$HaiosStatus
    )
    # Returns: array of item IDs that have related: $CompletedId
}

function Get-MilestoneDelta {
    param(
        [string]$CompletedId,
        [PSObject]$HaiosStatus
    )
    # Returns: @{ milestone = "M2"; old = 78; new = 80 }
}

function Get-SubstantiveReferences {
    param(
        [string]$CompletedId,
        [string]$ProjectRoot
    )
    # Scans CLAUDE.md, READMEs for body references to $CompletedId
    # Returns: array of @{ file = "CLAUDE.md"; type = "substantive" }
}

function Format-CascadeMessage {
    param(
        [string]$CompletedId,
        [string]$NewStatus,
        [array]$UnblockedItems,
        [array]$RelatedItems,
        [hashtable]$MilestoneDelta,
        [array]$SubstantiveRefs
    )
    # Returns: formatted cascade message string with all sections
}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate CascadeHook.ps1 | Yes | Isolation, testability, maintainability |
| Trigger on COMPLETE only | Yes | Most impactful status; others are noise |
| Read from haios-status.json | Yes | Already computed, no new graph store needed |
| Output to stdout | Yes | Hook pattern - messages appear to agent |
| Auto-refresh haios-status | **REQUIRED** | Without refresh, Vitals shows stale data (FIX from design review) |
| Multiple blockers check | **REQUIRED** | Must check ALL blockers complete, not just triggering one |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No blocked items | Output "No dependents affected" | Test 4 |
| Circular reference | DAG constraint prevents; skip if detected | N/A |
| Missing haios-status.json | Silent fail, no cascade | Test error handling |
| Multiple blockers | **REQUIRED:** Item unblocks only when ALL blockers complete | Test 6 |
| Partial unblock | Show "E2-xxx still blocked by [E2-yyy, E2-zzz]" | Test 7 |

### Multiple Blockers Logic (FIX from design review)

```
# Pseudo-graphviz: Multiple blocker resolution

digraph unblock {
    rankdir=LR

    E2_076a [label="E2-076a\nCOMPLETE" style=filled fillcolor=green]
    E2_076b [label="E2-076b\nIN_PROGRESS" style=filled fillcolor=yellow]
    E2_076e [label="E2-076e\nBLOCKED" style=filled fillcolor=red]

    E2_076a -> E2_076e [label="blocked_by"]
    E2_076b -> E2_076e [label="blocked_by"]

    note [shape=note label="E2-076e.blocked_by = [E2-076a, E2-076b]\n\nWhen E2-076a completes:\n  Check: Is E2-076b complete? NO\n  Result: E2-076e stays BLOCKED\n  Message: 'still blocked by E2-076b'\n\nWhen E2-076b completes:\n  Check: Is E2-076a complete? YES\n  Result: E2-076e becomes READY\n  Message: 'E2-076e is now READY'"]
}
```

**Algorithm:**
```
function Get-UnblockedItems(completed_id, status_data):
    candidates = find_items_where(blocked_by CONTAINS completed_id)

    for each candidate in candidates:
        all_blockers = candidate.blocked_by  # may be array

        incomplete_blockers = []
        for blocker in all_blockers:
            if blocker != completed_id AND status(blocker) != "complete":
                incomplete_blockers.append(blocker)

        if incomplete_blockers.length == 0:
            yield { item: candidate, status: "READY" }
        else:
            yield { item: candidate, status: "STILL_BLOCKED", remaining: incomplete_blockers }
```

---

## Implementation Steps

### Step 1: Create CascadeHook.ps1 Skeleton
- [ ] Create `.claude/hooks/CascadeHook.ps1`
- [ ] Accept parameters: `-FilePath`, `-BacklogId`, `-NewStatus`
- [ ] Load haios-status.json
- [ ] Define empty effects collection

### Step 2: Implement Unblock Cascade (with Multiple Blockers)
- [ ] Implement `Get-UnblockedItems` function per algorithm above
- [ ] Scan haios-status for items with `blocked_by` containing `$CompletedId`
- [ ] For each candidate: get ALL blockers, check if ALL are complete
- [ ] If ALL complete: `[UNBLOCK] E2-xxx is now READY`
- [ ] If partial: `[PARTIAL] E2-xxx still blocked by [E2-yyy]`
- [ ] Test: Single blocker scenario
- [ ] Test: Multiple blockers, one completes (should stay blocked)
- [ ] Test: Multiple blockers, all complete (should unblock)

### Step 3: Implement Related Cascade
- [ ] Implement `Get-RelatedItems` function
- [ ] Scan haios-status for items with `related: $CompletedId`
- [ ] Add to effects: `[RELATED] E2-yyy may need review`
- [ ] Test: Mock related, verify detection

### Step 4: Implement Milestone Cascade
- [ ] Implement `Get-MilestoneDelta` function
- [ ] Parse milestone from completed item frontmatter
- [ ] Calculate progress: completed items / total items in milestone
- [ ] Add to effects: `[MILESTONE] M2: 78% -> 80%`
- [ ] Test: Mock milestone, verify calculation

### Step 5: Implement Substantive Cascade
- [ ] Implement `Get-SubstantiveReferences` function
- [ ] Scan CLAUDE.md, **/README.md for body references to $CompletedId
- [ ] Distinguish frontmatter (mechanical) vs body (substantive)
- [ ] Add to effects: `[SUBSTANTIVE] CLAUDE.md -> Consider update`
- [ ] Future: Auto-spawn E2-UPDATE-xxx work item

### Step 6: Format and Output
- [ ] Implement `Format-CascadeMessage` function
- [ ] Combine all effects into structured message
- [ ] Output via Write-Output (appears to agent)

### Step 7: Integrate with PostToolUse.ps1
- [ ] After template validation block (~line 288)
- [ ] Parse frontmatter for `status` and `backlog_id`
- [ ] Check if status is in cascade-trigger set (`complete`, `accepted`, `closed`)
- [ ] If trigger, call CascadeHook.ps1 with parameters

### Step 8: Refresh Status After Cascade (FIX from design review)
- [ ] At end of CascadeHook.ps1, call UpdateHaiosStatus.ps1
- [ ] This ensures haios-status.json reflects new state immediately
- [ ] This regenerates haios-status-slim.json for Vitals
- [ ] Test: After cascade, slim.json has updated blocked_items

### Step 8b: Write Cascade Events to Event Log (E2-081 Integration)
- [ ] Append cascade event to `.claude/haios-events.jsonl`
- [ ] Event format: `{"ts":"...", "type":"cascade", "source":"<backlog_id>", "effects":["unblock:E2-xxx", "milestone:+N"]}`
- [ ] This enables E2-084 (Event Log Foundation) to analyze cascade patterns
- [ ] Test: After cascade, `just events` shows cascade entry

```
# ASCII flow: Cascade -> Refresh -> Fresh Vitals

+------------------+     +-------------------+     +------------------+
| CascadeHook.ps1  | --> | UpdateHaiosStatus | --> | haios-status-    |
| (computes        |     | .ps1              |     | slim.json        |
|  effects)        |     | (refreshes files) |     | (fresh for       |
+------------------+     +-------------------+     | next prompt)     |
                                                   +------------------+
                                                           |
                                                           v
                                                   +------------------+
                                                   | UserPromptSubmit |
                                                   | reads fresh      |
                                                   | Vitals           |
                                                   +------------------+
```

**LEVERAGE NOTE (Session 80):** UpdateHaiosStatus.ps1 already has:
- `Get-BlockedItems` - finds items with unresolved blocked_by
- `Get-MilestoneProgress` - calculates milestone % from items vs complete
- These can be called from CascadeHook.ps1 or factored into shared module

### Step 9: Integration Verification
- [ ] Test: Complete a plan, verify cascade message appears
- [ ] Test: Verify all four cascade types work
- [ ] Test: No cascade for draft/in_progress status
- [ ] Test: Graceful handling when haios-status.json missing
- [ ] Test: After cascade, next prompt shows updated Vitals (fresh slim.json)

---

## Verification

- [ ] CascadeHook.ps1 exists and is callable
- [ ] PostToolUse.ps1 calls cascade on status: complete/accepted
- [ ] **Unblock cascade:** blocked_by items detected and surfaced
- [ ] **Related cascade:** related items detected and surfaced
- [ ] **Milestone cascade:** progress % calculated and surfaced
- [ ] **Substantive cascade:** CLAUDE.md/README references detected
- [ ] **Event logging:** Cascade events written to haios-events.jsonl (E2-081 integration)
- [ ] Cascade message format matches spec (all four sections)
- [ ] No errors for missing haios-status.json

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance (scanning on every edit) | Medium | Only scan governed .md files, exit early |
| False positives (detecting "complete" in content) | Low | Parse frontmatter only, not body |
| haios-status.json stale | Medium | Cascade message includes "based on last refresh" note |
| Hook timeout | Medium | Keep CascadeHook.ps1 fast (<2s) |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 75 | 2025-12-14 | - | Draft | Subplan created |
| 81 | 2025-12-16 | - | Complete | Full implementation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/CascadeHook.ps1` | Exists, implements Get-BlockedItems, Format-CascadeMessage | [x] | 380 lines, all functions |
| `.claude/hooks/PostToolUse.ps1` | Calls CascadeHook.ps1 after validation | [x] | Lines 290-324 |
| Test output | Cascade message appears on plan completion | [x] | `just cascade E2-076d complete` works |

**Verification Commands:**
```bash
# Via justfile (Claude-facing - preferred)
just cascade E2-076d complete    # Tests cascade hook directly
just validate docs/plans/PLAN-E2-076d-vitals-injection.md  # Full validation + cascade

# Raw PowerShell (internal - wrapped by just)
powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/CascadeHook.ps1' -FilePath 'docs/plans/PLAN-E2-076d-vitals-injection.md' -BacklogId 'E2-076d' -NewStatus 'complete'"
# Expected: Cascade message with any blocked items

# Verify PostToolUse integration
# Edit a plan to status: complete, observe cascade output
```

**Note:** After E2-080 (Justfile) is implemented, prefer `just cascade <id> <status>` over raw PowerShell.

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read CascadeHook.ps1, PostToolUse.ps1 |
| Cascade message appears on completion? | Yes | Tested via justfile and direct call |
| Any deviations from plan? | No | Implemented as designed |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (manual verification for PowerShell)
- [x] WHY captured (reasoning stored to memory)
- [x] Documentation current (CLAUDE.md describes cascade behavior)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## Dependencies

### Blocked By
- ~~**E2-076b** (Frontmatter Schema)~~ - COMPLETE (Session 79)
- ~~**E2-076d** (Vitals/Slim)~~ - COMPLETE (Session 80)
- **STATUS: UNBLOCKED** - Ready for implementation

### Blocks
- **E2-084** (Event Log Foundation) - Cascade writes events

---

## References

- **Parent Plan:** `docs/plans/PLAN-E2-076-dag-governance-architecture-adr.md`
- **Related:** E2-076d (Vitals), ADR-033 (Work Item Lifecycle)
- **Memory:** Concepts 50372, 71375 (DAG structure, heartbeat)

---
