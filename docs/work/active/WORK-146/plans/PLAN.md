---
template: implementation_plan
status: complete
date: 2026-02-14
backlog_id: WORK-146
title: "Gate Skip Violation Logging"
author: Hephaestus
lifecycle_phase: plan
session: 371
version: "1.5"
generated: 2026-02-14
last_updated: 2026-02-14T16:35:00
---
# Implementation Plan: Gate Skip Violation Logging

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory 84270 (feature request), 84269 (gate skip recommendation) queried |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

When MUST gates detect violations and allow them (warn mode), a `GateViolation` event is emitted to `governance-events.jsonl` with gate_id, work_id, violation_type, timestamp, and context — making governance bypasses observable without blocking agent workflow.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/haios/lib/governance_events.py` (371 lines), `.claude/hooks/hooks/pre_tool_use.py` (844 lines) |
| New files to create | 0 | All changes in existing files |
| Tests to write | 5 | In existing `tests/test_governance_events.py` (262 lines) |
| Dependencies | 0 | No new imports; governance_events.py already imported by pre_tool_use.py via GovernanceLayer |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | governance_events.py is standalone; pre_tool_use.py calls it indirectly via GovernanceLayer |
| Risk of regression | Low | Adding new function + new call sites; existing functions untouched. 13 existing tests cover current behavior. |
| External dependencies | Low | No APIs/services; file append only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests (RED) | 15 min | High |
| Implement `log_gate_violation()` | 10 min | High |
| Wire into pre_tool_use.py | 15 min | High |
| Integration verification | 10 min | High |
| **Total** | ~50 min | High |

---

## Current State vs Desired State

### Current State

`.claude/hooks/hooks/pre_tool_use.py:475-483` — When a governance check allows with warning, it returns the warning message but produces no audit event:

```python
def _allow_with_warning(reason: str) -> dict:
    """Return allow response with warning."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason
        }
    }
```

`.claude/hooks/hooks/pre_tool_use.py:524-548` — `_allow_with_context()` similarly returns context information but logs nothing to governance-events.jsonl.

**Behavior:** Gate violations (warn mode) are surfaced in hook output but invisible to audit. No record in governance-events.jsonl.

**Result:** System cannot observe its own governance violations. Anti-pattern "Skipping MUST gates without logging" (E2.5).

### Desired State

`.claude/haios/lib/governance_events.py` gains `log_gate_violation()`:

```python
def log_gate_violation(
    gate_id: str, work_id: str, violation_type: str, context: str
) -> dict:
    event = {
        "type": "GateViolation",
        "gate_id": gate_id,
        "work_id": work_id,
        "violation_type": violation_type,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event
```

`.claude/hooks/hooks/pre_tool_use.py` — Hook helpers (`_allow_with_warning`, `_allow_with_context`) emit `GateViolation` events when `permissionDecisionReason` contains governance warnings.

**Behavior:** Every gate violation in warn mode produces a `GateViolation` event in governance-events.jsonl.

**Result:** `just events` shows governance bypasses. Metrics include violation counts. Audit trail complete.

---

## Tests First (TDD)

### Test 1: log_gate_violation creates structured event
```python
def test_log_gate_violation_creates_event(self, temp_events_file):
    """Verify gate violation creates structured event with all fields."""
    from governance_events import log_gate_violation, read_events

    with patch("governance_events.EVENTS_FILE", temp_events_file):
        log_gate_violation(
            gate_id="ceremony_contract",
            work_id="WORK-146",
            violation_type="warn",
            context="Missing input contract field"
        )

        events = read_events()
        violations = [e for e in events if e["type"] == "GateViolation"]
        assert len(violations) == 1
        v = violations[0]
        assert v["gate_id"] == "ceremony_contract"
        assert v["work_id"] == "WORK-146"
        assert v["violation_type"] == "warn"
        assert v["context"] == "Missing input contract field"
        assert "timestamp" in v
```

### Test 2: log_gate_violation returns event dict
```python
def test_log_gate_violation_returns_event(self, temp_events_file):
    """Verify log_gate_violation returns the event dict."""
    from governance_events import log_gate_violation

    with patch("governance_events.EVENTS_FILE", temp_events_file):
        result = log_gate_violation("sql_block", "WORK-100", "block", "Direct SQL")
        assert result["type"] == "GateViolation"
        assert result["gate_id"] == "sql_block"
```

### Test 3: get_gate_violations filters by work_id
```python
def test_get_gate_violations_filters_by_work_id(self, temp_events_file):
    """Verify get_gate_violations returns only violations for given work_id."""
    from governance_events import log_gate_violation, get_gate_violations

    with patch("governance_events.EVENTS_FILE", temp_events_file):
        log_gate_violation("sql", "WORK-100", "block", "SQL detected")
        log_gate_violation("ceremony", "WORK-146", "warn", "Contract missing")
        log_gate_violation("powershell", "WORK-100", "block", "PS detected")

        violations = get_gate_violations("WORK-100")
        assert len(violations) == 2
        assert all(v["work_id"] == "WORK-100" for v in violations)
```

### Test 4: get_gate_violations returns empty list when no violations
```python
def test_get_gate_violations_empty_when_none(self, temp_events_file):
    """Verify get_gate_violations returns [] when no violations exist."""
    from governance_events import get_gate_violations

    with patch("governance_events.EVENTS_FILE", temp_events_file):
        violations = get_gate_violations("WORK-999")
        assert violations == []
```

### Test 5: Existing behavior unchanged (backward compatibility)
```python
def test_existing_log_functions_unaffected(self, temp_events_file):
    """Verify existing log_phase_transition and log_validation_outcome still work."""
    from governance_events import (
        log_phase_transition, log_validation_outcome,
        log_gate_violation, read_events
    )

    with patch("governance_events.EVENTS_FILE", temp_events_file):
        log_phase_transition("PLAN", "WORK-146", "Hephaestus")
        log_validation_outcome("preflight", "WORK-146", "pass", "OK")
        log_gate_violation("sql", "WORK-146", "block", "SQL")

        events = read_events()
        types = [e["type"] for e in events]
        assert "CyclePhaseEntered" in types
        assert "ValidationOutcome" in types
        assert "GateViolation" in types
```

---

## Detailed Design

### Component 1: `log_gate_violation()` in governance_events.py

New function following exact pattern of `log_phase_transition()` and `log_validation_outcome()`.

**File:** `.claude/haios/lib/governance_events.py`
**Location:** After `log_validation_outcome()` (line 88), before session lifecycle section (line 91)

```python
def log_gate_violation(
    gate_id: str, work_id: str, violation_type: str, context: str
) -> dict:
    """
    Log gate violation event.

    Emitted when a MUST gate detects a violation and allows it (warn mode)
    or blocks it (block mode). Provides audit trail for governance bypasses.

    Args:
        gate_id: Gate/check identifier (e.g., "sql_block", "ceremony_contract", "no_governance_cycle")
        work_id: Work item ID (e.g., "WORK-146") or "unknown" if outside work context
        violation_type: "warn" (allowed but flagged) or "block" (denied)
        context: Human-readable description of the violation

    Returns:
        The logged event dict
    """
    event = {
        "type": "GateViolation",
        "gate_id": gate_id,
        "work_id": work_id,
        "violation_type": violation_type,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event


def get_gate_violations(work_id: str) -> list[dict]:
    """
    Get all gate violations for a work item.

    Args:
        work_id: Work item ID to filter by

    Returns:
        List of GateViolation event dicts
    """
    events = read_events()
    return [
        e for e in events
        if e.get("type") == "GateViolation" and e.get("work_id") == work_id
    ]
```

### Component 2: Wire violation logging into pre_tool_use.py

**Approach:** Add a helper `_log_violation()` in pre_tool_use.py that calls `log_gate_violation()`. Call it from `_deny()`, `_allow_with_warning()`, and `_deny_with_context()`.

The challenge: pre_tool_use.py doesn't currently import from governance_events.py directly — it uses GovernanceLayer (which imports governance_events). To avoid import complexity, we add a lightweight import inside the helper (same fail-permissive pattern used throughout the file).

**File:** `.claude/hooks/hooks/pre_tool_use.py`

New helper function:
```python
def _log_violation(gate_id: str, violation_type: str, reason: str) -> None:
    """Log gate violation event. Fail-permissive."""
    try:
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from governance_events import log_gate_violation

        # Extract work_id from current cycle state (best-effort)
        work_id = _get_current_work_id()
        log_gate_violation(gate_id, work_id, violation_type, reason)
    except Exception:
        pass  # Fail-permissive: logging must never break agent workflow
```

Work ID extraction helper:
```python
def _get_current_work_id() -> str:
    """Get current work_id from cycle state. Returns 'unknown' on failure."""
    try:
        import subprocess
        result = subprocess.run(
            ["just", "get-cycle"],
            capture_output=True, text=True, timeout=3,
            cwd=str(Path(__file__).parent.parent.parent.parent),
        )
        parts = result.stdout.strip().split("/")
        return parts[2] if len(parts) >= 3 else "unknown"
    except Exception:
        return "unknown"
```

**Integration points** (where `_log_violation()` is called):

1. `_deny()` — all blocked operations:
   ```python
   def _deny(reason: str) -> dict:
       _log_violation(_infer_gate_id(reason), "block", reason)
       return { ... }
   ```

2. `_allow_with_warning()` — warned operations:
   ```python
   def _allow_with_warning(reason: str) -> dict:
       _log_violation(_infer_gate_id(reason), "warn", reason)
       return { ... }
   ```

3. `_deny_with_context()` — blocked with state context:
   ```python
   def _deny_with_context(reason: str, state: str, layer) -> dict:
       _log_violation(_infer_gate_id(reason), "block", reason)
       return { ... }
   ```

Gate ID inference helper:
```python
def _infer_gate_id(reason: str) -> str:
    """Infer gate_id from denial/warning reason text."""
    reason_lower = reason.lower()
    if "sql" in reason_lower:
        return "sql_block"
    if "powershell" in reason_lower:
        return "powershell_block"
    if "scaffold" in reason_lower:
        return "scaffold_block"
    if "governed path" in reason_lower:
        return "path_governance"
    if "backlog_id" in reason_lower or "duplicate" in reason_lower:
        return "backlog_id_uniqueness"
    if "ceremony" in reason_lower and "contract" in reason_lower:
        return "ceremony_contract"
    if "memory_refs" in reason_lower:
        return "memory_refs"
    if "exit" in reason_lower and "gate" in reason_lower:
        return "exit_gate"
    if "activity" in reason_lower or "state" in reason_lower:
        return "activity_governance"
    return "unknown_gate"
```

### Call Chain Context

```
Claude Code dispatches PreToolUse hook
    |
    v
hook_dispatcher.py -> pre_tool_use.handle()
    |
    +-> _check_governed_activity() -> _deny_with_context() or _allow_with_context()
    +-> _check_sql_governance()    -> _deny()
    +-> _check_powershell_governance() -> _deny()
    +-> _check_scaffold_governance()   -> _deny()
    +-> _check_plan_validation()   -> _deny()
    +-> _check_memory_refs()       -> _allow_with_warning()
    +-> _check_backlog_id_uniqueness() -> _deny()
    +-> _check_exit_gate()         -> _allow_with_warning()
    +-> _check_ceremony_contract() -> _allow_with_warning() or _deny()
                                          |
                                          v  (NEW)
                                   _log_violation() -> governance_events.log_gate_violation()
                                                              |
                                                              v
                                                    governance-events.jsonl
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Log in `_deny()`/`_allow_with_warning()` helpers | Not in each `_check_*` function | 3 call sites vs 8+. Less code, guaranteed coverage of all current and future checks. |
| Infer gate_id from reason text | Not pass gate_id through call chain | Avoids changing signatures of 8 `_check_*` functions. Reason text is stable and unique per gate. |
| Fail-permissive `_log_violation()` | Not raise on logging failure | Acceptance criterion: "Logging does not block agent workflow". Wrap in try/except. |
| Work ID from `just get-cycle` | Not from hook_data | hook_data has no work_id field. `just get-cycle` returns `cycle/phase/work_id`. Same pattern as `get_activity_state()`. |
| `subprocess.run` with 3s timeout for work_id | Not cache or global | Hook runs per-tool-call. 3s timeout prevents hanging. Cost is acceptable for logging. |
| `get_gate_violations()` query function | Not just log | Enables `check_work_item_events()` to surface violations at close time. Follows pattern of `get_threshold_warnings()`. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No active cycle (work_id unknown) | `_get_current_work_id()` returns "unknown" | Implicit in fail-permissive design |
| `governance_events` import fails | `_log_violation()` catches exception, returns silently | Fail-permissive pattern |
| `just get-cycle` times out | 3s timeout, returns "unknown" | Fail-permissive pattern |
| Multiple violations in single hook call | Each `_deny`/`_allow_with_warning` call logs independently | Normal operation |
| `_allow_with_context()` without warning | Not a violation — no reason field means no gate was triggered | Only log when reason is present |

### Open Questions

**Q: Should `_allow_with_context()` (line 524) also log violations?**

No. `_allow_with_context()` is called for ALL allowed operations to provide state visibility. It's not a gate violation. Only `_allow_with_warning()` (line 475) indicates a gate detected something and warned. The distinction: `_allow_with_context(reason=None)` = normal operation; `_allow_with_warning(reason=...)` = gate violation in warn mode.

---

## Open Decisions (MUST resolve before implementation)

No `operator_decisions` in WORK-146 frontmatter. No blocking decisions.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | - | - | No operator decisions required |

---

## Implementation Steps

### Step 1: Write Failing Tests (RED)
- [ ] Add 5 tests to `tests/test_governance_events.py` in new `TestGateViolationLogging` class
- [ ] Verify all 5 tests fail (functions don't exist yet)

### Step 2: Implement `log_gate_violation()` and `get_gate_violations()` (GREEN)
- [ ] Add `log_gate_violation()` to `governance_events.py` after line 88
- [ ] Add `get_gate_violations()` to `governance_events.py` after `log_gate_violation()`
- [ ] Tests 1-5 pass

### Step 3: Wire into pre_tool_use.py
- [ ] Add `_log_violation()`, `_get_current_work_id()`, `_infer_gate_id()` helpers
- [ ] Modify `_deny()` to call `_log_violation()`
- [ ] Modify `_allow_with_warning()` to call `_log_violation()`
- [ ] Modify `_deny_with_context()` to call `_log_violation()`

### Step 4: Integration Verification
- [ ] All 5 new tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: run hook outside governance cycle, verify event in governance-events.jsonl

### Step 5: Update Event Type Documentation
- [ ] Add `GateViolation` to governance_events.py module docstring
- [ ] Update WORK-146 deliverables

### Step 6: Consumer Verification
- [ ] **SKIPPED:** No migration/rename — new functions added to existing files, no consumers to update

---

## Verification

- [ ] 5 new tests pass (`tests/test_governance_events.py::TestGateViolationLogging`)
- [ ] Full test suite passes (no regressions)
- [ ] **MUST:** All READMEs current (no README changes needed — existing files only)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `_get_current_work_id()` subprocess adds latency to every deny/warn | Low | 3s timeout; only runs on violations (not every tool call). Violations are rare. |
| `_infer_gate_id()` text matching breaks if reason text changes | Low | Gate IDs are best-effort labels, not machine-critical. Fallback to "unknown_gate". |
| Logging in `_deny()` creates event even for non-governance denials | Low | All denials from pre_tool_use.py ARE governance denials by definition. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 371 | 2026-02-14 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-146/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Event schema defined for gate violations | [ ] | `GateViolation` type in governance_events.py |
| PreToolUse hooks emit violation events on skip | [ ] | `_log_violation()` called from `_deny()`/`_allow_with_warning()` |
| Events include: gate_id, work_id, violation_type, timestamp, context | [ ] | Fields in `log_gate_violation()` event dict |
| Verification: run outside governance, confirm event logged | [ ] | Demo during CHECK phase |
| Documentation updated (event types in L4 observability section) | [ ] | Module docstring updated |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/governance_events.py` | `log_gate_violation()` + `get_gate_violations()` added | [ ] | |
| `.claude/hooks/hooks/pre_tool_use.py` | `_log_violation()` + `_get_current_work_id()` + `_infer_gate_id()` added; `_deny()`, `_allow_with_warning()`, `_deny_with_context()` modified | [ ] | |
| `tests/test_governance_events.py` | 5 new tests in `TestGateViolationLogging` class | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_governance_events.py -v
# Expected: 18+ tests passed (13 existing + 5 new)
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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (pre_tool_use.py calls log_gate_violation via _log_violation — runtime consumer)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-146/WORK.md (work item)
- @.claude/haios/lib/governance_events.py (target: new function)
- @.claude/hooks/hooks/pre_tool_use.py (target: wire violation logging)
- @tests/test_governance_events.py (target: new tests)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-OBSERVE-005)
- Memory 84270: Feature request for gate skip logging
- Memory 84269: Gate skip recommendation pattern

---
