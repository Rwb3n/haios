---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-07
backlog_id: WORK-247
title: "Context Budget Gate Production Wiring"
author: Hephaestus
lifecycle_phase: plan
session: 471
generated: 2026-03-07
last_updated: 2026-03-07T14:36:19

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-247/WORK.md"
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
# Implementation Plan: Context Budget Gate Production Wiring

## Goal

Wire the S469 context budget gate prototype into production by retiring transcript-based context parsing, updating the slim relay to read from `.claude/context_remaining`, and adding comprehensive tests for the new budget gate functions.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Keep `_get_context_usage` display in UserPromptSubmit? | A) Remove entirely, B) Replace with file read | A) Remove entirely | statusLine already shows context in terminal. Duplicate display wastes tokens. PreToolUse injects warnings when low. |
| Update `_read_context_pct_from_slim` in governance_events.py? | A) Keep reading slim, B) Read `.claude/context_remaining` directly | A) Keep reading slim | Slim relay pattern (WORK-237) is working. Just update the write side to read from file instead of transcript. Fewer blast radius. |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 2 |
| `.claude/hooks/statusline.py` | MODIFY | 2 |
| `.claude/hooks/hooks/pre_tool_use.py` | NO CHANGE | — |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_context_usage_injection.py` | tests `_get_context_usage` + surviving tests | partial | PARTIAL DELETE (keep TestGetSessionStateWarning, TestGetPhaseContract) |
| `tests/test_hooks.py` | tests `_estimate_context_usage`, `_check_context_threshold` | 481-511 | UPDATE (remove tests) |
| `tests/test_governance_events.py` | tests `_extract_context_pct`, consistency with `_get_context_usage` | 739-783 | UPDATE (remove/update tests) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_context_budget_gate.py` | CREATE | New: tests for `_check_context_budget`, `_inject_context_warning`, `statusline.main` |
| `tests/test_context_usage_injection.py` | PARTIAL DELETE | Remove TestGetContextUsage (5 tests) + TestHandleIntegration (1 test). Keep TestGetSessionStateWarning (3 tests) + TestGetPhaseContract (1 test) — these test active functions |
| `tests/test_hooks.py` | UPDATE | Remove `_estimate_context_usage` and `_check_context_threshold` tests |
| `tests/test_governance_events.py` | UPDATE | Remove `_extract_context_pct` consistency test, update `_extract_context_pct` test |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | test_context_budget_gate.py |
| Files to modify | 5 | user_prompt_submit.py, statusline.py, test_context_usage_injection.py, test_hooks.py, test_governance_events.py |
| Files to delete | 0 | (partial delete of test_context_usage_injection.py counted as modify) |
| Tests to write | 10 | Test Files table |
| Total blast radius | 6 | Sum of all unique files |

---

## Layer 1: Specification

### Current State

```python
# user_prompt_submit.py:91-99 — transcript-based context injection in handle()
    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)
    # WORK-237: Write context_pct float to slim for governance event relay
    context_pct = _extract_context_pct(transcript_path)
    if context_pct is not None:
        _write_context_pct_to_slim(cwd, context_pct)
```

**Behavior:** On every UserPromptSubmit, parses entire transcript JSONL to extract token usage, formats as `[CONTEXT: N% remaining]`, and writes float to slim for governance events.
**Problem:** Transcript parsing is O(n) on file size, uses hardcoded 200K limit, and is now redundant — statusLine writes native `context_window.remaining_percentage` to `.claude/context_remaining` on every statusLine refresh (much more frequent than UserPromptSubmit).

### Desired State

```python
# user_prompt_submit.py:91-96 — file-based context relay in handle()
    # Part 1.5: Context budget — relay .claude/context_remaining to slim for governance events
    # (Display removed: statusLine shows context in terminal; PreToolUse injects warnings when low)
    context_pct = _read_context_remaining(cwd)
    if context_pct is not None:
        _write_context_pct_to_slim(cwd, context_pct)
```

**Behavior:** On every UserPromptSubmit, reads the single float from `.claude/context_remaining` (written by statusLine) and relays to slim for governance events. No transcript parsing. No display injection (statusLine handles that).
**Result:** Removes ~150 lines of dead code. Governance events still get fresh context_pct via slim relay. Context warnings still appear via PreToolUse `_check_context_budget`.

### Tests

#### Test 1: _check_context_budget returns None when file missing
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_no_file(tmp_path)`
- **setup:** tmp_path with no `.claude/context_remaining` file
- **assertion:** `_check_context_budget(str(tmp_path))` returns `None`

#### Test 2: _check_context_budget returns None when above 20%
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_safe(tmp_path)`
- **setup:** Write "45.0" to `tmp_path/.claude/context_remaining`
- **assertion:** `_check_context_budget(str(tmp_path))` returns `None`

#### Test 3: _check_context_budget returns LOW warning at 20%
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_low(tmp_path)`
- **setup:** Write "20.0" to `tmp_path/.claude/context_remaining`
- **assertion:** Result contains `"[CONTEXT LOW"` and `"20.0%"`

#### Test 4: _check_context_budget returns SESSION-END warning at 15%
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_session_end(tmp_path)`
- **setup:** Write "15.0" to `tmp_path/.claude/context_remaining`
- **assertion:** Result contains `"[CONTEXT SESSION-END"` and `"15.0%"`

#### Test 5: _check_context_budget returns CRITICAL warning at 10%
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_critical(tmp_path)`
- **setup:** Write "10.0" to `tmp_path/.claude/context_remaining`
- **assertion:** Result contains `"[CONTEXT CRITICAL"` and `"10.0%"`

#### Test 6: _check_context_budget returns CRITICAL at 5% (below 10)
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_very_critical(tmp_path)`
- **setup:** Write "5.0" to `tmp_path/.claude/context_remaining`
- **assertion:** Result contains `"[CONTEXT CRITICAL"`

#### Test 7: _check_context_budget handles malformed file gracefully
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_check_context_budget_malformed(tmp_path)`
- **setup:** Write "not_a_number" to `tmp_path/.claude/context_remaining`
- **assertion:** Returns `None` (fail-silent)

#### Test 8: _inject_context_warning merges warning into existing result
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_inject_context_warning_merge()`
- **setup:** Existing result with `additionalContext: "[STATE: DO]"`, warning `"[CONTEXT LOW]"`
- **assertion:** Result `additionalContext` contains both `"[STATE: DO]"` and `"[CONTEXT LOW]"`

#### Test 9: _inject_context_warning creates result when None
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_inject_context_warning_create()`
- **setup:** `result=None`, warning `"[CONTEXT LOW]"`
- **assertion:** Returns dict with `permissionDecision: "allow"` and `additionalContext` containing warning

#### Test 10: statusline.main writes context_remaining file
- **file:** `tests/test_context_budget_gate.py`
- **function:** `test_statusline_writes_context_remaining(tmp_path, monkeypatch)`
- **setup:** Create `tmp_path/.claude/` directory. Mock stdin with JSON `{"context_window": {"remaining_percentage": 42.5, "used_percentage": 57.5}, "model": {"display_name": "Claude"}, "workspace": {"current_dir": str(tmp_path)}}`. Monkeypatch `sys.stdin` to StringIO with that JSON.
- **assertion:** `tmp_path/.claude/context_remaining` contains `"42.5"`, stdout contains `"57.5% used"` (A1 fix: statusline uses `cwd` from JSON, so `workspace.current_dir = tmp_path` naturally isolates the write)

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**Changes:**

1. **Replace handle() lines 91-99** — Remove transcript parsing, add file read relay:

**Current Code:**
```python
    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)
    # WORK-237: Write context_pct float to slim for governance event relay
    context_pct = _extract_context_pct(transcript_path)
    if context_pct is not None:
        _write_context_pct_to_slim(cwd, context_pct)
```

**Target Code:**
```python
    # Part 1.5: Context budget — relay .claude/context_remaining to slim for governance events
    # (Display removed: statusLine shows context in terminal; PreToolUse injects warnings when low)
    context_pct = _read_context_remaining(cwd)
    if context_pct is not None:
        _write_context_pct_to_slim(cwd, context_pct)
```

2. **Add `_read_context_remaining` function** (new, ~15 lines):

```python
def _read_context_remaining(cwd: str) -> Optional[float]:
    """Read remaining context percentage from .claude/context_remaining.

    File written by statusLine with Claude Code native context_window.remaining_percentage.
    Returns float 0-100 or None if unavailable. Fail-silent.

    WORK-247: Replaces _extract_context_pct (transcript parsing) for slim relay.
    """
    if not cwd:
        return None
    try:
        remaining_file = Path(cwd) / ".claude" / "context_remaining"
        if not remaining_file.exists():
            return None
        return float(remaining_file.read_text(encoding="utf-8").strip())
    except Exception:
        return None
```

3. **Delete dead functions** (~150 lines):
   - `_get_context_usage` (lines 335-394) — transcript JSONL parsing for display
   - `_extract_context_pct` (lines 397-441) — transcript JSONL parsing for float
   - SUPERSEDED comment + `_estimate_context_usage` (lines 675-700) — file-size heuristic
   - SUPERSEDED comment + `_check_context_threshold` (lines 703-721) — threshold check on file-size heuristic

#### File 2 (MODIFY): `.claude/hooks/statusline.py`

**Location:** Line 39 in `main()`

**Critique A1 fix:** statusline.py writes to relative `Path(".claude/context_remaining")` which depends on process cwd. Must use absolute path anchored to `workspace.current_dir` from stdin JSON (already parsed on line 28).

**Current Code:**
```python
            remaining_file = Path(".claude/context_remaining")
```

**Target Code:**
```python
            remaining_file = Path(dirname_full) / ".claude" / "context_remaining"
```

Where `dirname_full` is the full `current_dir` path (already available from line 28 as `cwd`). We need to preserve the full path before the dirname extraction:

**Current Code (lines 27-28):**
```python
    cwd = data.get("workspace", {}).get("current_dir", "~")
    dirname = cwd.rsplit("/", 1)[-1] if "/" in cwd else cwd.rsplit("\\", 1)[-1] if "\\" in cwd else cwd
```

**Target Code (lines 27-28 unchanged, line 39 changed):**
```python
    cwd = data.get("workspace", {}).get("current_dir", "~")
    dirname = cwd.rsplit("/", 1)[-1] if "/" in cwd else cwd.rsplit("\\", 1)[-1] if "\\" in cwd else cwd
    # ... (existing code) ...
    # Line 39 change:
    remaining_file = Path(cwd) / ".claude" / "context_remaining"
```

**Risk:** `cwd` could be `"~"` if workspace data is missing. `Path("~") / ".claude" / "context_remaining"` would create a literal `~` directory, not expand it. This is acceptable: if workspace data is missing, the file won't be found by PreToolUse either (same fail-silent behavior).

#### No changes to pre_tool_use.py

Already has the correct implementation from S469 prototype. `_check_context_budget` and `_inject_context_warning` are correct.

### Call Chain

```
statusLine (Claude Code native refresh, every tool call)
    |
    +-> statusline.py::main()
    |       Writes: .claude/context_remaining (float)
    |
    +----> PreToolUse hook (every tool call)
    |       |
    |       +-> _check_context_budget(cwd)
    |       |       Reads: .claude/context_remaining
    |       |       Returns: warning string or None
    |       |
    |       +-> _inject_context_warning(result, warning)
    |               Merges warning into additionalContext
    |
    +----> UserPromptSubmit hook (every user prompt)
            |
            +-> _read_context_remaining(cwd)    # NEW (replaces _extract_context_pct)
            |       Reads: .claude/context_remaining
            |       Returns: float or None
            |
            +-> _write_context_pct_to_slim(cwd, context_pct)
                    Writes: haios-status-slim.json["context_pct"]
                    |
                    +----> governance_events._read_context_pct_from_slim()
                               Reads: slim["context_pct"] → event["context_pct"]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove display injection from UserPromptSubmit | Yes | statusLine already shows context % in terminal bar. Duplicate `[CONTEXT: N% remaining]` text wastes tokens. |
| Keep slim relay pattern | Yes | governance_events.py reads context_pct from slim (WORK-237). Changing that requires modifying governance_events.py — unnecessary blast radius. Just update the write side. |
| Keep `_write_context_pct_to_slim` unchanged | Yes | Function itself is fine. Only its caller changes (from transcript float to file float). |
| Delete `_estimate_context_usage` and `_check_context_threshold` | Yes | Marked SUPERSEDED since WORK-189. No callers in production. Only referenced by tests. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `.claude/context_remaining` missing (first prompt before statusLine runs) | `_read_context_remaining` returns None, slim not updated | Test 1 |
| File contains non-numeric text | `float()` raises ValueError, caught by except, returns None | Test 7 |
| `_check_context_budget` with empty cwd | Returns None immediately | Covered by existing code path |
| Boundary: exactly 20.0% remaining | Triggers LOW warning (<=20.0 check) | Test 3 |
| Boundary: exactly 15.0% remaining | Triggers SESSION-END (<=15.0 before <=20.0) | Test 4 |
| Boundary: exactly 10.0% remaining | Triggers CRITICAL (<=10.0 before <=15.0) | Test 5 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing tests import deleted functions | M | Delete test_context_usage_injection.py, update test_hooks.py and test_governance_events.py |
| Governance events lose context_pct | M | Slim relay preserved — only the write source changes |
| statusLine not running (no file) | L | Both `_read_context_remaining` and `_check_context_budget` handle missing file gracefully |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_context_budget_gate.py` with all 10 tests from Layer 1
- **output:** Test file exists, tests 1-9 pass (testing existing functions), test 10 requires statusline import setup
- **verify:** `pytest tests/test_context_budget_gate.py -v` — at least 9 tests pass (existing functions already implemented)

### Step 2: Fix statusline.py Path (Critique A1)
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 1 complete (tests exist)
- **action:** Change `Path(".claude/context_remaining")` to `Path(cwd) / ".claude" / "context_remaining"` in statusline.py line 39
- **output:** statusline writes to absolute cwd-anchored path
- **verify:** Test 10 passes — `pytest tests/test_context_budget_gate.py::test_statusline_writes_context_remaining -v`

### Step 3: Delete Dead Code and Add `_read_context_remaining` (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 2 complete
- **action:**
  1. Replace handle() lines 91-99 with file-read relay
  2. Add `_read_context_remaining` function
  3. Delete `_get_context_usage`, `_extract_context_pct`, `_estimate_context_usage`, `_check_context_threshold` and their SUPERSEDED comments
- **output:** All new tests pass, dead code removed
- **verify:** `pytest tests/test_context_budget_gate.py -v` — 10 passed, 0 failed

### Step 4: Update Consumer Tests
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 3 complete
- **action:**
  1. In `tests/test_context_usage_injection.py`: delete `TestGetContextUsage` class (lines 32-120), `TestHandleIntegration` class (lines 169-189), and `_write_jsonl` helper (lines 25-29). Keep `TestGetSessionStateWarning` (lines 123-154) and `TestGetPhaseContract` (lines 157-166). Update module docstring to reflect surviving tests.
  2. Remove `test_estimate_context_usage_calculates_percentage`, `test_check_context_threshold_warns_above_80`, `test_check_context_threshold_silent_below_80` from `tests/test_hooks.py`
  3. Remove `test_extract_context_pct_returns_float` and `test_extract_context_pct_consistent_with_get_context_usage` from `tests/test_governance_events.py`
- **output:** No test references to deleted functions, surviving tests still pass
- **verify:** `pytest tests/test_context_usage_injection.py tests/test_hooks.py tests/test_governance_events.py -v` — 0 failures, 4 surviving tests in test_context_usage_injection.py pass

### Step 5: Full Test Suite Verification
- **spec_ref:** Ground Truth Verification
- **input:** Steps 1-4 complete
- **action:** Run full test suite to verify no regressions
- **output:** All tests pass
- **verify:** `pytest tests/ -v --tb=short` — 0 new failures

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_context_budget_gate.py -v` | 10 passed, 0 failed |
| `pytest tests/test_hooks.py -v` | 0 new failures (3 dead tests removed) |
| `pytest tests/test_governance_events.py -v` | 0 new failures |
| `pytest tests/ -v --tb=short` | 0 new failures vs pre-existing |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| statusline.py writes context_remaining | Already implemented (S469) | File exists at runtime |
| PreToolUse reads context_remaining and injects warnings | Already implemented (S469) | Tested in test_context_budget_gate.py |
| Retire transcript-based functions | `grep "_extract_context_pct\|_get_context_usage\|_estimate_context_usage\|_check_context_threshold" .claude/hooks/hooks/user_prompt_submit.py` | 0 matches |
| Slim relay reads from file | `grep "_read_context_remaining" .claude/hooks/hooks/user_prompt_submit.py` | 1+ match |
| Tests for budget gate | `pytest tests/test_context_budget_gate.py -v` | 10 passed |
| .claude/context_remaining is gitignored | `grep "context_remaining" .gitignore` | 1 match |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No references to deleted functions in production | `grep -r "_get_context_usage\|_extract_context_pct\|_estimate_context_usage\|_check_context_threshold" .claude/hooks/ --include="*.py"` | 0 matches |
| No test imports of deleted functions | `grep -r "_get_context_usage\|_extract_context_pct\|_estimate_context_usage\|_check_context_threshold" tests/ --include="*.py"` | 0 matches |
| Slim relay intact | `grep "_write_context_pct_to_slim" .claude/hooks/hooks/user_prompt_submit.py` | 1 match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md acceptance criteria verified (Deliverables table above)
- [ ] Dead code removed (Consumer Integrity table above)
- [ ] No stale references (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- WORK-247: Context Budget Gate — Wire Prototype to Production
- WORK-189: Context Window Usage Injection (original transcript approach, now superseded)
- WORK-237: Context PCT Slim Relay
- S469: Context budget gate prototype implementation
- mem:89540: Decision to retire transcript-based context_pct extraction

---
