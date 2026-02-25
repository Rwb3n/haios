---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-215
title: "Session ID Field on Governance Events"
author: Hephaestus
lifecycle_phase: plan
session: 442
generated: 2026-02-24
last_updated: 2026-02-24T15:10:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-215/WORK.md"
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
# Implementation Plan: Session ID Field on Governance Events

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification. -->

---

## Goal

Add a `session_id` integer field to every governance event by reading `.claude/session` in `_append_event()` — the single write path — with graceful degradation to 0 when the file is missing or non-integer.

---

## Open Decisions

No operator decisions exist for this work item. All design choices are resolved below in Key Design Decisions.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | — | — | No unresolved operator decisions in WORK.md |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/governance_events.py` | MODIFY | 2 |

### Consumer Files

No consumer files need updating. `_append_event()` is an internal function; its callers receive the enriched event dict automatically. The `session_id` field is additive — no existing callers pass or read this field today.

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/governance_events.py` | self-contained (no external callers of `_append_event`) | 456-460 | MODIFY (primary file above) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_governance_events.py` | UPDATE | Add 4 new test methods to existing file — session_id in log_phase_transition, log_session_start, log_session_end, and degradation edge case |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files required |
| Files to modify | 1 | governance_events.py (primary) |
| Tests to write | 5 | Test Files table |
| Total blast radius | 2 | governance_events.py + test_governance_events.py |

---

## Layer 1: Specification

### Current State

```python
# .claude/haios/lib/governance_events.py:456-460 — what exists now

def _append_event(event: dict) -> None:
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Behavior:** Appends event dict as-is to the JSONL file. No session context is injected.

**Problem:** Governance events have no `session_id` field, making cross-session correlation require fragile timestamp-based inference.

### Desired State

```python
# .claude/haios/lib/governance_events.py — target implementation

# Module-level constant (alongside EVENTS_FILE constant at line 35):
SESSION_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "session"


def _read_session_id() -> int:
    """Read current session number from .claude/session.

    Returns session number as int, or 0 if file missing, unreadable,
    or contains no parseable integer line.

    Pattern mirrors checkpoint_auto._read_session_number() and
    session_end_actions.read_session_number() (established in E2.8).
    """
    try:
        if not SESSION_FILE.exists():
            return 0
        for line in SESSION_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                return int(line)
            except ValueError:
                continue
        return 0
    except Exception:
        return 0


def _append_event(event: dict) -> None:
    """Append event to JSONL file, injecting session_id."""
    event["session_id"] = _read_session_id()
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Behavior:** Every event written via `_append_event()` automatically gains `session_id` from `.claude/session`. Callers do not need to change.

**Result:** All governance events in `governance-events.jsonl` are correlated to a session number, enabling `grep session_id:442` style queries during debugging. Satisfies REQ-OBSERVE-001 (all state transitions logged with full context).

### Tests

#### Test 1: session_id present in log_phase_transition event
- **file:** `tests/test_governance_events.py`
- **function:** `test_log_phase_transition_includes_session_id()`
- **setup:** `temp_events_file` fixture (patches `EVENTS_FILE`); patch `governance_events.SESSION_FILE` to a tmp file containing `"442\n"` (write it to `tmp_path / "session"`)
- **assertion:** `events[0]["session_id"] == 442`

#### Test 2: session_id present in log_session_start event
- **file:** `tests/test_governance_events.py`
- **function:** `test_log_session_start_includes_session_id()`
- **setup:** Patch `SESSION_FILE` to tmp file containing `"442\n"`; patch `EVENTS_FILE` to tmp JSONL
- **assertion:** `event["session_id"] == 442` (use the return value of `log_session_start`)

#### Test 3: session_id present in log_session_end event
- **file:** `tests/test_governance_events.py`
- **function:** `test_log_session_end_includes_session_id()`
- **setup:** Patch `SESSION_FILE` to tmp file containing `"442\n"`; patch `EVENTS_FILE` to tmp JSONL
- **assertion:** `event["session_id"] == 442` (use the return value of `log_session_end`)

#### Test 4: Graceful degradation — session file missing
- **file:** `tests/test_governance_events.py`
- **function:** `test_session_id_defaults_to_zero_when_file_missing()`
- **setup:** Patch `SESSION_FILE` to a non-existent path; patch `EVENTS_FILE` to tmp JSONL
- **assertion:** `events[0]["session_id"] == 0` after calling `log_phase_transition`

#### Test 5: Graceful degradation — session file malformed
- **file:** `tests/test_governance_events.py`
- **function:** `test_session_id_defaults_to_zero_when_malformed()`
- **setup:** Patch `SESSION_FILE` to tmp file containing `"not-an-integer\n"`; patch `EVENTS_FILE` to tmp JSONL
- **assertion:** `events[0]["session_id"] == 0`

### Design

#### File 1 (MODIFY): `.claude/haios/lib/governance_events.py`

**Location 1:** After line 35 (EVENTS_FILE constant), add SESSION_FILE constant:

**Current Code (line 35):**
```python
# Events file location (append-only JSONL)
EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"
```

**Target Code:**
```python
# Events file location (append-only JSONL)
EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"

# Session file location — read to inject session_id on every event
SESSION_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "session"
```

**Location 2:** Before `_append_event()` at line 456, add `_read_session_id()`:

**Current Code (line 456-460):**
```python
def _append_event(event: dict) -> None:
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Target Code:**
```python
def _read_session_id() -> int:
    """Read current session number from .claude/session.

    Returns session number as int, or 0 if file missing, unreadable,
    or contains no parseable integer line.

    Pattern mirrors checkpoint_auto._read_session_number() and
    session_end_actions.read_session_number() (established in E2.8).
    """
    try:
        if not SESSION_FILE.exists():
            return 0
        for line in SESSION_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                return int(line)
            except ValueError:
                continue
        return 0
    except Exception:
        return 0


def _append_event(event: dict) -> None:
    """Append event to JSONL file, injecting session_id."""
    event["session_id"] = _read_session_id()
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

**Diff:**
```diff
+# Session file location — read to inject session_id on every event
+SESSION_FILE = Path(__file__).parent.parent.parent.parent / ".claude" / "session"
+
+
+def _read_session_id() -> int:
+    """Read current session number from .claude/session.
+
+    Returns session number as int, or 0 if file missing, unreadable,
+    or contains no parseable integer line.
+
+    Pattern mirrors checkpoint_auto._read_session_number() and
+    session_end_actions.read_session_number() (established in E2.8).
+    """
+    try:
+        if not SESSION_FILE.exists():
+            return 0
+        for line in SESSION_FILE.read_text(encoding="utf-8").splitlines():
+            line = line.strip()
+            if not line or line.startswith("#"):
+                continue
+            try:
+                return int(line)
+            except ValueError:
+                continue
+        return 0
+    except Exception:
+        return 0
+

 def _append_event(event: dict) -> None:
-    """Append event to JSONL file."""
+    """Append event to JSONL file, injecting session_id."""
+    event["session_id"] = _read_session_id()
     EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
     with open(EVENTS_FILE, "a", encoding="utf-8") as f:
         f.write(json.dumps(event) + "\n")
```

### Call Chain

```
log_phase_transition() / log_session_start() / log_session_end() / log_gate_violation() / etc.
    |
    +-> _append_event(event)       # <-- WHERE session_id is injected
    |       Calls: _read_session_id()
    |       Reads: SESSION_FILE (.claude/session)
    |       Mutates: event["session_id"] = <int>
    |       Writes: EVENTS_FILE (governance-events.jsonl)
    |
    +-> returns enriched event dict to caller
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Inject at `_append_event()` not at each log_* function | Single write path injection | 7+ log_* functions call `_append_event()`. Adding injection once at the write path is DRY; adding to each caller would require 7 changes and risk missing future log_* additions. |
| `SESSION_FILE` as module-level constant | Yes, mirror of `EVENTS_FILE` pattern | Consistent with existing module constant style; allows test patching via `patch("governance_events.SESSION_FILE", ...)`. |
| Separate `_read_session_id()` helper | Yes | Keeps `_append_event()` minimal; makes the session-read logic independently testable; mirrors established pattern from `checkpoint_auto._read_session_number()` and `session_end_actions.read_session_number()`. |
| Default to 0 on failure | Yes (not None or raise) | Graceful degradation: 0 is a sentinel meaning "session unknown" — integer type is preserved, JSON serialization stays clean, no callers need null-guards. WORK item acceptance criteria explicitly require `default to 0`. |
| Skip comment lines starting with `#` | Yes | `.claude/session` has `# generated:` header lines. Mirrors the exact pattern from `session_end_actions.read_session_number()` (lines 46-53). |
| Mutate event dict before write | Yes (`event["session_id"] = ...`) | `_append_event()` already receives a mutable dict. Mutation before serialization is simpler than creating a copy. Return value of log_* functions will also contain session_id, which tests can assert. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `.claude/session` file does not exist | `SESSION_FILE.exists()` returns False → return 0 | Test 4 |
| File exists but contains only `# generated:` comment lines | Loop skips `#` lines, falls through to `return 0` | Test 5 (malformed) |
| File contains non-integer text (e.g., "not-an-integer") | `int(line)` raises ValueError → `continue` → return 0 | Test 5 |
| File contains valid integer (e.g., "442") | Parsed and returned as int 442 | Tests 1, 2, 3 |
| File readable but unexpected exception | `except Exception: return 0` outer guard | Covered by graceful degradation contract |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| PATH resolution for SESSION_FILE wrong in hook subprocess context | M | `Path(__file__).parent.parent.parent.parent` anchors to file location, not `cwd` — mirrors `session_end_actions._default_project_root()` which uses same technique. Verified: `lib/` → `haios/` → `.claude/` → `project_root/`, then `/ ".claude" / "session"` = project_root/.claude/session. |
| Mutation of caller's event dict | L | All callers construct the dict locally in the same function scope (`event = {...}`); no caller re-uses the dict after `_append_event()`. Mutation is safe. |
| Regression in existing tests | M | Existing tests patch `EVENTS_FILE` but not `SESSION_FILE` — `_read_session_id()` will attempt to read the real `.claude/session`. If that file exists (it does: contains "442"), tests will see `session_id: 442`. This is not a test failure — assertions on other fields remain unaffected. New tests explicitly control SESSION_FILE. |
| `session_id` field name collides with existing field | L | Grep confirms no event type currently uses `session_id` key. `log_session_start/end` use `"session"` (not `"session_id"`). No collision. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add 5 new test methods to `tests/test_governance_events.py` — a new class `TestSessionIdInjection` containing `test_log_phase_transition_includes_session_id`, `test_log_session_start_includes_session_id`, `test_log_session_end_includes_session_id`, `test_session_id_defaults_to_zero_when_file_missing`, `test_session_id_defaults_to_zero_when_malformed`
- **output:** New test class exists; all 5 tests fail with `KeyError: 'session_id'` or `AssertionError`
- **verify:** `pytest tests/test_governance_events.py::TestSessionIdInjection -v 2>&1 | grep -c "FAILED\|ERROR"` equals 5

### Step 2: Implement session_id injection (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (5 tests exist and fail)
- **action:** Add `SESSION_FILE` constant after `EVENTS_FILE` constant; add `_read_session_id()` function before `_append_event()`; add `event["session_id"] = _read_session_id()` as first line of `_append_event()`
- **output:** All 5 new tests pass; existing tests unaffected
- **verify:** `pytest tests/test_governance_events.py -v` exits 0, all tests pass

### Step 3: Verify real event written
- **spec_ref:** Layer 0 > Primary Files
- **input:** Step 2 complete (implementation live)
- **action:** Run any governance event-emitting command (e.g., `just set-cycle WORK-215 DO`) or call `log_phase_transition` once from Python REPL; inspect governance-events.jsonl tail
- **output:** At least one event in governance-events.jsonl contains `"session_id": 442` (or current session number)
- **verify:** `tail -1 .claude/haios/governance-events.jsonl | python3 -c "import sys,json; e=json.load(sys.stdin); assert 'session_id' in e, 'missing'; print('OK:', e['session_id'])"` prints `OK: <integer>`

### Step 4: Full regression check
- **spec_ref:** Layer 0 > Test Files
- **input:** Step 3 complete
- **action:** Run full test suite
- **output:** Zero new failures introduced
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `passed` with 0 failed (compare to pre-existing baseline: 1571 passed, 0 failed, 8 skipped)

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_governance_events.py::TestSessionIdInjection -v` | 5 passed, 0 failed |
| `pytest tests/test_governance_events.py -v` | All existing + 5 new pass, 0 failed |
| `pytest tests/ -v` | 0 new failures vs baseline (1571 passed, 0 failed, 8 skipped) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| `session_id` integer field in `_append_event()` | `grep "session_id" .claude/haios/lib/governance_events.py` | 2+ matches (`SESSION_FILE =`, `event["session_id"]`, `_read_session_id`) |
| Graceful degradation on missing file | `pytest tests/test_governance_events.py::TestSessionIdInjection::test_session_id_defaults_to_zero_when_file_missing -v` | 1 passed |
| Unit tests for log_phase_transition, log_session_start, log_session_end | `pytest tests/test_governance_events.py::TestSessionIdInjection -v` | 5 passed |
| Real event in governance-events.jsonl contains session_id | `tail -1 .claude/haios/governance-events.jsonl \| python3 -c "import sys,json; e=json.loads(sys.stdin.read()); print('session_id' in e)"` | `True` |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No callers of `_append_event` broken | `pytest tests/ -v 2>&1 \| grep FAILED` | 0 matches |
| SESSION_FILE constant patchable | `grep "SESSION_FILE" .claude/haios/lib/governance_events.py` | 1+ match |
| `_read_session_id` function exists | `grep "_read_session_id" .claude/haios/lib/governance_events.py` | 2+ matches (def + call site) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Real event in governance-events.jsonl contains session_id (Step 3 verify)
- [ ] No stale references (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/haios/lib/governance_events.py` — primary implementation target (source file read)
- `.claude/haios/lib/session_end_actions.py` — `read_session_number()` sibling pattern (lines 29-57)
- `.claude/haios/lib/checkpoint_auto.py` — `_read_session_number()` sibling pattern (lines 67-83)
- `tests/test_governance_events.py` — existing test file to extend
- `docs/work/active/WORK-215/WORK.md` — work item spec
- `docs/work/active/WORK-212/WORK.md` — parent (mechanical phase delegation)
- Memory 88283 — WORK-215 work item creation context
- Memory 88284, 88285 — WORK-212 retro directives on session_id
- REQ-OBSERVE-001: All state transitions logged to events file
- `.claude/haios/epochs/E2_8/arcs/call/chapters/CH-059-CeremonyAutomation/CHAPTER.md`

---
