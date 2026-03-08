---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-03-08
backlog_id: WORK-253
title: "Mechanical Retro-Before-Close Enforcement"
author: Hephaestus
lifecycle_phase: plan
session: 479
generated: 2026-03-08
last_updated: 2026-03-08T12:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-253/WORK.md"
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
# Implementation Plan: Mechanical Retro-Before-Close Enforcement

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification. -->

---

## Goal

Add a `retro_gate.py` lib module and wire it into the PreToolUse hook so that any `close-work-cycle` skill invocation is blocked with a clear message when no `RetroCycleCompleted` event exists for the current work item in the current session.

---

## Open Decisions

No operator decisions were specified in WORK.md. No decisions blocked.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | — | — | No operator decisions in WORK.md |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/retro_gate.py` | CREATE | 2 |
| `.claude/hooks/hooks/pre_tool_use.py` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/hooks/hooks/pre_tool_use.py` | imports retro_gate / calls check_retro_gate | new section | UPDATE (already in Primary) |

No other files import `pre_tool_use.py` or `retro_gate.py` — hook is invoked by Claude Code runtime, not by application code.

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_retro_gate.py` | CREATE | New test file for retro_gate.py |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 2 | retro_gate.py + test_retro_gate.py |
| Files to modify | 1 | pre_tool_use.py (hook wiring) |
| Tests to write | 5 | Test Files table |
| Total blast radius | 3 | 2 new + 1 modified |

---

## Layer 1: Specification

### Current State

```python
# .claude/hooks/hooks/pre_tool_use.py — _check_governed_activity(), lines 186-214
# When skill_name matches a ceremony skill:
#   1. _check_skill_restriction()
#   2. _check_ceremony_contract()    # validates input_contract fields
#   3. _check_critique_injection()   # injects critique checklist/subagent directive
# No check for retro-cycle completion before close-work-cycle invocation.
```

**Behavior:** The PreToolUse hook checks ceremony contract (input fields present) and critique injection when a Skill tool is invoked, but does NOT verify that retro-cycle ran before close-work-cycle.

**Problem:** Agents can invoke `close-work-cycle` without first running `retro-cycle`, silently losing session learnings (mem:89173, mem:89182).

### Desired State

```python
# .claude/hooks/hooks/pre_tool_use.py — _check_governed_activity(), after _check_ceremony_contract()

# 4b-NEW: Retro gate (WORK-253) — must appear between ceremony_contract and critique injection
retro_result = _check_retro_gate(skill_name, tool_input)
if retro_result:
    ctx = _build_additional_context(state, layer)
    retro_result["hookSpecificOutput"]["additionalContext"] = ctx
    return retro_result
```

```python
# .claude/hooks/hooks/pre_tool_use.py — new helper function

def _check_retro_gate(skill_name: str, tool_input: dict) -> Optional[dict]:
    """
    Block close-work-cycle invocation if retro-cycle not completed this session (WORK-253).

    Returns deny response if retro gate fails, None otherwise.
    Fail-permissive: if events file unreadable, returns None (WARN logged, not block).
    """
    if skill_name not in ("close-work-cycle", "close"):
        return None

    try:
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from retro_gate import check_retro_gate

        work_id = _extract_ceremony_inputs(tool_input).get("work_id", "")
        result = check_retro_gate(work_id)

        if result["blocked"]:
            return _deny(result["reason"])
        if result.get("warning"):
            return _allow_with_warning(result["warning"])
    except Exception:
        pass  # Fail-permissive

    return None
```

```python
# .claude/haios/lib/retro_gate.py — new lib module

"""
Retro-before-close gate (WORK-253).

Checks governance-events.jsonl for RetroCycleCompleted event matching
work_id in the current session. Called by PreToolUse hook before
close-work-cycle is allowed to proceed.

Pattern: retro_scale.py (fail-permissive, _default_project_root,
pure function, no exceptions escape).
"""
import json
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def _read_session_id(project_root: Path) -> int:
    """Read current session number from .claude/session.

    Returns session number as int, or 0 if file missing/unreadable.
    Pattern: governance_events._read_session_id().
    """
    try:
        session_file = project_root / ".claude" / "session"
        if not session_file.exists():
            return 0
        for line in session_file.read_text(encoding="utf-8").splitlines():
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


def check_retro_gate(
    work_id: str,
    project_root: Optional[Path] = None,
) -> dict:
    """Check if retro-cycle completed for work_id in the current session.

    Scans governance-events.jsonl for a RetroCycleCompleted event
    matching the given work_id and current session_id.

    Args:
        work_id: Work item ID to check (e.g., "WORK-253"). May be empty
                 string if not parseable from Skill tool args.
        project_root: Project root. Defaults to derived path.

    Returns:
        dict with keys:
          - blocked: bool — True if close should be denied
          - reason: str — denial message (when blocked=True)
          - warning: str — warning message (when blocked=False but uncertain)
          - retro_found: bool — True if RetroCycleCompleted found

    Never raises — all exceptions handled fail-permissive.
    Fail-permissive means: if events file unreadable, returns
    blocked=False with a warning (WARN, not BLOCK).
    """
    try:
        root = project_root or _default_project_root()
        events_file = root / ".claude" / "haios" / "governance-events.jsonl"
        current_session = _read_session_id(root)

        # Edge case: work_id not parseable from tool args
        if not work_id:
            return {
                "blocked": False,
                "reason": "",
                "warning": (
                    "WARNING: close-work-cycle invoked but work_id could not be determined. "
                    "Verify retro-cycle ran before closing. (WORK-253)"
                ),
                "retro_found": False,
            }

        # Read events file
        if not events_file.exists():
            # Fail-permissive: no events file → warn but don't block
            return {
                "blocked": False,
                "reason": "",
                "warning": (
                    f"WARNING: governance-events.jsonl not found. "
                    f"Cannot verify retro-cycle ran for {work_id}. "
                    "Ensure retro-cycle completes before /close. (WORK-253)"
                ),
                "retro_found": False,
            }

        retro_found = False
        for line in events_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if (
                event.get("type") == "RetroCycleCompleted"
                and event.get("work_id") == work_id
            ):
                event_session = event.get("session_id") or event.get("session")
                # Match: same session, or no session tracking on event (legacy)
                if event_session is None or event_session == current_session:
                    retro_found = True
                    break

        if retro_found:
            return {
                "blocked": False,
                "reason": "",
                "warning": "",
                "retro_found": True,
            }

        # No RetroCycleCompleted found for this work_id in this session
        return {
            "blocked": True,
            "reason": (
                f"BLOCKED: retro-cycle must complete before closing {work_id}. "
                "Run: Skill(skill='retro-cycle') with work_id='{work_id}'. "
                "Retro captures session learnings — skipping loses them permanently. "
                "(WORK-253, mem:89182)"
            ),
            "warning": "",
            "retro_found": False,
        }

    except Exception:
        # Fail-permissive: any unexpected error → warn but don't block
        return {
            "blocked": False,
            "reason": "",
            "warning": (
                f"WARNING: retro gate check failed for {work_id}. "
                "Verify retro-cycle ran before closing. (WORK-253)"
            ),
            "retro_found": False,
        }
```

**Behavior:** PreToolUse hook blocks `close-work-cycle` (and `close`) skill invocations when no `RetroCycleCompleted` event exists for the current work_id in the current session. Warns (does not block) when events file is unreadable or work_id is unknown.

**Result:** Agents cannot accidentally skip retro-cycle; learnings are preserved mechanically, not by convention.

### Tests

#### Test 1: Block when no retro event exists
- **file:** `tests/test_retro_gate.py`
- **function:** `test_check_retro_gate_blocks_when_no_retro()`
- **setup:** Write events file with `SessionStarted` for session 479 but NO `RetroCycleCompleted` for WORK-253. Write `.claude/session` with `479`.
- **assertion:** `check_retro_gate("WORK-253", project_root=tmp_path)["blocked"] is True` and `reason` contains "retro-cycle must complete"

#### Test 2: Allow when retro completed this session
- **file:** `tests/test_retro_gate.py`
- **function:** `test_check_retro_gate_allows_when_retro_completed()`
- **setup:** Write events file with `RetroCycleCompleted` for WORK-253 with `session_id: 479`. Write `.claude/session` with `479`.
- **assertion:** `check_retro_gate("WORK-253", project_root=tmp_path)["blocked"] is False` and `retro_found is True`

#### Test 3: Fail-permissive when events file missing
- **file:** `tests/test_retro_gate.py`
- **function:** `test_check_retro_gate_warns_when_events_file_missing()`
- **setup:** tmp_path with no governance-events.jsonl at all. Write `.claude/session` with `479`.
- **assertion:** `result["blocked"] is False` and `result["warning"]` contains "governance-events.jsonl not found"

#### Test 4: Warn when work_id is empty string
- **file:** `tests/test_retro_gate.py`
- **function:** `test_check_retro_gate_warns_when_work_id_empty()`
- **setup:** Any valid tmp_path with events file present.
- **assertion:** `check_retro_gate("", project_root=tmp_path)["blocked"] is False` and `result["warning"]` contains "work_id could not be determined"

#### Test 5: Block ignores retro from a different session
- **file:** `tests/test_retro_gate.py`
- **function:** `test_check_retro_gate_blocks_when_retro_from_different_session()`
- **setup:** Write events file with `RetroCycleCompleted` for WORK-253 with `session_id: 400` (prior session). Write `.claude/session` with `479`.
- **assertion:** `check_retro_gate("WORK-253", project_root=tmp_path)["blocked"] is True`

### Design

#### File 1 (NEW): `.claude/haios/lib/retro_gate.py`

Complete implementation is in Desired State above — copy verbatim to the file. The module exports one public function: `check_retro_gate(work_id, project_root)`.

Key implementation notes:
- Path anchored from `__file__` (not `cwd`) — same as `retro_scale.py`, `critique_injector.py`
- Session matching: check `session_id` field first (modern events), fall back to `session` field (retro-cycle uses `session` not `session_id` per observed events), accept event if neither field present (legacy events without session tracking)
- Events read line-by-line with `json.loads()` per line — same as `retro_scale.py`
- Import pattern from sibling `governance_events.py`: no relative imports, bare `from governance_events import ...` with `sys.path` insertion

#### File 2 (MODIFY): `.claude/hooks/hooks/pre_tool_use.py`

**Location:** `_check_governed_activity()` function, in the `skill-invoke` branch, after `_check_ceremony_contract()` call (lines 196-200), before `_check_critique_injection()` call (lines 202-215).

**Current Code:**
```python
# 4b. Ceremony contract validation (WORK-114)
# Note: if ceremony contract fires, its early-return skips critique injection.
# Acceptable: no ceremony-registered skills are in TRANSITION_SKILLS (WORK-169).
ceremony_result = _check_ceremony_contract(skill_name, tool_input)
if ceremony_result:
    # Merge state context into ceremony result
    ctx = _build_additional_context(state, layer)
    ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
    return ceremony_result

# 4c. Critique injection (WORK-169)
critique_ctx = _check_critique_injection(skill_name)
```

**Target Code:**
```python
# 4b. Ceremony contract validation (WORK-114)
# Note: if ceremony contract fires, its early-return skips critique injection.
# Acceptable: no ceremony-registered skills are in TRANSITION_SKILLS (WORK-169).
ceremony_result = _check_ceremony_contract(skill_name, tool_input)
if ceremony_result:
    # Merge state context into ceremony result
    ctx = _build_additional_context(state, layer)
    ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
    return ceremony_result

# 4b-NEW. Retro gate (WORK-253) — block close-work-cycle if retro not completed
retro_result = _check_retro_gate(skill_name, tool_input)
if retro_result:
    ctx = _build_additional_context(state, layer)
    retro_result["hookSpecificOutput"]["additionalContext"] = ctx
    return retro_result

# 4c. Critique injection (WORK-169)
critique_ctx = _check_critique_injection(skill_name)
```

**Also add new helper function** `_check_retro_gate()` to `pre_tool_use.py` (implementation in Desired State above). Place it in the `# =============================================================================` section grouping with other skill-invoke helpers, after `_check_critique_injection()` definition (end of file).

**Diff (inline section addition):**
```diff
         return ceremony_result

+        # 4b-NEW. Retro gate (WORK-253) — block close-work-cycle if retro not completed
+        retro_result = _check_retro_gate(skill_name, tool_input)
+        if retro_result:
+            ctx = _build_additional_context(state, layer)
+            retro_result["hookSpecificOutput"]["additionalContext"] = ctx
+            return retro_result
+
         # 4c. Critique injection (WORK-169)
```

### Call Chain

```
Claude Code runtime (Skill tool invoked)
    |
    +-> PreToolUse hook → handle()
    |       |
    |       +-> _check_governed_activity()   # E2.4 CH-004
    |               |
    |               +-> primitive == "skill-invoke"?
    |                       |
    |                       +-> _check_skill_restriction()
    |                       +-> _check_ceremony_contract()   # WORK-114
    |                       +-> _check_retro_gate()          # WORK-253 (NEW)
    |                       |       |
    |                       |       +-> check_retro_gate()   # lib/retro_gate.py
    |                       |               |
    |                       |               +-> reads governance-events.jsonl
    |                       |               +-> reads .claude/session
    |                       |               Returns: {blocked, reason, warning, retro_found}
    |                       |
    |                       +-> _check_critique_injection()  # WORK-169
    |
    +-> Returns: deny (retro missing) | allow (retro found or fail-permissive)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Logic in lib/, wiring in hook | `retro_gate.py` in lib/, `_check_retro_gate()` in hook | mem:88010: portable lib vs hook-specific wiring. Testable without hook infrastructure. Pattern: retro_scale.py, critique_injector.py |
| Orthogonal check function | `_check_retro_gate()` not folded into `_check_ceremony_contract()` | mem:88837: _check_tool_gate orthogonal to ceremony_context. Avoids coupling two governance concerns. Follows pattern of `_check_critique_injection()` as independent helper. |
| Fail-permissive (warn, not block) on IO errors | Return `blocked=False` with warning when events file unreadable | Gate failure must not block all closes. The governance problem (skipping retro) is worse than occasional unverified close on infra failure. Pattern matches all other hook checks. |
| Session-scoped check | Match `session_id` OR `session` field on RetroCycleCompleted | RetroCycleCompleted events use `session` field (observed in governance-events.jsonl lines 15310); `_append_event()` injects `session_id`. Both fields checked for compatibility. |
| Intercept skill name "close-work-cycle" | Not "close" command | The Skill() tool is invoked with `skill="close-work-cycle"`. The `/close` command name does not appear as `tool_name`. Checked via `skill_name in ("close-work-cycle", "close")` for forward compatibility. |
| Block position: after ceremony_contract, before critique | Between 4b and 4c in `_check_governed_activity()` | Ceremony contract validates inputs first (fast fail on missing work_id). Retro gate needs work_id from `_extract_ceremony_inputs()`. Critique injection is irrelevant if blocked. |
| No new event type logged | Use existing `_deny()` / `_allow_with_warning()` helpers | These already call `_log_violation()` → `log_gate_violation()`. Gate violation log provides audit trail without new event type. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| work_id not parseable from Skill args | Return `blocked=False`, warning message | Test 4 |
| governance-events.jsonl does not exist | Return `blocked=False`, warning message | Test 3 |
| RetroCycleCompleted exists from prior session | Treat as not found (session-scoped) → block | Test 5 |
| RetroCycleCompleted has no session field (legacy) | Accept as valid (session=None branch) | Covered by Test 2 variant |
| close-work-cycle not the skill being invoked | Return `None` immediately (fast path) | Implicit in all non-close tests |
| Events file has malformed JSON lines | Skip line, continue scanning | Covered by retro_scale.py pattern |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook path import fails (sys.path not set) | M | Same `lib_dir = Path(__file__).parent...` pattern as all existing hooks. Try/except wraps entire `_check_retro_gate()` body → fail-permissive. |
| retro-cycle logs event with `session` field, hook reads `session_id` | H | Observed events use both `session` and `session_id` (lines 15310 vs 16423). Gate checks both fields: `event_session = event.get("session_id") or event.get("session")`. |
| Agents call `Skill(skill="close")` not `close-work-cycle` | M | Both checked in skill_name filter. Unlikely in practice (SKILL.md uses "close-work-cycle") but safe. |
| False positive: retro from DIFFERENT work_id in same session | L | Filter includes `work_id == event.get("work_id")`. Only exact match accepted. |
| RetroCycleSkipped escape hatch — retro skipped deliberately | M | `RetroCycleSkipped` is a different event type. If retro was skipped, gate will block. Operator should use `--skip-retro` workflow; if that also sets a `RetroCycleCompleted`, no issue. If not, operator must close via different path. Acceptable trade-off: retro skip is escape hatch, not normal path. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_retro_gate.py` from Layer 1 Tests section. Import `check_retro_gate` from `retro_gate` using sys.path insertion to `.claude/haios/lib`. Write all 5 test functions with tmp_path fixtures. Do NOT create retro_gate.py yet.
- **output:** `tests/test_retro_gate.py` exists, all 5 tests fail with `ModuleNotFoundError` or `ImportError`
- **verify:** `pytest tests/test_retro_gate.py -v 2>&1 | grep -c "ERROR\|FAILED"` equals 5

### Step 2: Implement retro_gate.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/retro_gate.py` with exact implementation from Desired State section. Use verbatim code — no paraphrasing.
- **output:** All 5 tests pass
- **verify:** `pytest tests/test_retro_gate.py -v` exits 0, `5 passed` in output

### Step 3: Wire hook (INTEGRATE)
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 2 complete (retro_gate.py tests green)
- **action:** Edit `.claude/hooks/hooks/pre_tool_use.py`:
  1. Add `_check_retro_gate()` helper function after `_check_critique_injection()` definition
  2. Insert call to `_check_retro_gate()` in `_check_governed_activity()` between ceremony_contract block and critique injection block (add 4b-NEW comment block)
- **output:** Hook calls `_check_retro_gate()` for every skill-invoke tool use
- **verify:** `grep "_check_retro_gate" .claude/hooks/hooks/pre_tool_use.py | wc -l` returns 2 (one def, one call)

### Step 4: Update _infer_gate_id
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 3 complete
- **action:** Add retro gate ID to `_infer_gate_id()` in pre_tool_use.py so gate violations are correctly labelled. Add: `if "retro-cycle" in reason_lower or "retro gate" in reason_lower: return "retro_gate"`
- **output:** Gate violations from retro_gate are logged with `gate_id: "retro_gate"` not `"unknown_gate"`
- **verify:** `grep "retro_gate" .claude/hooks/hooks/pre_tool_use.py` returns 1 match

### Step 5: Run full test suite
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Steps 1–4 complete
- **action:** Run full pytest suite to confirm no regressions
- **output:** All prior passing tests still pass; 5 new tests pass
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures vs pre-implementation baseline

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_retro_gate.py -v` | 5 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs pre-implementation baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| AC1: PreToolUse blocks /close if no retro | `grep "_check_retro_gate" .claude/hooks/hooks/pre_tool_use.py` | 2+ matches (def + call) |
| AC2: Check governance-events.jsonl for event | `grep "RetroCycleCompleted" .claude/haios/lib/retro_gate.py` | 1+ match |
| AC3: Prevents skipped retro pattern | `pytest tests/test_retro_gate.py::test_check_retro_gate_blocks_when_no_retro -v` | 1 passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| retro_gate.py in lib/ | `ls .claude/haios/lib/retro_gate.py` | file exists |
| Hook imports retro_gate via lib_dir | `grep "from retro_gate import" .claude/hooks/hooks/pre_tool_use.py` | 1 match |
| No stale references | `grep "_check_tool_gate" .claude/hooks/hooks/pre_tool_use.py` | 0 matches (avoided per mem:88837) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists — pre_tool_use.py calls _check_retro_gate()
- [ ] No stale references
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/hooks/hooks/pre_tool_use.py` — existing hook, wiring target
- `.claude/haios/lib/retro_scale.py` — sibling lib module pattern (fail-permissive, _default_project_root)
- `.claude/haios/lib/critique_injector.py` — sibling lib module pattern (orthogonal check)
- `.claude/haios/lib/governance_events.py` — event log reader pattern (read_events, _read_session_id)
- `.claude/skills/close-work-cycle/SKILL.md` — skill being gated
- `.claude/skills/retro-cycle/SKILL.md` — source of RetroCycleCompleted events
- `.claude/haios/config/haios.yaml` — governance_events path: `.claude/haios/governance-events.jsonl`
- mem:89173 — gap: no mechanical enforcement of retro-before-close
- mem:89182 — directive: enforce mechanically
- mem:88837 — pattern: orthogonal checks, avoid coupling governance concerns
- mem:89698 — pattern: PreToolUse hook for gate enforcement (critique-agent)
- REQ-CEREMONY-001 — ceremony contract requirements

---
