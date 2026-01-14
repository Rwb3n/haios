---
template: implementation_plan
status: complete
date: 2026-01-14
backlog_id: E2-287
title: Add UserPromptSubmit warning for work outside cycle
author: Hephaestus
lifecycle_phase: plan
session: 190
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-14T22:11:41'
---
# Implementation Plan: Add UserPromptSubmit warning for work outside cycle

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

UserPromptSubmit hook will inject a warning when agent attempts work outside an active governance cycle (session_state.active_cycle is null), providing soft enforcement for cycle compliance.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/user_prompt_submit.py` |
| Lines of code affected | ~30 | Add new function + call in handle() |
| New files to create | 0 | Modification only |
| Tests to write | 3 | Warning present, warning absent, override behavior |
| Dependencies | 0 | No new imports (uses existing json, Path) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single hook file, reads existing JSON |
| Risk of regression | Low | Additive change, existing tests cover current behavior |
| External dependencies | Low | Reads haios-status-slim.json (E2-286 added session_state) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Implement warning function | 15 min | High |
| Integration verification | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/user_prompt_submit.py:50-107 - handle() function
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())
    # ... vitals disabled ...
    thresholds = _get_thresholds(cwd)
    if thresholds:
        output_parts.append(thresholds)
    lifecycle = _get_lifecycle_guidance(prompt, cwd)
    if lifecycle:
        output_parts.append("")
        output_parts.append(lifecycle)
    rfc2119 = _get_rfc2119_reminders(prompt)
    if rfc2119:
        output_parts.append("")
        output_parts.append(rfc2119)
    return "\n".join(output_parts)
```

**Behavior:** Hook injects date/time, thresholds, lifecycle guidance, and RFC2119 reminders but has no awareness of session_state.active_cycle.

**Result:** Agent can work outside governance cycles without any warning - the soft enforcement gap identified in INV-062.

### Desired State

```python
# .claude/hooks/hooks/user_prompt_submit.py:50-115 - handle() after change
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())
    # ... vitals disabled ...

    # E2-287: Session state warning (before thresholds)
    session_warning = _get_session_state_warning(cwd)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    thresholds = _get_thresholds(cwd)
    # ... rest unchanged ...
```

**Behavior:** Hook checks session_state.active_cycle and injects warning if null.

**Result:** Agent sees warning when working outside active cycle, creating friction for governance bypass.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Warning Present When No Active Cycle
```python
def test_session_state_warning_when_no_cycle(tmp_path):
    """E2-287: Inject warning when session_state.active_cycle is null."""
    from hooks.user_prompt_submit import _get_session_state_warning

    # Create slim status with null active_cycle
    slim = {"session_state": {"active_cycle": None}}
    slim_path = tmp_path / ".claude" / "haios-status-slim.json"
    slim_path.parent.mkdir(parents=True)
    slim_path.write_text(json.dumps(slim))

    warning = _get_session_state_warning(str(tmp_path))

    assert warning is not None
    assert "No active governance cycle" in warning
    assert "invoke a skill" in warning.lower() or "skill" in warning.lower()
```

### Test 2: No Warning When Cycle Active
```python
def test_no_warning_when_cycle_active(tmp_path):
    """E2-287: No warning when session_state.active_cycle is set."""
    from hooks.user_prompt_submit import _get_session_state_warning

    # Create slim status with active cycle
    slim = {"session_state": {"active_cycle": "implementation-cycle"}}
    slim_path = tmp_path / ".claude" / "haios-status-slim.json"
    slim_path.parent.mkdir(parents=True)
    slim_path.write_text(json.dumps(slim))

    warning = _get_session_state_warning(str(tmp_path))

    assert warning is None
```

### Test 3: Graceful Handling of Missing session_state
```python
def test_no_warning_when_session_state_missing(tmp_path):
    """E2-287: Handle missing session_state gracefully (backward compat)."""
    from hooks.user_prompt_submit import _get_session_state_warning

    # Create slim status without session_state (old format)
    slim = {"generated": "2026-01-14"}
    slim_path = tmp_path / ".claude" / "haios-status-slim.json"
    slim_path.parent.mkdir(parents=True)
    slim_path.write_text(json.dumps(slim))

    warning = _get_session_state_warning(str(tmp_path))

    # Should not crash, should return None (no warning for old format)
    assert warning is None
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/user_prompt_submit.py`

#### Change 1: Add _get_session_state_warning function (after _get_datetime_context)

**New Function (add after line 116):**
```python
def _get_session_state_warning(cwd: str) -> Optional[str]:
    """
    Check if agent is working outside an active governance cycle.

    E2-287: Soft enforcement - inject warning when session_state.active_cycle is null.
    This creates friction for governance bypass without blocking.

    Args:
        cwd: Working directory path

    Returns:
        Warning message if no active cycle, None otherwise.
    """
    if not cwd:
        return None

    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None

    try:
        slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        session_state = slim.get("session_state", {})

        # If session_state is missing or active_cycle is null, warn
        if session_state.get("active_cycle") is None:
            return (
                "--- Session State Warning (E2-287) ---\n"
                "No active governance cycle detected.\n"
                "Invoke a skill (/coldstart, /implement, /close) to enter a cycle.\n"
                "Working outside cycles bypasses governance gates.\n"
                "---"
            )
        return None
    except Exception:
        return None
```

#### Change 2: Call _get_session_state_warning in handle() (after line 87)

**Current Code (lines 86-92):**
```python
    cwd = hook_data.get("cwd", "")
    # vitals disabled - no append

    # Part 3: Dynamic thresholds
    thresholds = _get_thresholds(cwd)
    if thresholds:
        output_parts.append(thresholds)
```

**Changed Code:**
```python
    cwd = hook_data.get("cwd", "")
    # vitals disabled - no append

    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 3: Dynamic thresholds
    thresholds = _get_thresholds(cwd)
    if thresholds:
        output_parts.append(thresholds)
```

**Diff:**
```diff
     cwd = hook_data.get("cwd", "")
     # vitals disabled - no append

+    # Part 2.5: Session state warning (E2-287)
+    session_warning = _get_session_state_warning(cwd)
+    if session_warning:
+        output_parts.append("")
+        output_parts.append(session_warning)
+
     # Part 3: Dynamic thresholds
     thresholds = _get_thresholds(cwd)
```

### Call Chain Context

```
Claude Code UserPromptSubmit event
    |
    +-> hook_dispatcher.dispatch_hook()
    |       Routes to user_prompt_submit.handle()
    |
    +-> user_prompt_submit.handle()
    |       Calls: _get_datetime_context()
    |       Calls: _get_session_state_warning()  # <-- NEW
    |       Calls: _get_thresholds()
    |       Calls: _get_lifecycle_guidance()
    |       Calls: _get_rfc2119_reminders()
    |       Returns: concatenated output string
    |
    +-> Claude sees injected context before processing prompt
```

### Function/Component Signatures

```python
def _get_session_state_warning(cwd: str) -> Optional[str]:
    """
    Check if agent is working outside an active governance cycle.

    Args:
        cwd: Working directory path (from hook_data)

    Returns:
        Warning message string if session_state.active_cycle is None,
        None otherwise (cycle is active or file doesn't exist).

    Raises:
        None - all exceptions caught and return None for graceful degradation.
    """
```

### Behavior Logic

**Current Flow:**
```
UserPromptSubmit → handle() → date/time + thresholds + lifecycle + rfc2119
                                    (no session state check)
```

**Fixed Flow:**
```
UserPromptSubmit → handle() → date/time
                                 ↓
                       → _get_session_state_warning(cwd)
                                 ├─ active_cycle != None → return None (no warning)
                                 └─ active_cycle == None → return warning string
                                 ↓
                       → thresholds + lifecycle + rfc2119
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Warning position | After vitals, before thresholds | Early in output so agent sees it prominently |
| Enforcement level | Soft (warning only) | INV-062 determined hard enforcement not possible with Skill() |
| Missing session_state | Return None (no warning) | Backward compatibility with old JSON format |
| Error handling | Return None | Graceful degradation per existing pattern in file |
| Warning format | RFC2119 style | Consistent with _get_rfc2119_reminders() pattern |

### Input/Output Examples

**Current haios-status-slim.json (real data after E2-286):**
```json
{
    "session_state": {
        "active_cycle": null,
        "current_phase": null,
        "work_id": null,
        "entered_at": null
    }
}
```

**Before Fix:**
```
UserPromptSubmit hook output:
"Today is Wednesday, 2026-01-14 09:40 PM"
(no session state warning - agent works without friction)
```

**After Fix:**
```
UserPromptSubmit hook output:
"Today is Wednesday, 2026-01-14 09:40 PM

--- Session State Warning (E2-287) ---
No active governance cycle detected.
Invoke a skill (/coldstart, /implement, /close) to enter a cycle.
Working outside cycles bypasses governance gates.
---"
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| session_state missing | Return None (backward compat) | Test 3 |
| active_cycle is null | Return warning | Test 1 |
| active_cycle has value | Return None | Test 2 |
| haios-status-slim.json missing | Return None | Implicit in Test 1 setup |
| Invalid JSON | Return None (try/except) | Covered by existing pattern |

### Open Questions

**Q: Should coldstart be exempt from the warning (it's the entry point)?**

Answer: No. Coldstart is the skill that sets up the cycle. The warning is appropriate during coldstart since it reminds the agent to complete the coldstart flow. Once coldstart chains to survey-cycle, the active_cycle will be set (by E2-288).

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| *None* | - | - | All design decisions resolved in INV-062 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 3 tests to `tests/test_hooks.py`
- [ ] `test_session_state_warning_when_no_cycle`
- [ ] `test_no_warning_when_cycle_active`
- [ ] `test_no_warning_when_session_state_missing`
- [ ] Verify all 3 tests fail (red)

### Step 2: Add _get_session_state_warning Function
- [ ] Add function after `_get_datetime_context()` in user_prompt_submit.py
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Call Function in handle()
- [ ] Add call to `_get_session_state_warning(cwd)` after vitals section
- [ ] Append warning to output_parts if not None
- [ ] Integration verification: run hook manually

### Step 4: Full Test Suite
- [ ] Run `pytest tests/test_hooks.py -v`
- [ ] No regressions in existing tests

### Step 5: README Sync (MUST)
- [ ] **SKIPPED:** No README updates needed - internal function addition

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Warning noise during normal work | Low | Warning only shows when active_cycle is null; E2-288 will set it on skill entry |
| Backward compatibility | Low | Function returns None if session_state missing (old JSON format) |
| Performance | Low | Single JSON read, already done for other checks |

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
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | `_get_session_state_warning` function exists | [ ] | |
| `.claude/hooks/hooks/user_prompt_submit.py` | `handle()` calls `_get_session_state_warning` | [ ] | |
| `tests/test_hooks.py` | 3 session_state tests exist | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_hooks.py -v -k session_state
# Expected: 3 tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-062: Session State Tracking and Cycle Enforcement Architecture (spawned this work)
- E2-286: Add session_state to haios-status-slim.json (provides the schema)
- E2-288: Add just set-cycle recipe (will populate session_state on skill entry)
- `.claude/hooks/hooks/user_prompt_submit.py`: Target implementation file

---
