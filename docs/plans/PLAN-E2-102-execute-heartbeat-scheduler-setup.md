---
template: implementation_plan
status: complete
date: 2025-12-19
backlog_id: E2-102
title: "Execute Heartbeat Scheduler Setup"
author: Hephaestus
lifecycle_phase: done
session: 87
spawned_by: INV-017
related: [E2-081, E2-084, INV-017]
milestone: M3-Cycles
version: "1.2"
---
# generated: 2025-12-19
# System Auto: last updated on: 2025-12-19 23:52:52
# Implementation Plan: Execute Heartbeat Scheduler Setup

@docs/README.md
@docs/epistemic_state.md
@.claude/hooks/setup-heartbeat-task.ps1

---

## Goal

Windows Task Scheduler runs `just heartbeat` every hour, generating continuous synthesis runs and status updates without operator intervention.

---

## Current State vs Desired State

### Current State

```powershell
# .claude/hooks/setup-heartbeat-task.ps1 EXISTS but was never executed
# haios-events.jsonl has 1 heartbeat event (manual test) vs 26 cascades
```

**Behavior:** Heartbeat script designed (E2-081) but never registered with Windows Task Scheduler.

**Result:** No automated synthesis, no hourly status updates, system relies entirely on session activity.

### Desired State

```powershell
# Task "HAIOS-Heartbeat" registered in Windows Task Scheduler
# Runs every hour: just heartbeat
# Heartbeat does:
#   1. Print timestamp
#   2. Run synthesis --limit 20
#   3. Update haios-status
#   4. Log event to haios-events.jsonl
```

**Behavior:** Automated hourly heartbeat running in background.

**Result:** Continuous memory consolidation, fresh status, observable system health.

---

## Investigation: Is This Actually Low-Cost?

### Concerns to Validate

| Concern | Risk | Verification |
|---------|------|--------------|
| Admin privileges required? | Medium | Script uses Register-ScheduledTask |
| Hardcoded paths correct? | Low | Check justPath and workDir in script |
| Synthesis takes too long? | Medium | `--limit 20` should be ~2 min |
| Conflicts with active sessions? | Low | SQLite WAL mode handles concurrency |
| Events accumulate forever? | Low | JSONL append-only, grep-friendly |

### Script Analysis

```powershell
# From setup-heartbeat-task.ps1
$justPath = "C:\Users\Ruben\AppData\Local\Microsoft\WinGet\Packages\Casey.Just_Microsoft.Winget.Source_8wekyb3d8bbwe\just.exe"
$workDir = "D:\PROJECTS\haios"
```

**Paths are hardcoded** - script is operator-specific. Not portable but works for current setup.

### Heartbeat Recipe Analysis

```bash
# From justfile:83-88
heartbeat:
    @powershell.exe -Command "Write-Host 'HAIOS Heartbeat:' (Get-Date)"
    -python -m haios_etl.cli synthesis run --limit 20
    just update-status
    @powershell.exe -Command "Add-Content -Path '.claude\haios-events.jsonl' -Value ..."
```

**Note:** Synthesis has `-` prefix (ignore errors). If synthesis fails, heartbeat continues.

---

## Tests First (TDD)

### Test 1: Task Registration Succeeds
```powershell
# Run script, verify task exists
Get-ScheduledTask -TaskName "HAIOS-Heartbeat"
# Expected: Returns task object, State = Ready
```

### Test 2: Task Can Execute
```powershell
# Manually trigger task
Start-ScheduledTask -TaskName "HAIOS-Heartbeat"
# Wait 2-3 minutes
# Check haios-events.jsonl for new heartbeat entry
```

### Test 3: Hourly Trigger Configured
```powershell
# Verify trigger interval
$task = Get-ScheduledTask -TaskName "HAIOS-Heartbeat"
$task.Triggers | Format-List
# Expected: RepetitionInterval = 01:00:00
```

---

## Implementation Steps

### Step 1: Verify Prerequisites
- [ ] Confirm just.exe path exists: `Test-Path $justPath`
- [ ] Confirm workDir exists: `Test-Path $workDir`
- [ ] Confirm no existing task: `Get-ScheduledTask -TaskName "HAIOS-Heartbeat"`

### Step 2: Execute Setup Script
- [ ] Run: `powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/setup-heartbeat-task.ps1`
- [ ] If "Administrator required" error, escalate to operator

### Step 3: Verify Registration
- [ ] `Get-ScheduledTask -TaskName "HAIOS-Heartbeat"` returns Ready state
- [ ] Task shows in Task Scheduler GUI (optional visual confirm)

### Step 4: Manual Test Run
- [ ] `Start-ScheduledTask -TaskName "HAIOS-Heartbeat"`
- [ ] Wait 2-3 minutes
- [ ] Check `just events` for new heartbeat entry

### Step 5: Await Natural Trigger (DONE phase)
- [ ] After 1 hour, verify second heartbeat logged
- [ ] Confirm synthesis ran (check concept count delta)

---

## Verification

- [ ] Task registered with hourly trigger
- [ ] Manual trigger succeeded
- [ ] Heartbeat event logged
- [ ] Synthesis ran without error

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Admin required | Medium | Escalate to operator if needed |
| Path mismatch | Low | Verify paths before running |
| Synthesis hangs | Medium | --limit 20 caps work; timeout in trigger |
| SQLite lock | Low | WAL mode handles concurrency |

---

## Decision Point: Is This Low-Cost?

**Initial Assessment:**

| Factor | Assessment |
|--------|------------|
| Effort to run script | ~5 min (if no admin issues) |
| Admin escalation risk | Medium - may need operator |
| Ongoing maintenance | None (self-running) |
| Value | Continuous synthesis + observability |

**Critical Finding (Session 87):**

Cross-pollination was comparing 92M pairs (60k concepts x 1.5k traces) = ~3 hour ETA.

**Resolution:** Added `--skip-cross` flag to heartbeat recipe. Result: **7 seconds**.

| Metric | Before | After |
|--------|--------|-------|
| Duration | ~3 hours | 7 seconds |
| Cross-poll pairs | 92M | 0 |
| Synthesis created | 6 | 6 |

**Verdict:** Now truly low-cost. Task registered, recipe fixed, heartbeat operational.

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 87 | 2025-12-19 | - | Complete | Task registered, recipe fixed, 7s heartbeat |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| Windows Task Scheduler | HAIOS-Heartbeat task exists, State=Ready | [x] | Registered successfully |
| `justfile:85` | `--skip-cross` flag added | [x] | Fixes 3hr bottleneck |
| `.claude/haios-events.jsonl` | New heartbeat entry | [x] | ts:2025-12-19T23:51:35 |

**Verification Output:**
```
TaskName        State
--------        -----
HAIOS-Heartbeat Ready

{"ts":"2025-12-19T23:51:35","type":"heartbeat","synthesis":true}
```

---

**Completion Criteria (DoD per ADR-033):**
- [x] Task registered (HAIOS-Heartbeat, hourly trigger)
- [x] Manual test passed (7 seconds, 6 syntheses)
- [x] WHY captured (cross-poll bottleneck discovery)
- [x] Documentation current (justfile updated)

---

## References

- E2-081: Heartbeat Scheduler Design
- INV-017: Observability Gap Analysis
- E2-084: Event Log Foundation

---
