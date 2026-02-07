---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-108
title: Gate Observability for Implementation Cycle
author: Hephaestus
lifecycle_phase: plan
session: 141
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-29T09:34:28'
---
# Implementation Plan: Gate Observability for Implementation Cycle

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Implementation-cycle and its bridge skills will emit structured events for phase transitions and validation outcomes, with actionable triggers that surface governance issues in real-time.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 5 | implementation-cycle SKILL.md, preflight-checker.md, dod-validation-cycle SKILL.md, observations.py, user_prompt_submit.py |
| Lines affected | ~1511 total | `wc -l` on target files |
| New files to create | 2 | `.claude/lib/governance_events.py`, `tests/test_governance_events.py` |
| Tests to write | 6 | Event logging, threshold triggers, metrics |
| Dependencies | 3 | Skills import events module, hooks read events |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | High | 5 skills/agents + hooks + status command |
| Risk of regression | Low | Additive changes, no behavior modification |
| External dependencies | Low | No external APIs, file-based events |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Event Schema + Logging | 45 min | High |
| Phase 2: Trigger Actions | 30 min | Medium |
| Phase 3: Metrics Surface | 30 min | Medium |
| Phase 4: Tests + Verification | 30 min | High |
| **Total** | ~2.25 hr | Medium |

---

## Current State vs Desired State

### Current State

Skills execute validation but don't emit events:

```python
# .claude/skills/implementation-cycle/SKILL.md - no event logging
# PLAN phase just reads files, no observability
# DO phase just writes code, no transition tracking
# Bridge skills validate but outcomes aren't recorded
```

**Behavior:** Validation happens silently. If preflight-checker blocks or dod-validation fails, there's no record.

**Result:** No visibility into governance effectiveness. Can't answer: "How often do agents skip phases?" or "What validation fails most?"

### Desired State

Skills emit structured events that trigger actions:

```python
# .claude/lib/governance_events.py
def log_phase_transition(phase: str, work_id: str, agent: str):
    """Log when agent enters a cycle phase."""
    event = {
        "type": "CyclePhaseEntered",
        "phase": phase,  # PLAN, DO, CHECK, DONE
        "work_id": work_id,
        "timestamp": datetime.now().isoformat(),
        "agent": agent
    }
    append_to_events(event)

def log_validation_outcome(gate: str, work_id: str, result: str, reason: str):
    """Log validation pass/fail with reason."""
    event = {
        "type": "ValidationOutcome",
        "gate": gate,  # preflight, dod, observation
        "work_id": work_id,
        "result": result,  # pass, warn, block
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    append_to_events(event)

    # Trigger action if threshold exceeded
    if result == "block":
        check_repeated_failure_threshold(gate, work_id)
```

**Behavior:** Every phase transition and validation outcome is logged. Thresholds trigger real-time warnings.

**Result:** Full visibility into governance health. Agents get warned about repeated failures. Metrics available for audit.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Phase Transition Event Logged
```python
def test_log_phase_transition_creates_event():
    """Verify phase transition creates structured event."""
    from governance_events import log_phase_transition, read_events

    log_phase_transition("PLAN", "E2-108", "Hephaestus")

    events = read_events()
    assert any(e["type"] == "CyclePhaseEntered" and e["phase"] == "PLAN" for e in events)
```

### Test 2: Validation Outcome Event Logged
```python
def test_log_validation_outcome_creates_event():
    """Verify validation outcome creates structured event with reason."""
    from governance_events import log_validation_outcome, read_events

    log_validation_outcome("preflight", "E2-108", "block", "Plan incomplete")

    events = read_events()
    last = [e for e in events if e["type"] == "ValidationOutcome"][-1]
    assert last["result"] == "block"
    assert last["reason"] == "Plan incomplete"
```

### Test 3: Repeated Failure Triggers Warning
```python
def test_repeated_failure_triggers_threshold():
    """Verify 3 failures of same gate triggers warning."""
    from governance_events import log_validation_outcome, get_threshold_warnings

    for _ in range(3):
        log_validation_outcome("dod", "E2-108", "block", "Tests failing")

    warnings = get_threshold_warnings("E2-108")
    assert "dod" in warnings  # Should flag repeated dod failures
```

### Test 4: Metrics Summary Returns Counts
```python
def test_governance_metrics_counts_events():
    """Verify metrics recipe returns correct counts."""
    from governance_events import get_governance_metrics

    metrics = get_governance_metrics()
    assert "phase_transitions" in metrics
    assert "validation_outcomes" in metrics
    assert "pass_rate" in metrics
```

### Test 5: Close Without Events Warns
```python
def test_close_without_events_produces_warning():
    """Verify closing work item with no cycle events produces warning."""
    from governance_events import check_work_item_events

    result = check_work_item_events("E2-999")  # No events for this ID
    assert result["has_events"] == False
    assert "warning" in result
```

### Test 6: Events File Append-Only
```python
def test_events_append_only():
    """Verify events are appended, not overwritten."""
    from governance_events import log_phase_transition, read_events

    initial_count = len(read_events())
    log_phase_transition("DO", "E2-108", "Hephaestus")
    assert len(read_events()) == initial_count + 1
```

---

## Detailed Design

### Component 1: governance_events.py (NEW)

**File:** `.claude/lib/governance_events.py`

```python
"""
Governance event logging and threshold monitoring.

Events are stored in .claude/governance-events.jsonl (append-only).
Thresholds trigger actions when patterns are detected.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

EVENTS_FILE = Path(".claude/governance-events.jsonl")

def log_phase_transition(phase: str, work_id: str, agent: str) -> dict:
    """Log cycle phase entry."""
    event = {
        "type": "CyclePhaseEntered",
        "phase": phase,
        "work_id": work_id,
        "agent": agent,
        "timestamp": datetime.now().isoformat()
    }
    _append_event(event)
    return event

def log_validation_outcome(gate: str, work_id: str, result: str, reason: str) -> dict:
    """Log validation outcome and check thresholds."""
    event = {
        "type": "ValidationOutcome",
        "gate": gate,
        "work_id": work_id,
        "result": result,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    _append_event(event)

    # Check if repeated failure threshold exceeded
    if result == "block":
        _check_repeated_failure(gate, work_id)

    return event

def get_threshold_warnings(work_id: str) -> list[str]:
    """Return list of gates that exceeded failure threshold for work_id."""
    events = read_events()
    failures = [e for e in events
                if e.get("type") == "ValidationOutcome"
                and e.get("work_id") == work_id
                and e.get("result") == "block"]

    # Count failures per gate
    gate_counts = {}
    for e in failures:
        gate = e.get("gate", "unknown")
        gate_counts[gate] = gate_counts.get(gate, 0) + 1

    # Return gates with 3+ failures
    return [g for g, c in gate_counts.items() if c >= 3]

def check_work_item_events(work_id: str) -> dict:
    """Check if work item has cycle events."""
    events = read_events()
    work_events = [e for e in events if e.get("work_id") == work_id]

    if not work_events:
        return {
            "has_events": False,
            "warning": f"No cycle events found for {work_id}. Was governance bypassed?"
        }
    return {"has_events": True, "event_count": len(work_events)}

def get_governance_metrics() -> dict:
    """Return governance health metrics."""
    events = read_events()
    phase_events = [e for e in events if e.get("type") == "CyclePhaseEntered"]
    validation_events = [e for e in events if e.get("type") == "ValidationOutcome"]

    passes = len([e for e in validation_events if e.get("result") == "pass"])
    total_validations = len(validation_events)

    return {
        "phase_transitions": len(phase_events),
        "validation_outcomes": total_validations,
        "pass_rate": passes / total_validations if total_validations else 1.0,
        "failure_reasons": _top_failure_reasons(validation_events)
    }

def read_events() -> list[dict]:
    """Read all events from file."""
    if not EVENTS_FILE.exists():
        return []
    events = []
    with open(EVENTS_FILE) as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events

def _append_event(event: dict):
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

def _check_repeated_failure(gate: str, work_id: str):
    """Log warning if repeated failure detected."""
    warnings = get_threshold_warnings(work_id)
    if gate in warnings:
        print(f"WARNING: {gate} has failed 3+ times for {work_id}")

def _top_failure_reasons(events: list[dict]) -> list[str]:
    """Return top 5 failure reasons."""
    failures = [e.get("reason") for e in events if e.get("result") == "block"]
    from collections import Counter
    return [r for r, _ in Counter(failures).most_common(5)]
```

### Component 2: Trigger→Action Integration

**Consumption Points (from work item):**

| Trigger | Action | Where Implemented |
|---------|--------|-------------------|
| Validation failure > threshold | WARNING in output | `_check_repeated_failure()` in governance_events.py |
| Phase skipped | Logged for audit | `get_governance_metrics()` surfaces missing transitions |
| Same gate fails 3x | Print warning | `_check_repeated_failure()` immediate output |
| Work closed without events | Warning in /close | `check_work_item_events()` called by close-work-cycle |

### Component 3: Skill Integration Points

Skills will document event logging in their prose (not code changes):

**implementation-cycle SKILL.md additions:**
- PLAN phase exit: `log_phase_transition("PLAN", work_id, agent)`
- DO phase exit: `log_phase_transition("DO", work_id, agent)`
- CHECK phase exit: `log_phase_transition("CHECK", work_id, agent)`
- DONE phase exit: `log_phase_transition("DONE", work_id, agent)`

**Bridge skills (dod-validation, plan-validation, preflight-checker):**
- APPROVE/BLOCK phase: `log_validation_outcome(gate, work_id, result, reason)`

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| JSONL format | Append-only file | Simple, no DB dependency, grep-able |
| In-process logging | Direct function calls | Skills are markdown, agents execute Python |
| Threshold = 3 | Hardcoded | Simple rule, can parameterize later |
| Immediate warning | Print to output | Agent sees it in current session |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Events file doesn't exist | Create on first write | Test 6 (append) |
| Malformed JSON line | Skip line, continue | Manual test needed |
| Work item never enters cycle | No events = warning on close | Test 5 |
| Same failure reason multiple times | Counted in metrics | Test 3 |

### Open Questions

**Q: Should phase transitions be logged by agent or by hook?**

Answer: By agent (during skill execution). Hooks don't have visibility into which skill phase is active. Agent must explicitly call `log_phase_transition()`.

**Q: How does close-work-cycle check for events?**

Answer: Add to MEMORY phase: call `check_work_item_events(work_id)` and surface warning if no events found. Not a blocker (soft gate behavior on this specific check).

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_governance_events.py`
- [ ] Add 6 test functions from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create governance_events.py
- [ ] Create `.claude/lib/governance_events.py` with full implementation
- [ ] Tests 1, 2, 6 pass (event logging, append-only)

### Step 3: Implement Threshold Logic
- [ ] Add `get_threshold_warnings()` function
- [ ] Add `_check_repeated_failure()` function
- [ ] Test 3 passes (repeated failure triggers warning)

### Step 4: Implement Metrics
- [ ] Add `get_governance_metrics()` function
- [ ] Add `check_work_item_events()` function
- [ ] Tests 4, 5 pass (metrics, close warning)

### Step 5: Add just recipe
- [ ] Add `just governance-metrics` to justfile
- [ ] Verify recipe outputs metrics summary

### Step 6: Update close-work-cycle Skill
- [ ] Add MEMORY phase check: call `check_work_item_events()`
- [ ] Surface warning if no events found

### Step 7: Update implementation-cycle Skill
- [ ] Document phase transition logging in each phase section
- [ ] Agent should call `log_phase_transition()` at phase exits

### Step 8: Full Verification
- [ ] All 6 tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: Complete a work item, verify events logged

### Step 9: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` with governance_events.py
- [ ] **MUST:** Update `.claude/skills/implementation-cycle/README.md` if exists

---

## Verification

- [ ] All 6 tests pass
- [ ] `just governance-metrics` returns valid output
- [ ] **MUST:** `.claude/lib/README.md` updated

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Events file grows unbounded | Low | Add rotation/archival in future iteration |
| Agent forgets to log events | Medium | Document prominently in skill; consider hook-based logging later |
| Threshold too aggressive | Low | Start with 3, adjust based on feedback |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/governance_events.py` | All 7 functions exist | [ ] | |
| `tests/test_governance_events.py` | 6 tests exist and pass | [ ] | |
| `.claude/governance-events.jsonl` | Created on first event | [ ] | |
| `.claude/lib/README.md` | Documents governance_events.py | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | MEMORY phase checks events | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_governance_events.py -v
# Expected: 6 tests passed

just governance-metrics
# Expected: JSON with phase_transitions, validation_outcomes, pass_rate
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- ADR-033: Work Item Lifecycle Governance (DoD criteria)
- Memory concept 27238: Trigger→Action→Owner→SLA chain
- Memory concept 79898: Hard gate > soft suggestion (decision evolution)
- E2-217: Observation Capture Gate (parallel pattern)

---
