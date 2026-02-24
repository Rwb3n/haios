---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-216
title: "Hook Output Trimming for Noise Reduction"
author: Hephaestus
lifecycle_phase: plan
session: 442
generated: 2026-02-24
last_updated: 2026-02-24T16:30:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-216/WORK.md"
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
# Implementation Plan: Hook Output Trimming for Noise Reduction

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add a module-level cache variable to `_get_phase_contract()` in `user_prompt_submit.py` that suppresses re-injection of the phase contract when the composite key `{active_cycle}/{current_phase}` is unchanged since the last injection, reducing per-prompt token cost from O(prompts_per_phase * phase_file_size) to O(1 * phase_file_size) per phase.

---

## Open Decisions

<!-- All decisions resolved — no operator_decisions in WORK.md frontmatter. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Cache storage mechanism | module-level variable vs state file | module-level variable | Hook process (`hook_dispatcher.py`) is long-lived per session — same Python process handles all tool calls. Module-level variable resets on new process (= new session). No file I/O, no new path config needed. Addresses A1 + A2 from critique. |
| Cache key composition | phase only vs active_cycle/current_phase | `active_cycle/current_phase` | Phase name alone (e.g., "DO") is ambiguous across different skills. Composite key distinguishes `implementation-cycle/DO` from `investigation-cycle/DO`. Addresses A3 from critique. |
| Session boundary handling | explicit SessionStart hook vs process restart | process restart (implicit) | No SessionStart hook exists for UserPromptSubmit. New session = new Claude Code process = module variable reset to None. Safe and zero-config. Addresses A2 from critique. |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 2 |

### Consumer Files

**SKIPPED:** No consumer files reference `_get_phase_contract()` directly — it is an internal function called only within the same module's `handle()`. No imports or call sites outside this file.

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_hooks.py` | test coverage — `TestSessionInjections` + new `TestPhaseContractCaching` class | 857–893 | UPDATE (add new test class) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_hooks.py` | UPDATE | Add `TestPhaseContractCaching` class with 4 tests |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files needed |
| Files to modify | 2 | `user_prompt_submit.py` (logic) + `test_hooks.py` (tests) |
| Tests to write | 4 | Test Files table |
| Total blast radius | 2 | Both files above |

---

## Layer 1: Specification

### Current State

```python
# .claude/hooks/hooks/user_prompt_submit.py — lines 266-309

def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
    is running, read and inject the current phase's contract file so the agent
    always has the behavioral contract in context (recovery after compaction).

    Phase files live at: .claude/skills/{cycle}/phases/{PHASE}.md

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    WORK-195: Accepts pre-parsed slim dict from handle(). No internal file read.

    Args:
        cwd: Working directory path
        slim: Pre-parsed haios-status-slim.json dict, or None if unavailable.

    Returns:
        Formatted phase contract string, or None if not applicable.
    """
    if not cwd:
        return None
    if slim is None:
        return None

    try:
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        phase_file = (
            Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        )
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None
```

**Behavior:** Reads and returns phase contract file content on every UserPromptSubmit call when an active cycle and phase exist.
**Problem:** Injects identical ~100+ line contract on every prompt during a single phase. O(prompts_per_phase) token cost per phase where content never changes.

### Desired State

```python
# .claude/hooks/hooks/user_prompt_submit.py — lines 266-322 (after change)

# Module-level cache: tracks last-injected phase contract key (WORK-216)
# Format: "{active_cycle}/{current_phase}" — reset to None on new Python process (= new session)
_LAST_INJECTED_KEY: Optional[str] = None


def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
    is running, read and inject the current phase's contract file so the agent
    always has the behavioral contract in context (recovery after compaction).

    WORK-216: Deduplication via module-level cache. Only injects on first prompt
    of session or phase transition. Within a single phase the contract is static
    so re-injection adds no value. ADR-048 compaction recovery is preserved:
    after compaction the module process may restart (new session = cache miss)
    or the phase may change (different key = cache miss).

    Phase files live at: .claude/skills/{cycle}/phases/{PHASE}.md

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    WORK-195: Accepts pre-parsed slim dict from handle(). No internal file read.

    Args:
        cwd: Working directory path
        slim: Pre-parsed haios-status-slim.json dict, or None if unavailable.

    Returns:
        Formatted phase contract string on first call for a given key, None on repeat.
    """
    global _LAST_INJECTED_KEY

    if not cwd:
        return None
    if slim is None:
        return None

    try:
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        cache_key = f"{active_cycle}/{current_phase}"

        # WORK-216: Skip re-injection when phase unchanged since last injection
        if cache_key == _LAST_INJECTED_KEY:
            return None

        phase_file = (
            Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        )
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        _LAST_INJECTED_KEY = cache_key
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None
```

**Behavior:** Reads and returns phase contract on first call for a given `active_cycle/current_phase` key; returns None on subsequent calls with the same key.
**Result:** Token cost reduced from O(prompts_per_phase * phase_file_size) to O(1 * phase_file_size) per phase. Phase transition or process restart (new session) automatically re-fires injection.

### Tests

#### Test 1: First Injection Fires
- **file:** `tests/test_hooks.py`
- **function:** `test_phase_contract_first_injection_fires()`
- **setup:** Import `user_prompt_submit` module; reset `user_prompt_submit._LAST_INJECTED_KEY = None`; create `tmp_path/.claude/skills/implementation-cycle/phases/DO.md` with content `"DO phase content"`; build `slim = {"session_state": {"active_cycle": "implementation-cycle", "current_phase": "DO"}}`
- **assertion:** `_get_phase_contract(str(tmp_path), slim)` is not None and `"DO phase content"` in result and `"--- Phase Contract: implementation-cycle/DO ---"` in result

#### Test 2: Repeat Injection Skipped (Same Key)
- **file:** `tests/test_hooks.py`
- **function:** `test_phase_contract_repeat_skipped()`
- **setup:** Same as Test 1; call `_get_phase_contract(str(tmp_path), slim)` once (first call)
- **assertion:** Second call to `_get_phase_contract(str(tmp_path), slim)` returns None

#### Test 3: Phase Transition Re-Fires
- **file:** `tests/test_hooks.py`
- **function:** `test_phase_contract_phase_transition_reinjected()`
- **setup:** Reset `_LAST_INJECTED_KEY = None`; create both `DO.md` and `CHECK.md` phase files; call first with `current_phase="DO"` (sets cache to `implementation-cycle/DO`)
- **assertion:** Call with `current_phase="CHECK"` returns non-None content (different cache key triggers injection)

#### Test 4: No Active Cycle Returns None (unchanged behavior)
- **file:** `tests/test_hooks.py`
- **function:** `test_phase_contract_no_active_cycle_returns_none()`
- **setup:** Reset `_LAST_INJECTED_KEY = None`; build `slim = {"session_state": {"active_cycle": None, "current_phase": None}}`
- **assertion:** `_get_phase_contract(str(tmp_path), slim)` returns None; `_LAST_INJECTED_KEY` remains None

### Design

#### File 1 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**Change 1 — Add module-level variable after imports (around line 19, after `from typing import Optional`):**

**Current Code (line 19):**
```python
from typing import Optional
```

**Target Code:**
```python
from typing import Optional

# Module-level cache: tracks last-injected phase contract key (WORK-216)
# Format: "{active_cycle}/{current_phase}" — reset to None on new Python process (= new session)
_LAST_INJECTED_KEY: Optional[str] = None
```

**Change 2 — Modify `_get_phase_contract()` function (lines 266-309):**

**Current Code (lines 266-309):**
```python
def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
    is running, read and inject the current phase's contract file so the agent
    always has the behavioral contract in context (recovery after compaction).

    Phase files live at: .claude/skills/{cycle}/phases/{PHASE}.md

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    WORK-195: Accepts pre-parsed slim dict from handle(). No internal file read.

    Args:
        cwd: Working directory path
        slim: Pre-parsed haios-status-slim.json dict, or None if unavailable.

    Returns:
        Formatted phase contract string, or None if not applicable.
    """
    if not cwd:
        return None
    if slim is None:
        return None

    try:
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        phase_file = (
            Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        )
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None
```

**Target Code:**
```python
def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
    is running, read and inject the current phase's contract file so the agent
    always has the behavioral contract in context (recovery after compaction).

    WORK-216: Deduplication via module-level cache. Only injects on first prompt
    of session or phase transition. Within a single phase the contract is static
    so re-injection adds no value. ADR-048 compaction recovery is preserved:
    after compaction the module process may restart (new session = cache miss)
    or the phase may change (different key = cache miss).

    Phase files live at: .claude/skills/{cycle}/phases/{PHASE}.md

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    WORK-195: Accepts pre-parsed slim dict from handle(). No internal file read.

    Args:
        cwd: Working directory path
        slim: Pre-parsed haios-status-slim.json dict, or None if unavailable.

    Returns:
        Formatted phase contract string on first call for a given key, None on repeat.
    """
    global _LAST_INJECTED_KEY

    if not cwd:
        return None
    if slim is None:
        return None

    try:
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        cache_key = f"{active_cycle}/{current_phase}"

        # WORK-216: Skip re-injection when phase unchanged since last injection
        if cache_key == _LAST_INJECTED_KEY:
            return None

        phase_file = (
            Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        )
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        _LAST_INJECTED_KEY = cache_key
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None
```

**Diff:**
```diff
+# Module-level cache: tracks last-injected phase contract key (WORK-216)
+# Format: "{active_cycle}/{current_phase}" — reset to None on new Python process (= new session)
+_LAST_INJECTED_KEY: Optional[str] = None
+

 def _get_phase_contract(cwd: str, slim: Optional[dict] = None) -> Optional[str]:
     """
-    Inject current phase's behavioral contract from phase file.
-
-    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
-    is running, read and inject the current phase's contract file so the agent
-    always has the behavioral contract in context (recovery after compaction).
+    ... (docstring updated with WORK-216 note) ...
-    Returns:
-        Formatted phase contract string, or None if not applicable.
+    Returns:
+        Formatted phase contract string on first call for a given key, None on repeat.
     """
+    global _LAST_INJECTED_KEY
+
     if not cwd:
         return None
     ...
         if not active_cycle or not current_phase:
             return None

+        cache_key = f"{active_cycle}/{current_phase}"
+
+        # WORK-216: Skip re-injection when phase unchanged since last injection
+        if cache_key == _LAST_INJECTED_KEY:
+            return None
+
         phase_file = (
             Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
         )
         if not phase_file.exists():
             return None

         content = phase_file.read_text(encoding="utf-8")
-        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
+        _LAST_INJECTED_KEY = cache_key
+        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
```

### Call Chain

```
handle()
    |
    +-> _read_slim(cwd)           # Returns slim dict
    |
    +-> _get_phase_contract(cwd, slim)    # <-- MODIFIED
    |       Checks: _LAST_INJECTED_KEY == cache_key?
    |       If YES: Returns None (suppressed)
    |       If NO:  Reads phase file, updates _LAST_INJECTED_KEY, returns content
    |       Returns: Optional[str]
    |
    +-> output_parts.append(phase_contract)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module-level variable vs state file | Module-level `_LAST_INJECTED_KEY: Optional[str] = None` | Hook process is long-lived within a session (same Python process handles all `UserPromptSubmit` calls). Variable resets on process restart = session boundary. Zero file I/O, no new path config required. Simpler than file-based approach. |
| Cache key as `active_cycle/current_phase` | Composite string `f"{active_cycle}/{current_phase}"` | Phase name alone is ambiguous ("DO" appears in multiple skills). Composite distinguishes `implementation-cycle/DO` from `investigation-cycle/DO`. Matches A3 critique finding. |
| Global mutation pattern | `global _LAST_INJECTED_KEY` declaration inside function | Standard Python pattern for module-level mutable state. Explicit — no magic. Test-friendly: tests reset by setting `module._LAST_INJECTED_KEY = None` directly. |
| ADR-048 compaction safety | Suppression is safe mid-phase | ADR-048 justifies re-injection for compaction recovery. Within a single phase the contract content is static. If compaction occurs mid-phase, Claude retains the contract from initial injection (compaction preserves recent context). Cross-session restart = process restart = cache miss = re-injection fires. |
| Exception path leaves cache unchanged | `except Exception: return None` path does not set `_LAST_INJECTED_KEY` | If phase file read fails, cache key is not stored. Next call retries read — correct fail-permissive behavior inherited from existing design. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| First call of session (key=None) | `None != "impl-cycle/DO"` → injection fires | Test 1 |
| Same phase, second call | `"impl-cycle/DO" == "impl-cycle/DO"` → returns None | Test 2 |
| Phase transition (DO → CHECK) | `"impl-cycle/DO" != "impl-cycle/CHECK"` → injection fires | Test 3 |
| No active cycle | Early return None before cache check | Test 4 |
| Phase file missing | Phase file check (`if not phase_file.exists()`) fires before cache update — cache NOT set | (covered by existing fall-permissive behavior) |
| Exception in try block | `except Exception: return None` — cache NOT updated, next call retries | (existing behavior preserved) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Test isolation: module-level variable leaks across test functions | M | Each test resets `user_prompt_submit._LAST_INJECTED_KEY = None` in setup. Pattern established in `test_hooks.py` (e.g., `TestSessionStateWarning` already imports functions directly). |
| Python module import caching means hook process IS long-lived | L | Confirmed: `hook_dispatcher.py` imports `user_prompt_submit` once per process. Module-level variable persists correctly. |
| Mid-phase compaction loses contract from context | L | ADR-048 analysis: Claude Code compaction preserves recent context including the injected contract. New session = new process = cache miss = re-injection. Risk is low. |
| cycle_name or phase_name contains `/` character | L | Existing slim dict values (`active_cycle`, `current_phase`) are controlled strings from HAIOS skill names and phase names. Neither contains `/`. No sanitization needed. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add `TestPhaseContractCaching` class to `tests/test_hooks.py` with 4 tests (Test 1–4 from Layer 1 > Tests). Each test imports `user_prompt_submit` as module, resets `_LAST_INJECTED_KEY = None`, creates tmp phase files as needed.
- **output:** 4 new tests exist, all fail (function has no caching logic yet)
- **verify:** `pytest tests/test_hooks.py::TestPhaseContractCaching -v 2>&1 | grep -c "FAILED\|ERROR"` equals 4 (or close — Test 4 may already pass since no active cycle behavior is unchanged)

### Step 2: Implement Caching Logic (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Apply two changes to `.claude/hooks/hooks/user_prompt_submit.py`: (1) add `_LAST_INJECTED_KEY: Optional[str] = None` after line 19 (`from typing import Optional`); (2) modify `_get_phase_contract()` to add `global _LAST_INJECTED_KEY`, composite key construction, cache check, and cache update before return.
- **output:** All 4 new tests pass
- **verify:** `pytest tests/test_hooks.py::TestPhaseContractCaching -v` exits 0, `4 passed` in output

### Step 3: Regression Check
- **spec_ref:** Layer 0 > Primary Files
- **input:** Step 2 complete (new tests green)
- **action:** Run full test suite to verify no existing tests broken
- **output:** All pre-existing tests continue to pass
- **verify:** `pytest tests/test_hooks.py -v` — count of passing tests equals baseline + 4; `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_hooks.py::TestPhaseContractCaching -v` | 4 passed, 0 failed |
| `pytest tests/test_hooks.py -v` | 0 new failures vs pre-implementation baseline |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures across full suite |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| `_get_phase_contract()` tracks last-injected phase and skips re-injection when unchanged | `grep "_LAST_INJECTED_KEY" .claude/hooks/hooks/user_prompt_submit.py` | 3+ matches (declaration + global statement + assignment) |
| Phase contract injected on first prompt of session and on phase transitions only | `pytest tests/test_hooks.py::TestPhaseContractCaching -v` | 4 passed |
| Unit tests covering: first injection fires, repeat injection skipped, phase change re-fires | `pytest tests/test_hooks.py::TestPhaseContractCaching -v` | 4 passed |
| Existing hook output (date, session, context, warnings) unchanged | `pytest tests/test_hooks.py -v` | All pre-existing tests pass |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No other callers of `_get_phase_contract` outside module | `grep "_get_phase_contract" .claude/hooks/hooks/ -r` | 2 matches (definition + call in handle()) |
| Module-level variable declared | `grep "_LAST_INJECTED_KEY" .claude/hooks/hooks/user_prompt_submit.py` | 3+ matches |
| Cache check present | `grep "cache_key == _LAST_INJECTED_KEY" .claude/hooks/hooks/user_prompt_submit.py` | 1 match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale references (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- ADR-048: Progressive Contracts — Phase-Per-File Skill Fracturing (belt-and-suspenders justification)
- WORK-195: Slim dict pre-parsing pattern (pass slim once, distribute to functions)
- WORK-215: `_read_session_id()` pattern in `governance_events.py` (session file reading — sibling reference)
- WORK-212: Parent — Mechanical Phase Delegation to Haiku Subagents
- REQ-OBSERVE-002: Session state visible via hooks

---
