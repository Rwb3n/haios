---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-02-23
backlog_id: WORK-209
title: "Enforce Session and Process Review Computable Predicates via Hooks"
author: Hephaestus
lifecycle_phase: plan
session: 436
generated: 2026-02-23
last_updated: 2026-02-23T18:45:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-209/WORK.md"
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
# Implementation Plan: Enforce Session and Process Review Computable Predicates via Hooks

---

## Goal

Extract the session-review trigger predicate into a testable lib function, wire it into the Stop hook so session-review reminders fire automatically at session-end, and add a PreToolUse gate that blocks writes to `manifesto/L3/` and `manifesto/L4/` unless a `ProcessReviewApproved` governance event exists in governance-events.jsonl.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No unresolved operator decisions in WORK-209 | N/A | N/A | Work item has no `operator_decisions` field |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/session_review_predicate.py` | CREATE | 2 |
| `.claude/hooks/hooks/stop.py` | MODIFY | 2 |
| `.claude/hooks/hooks/pre_tool_use.py` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/README.md` | Documents lib modules | 104-109 | UPDATE — add session_review_predicate row |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_session_review_predicate.py` | CREATE | New test file for predicate module |
| `tests/test_pre_tool_use_process_review.py` | CREATE | New test file for L3/L4 write-block gate |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 3 | Primary (1) + Test (2) tables |
| Files to modify | 3 | Primary (2) + Consumer (1) |
| Tests to write | 8 | Test Files table (see Layer 1 Tests) |
| Total blast radius | 6 | Sum of all unique files above |

---

## Layer 1: Specification

### Current State

```python
# .claude/hooks/hooks/stop.py lines 72-103 — _run_session_end_actions()
def _run_session_end_actions() -> None:
    try:
        lib_dir = Path(__file__).parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from session_end_actions import (
            read_session_number,
            log_session_ended,
            clear_cycle_state,
            detect_uncommitted_changes,
        )

        session_num = read_session_number()
        if session_num is not None:
            log_session_ended(session_num, agent="Hephaestus")

        clear_cycle_state()

        changes = detect_uncommitted_changes()
        if changes:
            sys.stderr.write(f"[session-end] {len(changes)} uncommitted change(s)\n")
    except Exception:
        pass  # Fail-permissive
```

**Behavior:** Stop hook runs session-end housekeeping (log SessionEnded, clear cycle state, detect uncommitted changes). No session-review predicate check.

**Problem:** Session-review trigger predicate lives in SKILL.md (agent-judged). No mechanical enforcement at session-end fires the reminder.

```python
# .claude/hooks/hooks/pre_tool_use.py lines 109-143 — Write/Edit checks
if tool_name in ("Write", "Edit"):
    file_path = tool_input.get("file_path", "")
    # ... plan validation, memory refs, backlog ID, exit gate, path governance
    result = _check_path_governance(file_path)
    if result:
        return result
```

**Behavior:** PreToolUse checks governed paths (new file creation) but does NOT check for ProcessReviewApproved events before writing to manifesto/L3/ or manifesto/L4/.

**Problem:** Agent can write L3/L4 content without running process-review-cycle. The governance event log has no write-gate enforcement.

```python
# .claude/haios/lib/session_review_predicate.py — DOES NOT EXIST
```

**Problem:** Predicate logic is duplicated across SKILL.md description and any future caller. No testable, canonical implementation.

### Desired State

**New file:** `.claude/haios/lib/session_review_predicate.py`

```python
# generated: 2026-02-23
"""
Session Review trigger predicate (WORK-209).

Computable predicate extracted from session-review-cycle SKILL.md.

Trigger condition (OR logic):
  - At least 1 work item CLOSED this session (event t="close" in session-log.jsonl)
  - OR at least 2 RetroCycleCompleted events in governance-events.jsonl

Public API:
    should_run_session_review()  -> bool
    _count_close_events()        -> int   (testable helper)
    _count_retro_completed()     -> int   (testable helper)

All functions are fail-permissive: they never raise exceptions.

Format dependency (critique A2): Close events depend on post_tool_use._append_session_event()
detecting "close" via Bash pattern match (regex: r"close.work|cli\\.py\\s+close").
If close is invoked differently, the close-event arm returns 0 silently.
The retro-count arm depends on RetroCycleCompleted events being logged by retro-cycle.
"""
import json
import sys
from pathlib import Path


def _get_lib_dir() -> Path:
    """Return lib directory path."""
    return Path(__file__).parent


def _count_close_events(session_log_path: Path = None) -> int:
    """Count work-close events in session-log.jsonl.

    Close events have t="close" in the compact JSONL format
    (produced by post_tool_use._append_session_event).

    Args:
        session_log_path: Override path for testing. If None, uses session_event_log.get_log_path().

    Returns:
        Count of close events. Returns 0 on any error.
    """
    try:
        lib_dir = _get_lib_dir()
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from session_event_log import get_log_path
        actual_path = session_log_path if session_log_path is not None else get_log_path()
        if not actual_path.exists():
            return 0
        count = 0
        for line in actual_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("t") == "close":
                    count += 1
            except (json.JSONDecodeError, AttributeError):
                pass
        return count
    except Exception:
        return 0


def _count_retro_completed(governance_events_path: Path = None) -> int:
    """Count RetroCycleCompleted events in governance-events.jsonl.

    Args:
        governance_events_path: Override Path for testing. If None, uses governance_events.EVENTS_FILE.

    Returns:
        Count of RetroCycleCompleted events. Returns 0 on any error.
    """
    try:
        lib_dir = _get_lib_dir()
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        if governance_events_path is not None:
            events_path = Path(governance_events_path)
        else:
            from governance_events import EVENTS_FILE
            events_path = EVENTS_FILE
        if not events_path.exists():
            return 0
        count = 0
        for line in events_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("type") == "RetroCycleCompleted":
                    count += 1
            except (json.JSONDecodeError, AttributeError):
                pass
        return count
    except Exception:
        return 0


def should_run_session_review(
    session_log_path: Path = None,
    governance_events_path: Path = None,
) -> bool:
    """Evaluate session-review trigger predicate.

    Predicate (OR logic):
      - At least 1 close event in session-log.jsonl, OR
      - At least 2 RetroCycleCompleted in governance-events.jsonl

    Args:
        session_log_path: Override for testing session-log.jsonl path.
        governance_events_path: Override for testing governance-events.jsonl path.

    Returns:
        True if session review should run. False on any error (fail-permissive).
    """
    try:
        close_count = _count_close_events(session_log_path)
        if close_count >= 1:
            return True
        retro_count = _count_retro_completed(governance_events_path)
        if retro_count >= 2:
            return True
        return False
    except Exception:
        return False  # Fail-permissive: never trigger review on error
```

**Modified file:** `.claude/hooks/hooks/stop.py` — add session-review injection to `_run_session_end_actions()`

**Location:** After `clear_cycle_state()` call, before `detect_uncommitted_changes()`

**Current Code:**
```python
        clear_cycle_state()

        changes = detect_uncommitted_changes()
```

**Target Code:**
```python
        clear_cycle_state()

        # Session-review predicate check (WORK-209)
        _inject_session_review_reminder()

        changes = detect_uncommitted_changes()
```

**New function to add at bottom of stop.py:**
```python
def _inject_session_review_reminder() -> None:
    """Check session-review predicate and inject reminder if it passes (WORK-209).

    If should_run_session_review() returns True, writes reminder to stderr
    so Claude Code displays it as context at session-end.

    Fail-permissive: never raises, never blocks session-end.
    """
    try:
        lib_dir = Path(__file__).parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from session_review_predicate import should_run_session_review
        if should_run_session_review():
            sys.stderr.write(
                "[session-end] MUST run session-review-cycle before closing this session. "
                "Trigger predicate passed (work closed or retro completed this session).\n"
            )
    except Exception:
        pass  # Fail-permissive
```

**Modified file:** `.claude/hooks/hooks/pre_tool_use.py` — add ProcessReviewApproved gate in `handle()`

**Location:** Inside the `if tool_name in ("Write", "Edit"):` block, after exit gate check and BEFORE `_check_path_governance`

**Current Code:**
```python
        # Exit gate check (E2-155) - only for Edit with old_string
        if tool_name == "Edit" and old_string:
            result = _check_exit_gate(file_path, old_string, new_string)
            if result:
                return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result
```

**Target Code:**
```python
        # Exit gate check (E2-155) - only for Edit with old_string
        if tool_name == "Edit" and old_string:
            result = _check_exit_gate(file_path, old_string, new_string)
            if result:
                return result

        # Process Review approval gate (WORK-209) - L3/L4 write protection
        result = _check_process_review_gate(file_path)
        if result:
            return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result
```

**New function to add to pre_tool_use.py (after `_check_exit_gate`):**
```python
def _check_process_review_gate(file_path: str) -> Optional[dict]:
    """
    Block writes to manifesto/L3/ and manifesto/L4/ without ProcessReviewApproved event (WORK-209).

    The process-review-cycle APPROVE phase logs a ProcessReviewApproved governance event
    BEFORE the Write call. This gate enforces that contract mechanically.

    Returns deny response if L3/L4 path without approval, None otherwise.
    """
    if not file_path:
        return None

    normalized = file_path.replace("\\", "/")

    # Only applies to manifesto L3/L4 paths
    is_l3_or_l4 = (
        "manifesto/L3/" in normalized or
        "manifesto/L4/" in normalized
    )
    if not is_l3_or_l4:
        return None

    try:
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from governance_events import read_events

        # TODO(WORK-209): This reads ALL historical events, not just current session.
        # Per-session scoping is a follow-on. Any prior ProcessReviewApproved event
        # permanently unlocks L3/L4 writes. Acceptable for V1 given fail-permissive stance.
        events = read_events()
        has_approval = any(
            e.get("type") == "ProcessReviewApproved"
            for e in events
        )

        if not has_approval:
            return _deny(
                "BLOCKED: Writing to manifesto/L3/ or manifesto/L4/ requires a "
                "ProcessReviewApproved governance event. "
                "Run process-review-cycle APPROVE phase first, which logs the event before Write. "
                "(WORK-209, REQ-FEEDBACK-007)"
            )

    except Exception:
        pass  # Fail-permissive: gate failure must not block all L3/L4 writes

    return None
```

**Bootstrapping note (critique A3):** The first L3/L4 write after WORK-209 deployment requires a process-review-cycle run to create the initial ProcessReviewApproved event. The block message guides operators to the correct action. If governance-events.jsonl does not exist or cannot be read, the exception block allows the write (fail-permissive).

**Behavior:** All three changes together:
1. `session_review_predicate.py` — computable, testable predicate function
2. Stop hook injection — mechanical reminder fires when predicate passes
3. PreToolUse gate — L3/L4 writes blocked without ProcessReviewApproved event

**Result:** CH-059 CeremonyAutomation: computable predicates moved from Tier 3 (agent-read SKILL.md) to Tier 1/2 (hooks + lib functions).

### Tests

#### Test 1: Predicate — passes on close event
- **file:** `tests/test_session_review_predicate.py`
- **function:** `test_should_run_when_close_event_exists(tmp_path)`
- **setup:** Write session-log.jsonl with `{"t": "close", "v": "WORK-100", "w": "WORK-100", "ts": "15:00"}`. Empty governance-events.jsonl.
- **assertion:** `should_run_session_review(session_log_path=..., governance_events_path=...)` returns `True`

#### Test 2: Predicate — passes on two retro events
- **file:** `tests/test_session_review_predicate.py`
- **function:** `test_should_run_when_two_retro_completed(tmp_path)`
- **setup:** Empty session-log.jsonl. Write governance-events.jsonl with 2 lines of `{"type": "RetroCycleCompleted", ...}`.
- **assertion:** `should_run_session_review(...)` returns `True`

#### Test 3: Predicate — does NOT pass on zero events
- **file:** `tests/test_session_review_predicate.py`
- **function:** `test_should_not_run_when_no_qualifying_events(tmp_path)`
- **setup:** Empty session-log.jsonl (0 close events). governance-events.jsonl with 1 `RetroCycleCompleted` (below threshold of 2).
- **assertion:** `should_run_session_review(...)` returns `False`

#### Test 4: Predicate — edge case: missing files
- **file:** `tests/test_session_review_predicate.py`
- **function:** `test_should_not_run_when_files_missing(tmp_path)`
- **setup:** Non-existent paths passed for both log files.
- **assertion:** `should_run_session_review(...)` returns `False` (not raises)

#### Test 5: PreToolUse — blocks L3 write without approval
- **file:** `tests/test_pre_tool_use_process_review.py`
- **function:** `test_l3_write_blocked_without_process_review_approved(tmp_path, monkeypatch)`
- **setup:** Write empty governance-events.jsonl to `tmp_path`. Patch: `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")` where `governance_events` is the imported module object.
- **assertion:** `_check_process_review_gate(".claude/haios/manifesto/L3/principles.md")` returns dict with `permissionDecision == "deny"`

#### Test 6: PreToolUse — allows L3 write with approval event
- **file:** `tests/test_pre_tool_use_process_review.py`
- **function:** `test_l3_write_allowed_with_process_review_approved(tmp_path, monkeypatch)`
- **setup:** Write `{"type": "ProcessReviewApproved", "timestamp": "..."}` to `tmp_path / "governance-events.jsonl"`. Patch: `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`.
- **assertion:** `_check_process_review_gate(".claude/haios/manifesto/L3/principles.md")` returns `None`

#### Test 7: PreToolUse — non-L3/L4 path not affected
- **file:** `tests/test_pre_tool_use_process_review.py`
- **function:** `test_non_manifesto_path_not_affected()`
- **setup:** No setup needed.
- **assertion:** `_check_process_review_gate("docs/work/active/WORK-100/WORK.md")` returns `None`

#### Test 8: Predicate — single retro event does not pass
- **file:** `tests/test_session_review_predicate.py`
- **function:** `test_one_retro_does_not_pass_threshold(tmp_path)`
- **setup:** Empty session-log.jsonl. governance-events.jsonl with exactly 1 `RetroCycleCompleted`.
- **assertion:** `should_run_session_review(...)` returns `False`

### Design

#### File 1 (NEW): `.claude/haios/lib/session_review_predicate.py`

Canonical implementation is in the Desired State section above. Key design points:
- `should_run_session_review()` is the public API — single boolean return
- `_count_close_events()` and `_count_retro_completed()` are testable helpers with explicit path overrides
- Path overrides use direct file reads (not `unittest.mock`) to keep production code clean
- Reads files directly with JSONL parsing — avoids coupling to `session_event_log.read_events()` or `governance_events.read_events()` which have hardcoded paths difficult to override in tests
- Format dependency: close events use `t="close"` format from `post_tool_use._append_session_event()` (critique A2)

#### File 2 (MODIFY): `.claude/hooks/hooks/stop.py`

**Location:** Lines 97-103 in `_run_session_end_actions()`, and add new `_inject_session_review_reminder()` function.

**Current Code (lines 97-103):**
```python
        clear_cycle_state()

        changes = detect_uncommitted_changes()
        if changes:
            sys.stderr.write(f"[session-end] {len(changes)} uncommitted change(s)\n")
```

**Target Code:**
```python
        clear_cycle_state()

        # Session-review predicate check (WORK-209)
        _inject_session_review_reminder()

        changes = detect_uncommitted_changes()
        if changes:
            sys.stderr.write(f"[session-end] {len(changes)} uncommitted change(s)\n")
```

**New function (append after `_run_session_end_actions`):**
```python
def _inject_session_review_reminder() -> None:
    """Check session-review predicate and inject reminder if it passes (WORK-209).

    If should_run_session_review() returns True, writes reminder to stderr
    so Claude Code displays it as context at session-end.

    Fail-permissive: never raises, never blocks session-end.
    """
    try:
        lib_dir = Path(__file__).parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from session_review_predicate import should_run_session_review
        if should_run_session_review():
            sys.stderr.write(
                "[session-end] MUST run session-review-cycle before closing this session. "
                "Trigger predicate passed (work closed or retro completed this session).\n"
            )
    except Exception:
        pass  # Fail-permissive
```

**Diff:**
```diff
         clear_cycle_state()
+
+        # Session-review predicate check (WORK-209)
+        _inject_session_review_reminder()
+
         changes = detect_uncommitted_changes()
```

#### File 3 (MODIFY): `.claude/hooks/hooks/pre_tool_use.py`

**Location:** Lines 131-139 in `handle()`, inside `if tool_name in ("Write", "Edit"):` block.

**Current Code (lines 131-139):**
```python
        # Exit gate check (E2-155) - only for Edit with old_string
        if tool_name == "Edit" and old_string:
            result = _check_exit_gate(file_path, old_string, new_string)
            if result:
                return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result
```

**Target Code:**
```python
        # Exit gate check (E2-155) - only for Edit with old_string
        if tool_name == "Edit" and old_string:
            result = _check_exit_gate(file_path, old_string, new_string)
            if result:
                return result

        # Process Review approval gate (WORK-209) - L3/L4 write protection
        result = _check_process_review_gate(file_path)
        if result:
            return result

        # Path governance - only for new files
        result = _check_path_governance(file_path)
        if result:
            return result
```

**New function (add after `_check_exit_gate` function body, before `_check_path_governance`):**
```python
def _check_process_review_gate(file_path: str) -> Optional[dict]:
    """
    Block writes to manifesto/L3/ and manifesto/L4/ without ProcessReviewApproved event (WORK-209).

    The process-review-cycle APPROVE phase logs a ProcessReviewApproved governance event
    BEFORE the Write call. This gate enforces that contract mechanically.

    Returns deny response if L3/L4 path without approval, None otherwise.
    """
    if not file_path:
        return None

    normalized = file_path.replace("\\", "/")

    # Only applies to manifesto L3/L4 paths
    is_l3_or_l4 = (
        "manifesto/L3/" in normalized or
        "manifesto/L4/" in normalized
    )
    if not is_l3_or_l4:
        return None

    try:
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from governance_events import read_events

        events = read_events()
        has_approval = any(
            e.get("type") == "ProcessReviewApproved"
            for e in events
        )

        if not has_approval:
            return _deny(
                "BLOCKED: Writing to manifesto/L3/ or manifesto/L4/ requires a "
                "ProcessReviewApproved governance event. "
                "Run process-review-cycle APPROVE phase first, which logs the event before Write. "
                "(WORK-209, REQ-FEEDBACK-007)"
            )

    except Exception:
        pass  # Fail-permissive: gate failure must not block all L3/L4 writes

    return None
```

### Call Chain

```
Stop hook fires at session-end
    |
    +-> handle(hook_data)
    |       Returns: Optional[str]
    |
    +-> _run_session_end_actions()          # <-- MODIFIED
    |       |
    |       +-> clear_cycle_state()
    |       |
    |       +-> _inject_session_review_reminder()   # <-- NEW
    |               |
    |               +-> should_run_session_review()  # NEW in lib/
    |                       |
    |                       +-> _count_close_events(session_log_path)
    |                       |       reads: session-log.jsonl (t="close")
    |                       |
    |                       +-> _count_retro_completed(governance_events_path)
    |                               reads: governance-events.jsonl (type="RetroCycleCompleted")
    |
    +-> detect_uncommitted_changes()

PreToolUse fires before Write/Edit
    |
    +-> handle(hook_data)
    |
    +-> if tool_name in ("Write", "Edit"):
            |
            +-> _check_process_review_gate(file_path)   # <-- NEW
                    |
                    +-> checks "manifesto/L3/" or "manifesto/L4/" in path
                    +-> reads governance_events.read_events()
                    +-> checks any event.type == "ProcessReviewApproved"
                    +-> if none found: _deny(...)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Predicate in lib/ (not inline in hook) | Separate `session_review_predicate.py` module | Testable in isolation without hook machinery. Matches existing pattern (session_end_actions.py, tier_detector.py, critique_injector.py). |
| Stop hook stderr injection (not return value) | `sys.stderr.write(...)` | Stop hook `handle()` return value is for extraction status. stderr is how session-end context is injected (matches `detect_uncommitted_changes` pattern in stop.py). |
| Path parameters for testability | `session_log_path`, `governance_events_path` as optional args | Avoids complex mock patching in tests. Direct file reads with optional override is the clean pattern. |
| L3/L4 gate reads full governance-events.jsonl | `read_events()` not scoped to session | ProcessReviewApproved events are logged per-proposal. Any prior approval for any file in this session is sufficient. Future scope refinement can narrow if needed. |
| Fail-permissive on L3/L4 gate error | `except Exception: pass` returns None (allow) | Hook errors must never permanently block L3/L4 writes. If governance_events.py is unavailable, allow the write. Per mem:87440. |
| Deny (not warn) for L3/L4 without approval | `_deny(...)` not `_allow_with_warning(...)` | L3/L4 are highest governance artifacts (REQ-GOVERN-002). Warn is not sufficient for irreversible changes. |
| No session-scoping for approval events | Check all events, not just current session | governance-events.jsonl has no session-scoping field by default. ProcessReviewApproved already contains session={N} in its message but the type check is sufficient. If per-session scoping is needed, it's a follow-on. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| session-log.jsonl missing | `_count_close_events()` returns 0, predicate returns False | Test 4 |
| governance-events.jsonl missing | `_count_retro_completed()` returns 0, predicate returns False | Test 4 |
| Exactly 1 retro event (below threshold) | Returns False (threshold is ≥2) | Test 8 |
| L3 path with approval event present | Gate returns None (allow) | Test 6 |
| Non-manifesto path | Gate returns None immediately | Test 7 |
| governance_events import fails | Except block returns None (allow write) | No dedicated test — fail-permissive |
| Malformed JSONL line in governance-events | `json.JSONDecodeError` caught, line skipped | Implicit in Tests 5-6 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ProcessReviewApproved event type doesn't match exactly | H | Read process-review-cycle SKILL.md source (done). Exact string: `"ProcessReviewApproved"` per Phase 4 governance event format. |
| Gate blocks ALL L3/L4 edits permanently if EVENTS_FILE is misconfigured | H | Fail-permissive except block returns None (allow) on any error. Only blocks when events are successfully read AND no approval found. |
| Stop hook stderr output not visible to agent | M | This is how `detect_uncommitted_changes` currently works. Same mechanism already validates. |
| RetroCycleCompleted event not yet logged by retro-cycle SKILL | M | Predicate also checks close events, which are already logged via PostToolUse. Either condition triggers reminder. |
| Session-log.jsonl close event format change | L | `_count_close_events()` checks `t == "close"` per compact format defined in session_event_log.py. Test 1 validates this. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_session_review_predicate.py` (Tests 1-4, 8) and `tests/test_pre_tool_use_process_review.py` (Tests 5-7) from Layer 1 Tests section
- **output:** 2 test files exist, all 8 tests fail (ImportError or AssertionError)
- **verify:** `pytest tests/test_session_review_predicate.py tests/test_pre_tool_use_process_review.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 8

### Step 2: Implement Predicate Module (GREEN for Tests 1-4, 8)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/session_review_predicate.py` from Layer 1 Design section
- **output:** Tests 1-4 and 8 pass
- **verify:** `pytest tests/test_session_review_predicate.py -v` exits 0, `5 passed` in output

### Step 3: Integrate Predicate into Stop Hook (GREEN for session-review reminder)
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY) — stop.py
- **input:** Step 2 complete (predicate module exists and tests pass)
- **action:** Modify `.claude/hooks/hooks/stop.py`: add `_inject_session_review_reminder()` call in `_run_session_end_actions()` and add new function body per Layer 1 Design
- **output:** Stop hook calls the predicate; no new test failures
- **verify:** `grep "_inject_session_review_reminder" .claude/hooks/hooks/stop.py` returns 2 matches (definition + call)

### Step 4: Implement PreToolUse Gate (GREEN for Tests 5-7)
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY) — pre_tool_use.py
- **input:** Step 2 complete (governance_events.py is unchanged — already exists)
- **action:** Modify `.claude/hooks/hooks/pre_tool_use.py`: add `_check_process_review_gate()` call in `handle()` and add new function body per Layer 1 Design
- **output:** Tests 5-7 pass; L3/L4 writes blocked without approval event
- **verify:** `pytest tests/test_pre_tool_use_process_review.py -v` exits 0, `3 passed` in output

### Step 5: Full Test Suite (No Regressions)
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Steps 2-4 complete
- **action:** Run full test suite
- **output:** All prior tests still pass, 8 new tests pass
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `1579 passed` (1571 + 8 new), 0 failed

### Step 6: Update Consumer Documentation
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 5 complete (all tests green)
- **action:** Update `.claude/haios/lib/README.md` to add `session_review_predicate.py` row to Modules table
- **output:** README reflects new module
- **verify:** `grep "session_review_predicate" .claude/haios/lib/README.md` returns 1+ match

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_session_review_predicate.py -v` | 5 passed, 0 failed |
| `pytest tests/test_pre_tool_use_process_review.py -v` | 3 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs baseline (1571 pre-existing passing) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| `lib/session_review_predicate.py` exists | `test -f .claude/haios/lib/session_review_predicate.py && echo OK` | `OK` |
| Predicate function exported | `python -c "from session_review_predicate import should_run_session_review; print('OK')"` (run from lib/) | `OK` |
| Stop hook calls `_inject_session_review_reminder` | `grep "_inject_session_review_reminder" .claude/hooks/hooks/stop.py` | 2 matches (definition + call) |
| PreToolUse has `_check_process_review_gate` | `grep "_check_process_review_gate" .claude/hooks/hooks/pre_tool_use.py` | 2 matches (definition + call) |
| L3/L4 block message present | `grep "ProcessReviewApproved" .claude/hooks/hooks/pre_tool_use.py` | 1+ matches |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| README updated | `grep "session_review_predicate" .claude/haios/lib/README.md` | 1+ match |
| No stale references to old inline predicate | `grep -r "WorkClosed.*SKILL\|session-review.*trigger" .claude/hooks/ --include="*.py"` | 0 matches |
| stop.py still fail-permissive | `grep "except Exception" .claude/hooks/hooks/stop.py` | 2+ matches |
| pre_tool_use.py still fail-permissive for gate | `grep -A2 "_check_process_review_gate" .claude/hooks/hooks/pre_tool_use.py \| grep "except"` | 1+ match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 5 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists — stop.py calls `_inject_session_review_reminder()` (Consumer Integrity table)
- [ ] Runtime consumer exists — pre_tool_use.py calls `_check_process_review_gate()` (Consumer Integrity table)
- [ ] No stale references (Consumer Integrity table)
- [ ] README updated (Consumer Integrity table)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-209/WORK.md` (work item)
- `.claude/skills/session-review-cycle/SKILL.md` (trigger predicate source — OR logic: ≥1 WorkClosed OR ≥2 RetroCycleCompleted)
- `.claude/skills/process-review-cycle/SKILL.md` (ProcessReviewApproved event — logged before Write in APPROVE phase)
- `.claude/hooks/hooks/stop.py` (session-end hook — target for predicate injection)
- `.claude/hooks/hooks/pre_tool_use.py` (PreToolUse hook — target for L3/L4 write gate)
- `.claude/haios/lib/session_event_log.py` (close event source — t="close" in compact format)
- `.claude/haios/lib/governance_events.py` (RetroCycleCompleted + ProcessReviewApproved event source)
- `.claude/haios/lib/session_end_actions.py` (pattern reference for fail-permissive lib functions)
- ADR-048 (progressive contracts, per-file skill fracturing)
- REQ-CEREMONY-005, REQ-FEEDBACK-006, REQ-FEEDBACK-007
- L3.21 (Computable Means Mechanical)
- Memory queried: hooks fail-permissive pattern (mem:87440), session events format (session_event_log.py), governance events structure (governance_events.py). No prior implementations of session-review predicate extraction found — this is first instance.

---
