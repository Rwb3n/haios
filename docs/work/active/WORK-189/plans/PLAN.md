---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-22
backlog_id: WORK-189
title: "Context Window Usage Injection via UserPromptSubmit Hook"
author: Hephaestus
lifecycle_phase: plan
session: 423
generated: 2026-02-22
last_updated: 2026-02-22T14:55:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-189/WORK.md"
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
# Implementation Plan: Context Window Usage Injection via UserPromptSubmit Hook

---

## Goal

The UserPromptSubmit hook will inject real context window usage percentage on every prompt by parsing the transcript JSONL for API usage metadata, giving agents accurate visibility into context consumption.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Data source | A) statusLine sidecar, B) transcript JSONL parsing | B | Single-file change, no sidecar management, proven pattern (nelson/count-tokens.py). Hook already has transcript_path. |
| Context window size | A) 200k hardcoded, B) configurable | A | All current Claude models use 200k. Can be parameterized later if needed. |
| Token sum formula | A) input_tokens only, B) input + cache_creation + cache_read | B | All three count toward context window occupancy. Matches nelson pattern. |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 2 |

### Consumer Files

**SKIPPED:** No consumer files. The hook is the terminal consumer — its output is injected by Claude Code into the agent's context. No other code imports or references the new function.

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_context_usage_injection.py` | CREATE | New test file for _get_context_usage function |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | Test file |
| Files to modify | 1 | user_prompt_submit.py |
| Tests to write | 6 | Test Files table |
| Total blast radius | 2 | 1 create + 1 modify |

---

## Layer 1: Specification

### Current State

```python
# .claude/hooks/hooks/user_prompt_submit.py:64-121
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())

    # Part 1.5: Context threshold check (E2-210)
    # DISABLED Session 179: Context estimate is unreliable, causes noise
    # transcript_path = hook_data.get("transcript_path", "")
    # context_warning = _check_context_threshold(transcript_path)

    # ... other parts ...
    return "\n".join(output_parts)
```

**Behavior:** Hook injects datetime, session state warning, phase contract, lifecycle guidance, and RFC2119 reminders. Context usage is disabled (S179) because the file-size heuristic was unreliable.

**Problem:** Agent has no visibility into real context window usage. Estimates are consistently wrong (S420: 80-100K estimated vs 150K actual).

### Desired State

```python
# .claude/hooks/hooks/user_prompt_submit.py:64-121
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())

    # Part 1.5: Context usage from transcript JSONL (WORK-189)
    transcript_path = hook_data.get("transcript_path", "")
    context_info = _get_context_usage(transcript_path)
    if context_info:
        output_parts.append(context_info)

    # ... other parts unchanged ...
    return "\n".join(output_parts)
```

**Behavior:** Hook parses the transcript JSONL, extracts last assistant message's usage metadata, calculates percentage, and injects `[CONTEXT: N% used]`.

**Result:** Agent sees real context consumption on every prompt, enabling informed decisions about session continuation vs checkpoint.

### Tests

#### Test 1: Happy path — usage data extracted and formatted
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_get_context_usage_happy_path(tmp_path)`
- **setup:** Create a JSONL file with 2 assistant messages containing `usage` data. Last message has `input_tokens: 100000, cache_creation_input_tokens: 20000, cache_read_input_tokens: 30000` (total 150000 = 75% of 200k).
- **assertion:** `_get_context_usage(str(jsonl_path))` returns string containing `[CONTEXT: 75% used]`

#### Test 2: No transcript file — graceful degradation
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_get_context_usage_missing_file()`
- **setup:** Pass a nonexistent path.
- **assertion:** `_get_context_usage("/nonexistent/path.jsonl")` returns `None`

#### Test 3: Empty transcript — graceful degradation
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_get_context_usage_empty_file(tmp_path)`
- **setup:** Create an empty JSONL file.
- **assertion:** `_get_context_usage(str(empty_path))` returns `None`

#### Test 4: No usage data in assistant messages
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_get_context_usage_no_usage_data(tmp_path)`
- **setup:** Create JSONL with assistant messages that have no `usage` key in their `message` dict.
- **assertion:** `_get_context_usage(str(jsonl_path))` returns `None`

#### Test 6: All-zero usage fields — graceful degradation not false 0%
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_get_context_usage_all_zero_returns_none(tmp_path)`
- **setup:** Create JSONL with assistant message containing `usage` dict where all three token fields are 0 (or absent — `.get(key, 0)` defaults to 0).
- **assertion:** `_get_context_usage(str(jsonl_path))` returns `None` (not `"[CONTEXT: 0% used]"`)

#### Test 5: Integration — handle() includes context usage
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_handle_includes_context_usage(tmp_path, monkeypatch)`
- **setup:** At module level: `HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"` and `sys.path.insert(0, str(HOOKS_DIR))`. Import via `from hooks import user_prompt_submit`. Monkeypatch with `monkeypatch.setattr(user_prompt_submit, "_get_context_usage", lambda p: "[CONTEXT: 50% used]")`. Call `user_prompt_submit.handle()` with `transcript_path` set to any string and `cwd` pointing to project root.
- **assertion:** Result string contains `"[CONTEXT: 50% used]"`

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**New function — add after `_get_phase_contract()` (after line 218):**

```python
def _get_context_usage(transcript_path: str) -> Optional[str]:
    """
    Extract real context window usage from transcript JSONL.

    Parses the last assistant message's API usage metadata to calculate
    context window consumption. Reflects usage as of last completed
    assistant response — current prompt tokens not yet recorded.
    Replaces the unreliable file-size heuristic (disabled S179).

    Pattern from: github.com/harrymunro/nelson/scripts/count-tokens.py

    Args:
        transcript_path: Path to Claude Code transcript JSONL file.

    Returns:
        Formatted string like "[CONTEXT: 75% used]", or None if unavailable.
    """
    if not transcript_path:
        return None

    path = Path(transcript_path)
    if not path.exists():
        return None

    try:
        last_usage = None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") != "assistant":
                    continue
                msg = record.get("message")
                if not isinstance(msg, dict) or "usage" not in msg:
                    continue
                last_usage = msg["usage"]

        if last_usage is None:
            return None

        input_tokens = last_usage.get("input_tokens", 0)
        cache_creation = last_usage.get("cache_creation_input_tokens", 0)
        cache_read = last_usage.get("cache_read_input_tokens", 0)
        total = input_tokens + cache_creation + cache_read

        if total == 0:
            return None  # No usage data found — graceful degradation (A13)

        context_limit = 200_000
        pct = min(100.0, (total / context_limit) * 100)

        return f"[CONTEXT: {pct:.0f}% used]"
    except Exception:
        return None
```

**Call-site modification — in `handle()`, replace disabled context check (lines 70-77):**

**Current Code:**
```python
    # Part 1.5: Context threshold check (E2-210)
    # DISABLED Session 179: Context estimate is unreliable, causes noise
    # transcript_path = hook_data.get("transcript_path", "")
    # context_warning = _check_context_threshold(transcript_path)
    # if context_warning:
    #     output_parts.append("")
    #     output_parts.append(context_warning)
```

**Target Code:**
```python
    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)
```

### Call Chain

```
Claude Code runtime (UserPromptSubmit event)
    |
    +-> hook_dispatcher.dispatch_hook(hook_input)
    |       |
    |       +-> user_prompt_submit.handle(hook_data)
    |               |
    |               +-> _get_datetime_context()
    |               +-> _get_context_usage(transcript_path)   # <-- NEW
    |               +-> _get_session_state_warning(cwd)
    |               +-> _get_phase_contract(cwd)
    |               +-> _get_lifecycle_guidance(prompt, cwd)
    |               +-> _get_rfc2119_reminders(prompt)
    |               |
    |               Returns: "\n".join(output_parts)
    |
    +-> Output injected as additionalContext before Claude sees prompt
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Parse entire JSONL vs seek from end | Parse entire file | Simpler, reliable. JSONL files in practice are <10MB. Python file I/O handles this in <100ms. Premature optimization avoided. |
| Replace disabled heuristic vs add alongside | Replace | The heuristic was disabled for being unreliable. The new approach supersedes it entirely. Keep old functions for reference but add `# SUPERSEDED by _get_context_usage (WORK-189)` comment to both `_estimate_context_usage` and `_check_context_threshold`. |
| Format: `[CONTEXT: N% used]` | Bracket format | Consistent with `[STATE: DO]` format from PreToolUse hook. Brackets denote system-injected metadata. |
| No warning thresholds | Just show percentage | Agent has the raw number and can make its own decisions. Threshold warnings were noisy (S179 learning). |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| No transcript file | Return None | Test 2 |
| Empty transcript | Return None | Test 3 |
| Assistant messages without usage data | Return None | Test 4 |
| Malformed JSON lines | Skip line, continue | Handled by try/except in loop |
| Very large transcript (>10MB) | Still parses — Python handles this | Not tested explicitly (performance, not correctness) |
| usage fields missing individual keys | `.get(key, 0)` defaults to 0 | Implicit in happy path |
| All usage fields absent/zero (renamed API keys) | `if total == 0: return None` — graceful degradation, not false 0% | Test 6 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Transcript parsing adds latency to every prompt | L | Python file I/O is fast (<100ms for 10MB). Hook is already doing file reads (slim status). |
| Token sum doesn't exactly match Claude Code's internal calculation | L | Same formula as nelson project. Difference is negligible for agent decision-making. |
| Future Claude models change context window size from 200k | L | Hardcoded constant is easy to update. Can parameterize later. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_context_usage_injection.py` with 6 tests from Layer 1 Tests section
- **output:** Test file exists, all 6 tests fail (function doesn't exist yet)
- **verify:** `pytest tests/test_context_usage_injection.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 6

### Step 2: Implement _get_context_usage (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) — New function
- **input:** Step 1 complete (tests exist and fail)
- **action:** Add `_get_context_usage()` function to `user_prompt_submit.py` after `_get_phase_contract()`
- **output:** Tests 1-4 pass (unit tests for the function)
- **verify:** `pytest tests/test_context_usage_injection.py -v -k "not test_handle"` exits 0, 5 passed

### Step 3: Wire call-site in handle()
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) — Call-site
- **input:** Step 2 complete (function tests green)
- **action:** Replace disabled context check block in `handle()` with call to `_get_context_usage()`
- **output:** Test 5 passes (integration test), all 6 tests green
- **verify:** `pytest tests/test_context_usage_injection.py -v` exits 0, 6 passed

### Step 4: Run Full Test Suite
- **spec_ref:** Ground Truth Verification > Tests
- **input:** Step 3 complete
- **action:** Run full test suite to verify no regressions
- **output:** No new failures
- **verify:** Run `pytest tests/ -q` before Step 1 to capture dynamic baseline count. After Step 3, rerun and assert: (a) no tests that previously passed are now failing, (b) 5 new tests added.

**SKIPPED: Step 5 (Update Documentation)** — No README exists for hooks directory. No consumer files to update.

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_context_usage_injection.py -v` | 6 passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs dynamic baseline (captured before Step 1) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Hook parses transcript JSONL for usage metadata | `grep "_get_context_usage" .claude/hooks/hooks/user_prompt_submit.py` | 2+ matches (def + call) |
| Agent sees [CONTEXT: N% used] | `grep "CONTEXT:" .claude/hooks/hooks/user_prompt_submit.py` | 1+ match |
| Graceful degradation if transcript missing | `pytest tests/test_context_usage_injection.py::test_get_context_usage_missing_file -v` | 1 passed |
| Existing tests pass | `pytest tests/test_hooks.py -v` | all passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Runtime consumer exists | `grep "_get_context_usage" .claude/hooks/hooks/user_prompt_submit.py` | 2+ matches (def + call-site in handle) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- @docs/work/active/WORK-189/WORK.md
- @docs/work/active/E2-235/WORK.md (prior art: hooks don't receive context_window)
- @.claude/haios/epochs/E2_3/observations/obs-212-002.md (constraint documentation)
- github.com/harrymunro/nelson/scripts/count-tokens.py (token counting pattern)
- REQ-OBSERVE-002 (Session state visible via hooks)

---
