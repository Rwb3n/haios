---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-03-07
backlog_id: WORK-248
title: "Hook Infrastructure Cleanup — Dead Code and Stale Gates"
author: Hephaestus
lifecycle_phase: plan
session: 474
generated: 2026-03-07
last_updated: 2026-03-07T17:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-248/WORK.md"
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
# Implementation Plan: Hook Infrastructure Cleanup — Dead Code and Stale Gates

---

## Goal

Remove disabled/dead code from hook scripts and fix a stale all-sessions process-review gate, leaving the hook infrastructure clean and each AC independently verifiable by test.

---

## Open Decisions

No operator decisions required — all 5 ACs are scoped deletions with clear boundaries.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| orphaned scripts disposition | delete vs keep-archived | delete both | Both files (memory_retrieval.py, reasoning_extraction.py) use old PowerShell caller pattern (called from archived Stop.ps1, UserPromptSubmit.ps1). Current stop.py uses MemoryBridge. Zero live callers confirmed by grep. |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 2 |
| `.claude/hooks/hooks/pre_tool_use.py` | MODIFY | 2 |
| `.claude/hooks/memory_retrieval.py` | DELETE | 2 |
| `.claude/hooks/reasoning_extraction.py` | DELETE | 2 |

### Consumer Files

<!-- Verified by grep: no live callers of memory_retrieval.py or reasoning_extraction.py
     outside archived PowerShell scripts. batch_work_bypass only referenced in pre_tool_use.py.
     _get_vitals / _get_thresholds / _refresh_slim_status not called outside user_prompt_submit.py. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/hooks/README.md` | lists memory_retrieval.py, reasoning_extraction.py | 195-197 | UPDATE (remove entries) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_hook_cleanup.py` | CREATE | New test file verifying dead code removal and gate scope |

Note: tests/test_lib_status.py, tests/test_manifest.py, tests/test_plan_authoring_agent.py are pre-existing failures already fixed by WORK-252 (status: complete). AC 5 verified as already-green; no new test changes needed for those files.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | Test Files table (CREATE) |
| Files to modify | 3 | user_prompt_submit.py, pre_tool_use.py, README.md |
| Files to delete | 2 | memory_retrieval.py, reasoning_extraction.py |
| Tests to write | 6 | Test Files table |
| Total blast radius | 6 | Sum of unique files |

---

## Layer 1: Specification

### Current State

**AC1: Disabled vitals/thresholds code in user_prompt_submit.py**

```python
# user_prompt_submit.py lines 98-104 (disabled S179)
    # Part 2: HAIOS Vitals (E2-119: refresh status before reading)
    # DISABLED Session 179: Vitals structure outdated after E2.2 chapter redesign
    # Milestones replaced by Chapters, slim status needs redesign
    # cwd = hook_data.get("cwd", "")
    # _refresh_slim_status(cwd)  # E2-119: Ensure fresh data on every prompt
    # vitals = _get_vitals(cwd)
    # if vitals:
    #     output_parts.append("")

# user_prompt_submit.py lines 119-123 (disabled S259)
    # Part 3: Dynamic thresholds
    # DISABLED Session 259: Thresholds read deprecated milestone data
    # Milestones replaced by Arcs/Chapters in E2.3 - needs status redesign
    # thresholds = _get_thresholds(cwd)
    # if thresholds:
    #     output_parts.append(thresholds)
```

Dead function bodies (never called from handle() after S179/S259):
- `_refresh_slim_status()` — lines 25-51, only referenced in now-deleted commented block
- `_get_vitals()` — lines 375-441, called only from disabled block
- `_get_thresholds()` — lines 444-502, called only from disabled block

**Behavior:** Commented-out code accumulates in file, increasing cognitive load for maintainers.
**Problem:** 7+ years of dead code; _get_vitals references `milestone` slim key (deprecated structure). `_get_thresholds` reads full haios-status.json for deprecated milestone data. Both bodies are pure dead weight.

---

**AC2: .batch_work_bypass dead code in pre_tool_use.py**

```python
# pre_tool_use.py lines 330-334 (inside _check_scaffold_governance)
    # Session 297: Temporary bypass for batch work item creation (E2.5 decomposition)
    # TODO: Remove after E2.5 Phase 1 work items created
    batch_bypass_file = Path(__file__).parent.parent.parent / "haios" / "config" / ".batch_work_bypass"
    if batch_bypass_file.exists():
        return None

# pre_tool_use.py lines 435-439 (inside _check_path_governance)
    # Session 297: Temporary bypass for batch work item creation (E2.5 decomposition)
    # TODO: Remove after E2.5 Phase 1 work items created
    batch_bypass_file = Path(__file__).parent.parent.parent / "haios" / "config" / ".batch_work_bypass"
    if batch_bypass_file.exists():
        return None
```

**Behavior:** If `.batch_work_bypass` file exists, scaffold and path governance are both silently bypassed.
**Problem:** E2.5 Phase 1 decomposition is complete. The file path `.claude/haios/config/.batch_work_bypass` no longer exists and the bypass is a security hole in governance.

---

**AC3: Orphaned hook scripts**

```
.claude/hooks/memory_retrieval.py  — 259 lines
  Called by: UserPromptSubmit.ps1 (archived) — no Python caller
  Imports: google.generativeai, haios_etl.retrieval (ReasoningAwareRetrieval)
  Status: ORPHANED — PS1 archived, stop.py uses MemoryBridge instead

.claude/hooks/reasoning_extraction.py  — 396 lines
  Called by: Stop.ps1 (archived) — no Python caller
  Imports: haios_etl.database, haios_etl.extraction, haios_etl.retrieval
  Status: ORPHANED — PS1 archived, stop.py uses MemoryBridge instead
```

**Behavior:** Two large Python files accumulate in hooks directory with no callers.
**Problem:** Confusing to maintainers; implies these are active; heavy dependencies (Google genai API calls) create false import surface.

---

**AC4: Process review gate scoped to all-sessions**

```python
# pre_tool_use.py lines 930-946 (inside _check_process_review_gate)
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
```

**Behavior:** ANY ProcessReviewApproved event in the entire history permanently unlocks L3/L4 writes.
**Problem:** One approval from session 100 unlocks all future sessions forever. Should scope to current session only.

---

**AC5: Pre-existing test failures**

Already fixed by WORK-252 (closed 2026-03-07). Verified as green in Session 472 final run: 1833 passed, 0 failed.

**Behavior:** tests pass.
**Problem:** None — pre-condition is already satisfied.

---

### Desired State

**AC1: After removal**

`handle()` in user_prompt_submit.py has no disabled blocks. The three dead functions (`_refresh_slim_status`, `_get_vitals`, `_get_thresholds`) are deleted. Comments about disabled sessions removed. File is ~200 lines shorter.

```python
# handle() after cleanup — Part 2 block removed, Part 3 block removed
    # Part 1.5: Context budget — relay .claude/context_remaining to slim for governance events
    context_pct = _read_context_remaining(cwd)
    if context_pct is not None:
        _write_context_pct_to_slim(cwd, context_pct)

    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd, slim)
    # ... (no dead Part 2 or Part 3 blocks between here)

    # Part 4: Lifecycle guidance
    prompt = hook_data.get("prompt", "")
    lifecycle = _get_lifecycle_guidance(prompt, cwd)
```

**Result:** Cleaner file; no references to deprecated milestone/vitals structure.

---

**AC2: After removal**

`_check_scaffold_governance()` and `_check_path_governance()` have no batch_work_bypass check. Each function begins its logic directly after the `if not command/file_path` guard.

```python
# _check_scaffold_governance() after cleanup
def _check_scaffold_governance(command: str) -> Optional[dict]:
    if not command:
        return None

    # Only block work_item scaffolding - other types are called by governed commands
    scaffold_patterns = { ... }
    ...

# _check_path_governance() after cleanup
def _check_path_governance(file_path: str) -> Optional[dict]:
    if not file_path:
        return None

    # If file already exists, allow edits
    if Path(file_path).exists():
        return None
    ...
```

**Result:** Governance cannot be bypassed by creating a file. Scaffold and path governance are always enforced.

---

**AC3: After deletion**

Files removed from disk. README.md updated to remove their entries from the File Structure section.

```
.claude/hooks/
├── hook_dispatcher.py
├── hooks/
│   ├── user_prompt_submit.py
│   ├── pre_tool_use.py
│   ├── post_tool_use.py
│   └── stop.py
├── statusline.py
├── archive/
│   └── ...  (unchanged)
└── tests/
```

**Result:** No orphaned scripts; hooks directory reflects only active components.

---

**AC4: After session-scoping**

`_check_process_review_gate()` filters events to current session only using `_read_session_id()` from governance_events.

```python
# pre_tool_use.py — _check_process_review_gate() after fix
        from governance_events import read_events, _read_session_id

        current_session = _read_session_id()
        events = read_events()
        has_approval = any(
            e.get("type") == "ProcessReviewApproved"
            and e.get("session_id") == current_session
            for e in events
        )
```

**Behavior:** ProcessReviewApproved approval only valid for the session in which it was logged.
**Result:** Per-session scoping enforced. Historic approvals don't permanently unlock future sessions.

---

### Tests

#### Test 1: Disabled vitals block removed from handle()
- **file:** `tests/test_hook_cleanup.py`
- **function:** `test_vitals_block_not_in_handle()`
- **setup:** Read user_prompt_submit.py source as text
- **assertion:** `"DISABLED Session 179"` not in source; `"_refresh_slim_status"` not in source

#### Test 2: Disabled thresholds block removed from handle()
- **file:** `tests/test_hook_cleanup.py`
- **function:** `test_thresholds_block_not_in_handle()`
- **setup:** Read user_prompt_submit.py source as text
- **assertion:** `"DISABLED Session 259"` not in source; `"_get_thresholds"` not in source; `"_get_vitals"` not in source

#### Test 3: Dead functions removed from user_prompt_submit.py
- **file:** `tests/test_hook_cleanup.py`
- **function:** `test_dead_functions_removed()`
- **setup:** Import user_prompt_submit module
- **assertion:** `hasattr(module, "_refresh_slim_status")` is False; `hasattr(module, "_get_vitals")` is False; `hasattr(module, "_get_thresholds")` is False

#### Test 4: batch_work_bypass removed from pre_tool_use.py
- **file:** `tests/test_hook_cleanup.py`
- **function:** `test_batch_bypass_removed()`
- **setup:** Read pre_tool_use.py source as text
- **assertion:** `".batch_work_bypass"` not in source; `"Session 297"` not in source

#### Test 5: Orphaned scripts deleted
- **file:** `tests/test_hook_cleanup.py`
- **function:** `test_orphaned_scripts_deleted()`
- **setup:** Check file paths
- **assertion:** `Path(".claude/hooks/memory_retrieval.py").exists()` is False; `Path(".claude/hooks/reasoning_extraction.py").exists()` is False

#### Test 6: Process review gate scoped to current session
- **file:** `tests/test_hook_cleanup.py`
- **function:** `test_process_review_gate_session_scoped()`
- **setup:** Import pre_tool_use; mock `read_events` to return list with one ProcessReviewApproved event with session_id=999; mock `_read_session_id` to return 474 (different session)
- **assertion:** `_check_process_review_gate("manifesto/L3/some.md")` returns deny response (cross-session approval rejected)

---

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**AC1 — Remove disabled vitals block (lines 98-104)**

**Current Code:**
```python
    # Part 2: HAIOS Vitals (E2-119: refresh status before reading)
    # DISABLED Session 179: Vitals structure outdated after E2.2 chapter redesign
    # Milestones replaced by Chapters, slim status needs redesign
    # cwd = hook_data.get("cwd", "")
    # _refresh_slim_status(cwd)  # E2-119: Ensure fresh data on every prompt
    # vitals = _get_vitals(cwd)
    # if vitals:
    #     output_parts.append("")
```

**Target Code:** Delete these 8 lines entirely.

**AC1 — Remove disabled thresholds block (lines 119-123)**

**Current Code:**
```python
    # Part 3: Dynamic thresholds
    # DISABLED Session 259: Thresholds read deprecated milestone data
    # Milestones replaced by Arcs/Chapters in E2.3 - needs status redesign
    # thresholds = _get_thresholds(cwd)
    # if thresholds:
    #     output_parts.append(thresholds)
```

**Target Code:** Delete these 6 lines entirely.

**AC1 — Remove dead `_refresh_slim_status()` function (lines 25-51)**

Delete the entire function definition from line 25 (`def _refresh_slim_status(cwd: str) -> None:`) through line 51 (`        pass`).

**AC1 — Remove dead `_get_vitals()` function (lines 375-441)**

Delete the entire function definition from `def _get_vitals(cwd: str, slim: Optional[dict] = None) -> Optional[str]:` through its closing `return None` within `except Exception`.

**AC1 — Remove dead `_get_thresholds()` function (lines 444-502)**

Delete the entire function definition from `def _get_thresholds(cwd: str, slim: Optional[dict] = None) -> Optional[str]:` through its final `return None`.

---

#### File 2 (MODIFY): `.claude/hooks/hooks/pre_tool_use.py`

**AC2 — Remove batch_work_bypass in `_check_scaffold_governance()` (lines 330-334)**

**Current Code:**
```python
    # Session 297: Temporary bypass for batch work item creation (E2.5 decomposition)
    # TODO: Remove after E2.5 Phase 1 work items created
    batch_bypass_file = Path(__file__).parent.parent.parent / "haios" / "config" / ".batch_work_bypass"
    if batch_bypass_file.exists():
        return None
```

**Target Code:** Delete these 4 lines entirely.

**AC2 — Remove batch_work_bypass in `_check_path_governance()` (lines 435-439)**

**Current Code:**
```python
    # Session 297: Temporary bypass for batch work item creation (E2.5 decomposition)
    # TODO: Remove after E2.5 Phase 1 work items created
    batch_bypass_file = Path(__file__).parent.parent.parent / "haios" / "config" / ".batch_work_bypass"
    if batch_bypass_file.exists():
        return None
```

**Target Code:** Delete these 4 lines entirely.

**AC4 — Session-scope the process review gate (lines 930-946)**

**Current Code:**
```python
        from governance_events import read_events

        # TODO(WORK-209): This reads ALL historical events, not just current session.
        # Per-session scoping is a follow-on. Any prior ProcessReviewApproved event
        # permanently unlocks L3/L4 writes. Acceptable for V1 given fail-permissive stance.
        events = read_events()
        has_approval = any(
            e.get("type") == "ProcessReviewApproved"
            for e in events
        )
```

**Target Code:**
```python
        from governance_events import read_events, _read_session_id

        # WORK-248: Scope to current session. A ProcessReviewApproved approval
        # is valid only for the session in which it was logged.
        current_session = _read_session_id()
        events = read_events()
        has_approval = any(
            e.get("type") == "ProcessReviewApproved"
            and e.get("session_id") == current_session
            for e in events
        )
```

**Diff:**
```diff
-        from governance_events import read_events
+        from governance_events import read_events, _read_session_id

-        # TODO(WORK-209): This reads ALL historical events, not just current session.
-        # Per-session scoping is a follow-on. Any prior ProcessReviewApproved event
-        # permanently unlocks L3/L4 writes. Acceptable for V1 given fail-permissive stance.
-        events = read_events()
-        has_approval = any(
-            e.get("type") == "ProcessReviewApproved"
-            for e in events
-        )
+        # WORK-248: Scope to current session. A ProcessReviewApproved approval
+        # is valid only for the session in which it was logged.
+        current_session = _read_session_id()
+        events = read_events()
+        has_approval = any(
+            e.get("type") == "ProcessReviewApproved"
+            and e.get("session_id") == current_session
+            for e in events
+        )
```

---

#### File 3 (DELETE): `.claude/hooks/memory_retrieval.py`

Delete file. No Python callers exist. Was called from `.claude/hooks/archive/UserPromptSubmit.ps1` (archived S94).

Verify before deletion:
```bash
grep -r "memory_retrieval" .claude --include="*.py" | grep -v "archive/" | grep -v "memory_retrieval.py"
```
Expected: 0 matches (excluding the file itself and archive).

---

#### File 4 (DELETE): `.claude/hooks/reasoning_extraction.py`

Delete file. No Python callers exist. Was called from `.claude/hooks/archive/Stop.ps1` (archived S94). Current `stop.py` uses MemoryBridge.

Verify before deletion:
```bash
grep -r "reasoning_extraction" .claude --include="*.py" | grep -v "archive/" | grep -v "reasoning_extraction.py"
```
Expected: 0 matches.

---

#### File 5 (MODIFY): `.claude/hooks/README.md`

Remove the two entries from the File Structure section:

**Current Code (lines 195-197):**
```
├── memory_retrieval.py     # Memory context injection
├── reasoning_extraction.py # Learning extraction
├── # error_capture.py moved to .claude/lib/ (E2-130)
```

**Target Code:**
```
├── statusline.py           # Context budget tracking
├── # error_capture.py moved to .claude/lib/ (E2-130)
```

---

### Call Chain

```
user_prompt_submit.handle()
    |
    +-> _get_datetime_context()
    +-> _read_slim()
    +-> _get_session_number()
    +-> _get_working_item()
    +-> _get_session_duration()
    +-> _read_context_remaining()   # <-- kept (active)
    +-> _write_context_pct_to_slim()# <-- kept (active)
    [REMOVED: _refresh_slim_status, _get_vitals, _get_thresholds]
    +-> _get_session_state_warning()
    +-> _get_phase_contract()
    +-> _get_lifecycle_guidance()
    +-> _get_rfc2119_reminders()

pre_tool_use._check_scaffold_governance()
    |
    +-> [guard] if not command: return None
    [REMOVED: batch_work_bypass check]
    +-> scaffold_patterns check  # <-- now always enforced

pre_tool_use._check_path_governance()
    |
    +-> [guard] if not file_path: return None
    +-> [guard] if Path(file_path).exists(): return None  (edits to existing files allowed)
    [REMOVED: batch_work_bypass check]
    +-> governed_paths check  # <-- now always enforced

pre_tool_use._check_process_review_gate()
    |
    +-> read_events()
    +-> _read_session_id()  # <-- NEW: session-scope filter
    +-> any(type==ProcessReviewApproved AND session_id==current)
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| `_get_vitals` / `_get_thresholds` deletion vs. keeping body | Delete both function bodies | Both functions reference deprecated slim structure (milestone key format changed in E2.2). Neither has been called since S179/S259. Keeping the bodies creates a false promise that they can be re-enabled without redesign. |
| `_refresh_slim_status` deletion | Delete entire function | Only referenced inside the now-deleted disabled vitals block. No other callers exist. Deleting removes the haios_etl import dependency from user_prompt_submit. |
| Orphaned scripts: delete vs. move to archive | Delete both | Archive already exists for PowerShell era scripts. Python-era orphans have no historical value — logic is superseded by MemoryBridge. archive/ is for the PS1 migration, not for Python stubs. |
| Process review gate: session-scope via `_read_session_id()` | Import `_read_session_id` from governance_events | It's a private function in governance_events.py, but it's the canonical session-number reader used throughout the lib. Importing it avoids duplicating the session-file parsing logic. Fail-permissive: if `_read_session_id()` returns 0 (file missing), the gate may not fire — but that's acceptable given the fail-permissive stance of the gate. |
| Test for AC5 (pre-existing failures) | Verify green via full pytest run, no new test file changes | WORK-252 already fixed these. WORK-248's job is to confirm they remain green after the cleanup changes. |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `_read_session_id()` returns 0 (session file missing) | `has_approval` will be False (no event has session_id=0 for ProcessReviewApproved), gate blocks — fail-safe | Not directly tested; fail-permissive behavior documented |
| `.batch_work_bypass` file somehow still exists after cleanup | File is irrelevant — the check is deleted from the code. File presence has no effect. | Test 4 verifies code removed |
| `_check_process_review_gate` called when events file missing | `read_events()` returns [], `has_approval=False`, gate blocks (fail-safe; existing behavior unchanged) | Existing test coverage |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `_read_session_id` is a private function in governance_events | Low | It's used internally by `_append_event`. Importing it is consistent with how pre_tool_use already imports from governance_events (read_events). If it ever moves, the test catches it. |
| Deleting dead functions breaks some import-based test | Low | Test 3 explicitly checks the functions are GONE. Run full suite after each step. |
| Deleting orphaned scripts breaks memory_bridge.py reference | Low | grep confirms memory_bridge.py uses its own MCP-based retrieval, not memory_retrieval.py. |
| Process review gate over-blocks after session-scope | Low | If ProcessReviewApproved was logged in session 473 but gate runs in session 474, approval is invalid. This is correct and intentional behavior. Process-review-cycle must be run each session. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_hook_cleanup.py` with 6 tests. Tests should initially PASS for existing passing ACs but FAIL for items not yet removed (AC1: disabled blocks still present, AC2: bypass still present, AC3: files still exist, AC4: gate not scoped).
- **output:** Test file exists; Tests 1-5 fail (dead code still there), Test 6 fails (gate not scoped)
- **verify:** `pytest tests/test_hook_cleanup.py -v 2>&1 | grep -c "FAILED"` equals 6

### Step 2: AC1 — Remove disabled vitals/thresholds code (GREEN for Tests 1-3)
- **spec_ref:** Layer 1 > Design > File 1
- **input:** Step 1 complete (tests written)
- **action:** Edit user_prompt_submit.py — delete disabled Part 2 block (lines 98-104), disabled Part 3 block (lines 119-123), `_refresh_slim_status()` function, `_get_vitals()` function, `_get_thresholds()` function
- **output:** user_prompt_submit.py cleaned; Tests 1-3 pass
- **verify:** `pytest tests/test_hook_cleanup.py::test_vitals_block_not_in_handle tests/test_hook_cleanup.py::test_thresholds_block_not_in_handle tests/test_hook_cleanup.py::test_dead_functions_removed -v` exits 0

### Step 3: AC2 — Remove batch_work_bypass dead code (GREEN for Test 4)
- **spec_ref:** Layer 1 > Design > File 2 (batch_work_bypass sections)
- **input:** Step 2 complete
- **action:** Edit pre_tool_use.py — delete batch_work_bypass block from `_check_scaffold_governance()` and from `_check_path_governance()`
- **output:** pre_tool_use.py cleaned; Test 4 passes
- **verify:** `pytest tests/test_hook_cleanup.py::test_batch_bypass_removed -v` exits 0; `grep -c "batch_work_bypass" .claude/hooks/hooks/pre_tool_use.py` returns 0

### Step 4: AC3 — Delete orphaned hook scripts (GREEN for Test 5)
- **spec_ref:** Layer 1 > Design > Files 3-4
- **input:** Step 3 complete. First verify no live callers with grep.
- **action:** Delete `.claude/hooks/memory_retrieval.py` and `.claude/hooks/reasoning_extraction.py`; update `.claude/hooks/README.md` File Structure section
- **output:** Files gone; README updated; Test 5 passes
- **verify:** `pytest tests/test_hook_cleanup.py::test_orphaned_scripts_deleted -v` exits 0

### Step 5: AC4 — Session-scope process review gate (GREEN for Test 6)
- **spec_ref:** Layer 1 > Design > File 2 (process review gate section)
- **input:** Step 4 complete
- **action:** Edit `_check_process_review_gate()` in pre_tool_use.py — add `_read_session_id` import, add `current_session = _read_session_id()`, add `and e.get("session_id") == current_session` filter
- **output:** Gate is session-scoped; Test 6 passes
- **verify:** `pytest tests/test_hook_cleanup.py -v` exits 0, 6 passed

### Step 6: Full Suite Verification (AC5 confirmed)
- **spec_ref:** Ground Truth Verification > Tests
- **input:** Step 5 complete
- **action:** Run full pytest suite to confirm no regressions and AC5 pre-existing failures remain fixed
- **output:** All tests pass, 0 new failures
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows "passed" with 0 failed; `pytest tests/test_lib_status.py tests/test_manifest.py tests/test_plan_authoring_agent.py -v` exits 0

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_hook_cleanup.py -v` | 6 passed, 0 failed |
| `pytest tests/test_lib_status.py tests/test_manifest.py tests/test_plan_authoring_agent.py -v` | All passed, 0 failed (AC5 — pre-existing, already fixed by WORK-252) |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs Session 472 baseline (1833+) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| AC1: disabled vitals code removed | `grep -c "DISABLED Session 179" .claude/hooks/hooks/user_prompt_submit.py` | 0 |
| AC1: disabled thresholds code removed | `grep -c "DISABLED Session 259" .claude/hooks/hooks/user_prompt_submit.py` | 0 |
| AC1: dead _get_vitals removed | `grep -c "def _get_vitals" .claude/hooks/hooks/user_prompt_submit.py` | 0 |
| AC1: dead _get_thresholds removed | `grep -c "def _get_thresholds" .claude/hooks/hooks/user_prompt_submit.py` | 0 |
| AC1: dead _refresh_slim_status removed | `grep -c "def _refresh_slim_status" .claude/hooks/hooks/user_prompt_submit.py` | 0 |
| AC2: batch_work_bypass removed | `grep -c "batch_work_bypass" .claude/hooks/hooks/pre_tool_use.py` | 0 |
| AC3: memory_retrieval.py deleted | `test -f .claude/hooks/memory_retrieval.py && echo exists || echo gone` | gone |
| AC3: reasoning_extraction.py deleted | `test -f .claude/hooks/reasoning_extraction.py && echo exists || echo gone` | gone |
| AC4: gate uses session filter | `grep -c "_read_session_id" .claude/hooks/hooks/pre_tool_use.py` | 1 |
| AC5: test_manifest passes | `pytest tests/test_manifest.py -v` | passed |
| AC5: test_lib_status passes | `pytest tests/test_lib_status.py -v` | passed |
| AC5: test_plan_authoring_agent passes | `pytest tests/test_plan_authoring_agent.py -v` | passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No live Python callers of memory_retrieval | `grep -r "memory_retrieval" .claude --include="*.py" \| grep -v archive/` | 0 matches |
| No live Python callers of reasoning_extraction | `grep -r "reasoning_extraction" .claude --include="*.py" \| grep -v archive/` | 0 matches |
| No stale batch_work_bypass references | `grep -r "batch_work_bypass" . --include="*.py"` | 0 matches |
| hook_dispatcher unchanged | `grep "user_prompt_submit\|pre_tool_use\|post_tool_use\|stop" .claude/hooks/hook_dispatcher.py` | 4 matches (unchanged routing) |
| handle() still callable | `python -c "import sys; sys.path.insert(0, '.claude/hooks/hooks'); import user_prompt_submit; print('ok')"` | ok |

### Completion Criteria (DoD)

- [ ] All 6 tests in test_hook_cleanup.py pass
- [ ] tests/test_lib_status.py passes (AC5 confirmed)
- [ ] tests/test_manifest.py passes (AC5 confirmed)
- [ ] tests/test_plan_authoring_agent.py passes (AC5 confirmed)
- [ ] grep confirms 0 batch_work_bypass references in .py files
- [ ] grep confirms 0 dead function definitions in user_prompt_submit.py
- [ ] memory_retrieval.py and reasoning_extraction.py deleted
- [ ] _check_process_review_gate scoped to current session_id
- [ ] Full suite: 0 new failures vs Session 472 baseline
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/hooks/hooks/user_prompt_submit.py` (primary source)
- `.claude/hooks/hooks/pre_tool_use.py` (primary source)
- `.claude/hooks/memory_retrieval.py` (to be deleted)
- `.claude/hooks/reasoning_extraction.py` (to be deleted)
- `.claude/haios/lib/governance_events.py` (provides `_read_session_id` for AC4)
- Memory pattern mem:84334 — pure additive hook extension: standalone function + single call-site + fail-permissive
- Memory pattern mem:89597 — context display already removed from UserPromptSubmit (statusLine shows it)
- Memory pattern mem:87635 — user_prompt_submit.py was reading slim JSON up to 4 times per call (WORK-195 already fixed)
- WORK-252 (complete) — confirmed test_lib_status, test_manifest, test_plan_authoring_agent green

---
