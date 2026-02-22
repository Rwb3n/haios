---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-02-22
backlog_id: WORK-195
title: "UserPromptSubmit Slim-Read-Once Refactor"
author: Hephaestus
lifecycle_phase: plan
session: 425
generated: 2026-02-22
last_updated: 2026-02-22T16:46:27

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-195/WORK.md"
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
# Implementation Plan: UserPromptSubmit Slim-Read-Once Refactor

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

`handle()` in `user_prompt_submit.py` reads and parses `haios-status-slim.json` exactly once, passing the parsed dict to all functions that need slim data.

---

## Open Decisions

None. Design is fully determined by WORK-194 investigation.

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 2 |

### Consumer Files

None — all changes are internal to the single file.

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_context_usage_injection.py` | UPDATE | Add tests for _get_session_state_warning and _get_phase_contract with slim dict param |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | - |
| Files to modify | 2 | user_prompt_submit.py + test file |
| Tests to write | 4 | See Layer 1 Tests |
| Total blast radius | 2 | Single module + test file |

---

## Layer 1: Specification

### Current State

```python
# user_prompt_submit.py:64-119 — handle() calls each function independently
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())
    # ...
    cwd = hook_data.get("cwd", "")
    session_warning = _get_session_state_warning(cwd)      # reads slim JSON
    # ...
    phase_contract = _get_phase_contract(cwd)               # reads slim JSON again
    # ...
```

```python
# user_prompt_submit.py:130-170 — each function reads slim independently
def _get_session_state_warning(cwd: str) -> Optional[str]:
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
    # ...

def _get_phase_contract(cwd: str) -> Optional[str]:
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
    # ...
```

**Behavior:** `haios-status-slim.json` read+parsed up to 4 times per `handle()` call.
**Problem:** Redundant I/O on every prompt. Blocks WORK-196 from adding more slim-based injections cleanly.

### Desired State

```python
# user_prompt_submit.py — handle() reads slim once, passes dict
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())
    # ...
    cwd = hook_data.get("cwd", "")
    slim = _read_slim(cwd)  # Read once
    session_warning = _get_session_state_warning(cwd, slim)
    # ...
    phase_contract = _get_phase_contract(cwd, slim)
    # ...
```

```python
def _read_slim(cwd: str) -> Optional[dict]:
    """Read and parse haios-status-slim.json once. Returns None if unavailable."""
    if not cwd:
        return None
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None
    try:
        return json.loads(slim_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None

def _get_session_state_warning(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """Accept pre-parsed slim dict. Falls back to reading if slim is None (backward compat)."""
    if slim is None:
        return None  # No slim data available
    # ... use slim directly, no file read ...

def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """Accept pre-parsed slim dict."""
    if slim is None:
        return None
    # ... use slim directly, no file read ...
```

**Behavior:** Slim JSON read exactly once per `handle()` call, dict passed to all consumers.
**Result:** Enables WORK-196 to add new injections by simply reading from the shared `slim` dict.

### Tests

#### Test 1: Session State Warning Returns Warning When No Active Cycle
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_session_state_warning_no_active_cycle()`
- **setup:** Create slim dict `{"session_state": {"active_cycle": None}}`
- **assertion:** Returns string containing "No active governance cycle detected"

#### Test 2: Session State Warning Returns None When Active Cycle Exists
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_session_state_warning_with_active_cycle()`
- **setup:** Create slim dict `{"session_state": {"active_cycle": "implementation-cycle", "current_phase": "DO", "work_id": "WORK-195"}}`
- **assertion:** Returns `None`

#### Test 3: Phase Contract Returns None When No Active Cycle
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_phase_contract_no_active_cycle()`
- **setup:** Create slim dict `{"session_state": {"active_cycle": None, "current_phase": None}}`
- **assertion:** Returns `None`

#### Test 4: Session State Warning Returns None When Slim Is None
- **file:** `tests/test_context_usage_injection.py`
- **function:** `test_session_state_warning_slim_none()`
- **setup:** Pass `slim=None`
- **assertion:** Returns `None` (graceful degradation)

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**Change 1: Add `_read_slim()` function** (after `_get_datetime_context`, ~line 129)

```python
def _read_slim(cwd: str) -> Optional[dict]:
    """Read and parse haios-status-slim.json once per handle() call."""
    if not cwd:
        return None
    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None
    try:
        return json.loads(slim_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
```

**Change 2: Update `handle()` to read slim once** (~lines 84-97)

Replace individual calls with:
```python
    cwd = hook_data.get("cwd", "")
    slim = _read_slim(cwd)

    session_warning = _get_session_state_warning(cwd, slim)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    phase_contract = _get_phase_contract(cwd, slim)
    if phase_contract:
        output_parts.append("")
        output_parts.append(phase_contract)
```

**Change 3: Update `_get_session_state_warning` signature** (~line 130)

Remove internal slim file read. Accept `slim: Optional[dict] = None` parameter. Guard on `slim is None`. Remove `slim_path` construction and `json.loads` call.

**Change 4: Update `_get_phase_contract` signature** (~line 173)

Same pattern as Change 3. Remove internal slim file read, accept `slim` parameter.

**Change 5: Update disabled functions to accept slim param**

Update `_get_vitals(cwd)` → `_get_vitals(cwd, slim=None)` and `_get_thresholds(cwd)` → `_get_thresholds(cwd, slim=None)`. Remove embedded `slim_path.read_text()` calls from their function bodies and replace with `slim` parameter usage. Both functions must add `if slim is None: return None` guard immediately after the existing `if not cwd: return None` guard — matching the pattern in Changes 3 and 4. Although these functions are disabled in `handle()`, their bodies must be refactored so that re-enabling them in WORK-196 does not silently break the single-read invariant. Note: `_get_thresholds` also reads `haios-status.json` (full status) — that read is unrelated to slim and stays.

### Call Chain

```
handle(hook_data)
    |
    +-> _get_datetime_context()
    +-> _get_context_usage(transcript_path)
    +-> _read_slim(cwd)              # NEW — reads once
    |       Returns: Optional[dict]
    |
    +-> _get_session_state_warning(cwd, slim)   # CHANGED — accepts slim
    +-> _get_phase_contract(cwd, slim)          # CHANGED — accepts slim
    +-> _get_lifecycle_guidance(prompt, cwd)     # unchanged
    +-> _get_rfc2119_reminders(prompt)           # unchanged
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate `_read_slim()` function | Extract read logic into dedicated function | Reusable by WORK-196 injections; single responsibility |
| `slim: Optional[dict] = None` default | Backward-compatible signature | Callers not passing slim get None → graceful degradation |
| Refactor disabled functions fully | Remove embedded slim reads from `_get_vitals`, `_get_thresholds` bodies | Critique A2: WORK-196 re-enabling them would silently break single-read invariant |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Slim file doesn't exist | `_read_slim` returns None → all consumers return None | Test 4 |
| Slim file has invalid JSON | `_read_slim` catches Exception, returns None | Existing behavior preserved |
| `session_state` key missing | `_get_session_state_warning` returns None (existing check) | Test 2 variant |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Silent regression in governance injections | H | Tests 1-4 verify both functions with slim dict (critique A2) |
| Breaking handle() integration test | M | Existing TestHandleIntegration still passes via monkeypatch |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add 4 test functions to `tests/test_context_usage_injection.py`
- **output:** 4 new tests fail (functions don't accept slim param yet)
- **verify:** `pytest tests/test_context_usage_injection.py -v` — 4 new FAILED, 6 existing PASSED

### Step 2: Implement Refactor (GREEN)
- **spec_ref:** Layer 1 > Design
- **input:** Step 1 complete (4 failing tests)
- **action:** Add `_read_slim()`, update `handle()` to read once, update `_get_session_state_warning` and `_get_phase_contract` signatures per Changes 3/4, remove embedded slim reads from `_get_vitals` and `_get_thresholds` bodies and add `slim: Optional[dict] = None` parameter with `if slim is None: return None` guard per Change 5
- **output:** All 10 tests pass (4 new + 6 existing)
- **verify:** `pytest tests/test_context_usage_injection.py -v` — 10 passed, 0 failed

### Step 3: Full Suite Regression
- **spec_ref:** Ground Truth Verification
- **input:** Step 2 complete
- **action:** Run full test suite
- **output:** No regressions
- **verify:** `pytest tests/ -v` — 0 new failures vs 1609 baseline

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_context_usage_injection.py -v` | 10 passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs 1609 baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| handle() reads slim once | `grep -c "_read_slim" .claude/hooks/hooks/user_prompt_submit.py` | 2 (def + call) |
| _get_session_state_warning accepts slim | `grep "def _get_session_state_warning" .claude/hooks/hooks/user_prompt_submit.py` | contains "slim" |
| _get_phase_contract accepts slim | `grep "def _get_phase_contract" .claude/hooks/hooks/user_prompt_submit.py` | contains "slim" |
| No redundant slim reads in active code | `grep -c "slim_path.read_text" .claude/hooks/hooks/user_prompt_submit.py` | 1 (only in _read_slim) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| handle() calls _read_slim | `grep "_read_slim(cwd)" .claude/hooks/hooks/user_prompt_submit.py` | 1 match |
| handle() passes slim to consumers | `grep "cwd, slim" .claude/hooks/hooks/user_prompt_submit.py` | 2 matches |

### Completion Criteria (DoD)

- [ ] All tests pass (10 in test file, full suite regression clean)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No redundant slim reads in active code paths
- [ ] WHY captured (memory_refs populated via ingester_ingest)

---

## References

- @docs/work/active/WORK-194/WORK.md (parent investigation)
- @docs/work/active/WORK-196/WORK.md (downstream: injection batch)
- @.claude/hooks/hooks/user_prompt_submit.py (target file)

---
