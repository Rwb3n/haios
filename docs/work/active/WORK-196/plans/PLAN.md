---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-23
backlog_id: WORK-196
title: "UserPromptSubmit Hook Injection Batch"
author: Hephaestus
lifecycle_phase: plan
session: 428
generated: 2026-02-23
last_updated: 2026-02-23T11:03:18

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-196/WORK.md"
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
# Implementation Plan: UserPromptSubmit Hook Injection Batch

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add three low-token context injections to `user_prompt_submit.py` — `[SESSION: N]`, `[WORKING: WORK-XXX]`, and `[DURATION: Nm]` — so the agent has ambient session awareness on every prompt without incurring more than ~15 extra tokens per call.

---

## Open Decisions

<!-- No operator_decisions in WORK.md. All design decisions were resolved by the
     WORK-194 investigation. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Which candidates to implement | Session / Working / Duration / Ready-count | Session + Working + Duration | WORK-194 evaluation: Candidate 4 (Ready-count) deferred — WorkEngine too heavy for per-prompt hook. Candidates 1-3 approved. |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 1 |

### Consumer Files

<!-- The hook is invoked by hook_dispatcher.py. Tests live in tests/test_hooks.py.
     No documentation file references the injections by name yet. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_hooks.py` | imports + calls `handle()` via dispatcher | multiple | UPDATE — add TestSessionInjections class |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_hooks.py` | UPDATE | Add new test class `TestSessionInjections` with 8 tests |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files; all changes in existing module |
| Files to modify | 1 | Primary Files table (user_prompt_submit.py) |
| Test files to update | 1 | tests/test_hooks.py |
| Total blast radius | 2 | user_prompt_submit.py + test_hooks.py |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent

     MUST INCLUDE:
     1. Actual current code that will be changed (copy from source)
     2. Exact target code (not pseudocode)
     3. Function signatures with types
     4. Input/output examples with REAL system data -->

### Current State

```python
# .claude/hooks/hooks/user_prompt_submit.py — lines 64-121 (handle() function)
def handle(hook_data: dict) -> str:
    output_parts = []

    # Part 1: Date/time context
    output_parts.append(_get_datetime_context())

    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)

    # Part 2: HAIOS Vitals (disabled)
    cwd = hook_data.get("cwd", "")

    # WORK-195: Read slim JSON once, pass to all consumers
    slim = _read_slim(cwd)

    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd, slim)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 2.6: Phase contract injection (WORK-188, ADR-048)
    phase_contract = _get_phase_contract(cwd, slim)
    if phase_contract:
        output_parts.append("")
        output_parts.append(phase_contract)

    # Part 4: Lifecycle guidance
    prompt = hook_data.get("prompt", "")
    lifecycle = _get_lifecycle_guidance(prompt, cwd)
    if lifecycle:
        output_parts.append("")
        output_parts.append(lifecycle)

    # Part 5: RFC2119 reminders
    rfc2119 = _get_rfc2119_reminders(prompt)
    if rfc2119:
        output_parts.append("")
        output_parts.append(rfc2119)

    return "\n".join(output_parts)
```

**Behavior:** Injects datetime, context usage percentage, optional session state warning, optional phase contract, optional lifecycle guidance, optional RFC2119 reminders.

**Problem:** No ambient session number, active work item, or duration are injected. Agent must deduce these from other sources or miss them entirely after compaction.

### Desired State

Three new private functions are added to `user_prompt_submit.py`:

```python
# NEW: _get_session_number(cwd: str) -> Optional[str]
def _get_session_number(cwd: str) -> Optional[str]:
    """
    Read session number from .claude/session (last non-blank line).

    Returns "[SESSION: N]" string or None if file unavailable.
    Graceful degradation: return None on any error.
    """
    if not cwd:
        return None
    session_path = Path(cwd) / ".claude" / "session"
    if not session_path.exists():
        return None
    try:
        text = session_path.read_text(encoding="utf-8").strip()
        # Last non-blank line is session number integer
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith('#')]
        if not lines:
            return None
        session_num = int(lines[-1])
        return f"[SESSION: {session_num}]"
    except Exception:
        return None


# NEW: _get_working_item(slim: Optional[dict]) -> Optional[str]
def _get_working_item(slim: Optional[dict]) -> Optional[str]:
    """
    Extract active work_id from pre-parsed slim dict.

    Returns "[WORKING: WORK-XXX]" string or None if no active work item.
    Only injects when session_state.work_id is present and non-null.
    WORK-196: slim already parsed once by handle() — no file I/O here.
    """
    if slim is None:
        return None
    try:
        work_id = slim.get("session_state", {}).get("work_id")
        if not work_id:
            return None
        return f"[WORKING: {work_id}]"
    except Exception:
        return None


# NEW: _get_session_duration(cwd: str) -> Optional[str]
def _get_session_duration(cwd: str) -> Optional[str]:
    """
    Calculate session duration from .claude/session file mtime.

    Returns "[DURATION: Nm]" string or None if mtime unavailable.
    Candidates 1+3 (WORK-194) share the same Path object — but this function
    accepts cwd and creates its own Path for simplicity. The OS page cache
    makes the double stat() negligible (<1µs).
    """
    if not cwd:
        return None
    session_path = Path(cwd) / ".claude" / "session"
    if not session_path.exists():
        return None
    try:
        mtime = session_path.stat().st_mtime
        start = datetime.fromtimestamp(mtime)
        elapsed_minutes = int((datetime.now() - start).total_seconds() / 60)
        return f"[DURATION: {elapsed_minutes}m]"
    except Exception:
        return None
```

`handle()` is extended to call these three new functions after `_get_datetime_context()` and before the context usage line, collecting results into a compact inline block:

```python
# Modified handle() — new block inserted after Part 1 (datetime) and before Part 1.5 (context usage)

def handle(hook_data: dict) -> str:
    output_parts = []

    # Part 1: Date/time context
    output_parts.append(_get_datetime_context())

    # Part 1.2: Compact session state line (WORK-196)
    cwd = hook_data.get("cwd", "")
    slim = _read_slim(cwd)  # Read once — passed to all consumers below
    session_parts = []
    session_num = _get_session_number(cwd)
    if session_num:
        session_parts.append(session_num)
    working_item = _get_working_item(slim)
    if working_item:
        session_parts.append(working_item)
    duration = _get_session_duration(cwd)
    if duration:
        session_parts.append(duration)
    if session_parts:
        output_parts.append(" ".join(session_parts))

    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)

    # NOTE: slim already read above (Part 1.2). Remove duplicate read from old position.
    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd, slim)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 2.6: Phase contract injection (WORK-188, ADR-048)
    phase_contract = _get_phase_contract(cwd, slim)
    if phase_contract:
        output_parts.append("")
        output_parts.append(phase_contract)

    # Part 4: Lifecycle guidance
    prompt = hook_data.get("prompt", "")
    lifecycle = _get_lifecycle_guidance(prompt, cwd)
    if lifecycle:
        output_parts.append("")
        output_parts.append(lifecycle)

    # Part 5: RFC2119 reminders
    rfc2119 = _get_rfc2119_reminders(prompt)
    if rfc2119:
        output_parts.append("")
        output_parts.append(rfc2119)

    return "\n".join(output_parts)
```

**Behavior:** Every prompt now includes a compact line like `[SESSION: 428] [WORKING: WORK-196] [DURATION: 23m]` immediately after the datetime line. Each component is independently optional — missing data sources degrade gracefully to None and are omitted.

**Result:** Agent has ambient session number, active work item, and duration on every prompt. Combined token overhead: ~15 tokens (3 x ~5 tokens each). WORK-195 slim-read-once pattern is preserved — `slim` is read at top of `handle()` and passed down.

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 1: Session number injection — happy path
- **file:** `tests/test_hooks.py`
- **function:** `test_get_session_number_reads_last_line()`
- **setup:** `tmp_path` fixture. Write `# comment\n# comment\n428\n` to `tmp_path/.claude/session`. Call `_get_session_number(str(tmp_path))`.
- **assertion:** Returns `"[SESSION: 428]"`

#### Test 2: Session number injection — file missing
- **file:** `tests/test_hooks.py`
- **function:** `test_get_session_number_returns_none_if_missing()`
- **setup:** Call `_get_session_number("/nonexistent/path")`.
- **assertion:** Returns `None`

#### Test 3: Working item injection — work_id present
- **file:** `tests/test_hooks.py`
- **function:** `test_get_working_item_returns_work_id()`
- **setup:** Pass `slim = {"session_state": {"work_id": "WORK-196"}}` to `_get_working_item(slim)`.
- **assertion:** Returns `"[WORKING: WORK-196]"`

#### Test 4: Working item injection — no active work_id
- **file:** `tests/test_hooks.py`
- **function:** `test_get_working_item_returns_none_when_no_work_id()`
- **setup:** Pass `slim = {"session_state": {"active_cycle": "implementation-cycle", "work_id": None}}` to `_get_working_item(slim)`.
- **assertion:** Returns `None`

#### Test 5: Working item injection — slim is None
- **file:** `tests/test_hooks.py`
- **function:** `test_get_working_item_returns_none_when_slim_none()`
- **setup:** Call `_get_working_item(None)`.
- **assertion:** Returns `None`

#### Test 6: Duration injection — happy path
- **file:** `tests/test_hooks.py`
- **function:** `test_get_session_duration_returns_elapsed_minutes()`
- **setup:** `tmp_path`. Write session file. Create explicit MagicMock for datetime:
  ```python
  from unittest.mock import MagicMock
  from datetime import datetime as real_datetime, timedelta
  fixed_start = real_datetime(2026, 2, 23, 10, 0, 0)
  fixed_now = fixed_start + timedelta(minutes=45)
  mock_dt = MagicMock()
  mock_dt.fromtimestamp.return_value = fixed_start
  mock_dt.now.return_value = fixed_now
  ```
  Patch `hooks.user_prompt_submit.datetime` with `mock_dt`. Call `_get_session_duration(str(tmp_path))`.
- **assertion:** Returns `"[DURATION: 45m]"`

#### Test 7: Duration injection — file missing
- **file:** `tests/test_hooks.py`
- **function:** `test_get_session_duration_returns_none_if_missing()`
- **setup:** Call `_get_session_duration("/nonexistent/path")`.
- **assertion:** Returns `None`

#### Test 9: Session number injection — trailing comment after number
- **file:** `tests/test_hooks.py`
- **function:** `test_get_session_number_ignores_comment_lines()`
- **setup:** `tmp_path`. Write `# generated\n# comment\n428\n# trailing\n` to `.claude/session`. Call `_get_session_number(str(tmp_path))`.
- **assertion:** Returns `"[SESSION: 428]"` — implementation filters comment lines with `not ln.strip().startswith('#')`

#### Test 8: Integration — all three injections appear in handle() output
- **file:** `tests/test_hooks.py`
- **function:** `test_handle_injects_session_working_duration()`
- **setup:** `tmp_path`. Write `.claude/session` with content `# generated\n# comment\n428\n`. Write `.claude/haios-status-slim.json` with `{"session_state": {"work_id": "WORK-196", "active_cycle": "implementation-cycle", "current_phase": "DO"}}`. Call `from hooks.user_prompt_submit import handle` with `hook_data = {"cwd": str(tmp_path), "prompt": "test", "transcript_path": ""}`.
- **assertion:** `"[SESSION: 428]"` in result, `"[WORKING: WORK-196]"` in result, `"[DURATION:"` in result (duration value is time-sensitive, only check prefix)

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**Imports:** No new imports required — `datetime`, `Path`, `Optional` already present at lines 16-18 of source file.

**Location:** Three new private functions inserted after `_read_slim()` (line ~147). `handle()` body restructured.

**Current `handle()` opening (lines 50-88):**
```python
def handle(hook_data: dict) -> str:
    output_parts = []

    # Part 1: Date/time context
    output_parts.append(_get_datetime_context())

    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)

    # Part 2: HAIOS Vitals (E2-119: refresh status before reading)
    # DISABLED Session 179: ...
    cwd = hook_data.get("cwd", "")

    # WORK-195: Read slim JSON once, pass to all consumers
    slim = _read_slim(cwd)
```

**Target `handle()` opening (replacement for lines 50-88):**
```python
def handle(hook_data: dict) -> str:
    output_parts = []

    # Part 1: Date/time context
    output_parts.append(_get_datetime_context())

    # Part 1.2: Compact session state line (WORK-196)
    # Read slim once here — passed to all downstream consumers
    cwd = hook_data.get("cwd", "")
    slim = _read_slim(cwd)
    session_parts = []
    session_num = _get_session_number(cwd)
    if session_num:
        session_parts.append(session_num)
    working_item = _get_working_item(slim)
    if working_item:
        session_parts.append(working_item)
    duration = _get_session_duration(cwd)
    if duration:
        session_parts.append(duration)
    if session_parts:
        output_parts.append(" ".join(session_parts))

    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)
```

The old `cwd = hook_data.get("cwd", "")` and `slim = _read_slim(cwd)` lines at lines 84-87 are REMOVED (they move up to Part 1.2). The rest of `handle()` from `session_warning = _get_session_state_warning(cwd, slim)` onwards is unchanged.

**Three new functions** inserted after `_read_slim()` (after line 146):

```python
def _get_session_number(cwd: str) -> Optional[str]:
    """
    Read session number from .claude/session (last non-blank line).

    Returns "[SESSION: N]" or None if file unavailable.
    WORK-196: Session file has 3 lines; last line is integer session number.
    """
    if not cwd:
        return None
    session_path = Path(cwd) / ".claude" / "session"
    if not session_path.exists():
        return None
    try:
        text = session_path.read_text(encoding="utf-8").strip()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith('#')]
        if not lines:
            return None
        session_num = int(lines[-1])
        return f"[SESSION: {session_num}]"
    except Exception:
        return None


def _get_working_item(slim: Optional[dict]) -> Optional[str]:
    """
    Extract active work_id from pre-parsed slim dict.

    Returns "[WORKING: WORK-XXX]" or None if no active work item.
    WORK-196: slim already parsed once by handle() — no file I/O here.
    """
    if slim is None:
        return None
    try:
        work_id = slim.get("session_state", {}).get("work_id")
        if not work_id:
            return None
        return f"[WORKING: {work_id}]"
    except Exception:
        return None


def _get_session_duration(cwd: str) -> Optional[str]:
    """
    Calculate session duration from .claude/session file mtime.

    Returns "[DURATION: Nm]" or None if mtime unavailable.
    WORK-196: Uses file mtime as session start proxy. Resolution: 1 minute.
    """
    if not cwd:
        return None
    session_path = Path(cwd) / ".claude" / "session"
    if not session_path.exists():
        return None
    try:
        mtime = session_path.stat().st_mtime
        start = datetime.fromtimestamp(mtime)
        elapsed_minutes = int((datetime.now() - start).total_seconds() / 60)
        return f"[DURATION: {elapsed_minutes}m]"
    except Exception:
        return None
```

**Diff summary for `handle()`:**
```diff
-    # Part 1.5: Context usage from transcript JSONL
-    transcript_path = hook_data.get("transcript_path", "")
+    # Part 1.2: Compact session state line (WORK-196)
+    cwd = hook_data.get("cwd", "")
+    slim = _read_slim(cwd)
+    session_parts = []
+    session_num = _get_session_number(cwd)
+    if session_num:
+        session_parts.append(session_num)
+    working_item = _get_working_item(slim)
+    if working_item:
+        session_parts.append(working_item)
+    duration = _get_session_duration(cwd)
+    if duration:
+        session_parts.append(duration)
+    if session_parts:
+        output_parts.append(" ".join(session_parts))
+
+    # Part 1.5: Context usage from transcript JSONL
+    transcript_path = hook_data.get("transcript_path", "")
     ...
-    cwd = hook_data.get("cwd", "")
-
-    # WORK-195: Read slim JSON once, pass to all consumers
-    slim = _read_slim(cwd)
-
     # Part 2.5: Session state warning (E2-287)
```

### Call Chain

```
Claude Code UserPromptSubmit event
    |
    +-> hook_dispatcher.dispatch_hook()
            |
            +-> user_prompt_submit.handle(hook_data)
                    |
                    +-> _get_datetime_context()          Returns: str (always)
                    |
                    +-> _read_slim(cwd)                  Returns: Optional[dict]
                    |
                    +-> _get_session_number(cwd)         Returns: Optional[str]  # NEW
                    |       Reads: .claude/session (last line → int)
                    |
                    +-> _get_working_item(slim)          Returns: Optional[str]  # NEW
                    |       Uses: slim["session_state"]["work_id"]
                    |
                    +-> _get_session_duration(cwd)       Returns: Optional[str]  # NEW
                    |       Reads: .claude/session stat().st_mtime
                    |
                    +-> _get_context_usage(transcript)   Returns: Optional[str]
                    |
                    +-> _get_session_state_warning(cwd, slim)
                    +-> _get_phase_contract(cwd, slim)
                    +-> _get_lifecycle_guidance(prompt, cwd)
                    +-> _get_rfc2119_reminders(prompt)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Placement of new injections | Immediately after datetime (Part 1.2), before CONTEXT% | Session metadata pairs naturally with time context. Keeps compact info together at top. |
| Single compact line for all 3 | `"[SESSION: 428] [WORKING: WORK-196] [DURATION: 23m]"` joined with spaces | Saves tokens vs separate lines; still scannable; aligns with CONTEXT injection format. |
| `slim` read moved to Part 1.2 | `cwd` and `slim = _read_slim(cwd)` moved up from old line ~84-87 | WORK-195 pattern: read once, pass to all consumers. Moving it earlier lets `_get_working_item` use it without a separate read. |
| `_get_working_item` accepts `slim` not `cwd` | Takes `Optional[dict]` not `str` | Consistent with WORK-195 pattern for `_get_session_state_warning` and `_get_phase_contract`. No I/O in function. |
| `_get_session_number` and `_get_session_duration` accept `cwd` not `slim` | Take `str` | Session file is independent of slim JSON. Avoids coupling to slim structure. |
| mtime as session start proxy | `session_path.stat().st_mtime` | Investigation (WORK-194) confirmed .claude/session is written at session start. Simpler than parsing governance-events.jsonl. |
| `int()` rounding for duration | `int((datetime.now() - start).total_seconds() / 60)` | Floor rounding avoids "0m" for fresh sessions showing as "1m". Shows 0 for <60s. |
| Graceful degradation for each function | `try/except Exception: return None` | Hook must never crash. Degrade independently — partial info is fine. |
| No shared Path object for session file | Each function creates its own `Path(cwd) / ".claude" / "session"` | OS page cache makes double stat() negligible. Keeps functions independently testable without coupling. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `.claude/session` missing | `_get_session_number` returns None, `_get_session_duration` returns None | Test 2, Test 7 |
| `session_state.work_id` is null | `_get_working_item` returns None | Test 4 |
| slim is None (no slim file) | `_get_working_item(None)` returns None | Test 5 |
| Session file has only comments (no integer) | `int(lines[-1])` raises ValueError → except → None | Test 1 implicitly; add comment-only scenario as variant |
| Duration is 0 minutes (just started) | Returns `"[DURATION: 0m]"` — valid, means <1 minute | Acceptable behavior |
| cwd is empty string | All three functions return None early | Covered by existing pattern tests |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `.claude/session` mtime reset by OS (e.g., file touch during git operations) | M | Duration shows incorrect value. Acceptable — it's a soft awareness signal, not audit data. |
| `int(lines[-1])` fails if session file format changes | L | try/except returns None. Function degrades gracefully. |
| Moving `cwd` and `slim` earlier in `handle()` breaks existing test expectations | M | Existing tests pass cwd and check output; behavior is additive only. Run full test suite to verify. |
| Compact line appears even when session data is partial | L | Only renders if at least one `session_parts` entry is non-None. If all three fail, line is omitted entirely. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add `TestSessionInjections` class to `tests/test_hooks.py` with Tests 1-8 from Layer 1 > Tests section. Import `_get_session_number`, `_get_working_item`, `_get_session_duration` from `hooks.user_prompt_submit`. Tests will fail because functions don't exist yet.
- **output:** 9 new test functions exist in `tests/test_hooks.py`, all fail with ImportError or NameError
- **verify:** `pytest tests/test_hooks.py::TestSessionInjections -v 2>&1 | grep -c "FAILED\|ERROR"` equals 9

### Step 2: Add Three New Functions (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) — three new functions
- **input:** Step 1 complete (tests exist and fail)
- **action:** Insert `_get_session_number()`, `_get_working_item()`, `_get_session_duration()` into `.claude/hooks/hooks/user_prompt_submit.py` after `_read_slim()` (after line 146). Copy exact implementations from Layer 1 > Design.
- **output:** Three functions exist; Tests 1-7 and Test 9 pass; Test 8 still fails (handle() not wired yet)
- **verify:** `pytest tests/test_hooks.py::TestSessionInjections -v 2>&1 | grep -c "PASSED"` equals 8

### Step 3: Wire Injections into handle() (INTEGRATE)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) — handle() restructure
- **input:** Step 2 complete (7 unit tests green)
- **action:** Restructure `handle()` per Layer 1 > Design: move `cwd` and `slim = _read_slim(cwd)` to Part 1.2, add session_parts block, remove duplicate `cwd`/`slim` lines at old position (~lines 84-87). **MUST preserve the disabled vitals comment block (lines 76-83)** — use insert/move approach, not wholesale replacement.
- **output:** All 9 tests pass; `handle()` returns compact session line
- **verify:** `pytest tests/test_hooks.py -v` shows 0 new failures; `pytest tests/test_hooks.py::TestSessionInjections -v 2>&1 | grep -c "PASSED"` equals 9

### Step 4: Full Suite Regression Check
- **spec_ref:** Layer 0 > Test Files
- **input:** Step 3 complete (all 8 new tests green)
- **action:** Run full test suite to confirm no regressions
- **output:** No new test failures vs pre-change baseline
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows same pass count as pre-change baseline (1571 passed, 0 failed); any delta investigated before proceeding

### Step 5: Update Deliverable Checkboxes
- **spec_ref:** WORK.md Deliverables section
- **input:** Step 4 complete (full suite green)
- **action:** Mark all deliverable checkboxes in `docs/work/active/WORK-196/WORK.md` as complete
- **output:** All 6 deliverable checkboxes are `[x]`
- **verify:** `grep "\- \[ \]" docs/work/active/WORK-196/WORK.md` returns 0 matches

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_hooks.py::TestSessionInjections -v` | 9 passed, 0 failed |
| `pytest tests/test_hooks.py -v` | 0 new failures vs pre-change baseline |
| `pytest tests/ -v 2>&1 \| tail -5` | 1571+ passed, 0 failed |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| `[SESSION: N]` injected on every prompt | `grep "_get_session_number" .claude/hooks/hooks/user_prompt_submit.py` | 2+ matches (definition + call) |
| `[WORKING: WORK-XXX]` injected when work_id set | `grep "_get_working_item" .claude/hooks/hooks/user_prompt_submit.py` | 2+ matches |
| `[DURATION: Nm]` injected from mtime | `grep "_get_session_duration" .claude/hooks/hooks/user_prompt_submit.py` | 2+ matches |
| Graceful degradation (None if unavailable) | `pytest tests/test_hooks.py::TestSessionInjections::test_get_session_number_returns_none_if_missing -v` | 1 passed |
| Tests for each new injection function | `pytest tests/test_hooks.py::TestSessionInjections -v 2>&1 \| grep PASSED \| wc -l` | 9 |
| Existing tests pass | `pytest tests/test_hooks.py -v 2>&1 \| grep -E "^(PASSED\|FAILED\|ERROR)" \| grep -c FAILED` | 0 |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| `slim` read only once in handle() | `grep -n "_read_slim" .claude/hooks/hooks/user_prompt_submit.py` | Exactly 2 matches: definition + 1 call in handle() |
| No duplicate cwd assignment in handle() | `grep -n "cwd = hook_data" .claude/hooks/hooks/user_prompt_submit.py` | Exactly 1 match |
| No stale slim-read in old position | `pytest tests/test_hooks.py -v` | All existing tests pass (no behavior regression) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists — `handle()` calls all three new functions (Consumer Integrity table)
- [ ] No stale references — slim read once, cwd assigned once (Consumer Integrity table)
- [ ] WORK.md deliverable checkboxes all `[x]` (Layer 2 Step 5)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-194/WORK.md` — investigation that approved candidates 1-3
- `docs/work/active/WORK-195/WORK.md` — prerequisite slim-read-once refactor (complete)
- `.claude/hooks/hooks/user_prompt_submit.py` — target file (as-refactored by WORK-195)
- `tests/test_hooks.py` — existing tests; new class appended here
- Memory refs from WORK-195 closure: 87635-87639, 87674-87675 (slim-read pattern)
- Memory refs from WORK-194: 87537-87539, 87580-87583 (candidate evaluation)

---
