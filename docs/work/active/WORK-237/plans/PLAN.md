---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-06
backlog_id: WORK-237
title: "Implement context_pct Auto-Injection via Slim Relay"
author: Hephaestus
lifecycle_phase: plan
session: 461
generated: 2026-03-06
last_updated: 2026-03-06T21:05:38

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-237/WORK.md"
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
# Implementation Plan: Implement context_pct Auto-Injection via Slim Relay

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add automatic `context_pct` population to all governance events by (1) writing the float computed by `_get_context_usage()` into `haios-status-slim.json` on every UserPromptSubmit and (2) reading it from slim inside `_append_event()` when callers do not supply an explicit override.

---

## Open Decisions

<!-- WORK-237 has no operator_decisions in frontmatter. WORK-236 investigation resolved
     all design decisions before spawning this work item. Table below documents those
     resolved decisions for traceability. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Relay mechanism | slim file vs per-caller | slim file | transcript_path absent from PostToolUse/PreToolUse; slim is already shared and read on every prompt |
| Injection point | per-caller (12 sites) vs single _append_event | _append_event | 1 change vs 12; WORK-233 kwargs become explicit-override mechanism |
| Staleness | refresh each event vs accept prompt-level staleness | accept staleness | context doesn't change between prompts (only API calls consume tokens); prompt-level granularity sufficient |
| context_pct semantics | remaining % vs used % | remaining % (float 0-100) | aligns with existing `_get_context_usage()` output format `[CONTEXT: X% remaining]` |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 1 |
| `.claude/haios/lib/governance_events.py` | MODIFY | 2 |

### Consumer Files

<!-- No per-caller changes needed — injection is inside _append_event() itself.
     12 runtime call sites require ZERO changes (by design). -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_governance_events.py` | test coverage for _append_event auto-injection | new class | UPDATE (add tests) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_governance_events.py` | UPDATE | Add TestContextPctAutoInjection class (7 test methods) + patch temp_events_file fixture |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 2 | user_prompt_submit.py + governance_events.py |
| Test files to update | 1 | tests/test_governance_events.py |
| Total blast radius | 3 | 2 source + 1 test |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

**Change 1: user_prompt_submit.py — `handle()` function (lines 91-95)**

```python
# .claude/hooks/hooks/user_prompt_submit.py:91-95
    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)
```

`_get_context_usage()` at line 331 returns a formatted string like `"[CONTEXT: 25% remaining]"` or `None`. The float value is computed internally at line 387 (`remaining = 100.0 - pct`) but is never extracted or stored anywhere.

**Change 2: governance_events.py — `_append_event()` (lines 491-498)**

```python
# .claude/haios/lib/governance_events.py:491-498
def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
    """Append event to JSONL file, injecting session_id and optional context_pct."""
    event["session_id"] = _read_session_id()
    if context_pct is not None:
        event["context_pct"] = context_pct
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

When `context_pct=None` (i.e., every caller today), `context_pct` is omitted from the event. No slim read exists in this file.

**Behavior:** Governance events are written without `context_pct` field. The field infrastructure exists (WORK-233) but is dead — no caller populates it.

**Problem:** ADR-033 requires runtime consumers exist before closure. Context budget analysis (memory: 85989, 86041, 88223) requires per-event context snapshots. Zero events currently carry `context_pct`.

---

### Desired State

**Change 1: user_prompt_submit.py — extract float, write to slim**

After calling `_get_context_usage()`, extract the computed `remaining` float and write it to slim.

New helper `_write_context_pct_to_slim(cwd: str, context_pct: float) -> None` writes the field:

```python
# .claude/hooks/hooks/user_prompt_submit.py — new helper function
def _write_context_pct_to_slim(cwd: str, context_pct: float) -> None:
    """Write context_pct float to haios-status-slim.json for governance event relay.

    WORK-237: Slim relay pattern — UserPromptSubmit writes, _append_event reads.
    Fail-silent: stale value is better than broken hook.

    Args:
        cwd: Working directory path.
        context_pct: Remaining context percentage (0-100 float).
    """
    if not cwd:
        return
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return
    try:
        data = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        data["context_pct"] = context_pct
        slim_path.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception:
        pass  # Fail silently — stale value is better than broken hook
```

Modify `_get_context_usage()` to return the float alongside the string — OR use a new extraction helper. The cleanest approach is a new private helper `_extract_context_pct(transcript_path: str) -> Optional[float]` that returns just the float, and call both from `handle()`:

```python
# .claude/hooks/hooks/user_prompt_submit.py — new helper
def _extract_context_pct(transcript_path: str) -> Optional[float]:
    """Extract remaining context percentage as float from transcript JSONL.

    WORK-237: Returns float 0-100 representing remaining % for slim relay.
    Mirrors _get_context_usage() computation without string formatting.

    Returns:
        Float 0-100 or None if unavailable.
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
            return None
        context_limit = 200_000
        pct = min(100.0, (total / context_limit) * 100)
        return round(100.0 - pct, 1)
    except Exception:
        return None
```

> **Note on code duplication:** `_extract_context_pct` mirrors `_get_context_usage` logic. This is intentional to preserve the existing string-returning function's interface without refactoring it (scope discipline). A future cleanup could unify them, but that is out of scope for WORK-237.

Modified `handle()` block for context usage (lines 91-95 → 91-99):

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

**Change 2: governance_events.py — `_append_event()` reads slim when context_pct not provided**

New module-level constant:

```python
# .claude/haios/lib/governance_events.py — after SESSION_FILE constant (line 38)
SLIM_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "haios-status-slim.json"
```

New private helper `_read_context_pct_from_slim()`:

```python
def _read_context_pct_from_slim() -> Optional[float]:
    """Read context_pct from haios-status-slim.json.

    WORK-237: Slim relay read side. Returns float 0-100 or None if unavailable.
    Fail-silent: missing/malformed slim returns None (event logged without context_pct).
    """
    try:
        if not SLIM_FILE.exists():
            return None
        data = json.loads(SLIM_FILE.read_text(encoding="utf-8-sig"))
        val = data.get("context_pct")
        if val is None:
            return None
        return float(val)
    except Exception:
        return None
```

Modified `_append_event()`:

```python
def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
    """Append event to JSONL file, injecting session_id and context_pct.

    WORK-237: context_pct auto-injected from slim when caller does not provide
    explicit value. Caller-supplied value overrides slim (explicit > implicit).
    """
    event["session_id"] = _read_session_id()
    # WORK-237: auto-inject from slim if not explicitly provided
    resolved_pct = context_pct if context_pct is not None else _read_context_pct_from_slim()
    if resolved_pct is not None:
        event["context_pct"] = resolved_pct
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Behavior:** Every governance event will include `context_pct` reflecting the remaining context % as of the most recent UserPromptSubmit. Callers that pass explicit `context_pct` override the slim value.

**Result:** Enables context budget analysis (memory: 85989, 86041) — all events in `governance-events.jsonl` carry a context snapshot without any per-caller changes across the 12 existing call sites.

---

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 0 (Prerequisite): Patch SLIM_FILE in All Existing Test Isolation Points
- **file:** `tests/test_governance_events.py`
- **function:** N/A (fixture + individual test modifications)
- **setup:**
  - (a) In the `temp_events_file` fixture (line ~20-25), add a nested `with patch("governance_events.SLIM_FILE", tmp_path / "nonexistent-slim.json"):` to match the existing `with patch(...)` style (do NOT use monkeypatch — keep consistent with existing unittest.mock pattern).
  - (b) In `TestContextPctField::test_log_phase_transition_without_context_pct` (line ~374), which uses its OWN `with patch(...)` blocks (NOT the shared fixture), add `patch("governance_events.SLIM_FILE", tmp_path / "nonexistent-slim.json")` to the existing `with` statement. This test asserts `"context_pct" not in event` and will fail non-deterministically without this patch once real slim gains context_pct.
- **assertion:** All existing tests continue to pass. `TestContextPctField::test_log_phase_transition_without_context_pct` still asserts `"context_pct" not in event` successfully.
- **rationale:** Critique A1/A3/A9 — after `_append_event` reads SLIM_FILE, ALL test isolation points must patch SLIM_FILE. Two separate paths: shared fixture (covers 6+ test classes) and inline patches (covers TestContextPctField which uses its own isolation).

#### Test 1: Auto-Injection from Slim
- **file:** `tests/test_governance_events.py`
- **function:** `test_append_event_reads_context_pct_from_slim()`
- **class:** `TestContextPctAutoInjection`
- **setup:** Create `tmp_path/haios-status-slim.json` with `{"context_pct": 42.5}`. Patch `governance_events.SLIM_FILE` to that path. Patch `EVENTS_FILE` and `SESSION_FILE` to tmp paths. Call `log_phase_transition("DO", "WORK-237", "Hephaestus")` without passing `context_pct`.
- **assertion:** Returned event dict has `event["context_pct"] == 42.5`. Event on disk also has `context_pct == 42.5`.

#### Test 2: Explicit Override Wins Over Slim
- **file:** `tests/test_governance_events.py`
- **function:** `test_explicit_context_pct_overrides_slim()`
- **class:** `TestContextPctAutoInjection`
- **setup:** Create slim at `tmp_path/haios-status-slim.json` with `{"context_pct": 42.5}`. Patch `SLIM_FILE`, `EVENTS_FILE`, `SESSION_FILE`. Call `log_phase_transition("DO", "WORK-237", "Hephaestus", context_pct=99.0)`.
- **assertion:** `event["context_pct"] == 99.0` (caller value wins, slim value 42.5 is ignored).

#### Test 3: Graceful Degradation When Slim Missing
- **file:** `tests/test_governance_events.py`
- **function:** `test_append_event_no_context_pct_when_slim_missing()`
- **class:** `TestContextPctAutoInjection`
- **setup:** Patch `governance_events.SLIM_FILE` to a nonexistent path. Patch `EVENTS_FILE` and `SESSION_FILE`. Call `log_phase_transition("DO", "WORK-237", "Hephaestus")` without `context_pct`.
- **assertion:** `"context_pct" not in event` — event is written without the field, no exception raised.

#### Test 4: Slim Missing context_pct Key
- **file:** `tests/test_governance_events.py`
- **function:** `test_append_event_no_context_pct_when_slim_lacks_field()`
- **class:** `TestContextPctAutoInjection`
- **setup:** Create slim at `tmp_path/haios-status-slim.json` with `{"session_state": {}}` (no `context_pct` key). Patch `SLIM_FILE`, `EVENTS_FILE`, `SESSION_FILE`. Call `log_phase_transition("DO", "WORK-237", "Hephaestus")`.
- **assertion:** `"context_pct" not in event` — no field added when slim exists but key absent.

#### Test 5: UserPromptSubmit Writes context_pct to Slim
- **file:** `tests/test_governance_events.py` (in `TestContextPctAutoInjection` class — keeps all context_pct tests together; avoids import path issues with hooks directory)
- **function:** `test_write_context_pct_to_slim()`
- **setup:** Create `tmp_path/.claude/haios-status-slim.json` with `{"session_state": {}}`. Import `_write_context_pct_to_slim` from `user_prompt_submit` (via sys.path insert for `.claude/hooks/hooks/`). Call `_write_context_pct_to_slim(str(tmp_path), 75.5)`.
- **assertion:** Re-read slim; `data["context_pct"] == 75.5`. Other keys (e.g., `session_state`) preserved.

#### Test 6: _extract_context_pct Returns Float
- **file:** `tests/test_governance_events.py` (in `TestContextPctAutoInjection` class)
- **function:** `test_extract_context_pct_returns_float()`
- **setup:** Create a minimal transcript JSONL at `tmp_path/transcript.jsonl` with one assistant message containing `usage: {input_tokens: 100000, cache_creation_input_tokens: 0, cache_read_input_tokens: 0}`. Import `_extract_context_pct` from `user_prompt_submit`. Call `_extract_context_pct(str(transcript_path))`.
- **assertion:** Returns `50.0` (100000/200000 = 50% used → 50% remaining).

#### Test 7: Consistency Between _extract_context_pct and _get_context_usage
- **file:** `tests/test_governance_events.py` (in `TestContextPctAutoInjection` class)
- **function:** `test_extract_context_pct_consistent_with_get_context_usage()`
- **setup:** Create a transcript JSONL with one assistant message containing `usage: {input_tokens: 150000, cache_creation_input_tokens: 0, cache_read_input_tokens: 0}`. Import both `_extract_context_pct` and `_get_context_usage` from `user_prompt_submit`. Call both with the same transcript path.
- **assertion:** `_get_context_usage` returns string containing "25" (25% remaining). `_extract_context_pct` returns `25.0`. Values are consistent (float matches integer in string).
- **rationale:** Critique A2 — catches divergence if either function's computation changes independently.

---

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**Location 1:** After line 95 in `handle()` (context_usage block), add slim write call.

**Current Code (lines 91-95):**
```python
    # Part 1.5: Context usage from transcript JSONL (WORK-189, replaces E2-210)
    transcript_path = hook_data.get("transcript_path", "")
    context_usage = _get_context_usage(transcript_path)
    if context_usage:
        output_parts.append(context_usage)
```

**Target Code (lines 91-99):**
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

**Location 2:** Add two new helper functions after `_get_context_usage()` (after line 390):

```python
def _extract_context_pct(transcript_path: str) -> Optional[float]:
    """Extract remaining context percentage as float from transcript JSONL.

    WORK-237: Returns float 0-100 representing remaining % for slim relay.
    Mirrors _get_context_usage() computation without string formatting.

    Returns:
        Float 0-100 (rounded to 1 decimal) or None if unavailable.
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
            return None
        context_limit = 200_000
        pct = min(100.0, (total / context_limit) * 100)
        return round(100.0 - pct, 1)
    except Exception:
        return None


def _write_context_pct_to_slim(cwd: str, context_pct: float) -> None:
    """Write context_pct float to haios-status-slim.json for governance event relay.

    WORK-237: Slim relay pattern — UserPromptSubmit writes, _append_event reads.
    Fail-silent: stale/missing slim is better than broken hook.

    Args:
        cwd: Working directory path.
        context_pct: Remaining context percentage (0-100 float).
    """
    if not cwd:
        return
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return
    try:
        data = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        data["context_pct"] = context_pct
        slim_path.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception:
        pass
```

**Diff:**
```diff
+    # WORK-237: Write context_pct float to slim for governance event relay
+    context_pct = _extract_context_pct(transcript_path)
+    if context_pct is not None:
+        _write_context_pct_to_slim(cwd, context_pct)
+
+
+def _extract_context_pct(transcript_path: str) -> Optional[float]:
+    """Extract remaining context percentage as float from transcript JSONL.
+    ...
+    """
+    ...
+
+
+def _write_context_pct_to_slim(cwd: str, context_pct: float) -> None:
+    """Write context_pct float to haios-status-slim.json for governance event relay.
+    ...
+    """
+    ...
```

---

#### File 2 (MODIFY): `.claude/haios/lib/governance_events.py`

**Location 1:** After `SESSION_FILE` constant (line 38), add `SLIM_FILE` constant.

**Current Code (lines 35-38):**
```python
# Events file location (append-only JSONL)
EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"

# Session file location — read to inject session_id on every event (WORK-215)
SESSION_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "session"
```

**Target Code (lines 35-41):**
```python
# Events file location (append-only JSONL)
EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"

# Session file location — read to inject session_id on every event (WORK-215)
SESSION_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "session"

# Slim status file — read to auto-inject context_pct on every event (WORK-237)
SLIM_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "haios-status-slim.json"
```

**Location 2:** Add `_read_context_pct_from_slim()` helper after `_read_session_id()` (after line 488).

**Target Code:**
```python
def _read_context_pct_from_slim() -> Optional[float]:
    """Read context_pct from haios-status-slim.json.

    WORK-237: Slim relay read side. Returns float 0-100 or None if unavailable.
    Fail-silent: missing/malformed slim returns None (event logged without context_pct).
    """
    try:
        if not SLIM_FILE.exists():
            return None
        data = json.loads(SLIM_FILE.read_text(encoding="utf-8-sig"))
        val = data.get("context_pct")
        if val is None:
            return None
        return float(val)
    except Exception:
        return None
```

**Location 3:** Modify `_append_event()` (lines 491-498).

**Current Code:**
```python
def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
    """Append event to JSONL file, injecting session_id and optional context_pct."""
    event["session_id"] = _read_session_id()
    if context_pct is not None:
        event["context_pct"] = context_pct
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Target Code:**
```python
def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
    """Append event to JSONL file, injecting session_id and context_pct.

    WORK-237: context_pct auto-injected from slim when caller does not provide
    explicit value. Caller-supplied value overrides slim (explicit > implicit).
    """
    event["session_id"] = _read_session_id()
    # WORK-237: explicit caller value overrides slim; slim auto-injects when not provided
    resolved_pct = context_pct if context_pct is not None else _read_context_pct_from_slim()
    if resolved_pct is not None:
        event["context_pct"] = resolved_pct
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Diff:**
```diff
-def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
-    """Append event to JSONL file, injecting session_id and optional context_pct."""
-    event["session_id"] = _read_session_id()
-    if context_pct is not None:
-        event["context_pct"] = context_pct
+def _append_event(event: dict, context_pct: Optional[float] = None) -> None:
+    """Append event to JSONL file, injecting session_id and context_pct.
+
+    WORK-237: context_pct auto-injected from slim when caller does not provide
+    explicit value. Caller-supplied value overrides slim (explicit > implicit).
+    """
+    event["session_id"] = _read_session_id()
+    # WORK-237: explicit caller value overrides slim; slim auto-injects when not provided
+    resolved_pct = context_pct if context_pct is not None else _read_context_pct_from_slim()
+    if resolved_pct is not None:
+        event["context_pct"] = resolved_pct
     EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
     with open(EVENTS_FILE, "a", encoding="utf-8") as f:
         f.write(json.dumps(event) + "\n")
```

---

### Call Chain

```
UserPromptSubmit hook fires (every user prompt)
    |
    +-> handle(hook_data)
    |       |
    |       +-> _get_context_usage(transcript_path)  # returns "[CONTEXT: X% remaining]"
    |       |
    |       +-> _extract_context_pct(transcript_path) # NEW: returns float 0-100
    |       |
    |       +-> _write_context_pct_to_slim(cwd, float) # NEW: writes to slim["context_pct"]
    |
Any log_* function called by any hook/module
    |
    +-> _append_event(event, context_pct=None)
            |
            +-> _read_session_id()              # existing
            |
            +-> _read_context_pct_from_slim()   # NEW: reads slim["context_pct"]
            |       Returns: float | None
            |
            +-> event["context_pct"] = resolved_pct  # written if not None
            |
            +-> EVENTS_FILE.write(json)         # governance-events.jsonl
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New helper `_extract_context_pct` vs refactor `_get_context_usage` | New helper (code duplication) | Preserves existing string-returning function interface. Refactoring `_get_context_usage` risks breaking existing callers and tests. Scope discipline: WORK-237 is small effort. |
| `SLIM_FILE` as module-level constant | Module constant (mirrors `SESSION_FILE` pattern) | Consistent with existing `SESSION_FILE` approach; patchable in tests via `monkeypatch.setattr`. |
| `_read_context_pct_from_slim` as standalone function | Standalone (not inlined) | Independently testable; mirrors `_read_session_id()` pattern in same file. |
| Fail-silent in slim read/write | `except Exception: pass` / `return None` | Hook context — any error must not propagate. Same pattern as all existing hook helpers. |
| `round(remaining, 1)` in `_extract_context_pct` | 1 decimal place | Compact in JSONL; precision sufficient for analysis. `_get_context_usage` uses `:.0f` (integer string) — float can carry more. |
| No changes to 12 call sites | Zero per-caller edits | Single injection point in `_append_event` makes this a true infrastructure change. WORK-233 kwargs remain as explicit override mechanism for future precision needs. |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Slim file does not exist | `_read_context_pct_from_slim` returns None; event written without context_pct | Test 3 |
| Slim exists but no `context_pct` key | Returns None; no field in event | Test 4 |
| Slim contains malformed JSON | `except Exception` catches; returns None | (covered by Test 3 variant) |
| transcript_path empty/missing | `_extract_context_pct` returns None; slim not updated | Test 6 setup |
| Caller passes explicit context_pct | `resolved_pct = context_pct` (not slim); explicit value wins | Test 2 |
| context window 100% used | `remaining = 0.0`; written to slim as 0.0; valid float | — |
| Slim write fails (permissions) | `except Exception: pass`; slim not updated; next event reads stale/absent value | — |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `_extract_context_pct` diverges from `_get_context_usage` in future | Med — different values shown vs stored | Add comment in both functions cross-referencing. Unit test with known transcript fixture validates both return consistent values. |
| Slim write latency on every prompt | Low — disk write already happens (_refresh_slim_status was disabled for other reasons, not perf) | Fail-silent + slim is already read/written by UserPromptSubmit; no new I/O path. |
| Slim overwritten by ContextLoader between write and event | Low — ContextLoader refresh (`_refresh_slim_status`) is disabled (line 99-104); only slim read happens in handle() | Risk dormant while _refresh_slim_status disabled. If re-enabled, move write after refresh. |
| WORK-233 explicit callers clash with auto-injection | None — resolved_pct logic: explicit wins | Backward compatible by design: callers passing context_pct=X still get X. |
| Test isolation: SLIM_FILE is module-level constant | Med — tests may bleed if not patched | All new tests must patch `governance_events.SLIM_FILE`. Follow SESSION_FILE patch pattern from TestSessionIdInjection. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit.
     Producer: plan-author agent
     Consumer: DO agent + orchestrator -->

### Step 1: Patch Fixture + Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests (Test 0 through Test 7)
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** (a) Patch `temp_events_file` fixture to also set `SLIM_FILE` to nonexistent path (Test 0). (b) Add `TestContextPctAutoInjection` class to `tests/test_governance_events.py` with Tests 1-7 (auto-injection, override, degradation, missing key, slim write, extract float, consistency).
- **output:** Fixture patched; 7 new test methods exist; Tests 1-4 fail (functions not yet changed), Tests 5-7 fail (helpers not yet created)
- **verify:** `pytest tests/test_governance_events.py::TestContextPctAutoInjection -v 2>&1 | grep -c "FAILED\|ERROR"` equals 7. Existing tests still pass: `pytest tests/test_governance_events.py::TestContextPctField -v` exits 0.

### Step 2: Implement governance_events.py Changes (GREEN — part 1)
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** (a) Add `SLIM_FILE` constant after `SESSION_FILE`. (b) Add `_read_context_pct_from_slim()` after `_read_session_id()`. (c) Modify `_append_event()` per target code.
- **output:** TestContextPctAutoInjection tests 1-4 pass
- **verify:** `pytest tests/test_governance_events.py::TestContextPctAutoInjection::test_append_event_reads_context_pct_from_slim tests/test_governance_events.py::TestContextPctAutoInjection::test_explicit_context_pct_overrides_slim tests/test_governance_events.py::TestContextPctAutoInjection::test_append_event_no_context_pct_when_slim_missing tests/test_governance_events.py::TestContextPctAutoInjection::test_append_event_no_context_pct_when_slim_lacks_field -v` exits 0, 4 passed

### Step 3: Implement user_prompt_submit.py Changes (GREEN — part 2)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 2 complete
- **action:** (a) Add `_extract_context_pct()` after `_get_context_usage()`. (b) Add `_write_context_pct_to_slim()` after `_extract_context_pct()`. (c) Add 4-line block in `handle()` after context_usage block.
- **output:** Tests 5-7 pass (slim write, extract float, consistency)
- **verify:** `pytest tests/test_governance_events.py::TestContextPctAutoInjection -v` exits 0, 7 passed

### Step 4: Full Suite Regression Check
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Step 3 complete
- **action:** Run full test suite to confirm no regressions. Existing TestContextPctField tests (WORK-233) must still pass.
- **output:** Full suite green
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `0 failed`

### Step 5: Verify Runtime Consumer Wiring
- **spec_ref:** Layer 1 > Call Chain
- **input:** Step 4 complete
- **action:** Verify `_write_context_pct_to_slim` is called from `handle()` and `_read_context_pct_from_slim` is called from `_append_event()`.
- **output:** Both call sites exist in source
- **verify:** `grep "_write_context_pct_to_slim" .claude/hooks/hooks/user_prompt_submit.py` returns 2 matches (definition + call). `grep "_read_context_pct_from_slim" .claude/haios/lib/governance_events.py` returns 2 matches (definition + call in _append_event).

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_governance_events.py::TestContextPctAutoInjection -v` | 7 passed, 0 failed |
| `pytest tests/test_governance_events.py -v` | 0 new failures vs pre-existing baseline |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 failed |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| UserPromptSubmit writes context_pct to slim | `grep "_write_context_pct_to_slim" .claude/hooks/hooks/user_prompt_submit.py` | 2 matches (def + call) |
| _append_event reads from slim | `grep "_read_context_pct_from_slim" .claude/haios/lib/governance_events.py` | 2 matches (def + call) |
| All governance events get context_pct | `pytest tests/test_governance_events.py::TestContextPctAutoInjection::test_append_event_reads_context_pct_from_slim -v` | 1 passed |
| Explicit override respected | `pytest tests/test_governance_events.py::TestContextPctAutoInjection::test_explicit_context_pct_overrides_slim -v` | 1 passed |
| Graceful degradation when slim missing | `pytest tests/test_governance_events.py::TestContextPctAutoInjection::test_append_event_no_context_pct_when_slim_missing -v` | 1 passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| SLIM_FILE constant added | `grep "SLIM_FILE" .claude/haios/lib/governance_events.py` | 2 matches (def + use in function) |
| No stale references to old _append_event signature | `grep "context_pct is not None" .claude/haios/lib/governance_events.py` | 0 matches (replaced by resolved_pct logic) |
| Existing WORK-233 tests unaffected | `pytest tests/test_governance_events.py::TestContextPctField -v` | 5 passed, 0 failed |
| Runtime consumer exists (slim write) | `grep "_write_context_pct_to_slim" .claude/hooks/hooks/user_prompt_submit.py` | 1+ match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists — `_write_context_pct_to_slim` called from `handle()` (Consumer Integrity table)
- [ ] No stale references — old `if context_pct is not None` pattern replaced in `_append_event` (Consumer Integrity table)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- @docs/work/active/WORK-236/investigations/001-contextpct-governance-event-consumer-design.md (source specification)
- @.claude/haios/lib/governance_events.py (primary target: _append_event, _read_session_id pattern)
- @.claude/hooks/hooks/user_prompt_submit.py (primary target: handle, _get_context_usage, _read_slim)
- @tests/test_governance_events.py (test extension target)
- WORK-233: Add context_pct Field to Governance Events (parent plumbing — created the parameter)
- WORK-236: context_pct Governance Event Consumer Design (investigation that produced this design)

---

## Memory Query Results

Query: `memory_search_with_experience` with "context_pct governance events slim relay injection pattern user_prompt_submit"

**Prior patterns found:**
- Memory 85989, 84897, 86041, 88223: Converge on context budget tracking need (from WORK-236 investigation — cited above in Design Outputs)
- Memory 88175: "Governance layer has opportunity to estimate context consumption" — identifies governance_layer.py as possible injection point (superseded by WORK-236 finding that _append_event is better)
- SESSION_FILE constant + _read_session_id() pattern (WORK-215): Directly mirrors what we are doing with SLIM_FILE + _read_context_pct_from_slim(). This is the strongest prior pattern — same module, same approach.

**Anti-patterns to avoid:**
- Memory 85111: Unquoted YAML description fields with colons — YAML fields in this plan wrapped in double quotes.
- Memory 85640: No epoch-scoped queries — not relevant to this implementation.

---
