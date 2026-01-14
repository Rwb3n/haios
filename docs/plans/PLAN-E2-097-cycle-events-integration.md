---
template: implementation_plan
status: complete
date: 2025-12-17
backlog_id: E2-097
title: "Cycle Events Integration"
author: Hephaestus
lifecycle_phase: done
session: 85
spawned_by: Session-83
blocked_by: [E2-091, E2-096]
related: [E2-084, E2-091, E2-096, E2-106, ADR-038, epoch3/foresight-spec.md]
milestone: M3-Cycles
version: "1.3"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-20 20:32:06
# Implementation Plan: Cycle Events Integration

@docs/README.md
@docs/epistemic_state.md
@docs/ADR/ADR-038-m2-governance-symphony-architecture.md

---

## Goal

Cycle phase transitions (PLAN→DO→CHECK→DONE) are logged as events in haios-events.jsonl, integrating M3-Cycles with M2-Governance's RESONANCE movement (ADR-038).

---

## Current State vs Desired State

### Current State

```jsonl
# haios-events.jsonl has M2 events:
{"type": "session_start", "session": 85, ...}
{"type": "item_complete", "id": "E2-091", ...}
{"type": "milestone_progress", ...}
# No cycle-specific events
```

**Behavior:** Events track sessions and completions but not cycle progress.

**Result:** Can't see where time is spent (PLAN vs DO vs CHECK).

### Desired State

```jsonl
# haios-events.jsonl with cycle events:
{"type": "cycle_transition", "id": "E2-092", "from": "PLAN", "to": "DO", ...}
{"type": "cycle_transition", "id": "E2-092", "from": "DO", "to": "CHECK", ...}
{"type": "cycle_stuck", "id": "E2-093", "phase": "DO", "duration_days": 3, ...}
```

**Behavior:** Cycle transitions logged as events.

**Result:** Full visibility into implementation flow, can detect stuck items.

---

## Tests First (TDD)

### Test 1: Event Schema Supports cycle_transition
```jsonl
# Verify event type is valid
{"type": "cycle_transition", "id": "E2-092", "from": "PLAN", "to": "DO", "timestamp": "..."}
```

### Test 2: PostToolUse Detects Phase Changes
```bash
# When plan's cycle_phase changes (Edit tool), event is logged
# Edit PLAN-E2-092.md: cycle_phase: PLAN → cycle_phase: DO
# haios-events.jsonl should have new cycle_transition event
```

### Test 3: Justfile Has cycle-events Command
```bash
just cycle-events
# Expected: List recent cycle transitions
```

---

## Detailed Design

### Event Schema

```json
{
  "type": "cycle_transition",
  "timestamp": "2025-12-18T23:00:00",
  "backlog_id": "E2-092",
  "from_phase": "PLAN",
  "to_phase": "DO",
  "session": 85,
  "source": "PostToolUse"
}
```

Additional event types:
- `cycle_stuck`: Item in same phase for >2 days
- `cycle_complete`: Full PLAN→DO→CHECK→DONE cycle finished

### FORESIGHT Prediction Events (E2-106)

When `foresight_prep` section is present, log prediction events for Epoch 3 calibration:

```json
{
  "type": "prediction_made",
  "timestamp": "2025-12-18T23:00:00",
  "backlog_id": "E2-094",
  "predicted_outcome": "Test runner subagent executes tests",
  "predicted_confidence": 0.75,
  "competence_domain": "subagent_creation",
  "knowledge_gaps": ["pytest fixtures"],
  "session": 86,
  "source": "PLAN_phase"
}

{
  "type": "prediction_calibrated",
  "timestamp": "2025-12-19T15:00:00",
  "backlog_id": "E2-094",
  "predicted_outcome": "Test runner subagent executes tests",
  "actual_outcome": "Works but fixture handling needed iteration",
  "prediction_error": 0.2,
  "competence_estimate": 0.7,
  "failure_modes": ["pytest collection complexity"],
  "session": 86,
  "source": "CHECK_phase"
}
```

These events prepare data for Epoch 3 FORESIGHT layer:
- `prediction_made` → Feeds World Model training
- `prediction_calibrated` → Enables Self Model calibration

### PostToolUse Enhancement

Add to PostToolUse.ps1 (after cascade detection):

```powershell
# ============================================================
# CYCLE TRANSITION DETECTION (E2-097)
# Log events when cycle_phase changes
# ============================================================
if ($hasYamlHeader -and $extension -eq ".md") {
    # Check if cycle_phase changed
    $oldCyclePhase = # Read from previous content (if available)
    $newCyclePhase = if ($yamlContent -match 'cycle_phase:\s*(\S+)') {
        $Matches[1].Trim()
    } else { $null }

    if ($oldCyclePhase -ne $newCyclePhase -and $newCyclePhase) {
        # Log cycle_transition event
        $event = @{
            type = "cycle_transition"
            timestamp = (Get-Date -Format "o")
            backlog_id = $backlogId
            from_phase = $oldCyclePhase
            to_phase = $newCyclePhase
            session = $sessionNumber  # From haios-status.json
            source = "PostToolUse"
        }
        # Append to haios-events.jsonl
        $eventJson = $event | ConvertTo-Json -Compress
        Add-Content -Path ".claude/haios-events.jsonl" -Value $eventJson
    }
}
```

### Symphony Integration (ADR-038)

| Movement | Integration |
|----------|-------------|
| **RHYTHM** | E2-096 provides cycle_phase for tracking |
| **DYNAMICS** | Add `cycle_stuck` threshold (>2 days in DO) |
| **LISTENING** | Could query memory for similar stuck patterns |
| **RESONANCE** | cycle_transition events join session/item events |

### Justfile Commands

```justfile
# Show recent cycle transitions
cycle-events:
    @powershell -Command "Get-Content .claude/haios-events.jsonl | ..." | Select-Object -Last 20

# Show stuck items
cycle-stuck:
    @powershell -Command "# Find items in same phase >2 days"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Event location | haios-events.jsonl | Consistent with M2 events (E2-084) |
| Trigger | PostToolUse | Same pattern as cascade detection |
| Track old phase | Best effort | May not always have previous value |
| Duration tracking | Separate event type | Keep transition events simple |

### Input/Output Examples

| Action | Event |
|--------|-------|
| Change cycle_phase: PLAN → DO | `{"type": "cycle_transition", "from": "PLAN", "to": "DO", ...}` |
| Item in DO for 3 days | `{"type": "cycle_stuck", "phase": "DO", "duration_days": 3, ...}` |
| Complete full cycle | `{"type": "cycle_complete", "id": "E2-092", ...}` |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No previous phase | from_phase: null | Test 2 |
| Direct to DONE | Log transition from null to DONE | N/A |
| Backward transition | Still log (CHECK → DO for fixes) | Manual |

---

## Implementation Steps

### Step 1: Define Event Schema
- [ ] Document event types in RESONANCE section of ADR-038
- [ ] Add to .claude/templates/event-schemas.md (if exists)

### Step 2: Enhance PostToolUse.ps1
- [ ] Add cycle transition detection after cascade section
- [ ] Parse cycle_phase from YAML
- [ ] Log events to haios-events.jsonl

### Step 3: Add Justfile Commands
- [ ] Add `cycle-events` command
- [ ] Add `cycle-stuck` command (optional)

### Step 4: Optional: Add DYNAMICS Threshold
- [ ] Add cycle_stuck threshold to UserPromptSubmit.ps1
- [ ] Warn when items stuck in DO phase

---

## Verification

- [ ] cycle_transition events logged on phase changes
- [ ] Events appear in haios-events.jsonl
- [ ] `just cycle-events` shows transitions
- [ ] No performance regression in PostToolUse

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Event file grows large | Low | Periodic archival (like events-archive) |
| Missing old phase | Low | null is valid from_phase |
| PostToolUse latency | Low | Event logging is fast |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 85 | 2025-12-18 | - | Plan filled | Design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/PostToolUse.ps1` | Has cycle transition detection | [ ] | |
| `haios-events.jsonl` | Contains cycle_transition events | [ ] | |
| `justfile` | Has cycle-events command | [ ] | |

**Verification Commands:**
```bash
# Check events exist
just cycle-events
# Expected: Shows recent cycle transitions

# Trigger a transition
# Edit a plan's cycle_phase and verify event logged
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Events logged on phase change? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (events logged)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] Ground Truth Verification completed above

---

## References

- E2-084: Event Log Foundation (haios-events.jsonl)
- E2-091: Implementation Cycle Skill
- E2-096: Cycle State Frontmatter (provides cycle_phase)
- ADR-038: M2-Governance Symphony (RESONANCE movement)

---
