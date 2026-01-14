---
template: implementation_plan
status: complete
date: 2025-12-16
backlog_id: E2-081
title: "Heartbeat Scheduler (Symphony: Rhythm)"
author: Hephaestus
lifecycle_phase: plan
session: 78
parent_plan: E2-076
spawned_by: Session-78-symphony-design
blocked_by: []
related: [E2-076, E2-080, E2-084, E2-076e]
execution_layer: E2-080
version: "1.1"
---
# generated: 2025-12-16
# System Auto: last updated on: 2025-12-16 21:51:08
# Implementation Plan: Heartbeat Scheduler (Symphony: Rhythm)

@docs/README.md
@docs/epistemic_state.md
@docs/plans/PLAN-E2-076-dag-governance-architecture-adr.md

---

## Goal

Establish external rhythmic pulse that runs synthesis and status updates on schedule, enabling the system to evolve even without operator interaction.

---

## Current State vs Desired State

### Current State

```
Claude session
    |
    v
[Operator prompts] --> [Claude responds] --> [Session ends]

No external triggers. System is purely reactive.
Synthesis only runs when explicitly invoked.
Status only updates when manually triggered.
```

**Behavior:** Claude responds to prompts, does nothing between sessions.

**Result:** No rhythm. Knowledge accumulates but doesn't synthesize. Status stales.

### Desired State

```
Windows Task Scheduler (hourly)
    |
    v
just heartbeat
    |
    +-- python -m haios_etl.cli synthesis run --quiet
    +-- just update-status
    +-- Append to .claude/haios-events.jsonl

System has pulse independent of operator presence.
```

**Behavior:** Hourly heartbeat runs synthesis and refreshes status.

**Result:** Knowledge continuously synthesizes. Status always fresh. Events logged.

---

## Tests First (TDD)

> Note: This is infrastructure, not Python code. Verification is manual.

### Test 1: Heartbeat Recipe Exists
```bash
just --list | grep heartbeat
# Expected: "heartbeat" appears in recipe list
```

### Test 2: Heartbeat Executes Successfully
```bash
just heartbeat
# Expected: No errors, synthesis runs, status updates
```

### Test 3: Event Logged
```bash
tail -1 .claude/haios-events.jsonl
# Expected: {"ts":"...","type":"heartbeat",...}
```

### Test 4: Task Scheduler Configured
```powershell
Get-ScheduledTask -TaskName "HAIOS-Heartbeat"
# Expected: Task exists, trigger is hourly
```

---

## Detailed Design

### Architecture

```
+-------------------+
| Task Scheduler    |
| (Windows)         |
| Trigger: Hourly   |
+--------+----------+
         |
         v
+-------------------+
| just heartbeat    |
| (justfile recipe) |
+--------+----------+
         |
    +----+----+----+
    |         |    |
    v         v    v
+-------+ +------+ +--------+
|synth- | |update| |append  |
|esis   | |status| |event   |
+-------+ +------+ +--------+
    |         |         |
    v         v         v
+-------+ +--------+ +----------+
|memory | |haios-  | |haios-    |
|.db    | |status  | |events    |
|bridges| |.json   | |.jsonl    |
+-------+ +--------+ +----------+
```

### Justfile Recipe

```just
# Heartbeat - external rhythm for the system
# Runs: synthesis, status update, event logging
# Triggered by: Windows Task Scheduler (hourly)
heartbeat:
    @echo "HAIOS Heartbeat: {{`date /t`}} {{`time /t`}}"
    python -m haios_etl.cli synthesis run --quiet || echo "Synthesis: skipped (no work)"
    just update-status
    powershell.exe -Command "Add-Content -Path '.claude/haios-events.jsonl' -Value '{\"ts\":\"$(Get-Date -Format o)\",\"type\":\"heartbeat\",\"synthesis\":true}'"
    @echo "Heartbeat complete"
```

### Task Scheduler Configuration

```xml
<!-- HAIOS-Heartbeat.xml -->
<Task>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT1H</Interval>  <!-- Every hour -->
      </Repetition>
      <StartBoundary>2025-12-16T00:00:00</StartBoundary>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>just</Command>
      <Arguments>heartbeat</Arguments>
      <WorkingDirectory>D:\PROJECTS\haios</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Use Task Scheduler | Yes | Already exists on Windows, no new dependencies |
| Hourly interval | Yes | Frequent enough for freshness, not wasteful |
| Quiet synthesis | Yes | Don't spam logs with routine output |
| Event logging | Yes | Enables E2-084 resonance detection |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Synthesis has no work | Graceful skip, log "skipped" | Test 2 |
| Status update fails | Continue, log error | - |
| Event file missing | PowerShell creates it | - |
| Just not in PATH | Task fails, check Task Scheduler history | Manual |

---

## Implementation Steps

### Step 1: Add Heartbeat Recipe to Justfile
- [x] Add `heartbeat` recipe per design above
- [x] Test: `just heartbeat` runs without error
- [x] Test: `just --list` shows heartbeat

### Step 2: Create Event Log File
- [x] Create `.claude/haios-events.jsonl` (empty)
- [ ] Add to .gitignore (events are local) - **Skipped: track for now**
- [x] Test: heartbeat appends event

### Step 3: Configure Task Scheduler
- [x] Create scheduled task via PowerShell script
- [x] Set trigger: hourly (365 day duration, auto-renew)
- [x] Set action: `just heartbeat` in project directory
- [x] Task: HAIOS-Heartbeat, State: Ready

### Step 4: Add Events Recipe
- [x] Add `just events` recipe (tail -20)
- [x] Add `just events-clear` recipe (truncate)
- [x] Test: `just events` shows recent heartbeats

---

## Verification

- [x] `just heartbeat` executes successfully
- [x] `just events` shows heartbeat entries
- [x] Task Scheduler task exists (HAIOS-Heartbeat, State: Ready)
- [x] System has pulse without operator (hourly trigger configured)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Task Scheduler not running | Medium | Document manual verification |
| Synthesis errors | Low | --quiet flag, error handling |
| Disk fills with events | Low | Add rotation or clear recipe |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 78 | 2025-12-16 | - | Draft | Plan created |
| 80 | 2025-12-16 | SESSION-80 | Complete | Implementation complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | Has `heartbeat` recipe | [x] | Lines 83-88 |
| `.claude/haios-events.jsonl` | Exists, has heartbeat events | [x] | 1 event logged |
| Task Scheduler | HAIOS-Heartbeat task exists | [x] | State: Ready |

**Verification Commands:**
```bash
just --list | grep heartbeat
# Expected: heartbeat recipe listed
# Actual: heartbeat recipe shown

just events
# Expected: Recent heartbeat events shown
# Actual: {"ts":"2025-12-16T21:47:11...","type":"heartbeat","synthesis":true}

powershell.exe -Command "Get-ScheduledTask -TaskName 'HAIOS-Heartbeat'"
# Expected: Task details shown
# Actual: HAIOS-Heartbeat, State: Ready, TaskPath: \
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 3 verified |
| Heartbeat runs successfully? | Yes | Event logged |
| Any deviations from plan? | Minor | Simplified synthesis command (--limit 20 vs --quiet) |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Heartbeat recipe works
- [x] WHY captured (see below)
- [x] Task Scheduler configured
- [x] Events logged
- [x] Ground Truth Verification completed above

---

## References

- **Parent Plan:** E2-076 (DAG Governance Architecture)
- **Enables:** E2-084 (Event Log), system rhythm
- **Uses:** E2-080 (Justfile)
- **Symphony Role:** RHYTHM - external pulse compensates for Claude's reactive nature

---
