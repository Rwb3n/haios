---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-08
backlog_id: WORK-291
title: "Fix RetroCycleCompleted Governance Event Not Emitted by Retro-Cycle"
author: Hephaestus
lifecycle_phase: plan
session: 482
generated: 2026-03-08
last_updated: 2026-03-08T19:06:07

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-291/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Fix RetroCycleCompleted Governance Event Not Emitted by Retro-Cycle

---

## Goal

After this plan is complete, retro-cycle will mechanically emit a `RetroCycleCompleted` governance event via a lib function, so that `retro_gate.py` passes without manual event injection.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Where to emit the event | (a) haiku subagent prompt, (b) skill text step, (c) lib/ function called by skill | (c) lib/ function | Mechanical — not reliant on agent remembering. Pattern: `log_tier_detected()`, `log_critique_injected()`. Skill text calls the function as an explicit step after EXTRACT. |
| Which module hosts the function | governance_events.py vs retro_gate.py | governance_events.py | All `log_*` functions live in governance_events.py. retro_gate.py is the consumer (reader), not the producer (writer). Separation of concerns. |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/governance_events.py` | MODIFY | 2 |
| `.claude/skills/retro-cycle/SKILL.md` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/retro_gate.py` | reads RetroCycleCompleted events | 114-118 | NO CHANGE (consumer reads, doesn't need update) |
| `.claude/haios/lib/session_review_predicate.py` | counts RetroCycleCompleted events | 70-100 | NO CHANGE |
| `.claude/haios/lib/README.md` | documents governance_events.py | ~90 | UPDATE — mention new function |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_retro_gate.py` | MODIFY | Add test for round-trip: emit then check gate passes |
| `tests/test_governance_events.py` | MODIFY | Add test for log_retro_completed function |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 4 | governance_events.py, SKILL.md, 2 test files |
| Tests to write | 3 | See Layer 1 Tests |
| Total blast radius | 5 | 4 modified + 1 README update |

---

## Layer 1: Specification

### Current State

```python
# governance_events.py — no log_retro_completed function exists
# Last log_* function is log_critique_injected() at ~line 226
```

```markdown
# retro-cycle SKILL.md Phase 4 EXTRACT, line ~453
# Governance event is documented but relies on agent/subagent to emit:
#   RetroCycleCompleted: {work_id}, scaling: {...}, reflect_count: N, kss_count: N, extract_count: N
```

**Behavior:** Retro-cycle completes all 4 phases but the `RetroCycleCompleted` governance event is only described in skill text. The EXTRACT haiku subagent may or may not emit it. The retro gate then blocks `/close` because no event is found.

**Problem:** Agent-dependent event emission is unreliable. S481 WORK-287 closure was blocked despite retro completing — required manual Python injection.

### Desired State

```python
# governance_events.py — new function
def log_retro_completed(
    work_id: str,
    scaling: str,
    reflect_count: int,
    kss_count: int,
    extract_count: int,
    *,
    context_pct: Optional[float] = None,
) -> dict:
    """Log RetroCycleCompleted governance event."""
    event = {
        "type": "RetroCycleCompleted",
        "work_id": work_id,
        "scaling": scaling,
        "reflect_count": reflect_count,
        "kss_count": kss_count,
        "extract_count": extract_count,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
    return event
```

```markdown
# retro-cycle SKILL.md — after Phase 4 EXTRACT, add explicit mechanical step:
# Phase 4 post-step: Emit governance event mechanically
from governance_events import log_retro_completed
log_retro_completed(work_id, scaling, reflect_count, kss_count, extract_count)
```

**Behavior:** After EXTRACT completes, the skill text instructs the agent to call `log_retro_completed()` as an explicit Python call — not "log a governance event" prose, but a concrete function invocation.

**Result:** `retro_gate.py` finds the `RetroCycleCompleted` event and allows `/close` to proceed.

### Tests

#### Test 1: log_retro_completed emits valid event
- **file:** `tests/test_governance_events.py`
- **function:** `test_log_retro_completed()`
- **setup:** tmp_path with empty governance-events.jsonl, monkeypatch EVENTS_FILE
- **assertion:** Event written to file with correct type, work_id, scaling, counts, timestamp

#### Test 2: Round-trip — emit then gate passes
- **file:** `tests/test_retro_gate.py`
- **function:** `test_retro_gate_passes_after_log_retro_completed()`
- **setup:** tmp_path, write session file, call `log_retro_completed()`, then `check_retro_gate()`
- **assertion:** `check_retro_gate()` returns `blocked=False, retro_found=True`

#### Test 3: Gate still blocks without event
- **file:** `tests/test_retro_gate.py`
- **function:** `test_retro_gate_blocks_without_retro_completed()`
- **setup:** tmp_path, write session file, empty events file, call `check_retro_gate()`
- **assertion:** `check_retro_gate()` returns `blocked=True`

### Design

#### File 1 (MODIFY): `.claude/haios/lib/governance_events.py`

**Location:** After `log_critique_injected()` (~line 250)

**Target Code:**
```python
def log_retro_completed(
    work_id: str,
    scaling: str,
    reflect_count: int,
    kss_count: int,
    extract_count: int,
    *,
    context_pct: Optional[float] = None,
) -> dict:
    """
    Log RetroCycleCompleted governance event.

    Emitted mechanically after retro-cycle Phase 4 EXTRACT completes.
    Consumed by retro_gate.py to allow close-work-cycle to proceed.

    Args:
        work_id: Work item ID (e.g., "WORK-291")
        scaling: Scale assessment result ("trivial" or "substantial")
        reflect_count: Number of REFLECT observations
        kss_count: Number of K/S/S directives
        extract_count: Number of EXTRACT items
        context_pct: Optional context usage percentage

    Returns:
        The logged event dict.
    """
    event = {
        "type": "RetroCycleCompleted",
        "work_id": work_id,
        "scaling": scaling,
        "reflect_count": reflect_count,
        "kss_count": kss_count,
        "extract_count": extract_count,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event, context_pct=context_pct)
    return event
```

#### File 2 (MODIFY): `.claude/skills/retro-cycle/SKILL.md`

**Location:** Phase 4 EXTRACT Governance Event section (~line 452-455)

**Current:**
```markdown
### Governance Event

Log full ceremony completion (extract_count now known):
```
RetroCycleCompleted: {work_id}, scaling: {trivial|substantial}, reflect_count: N, kss_count: N, extract_count: N
```
```

**Target:**
```markdown
### Governance Event (MECHANICAL — MUST)

After EXTRACT completes, emit the governance event mechanically via lib function.
This is NOT optional prose — it is a required function call that the retro gate depends on.

```python
# MUST execute after EXTRACT phase completes (WORK-291)
from governance_events import log_retro_completed
log_retro_completed(
    work_id="{work_id}",
    scaling="{scaling}",
    reflect_count={reflect_count},
    kss_count={kss_count},
    extract_count={extract_count},
)
```

**Why mechanical:** retro_gate.py (WORK-253) blocks `/close` unless this event exists.
Agent-dependent emission failed in S481 (WORK-287). This function call is the fix.
```

### Call Chain

```
/close {work_id}
    |
    +-> retro-cycle
    |     |
    |     +-> Phase 4: EXTRACT (haiku subagent)
    |     |     Returns: extracted_items, extract_count
    |     |
    |     +-> log_retro_completed()    # <-- NEW: mechanical event emission
    |           Writes: governance-events.jsonl
    |
    +-> close-work-cycle
          |
          +-> PreToolUse hook -> _check_retro_gate()
                |
                +-> check_retro_gate()  # reads governance-events.jsonl
                      Finds: RetroCycleCompleted event -> ALLOW
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| lib/ function not subagent prompt | Mechanical > agent-dependent | S481 proved agent-dependent emission is unreliable |
| governance_events.py hosts function | Pattern consistency | All log_* functions in one module |
| Skill text has explicit Python call | Agent reads concrete invocation | "Log a governance event" is ambiguous; `log_retro_completed()` is unambiguous |
| Main agent calls, not haiku subagent | Main agent orchestrates post-EXTRACT | EXTRACT subagent returns, main agent calls the function inline |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| EXTRACT subagent fails | Main agent still calls log_retro_completed with extract_count=0 | Covered by Test 1 (count=0 is valid) |
| governance-events.jsonl missing | _append_event creates parent dirs (existing behavior) | Existing governance_events.py tests |
| skip_retro escape hatch | Already logs RetroCycleSkipped (different event) — retro gate accepts this | Existing retro_gate.py test |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent still ignores the skill text call | L | Skill text uses MUST + concrete Python, not prose. Hook-level enforcement deferred to WORK-263. |
| Existing tests break | L | Only adding new tests and new function — no existing behavior changed |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add test_log_retro_completed to test_governance_events.py, add round-trip test to test_retro_gate.py
- **output:** Test files updated, new tests fail (function doesn't exist yet)
- **verify:** `pytest tests/test_governance_events.py::test_log_retro_completed tests/test_retro_gate.py::test_retro_gate_passes_after_log_retro_completed -v 2>&1` shows FAILED/ERROR

### Step 2: Implement log_retro_completed (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Add log_retro_completed function to governance_events.py after log_critique_injected
- **output:** All new tests pass
- **verify:** `pytest tests/test_governance_events.py::test_log_retro_completed tests/test_retro_gate.py::test_retro_gate_passes_after_log_retro_completed tests/test_retro_gate.py::test_retro_gate_blocks_without_retro_completed -v` exits 0

### Step 3: Update retro-cycle SKILL.md
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 2 complete (function exists and tests pass)
- **action:** Replace Phase 4 Governance Event section with mechanical call instruction
- **output:** SKILL.md has concrete Python invocation instead of prose
- **verify:** `grep "log_retro_completed" .claude/skills/retro-cycle/SKILL.md` returns 1+ match

### Step 4: Update Documentation
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 3 complete
- **action:** Update lib/README.md to mention log_retro_completed, update governance_events.py module docstring
- **output:** Documentation reflects new function
- **verify:** `grep "log_retro_completed" .claude/haios/lib/README.md` returns 1+ match

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_governance_events.py::test_log_retro_completed -v` | 1 passed, 0 failed |
| `pytest tests/test_retro_gate.py -v` | all passed (existing + 2 new), 0 failed |
| `pytest tests/ -v` | 0 new failures vs baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| log_retro_completed function exists | `grep "def log_retro_completed" .claude/haios/lib/governance_events.py` | 1 match |
| SKILL.md has mechanical call | `grep "log_retro_completed" .claude/skills/retro-cycle/SKILL.md` | 1+ matches |
| Round-trip test passes | `pytest tests/test_retro_gate.py::test_retro_gate_passes_after_log_retro_completed -v` | 1 passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| retro_gate.py unchanged | `git diff .claude/haios/lib/retro_gate.py` | empty (no changes needed) |
| README updated | `grep "log_retro_completed" .claude/haios/lib/README.md` | 1+ match |
| No stale references | `grep "RetroCycleCompleted" .claude/skills/retro-cycle/SKILL.md` | references new function |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (retro_gate.py reads events, SKILL.md calls function)
- [ ] No stale references (Consumer Integrity table above)
- [ ] READMEs updated (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

---

## References

- WORK-253: Retro-before-close gate (created retro_gate.py)
- WORK-287: S481 — closure blocked, required manual event injection (bug evidence)
- REQ-OBSERVE-001: All state transitions logged to events file
- `.claude/haios/lib/governance_events.py`: All log_* functions
- `.claude/haios/lib/retro_gate.py`: Consumer (check_retro_gate)
- `.claude/skills/retro-cycle/SKILL.md`: Ceremony definition

---
