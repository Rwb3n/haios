---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-219
title: "Extract State Management Abstractions"
author: Hephaestus
lifecycle_phase: plan
session: 450
generated: 2026-02-25
last_updated: 2026-02-25T10:41:26

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-219/WORK.md"
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
# Implementation Plan: Extract State Management Abstractions

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Extract 4 inline-JSON justfile recipes into testable lib/ functions (`cycle_state.set_cycle_state`, `cycle_state.clear_cycle_state`, `cycle_state.set_active_queue`, `session_mgmt.start_session`) so they can be called from Python code and wrapped as MCP tools in WORK-220.

---

## Open Decisions

<!-- No operator_decisions in WORK.md frontmatter — none required for this work item. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| clear_cycle_state ownership | session_end_actions owns it / cycle_state owns it | cycle_state.py owns canonical impl | session_end_actions is Stop-hook context; cycle_state.py is the natural home for all session_state mutations. session_end_actions.clear_cycle_state delegates to cycle_state.clear_cycle_state. |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/cycle_state.py` | MODIFY | 2 |
| `.claude/haios/lib/session_mgmt.py` | CREATE | 2 |
| `.claude/haios/lib/session_end_actions.py` | MODIFY | 2 |
| `justfile` | MODIFY | 2 |

### Consumer Files

<!-- Files that import or call the new functions -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `justfile` | calls set-cycle, clear-cycle, set-queue, session-start recipes | 300, 310-312, 321, 326 | UPDATE — replace inline Python with lib/ calls |
| `.claude/haios/lib/session_end_actions.py` | owns `clear_cycle_state()` | 78-108 | UPDATE — delegate to cycle_state.clear_cycle_state |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_cycle_state_mgmt.py` | CREATE | New test file for set_cycle_state, clear_cycle_state, set_active_queue |
| `tests/test_session_mgmt.py` | CREATE | New test file for start_session |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 3 | session_mgmt.py, test_cycle_state_mgmt.py, test_session_mgmt.py |
| Files to modify | 3 | cycle_state.py, session_end_actions.py, justfile |
| Tests to write | 8 | 5 for cycle_state functions, 3 for session_mgmt |
| Total blast radius | 7 | Sum of all unique files above |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

```python
# justfile:310 — set-cycle recipe (inline Python)
@python -c "import json; from datetime import datetime; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']={'active_cycle':'{{cycle}}','current_phase':'{{phase}}','work_id':'{{work_id}}','entered_at':datetime.now().isoformat()}; json.dump(d,open(p,'w'),indent=4); print(f'Set: {{cycle}}/{{phase}}/{{work_id}}')"
@python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from cycle_state import sync_work_md_phase; sync_work_md_phase('{{work_id}}','{{phase}}')" 2>/dev/null || true
@python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from governance_events import log_phase_transition; log_phase_transition('{{phase}}','{{work_id}}','Hephaestus')" 2>/dev/null || true

# justfile:321 — clear-cycle recipe (inline Python)
@python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']={'active_cycle':None,'current_phase':None,'work_id':None,'entered_at':None,'active_queue':None,'phase_history':[]}; json.dump(d,open(p,'w'),indent=4); print('Cleared session_state')"

# justfile:326 — set-queue recipe (inline Python)
@python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']['active_queue']='{{queue_name}}'; json.dump(d,open(p,'w'),indent=4); print(f'Set queue: {{queue_name}}')"

# justfile:300 — session-start recipe (inline Python)
@python -c "import json,os,sys; sys.path.insert(0,'.claude/haios/lib'); from governance_events import log_session_start; from session_event_log import reset_log; sf='.claude/session'; jf='.claude/haios-status.json'; s={{session}}; lines=open(sf).readlines() if os.path.exists(sf) else []; hdr=[l for l in lines if l.startswith('#')]; open(sf,'w').write(''.join(hdr)+str(s)+chr(10)); j=json.load(open(jf)) if os.path.exists(jf) else {}; j['session_delta']={'current_session':s,'prior_session':s-1}; json.dump(j,open(jf,'w'),indent=2); log_session_start(s,'Hephaestus'); reset_log(); print(f'Session {s} start logged')"
```

**Behavior:** All 4 operations are implemented as inline Python one-liners inside justfile recipes. They use raw `json.load(open(p))` calls with hardcoded relative paths that depend on CWD being the project root.

**Problem:** No Python call site exists — impossible to call from MCP tools (WORK-220) or from tests. No error handling. Hardcoded relative paths. The `set-cycle` recipe also has no `phase_history` or `active_queue` in the written dict (4-field schema, while 6-field is the standard).

**Note on clear_cycle_state:** `session_end_actions.clear_cycle_state` (lines 78-108) already implements the same logic as `clear-cycle` justfile recipe. The plan is to move canonical ownership to `cycle_state.py` and have `session_end_actions.clear_cycle_state` delegate to it.

### Desired State

```python
# .claude/haios/lib/cycle_state.py — additions at end of file

def set_cycle_state(
    cycle: str,
    phase: str,
    work_id: str,
    project_root: Optional[Path] = None,
) -> bool:
    """Set session_state in haios-status-slim.json for a new cycle phase.

    Writes the 6-field session_state schema, then calls sync_work_md_phase
    and log_phase_transition (both fail-permissive).

    Args:
        cycle: Lifecycle cycle name (e.g., "implementation-cycle")
        phase: Phase name (e.g., "DO", "PLAN")
        work_id: Work item ID (e.g., "WORK-219")
        project_root: Project root. Defaults to derived path.

    Returns:
        True if session_state was written, False on error/missing file.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return False

        data = json.loads(slim_file.read_text(encoding="utf-8"))
        now = datetime.now().isoformat()
        data["session_state"] = {
            "active_cycle": cycle,
            "current_phase": phase,
            "work_id": work_id,
            "entered_at": now,
            "active_queue": None,
            "phase_history": [],
        }
        slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")

        # Sync WORK.md cycle_phase (fail-permissive)
        sync_work_md_phase(work_id, phase, project_root=root)

        # Log governance event (fail-permissive)
        try:
            _lib_dir = Path(__file__).parent
            if str(_lib_dir) not in sys.path:
                sys.path.insert(0, str(_lib_dir))
            from governance_events import log_phase_transition
            log_phase_transition(phase, work_id, "Hephaestus")
        except Exception:
            pass

        return True
    except Exception:
        return False


def clear_cycle_state(project_root: Optional[Path] = None) -> bool:
    """Zero out session_state in haios-status-slim.json.

    Canonical implementation (moved from session_end_actions.py).
    Always writes all 6 fields to normalize schema.

    Args:
        project_root: Project root path. Defaults to derived path.

    Returns:
        True if cleared successfully, False on error/missing file.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return False

        data = json.loads(slim_file.read_text(encoding="utf-8"))
        data["session_state"] = {
            "active_cycle": None,
            "current_phase": None,
            "work_id": None,
            "entered_at": None,
            "active_queue": None,
            "phase_history": [],
        }
        slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
        return True
    except Exception:
        return False


def set_active_queue(
    queue_name: str,
    project_root: Optional[Path] = None,
) -> bool:
    """Set active_queue in session_state of haios-status-slim.json.

    Args:
        queue_name: Queue name (e.g., "governance", "default")
        project_root: Project root. Defaults to derived path.

    Returns:
        True if written, False on error/missing file/missing session_state.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return False

        data = json.loads(slim_file.read_text(encoding="utf-8"))
        if "session_state" not in data:
            return False
        data["session_state"]["active_queue"] = queue_name
        slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
        return True
    except Exception:
        return False
```

```python
# .claude/haios/lib/session_mgmt.py — new file

"""
Session start management for justfile session-start recipe (WORK-219).

Extracted from justfile session-start inline Python. Encapsulates:
- Writing session number to .claude/session (preserving # comment headers)
- Writing session_delta to haios-status.json
- Logging session start governance event
- Resetting session event log

Pure function: takes explicit params, no global state.
Fail-permissive: never raises.
"""
import json
import sys
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def start_session(
    session_number: int,
    agent: str = "Hephaestus",
    project_root: Optional[Path] = None,
) -> bool:
    """Encapsulate justfile session-start recipe logic.

    Actions performed (in order, all fail-permissive):
    1. Write session_number to .claude/session (preserving # comment headers)
    2. Write session_delta to .claude/haios-status.json
    3. Log SessionStarted governance event via log_session_start()
    4. Truncate session event log via reset_log()

    Args:
        session_number: New session number (e.g., 451)
        agent: Agent name for governance event (default: "Hephaestus")
        project_root: Project root. Defaults to derived path.

    Returns:
        True if all 4 actions completed without error, False if any failed.
    """
    try:
        root = project_root or _default_project_root()
        lib_dir = Path(__file__).parent
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        all_ok = True

        # 1. Write session number to .claude/session
        try:
            session_file = root / ".claude" / "session"
            lines = session_file.read_text(encoding="utf-8").splitlines(keepends=True) if session_file.exists() else []
            headers = [l for l in lines if l.startswith("#")]
            session_file.write_text("".join(headers) + str(session_number) + "\n", encoding="utf-8")
        except Exception:
            all_ok = False

        # 2. Write session_delta to haios-status.json
        try:
            status_file = root / ".claude" / "haios-status.json"
            status = json.loads(status_file.read_text(encoding="utf-8")) if status_file.exists() else {}
            status["session_delta"] = {
                "current_session": session_number,
                "prior_session": session_number - 1,
            }
            status_file.write_text(json.dumps(status, indent=2), encoding="utf-8")
        except Exception:
            all_ok = False

        # 3. Log governance event
        try:
            from governance_events import log_session_start
            log_session_start(session_number, agent)
        except Exception:
            all_ok = False

        # 4. Reset session event log
        try:
            from session_event_log import reset_log
            reset_log()
        except Exception:
            all_ok = False

        return all_ok

    except Exception:
        return False
```

```python
# .claude/haios/lib/session_end_actions.py — updated clear_cycle_state (delegate)

def clear_cycle_state(project_root: Optional[Path] = None) -> bool:
    """Zero out session_state in haios-status-slim.json.

    Delegates to cycle_state.clear_cycle_state (canonical impl moved to
    cycle_state.py by WORK-219).

    Args:
        project_root: Project root path. Defaults to derived path.

    Returns:
        True if cleared successfully, False on error/missing file.
    """
    try:
        _lib_dir = Path(__file__).parent
        if str(_lib_dir) not in sys.path:
            sys.path.insert(0, str(_lib_dir))
        from cycle_state import clear_cycle_state as _clear
        return _clear(project_root=project_root)
    except Exception:
        return False
```

```
# justfile — updated recipes (replace inline Python with lib/ calls)

session-start session:
    @python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from session_mgmt import start_session; ok=start_session({{session}}); print(f'Session {{session}} start logged' if ok else 'Session {{session}} start logged (partial)')"

set-cycle cycle phase work_id:
    @python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from cycle_state import set_cycle_state; set_cycle_state('{{cycle}}','{{phase}}','{{work_id}}'); print(f'Set: {{cycle}}/{{phase}}/{{work_id}}')"

clear-cycle:
    @python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from cycle_state import clear_cycle_state; clear_cycle_state(); print('Cleared session_state')"

set-queue queue_name:
    @python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from cycle_state import set_active_queue; set_active_queue('{{queue_name}}'); print(f'Set queue: {{queue_name}}')"
```

**Behavior:** All 4 operations are implemented as Python functions with explicit parameters, absolute paths derived from `__file__`, fail-permissive error handling, and full test coverage.

**Result:** WORK-220 can import these functions directly to create MCP tool wrappers.

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 1: set_cycle_state writes 6-field session_state
- **file:** `tests/test_cycle_state_mgmt.py`
- **function:** `test_set_cycle_state_writes_session_state(tmp_path)`
- **setup:** Write slim JSON with empty session_state via `_write_slim(tmp_path, {})`. Call `set_cycle_state("implementation-cycle", "DO", "WORK-219", project_root=tmp_path)`.
- **assertion:** Read slim JSON; assert `session_state["active_cycle"] == "implementation-cycle"`, `session_state["current_phase"] == "DO"`, `session_state["work_id"] == "WORK-219"`, `session_state["active_queue"] is None`, `session_state["phase_history"] == []`, `"entered_at" in session_state`.

#### Test 2: set_cycle_state returns False on missing file
- **file:** `tests/test_cycle_state_mgmt.py`
- **function:** `test_set_cycle_state_missing_file(tmp_path)`
- **setup:** Do not create slim JSON (tmp_path is empty).
- **assertion:** `set_cycle_state("implementation-cycle", "DO", "WORK-219", project_root=tmp_path)` returns `False`.

#### Test 3: clear_cycle_state zeroes all 6 fields
- **file:** `tests/test_cycle_state_mgmt.py`
- **function:** `test_clear_cycle_state_zeroes_fields(tmp_path)`
- **setup:** Write slim JSON with active session_state (`active_cycle="implementation-cycle"`, `current_phase="DO"`, `work_id="WORK-219"`, `entered_at="now"`, `active_queue="governance"`, `phase_history=[{"from":"PLAN","to":"DO","at":"now"}]`).
- **assertion:** `clear_cycle_state(project_root=tmp_path)` returns `True`. Read slim JSON; assert all 6 fields are null/empty: `active_cycle` is `None`, `current_phase` is `None`, `work_id` is `None`, `entered_at` is `None`, `active_queue` is `None`, `phase_history == []`.

#### Test 4: set_active_queue mutates only active_queue field
- **file:** `tests/test_cycle_state_mgmt.py`
- **function:** `test_set_active_queue_mutates_field(tmp_path)`
- **setup:** Write slim JSON with `session_state={"active_cycle":"implementation-cycle","current_phase":"DO","work_id":"WORK-219","entered_at":"now","active_queue":None,"phase_history":[]}`. Call `set_active_queue("governance", project_root=tmp_path)`.
- **assertion:** Read slim JSON; assert `session_state["active_queue"] == "governance"` and `session_state["active_cycle"] == "implementation-cycle"` (other fields unchanged).

#### Test 5: set_active_queue returns False on missing session_state key
- **file:** `tests/test_cycle_state_mgmt.py`
- **function:** `test_set_active_queue_missing_session_state(tmp_path)`
- **setup:** Write slim JSON with `{}` (no session_state key).
- **assertion:** `set_active_queue("governance", project_root=tmp_path)` returns `False`.

#### Test 6: start_session writes session file and status delta
- **file:** `tests/test_session_mgmt.py`
- **function:** `test_start_session_writes_files(tmp_path)`
- **setup:** Create `.claude/session` with content `"# generated: test\n449\n"`. Create `.claude/haios-status.json` with `{}`. Mock `governance_events.log_session_start` and `session_event_log.reset_log` to no-ops. Call `start_session(451, project_root=tmp_path)`.
- **assertion:** Read `.claude/session` — assert `"451"` is in content and `"# generated: test"` header is preserved. Read `.claude/haios-status.json` — assert `session_delta["current_session"] == 451` and `session_delta["prior_session"] == 450`.

#### Test 7: start_session preserves session file headers
- **file:** `tests/test_session_mgmt.py`
- **function:** `test_start_session_preserves_headers(tmp_path)`
- **setup:** Create `.claude/session` with `"# generated: 2026-01-21\n# System Auto: last updated on: 2026-01-21T11:26:51\n450\n"`. Mock governance and log calls. Call `start_session(451, project_root=tmp_path)`.
- **assertion:** Session file content starts with `"# generated: 2026-01-21\n# System Auto: last updated on: 2026-01-21T11:26:51\n"` and ends with `"451\n"`.

#### Test 8: start_session returns True on success
- **file:** `tests/test_session_mgmt.py`
- **function:** `test_start_session_returns_true(tmp_path)`
- **setup:** Create minimal `.claude/session` and `.claude/haios-status.json`. Mock governance and log calls to no-ops. Call `start_session(451, project_root=tmp_path)`.
- **assertion:** Return value is `True`.

### Design

#### File 1 (MODIFY): `.claude/haios/lib/cycle_state.py`

**Location:** Append after `read_phase_contract()` at end of file (line 216+).

**Current Code (end of file):**
```python
# cycle_state.py lines 205-215
    try:
        root = project_root or _default_project_root()
        phase_file = (
            root / ".claude" / "skills" / cycle_name / "phases" / f"{phase_name}.md"
        )
        if not phase_file.exists():
            return None
        return phase_file.read_text(encoding="utf-8")
    except Exception:
        return None
```

**Target Code:** Append 3 new functions after line 215 (see Desired State section above for complete implementations of `set_cycle_state`, `clear_cycle_state`, `set_active_queue`).

**Note:** `sys` is already imported at line 13. `datetime` is already imported at line 14. No new imports needed at module level for cycle_state.py.

#### File 2 (CREATE): `.claude/haios/lib/session_mgmt.py`

Complete new file (see Desired State section above). No sibling imports at module level — uses try/except conditional imports inside `start_session()` to match the pattern used by `advance_cycle_phase()` in cycle_state.py.

#### File 3 (MODIFY): `.claude/haios/lib/session_end_actions.py`

**Location:** Lines 78-108 — `clear_cycle_state` function.

**Current Code:**
```python
def clear_cycle_state(project_root: Optional[Path] = None) -> bool:
    """Zero out session_state in haios-status-slim.json.
    ...
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return False

        data = json.loads(slim_file.read_text(encoding="utf-8"))
        data["session_state"] = {
            "active_cycle": None,
            "current_phase": None,
            "work_id": None,
            "entered_at": None,
            "active_queue": None,
            "phase_history": [],
        }
        slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
        return True
    except Exception:
        return False
```

**Target Code:** Replace body with delegation to `cycle_state.clear_cycle_state` (see Desired State section above). Preserves public API — callers are unaffected.

#### File 4 (MODIFY): `justfile`

**Location:** Lines 299-326 — 4 recipe bodies.

**Current Code:** 4 inline one-liner Python strings (see Current State above).

**Target Code:** Replace each recipe body with a single lib/ call (see Desired State above).

**Note on set-cycle upgrade:** The justfile set-cycle recipe currently writes a 4-field `session_state` dict (no `active_queue`, no `phase_history`). `set_cycle_state()` writes the canonical 6-field schema. This is a silent upgrade — no callers depend on the 4-field behavior.

### Call Chain

```
justfile set-cycle recipe
    |
    +-> cycle_state.set_cycle_state(cycle, phase, work_id)
            |
            +-> slim_file write (6-field schema)
            |
            +-> sync_work_md_phase(work_id, phase)   [fail-permissive]
            |
            +-> governance_events.log_phase_transition(phase, work_id, agent)  [fail-permissive]

justfile clear-cycle recipe
    |
    +-> cycle_state.clear_cycle_state()
            |
            +-> slim_file write (all fields nulled)

    session_end_actions.clear_cycle_state()  [Stop hook]
            |
            +-> cycle_state.clear_cycle_state()  [delegates]

justfile set-queue recipe
    |
    +-> cycle_state.set_active_queue(queue_name)
            |
            +-> slim_file write (active_queue field only)

justfile session-start recipe
    |
    +-> session_mgmt.start_session(session_number)
            |
            +-> .claude/session file write (headers preserved)
            |
            +-> haios-status.json session_delta write
            |
            +-> governance_events.log_session_start(session_number, agent)
            |
            +-> session_event_log.reset_log()
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| clear_cycle_state ownership | cycle_state.py owns canonical impl | session_end_actions is Stop-hook context; cycle_state.py is the natural home for all session_state mutations. Avoids duplication. |
| session_end_actions delegation | Delegate to cycle_state.clear_cycle_state | Preserves Stop hook public API with zero behavior change. Single source of truth. |
| set_cycle_state writes 6-field schema | Always write active_queue=None, phase_history=[] | Normalizes schema on every set. Current justfile recipe only writes 4 fields — silent upgrade, no consumer breakage. |
| start_session returns bool | Returns True if all 4 actions succeed, False if any fail | Allows callers to detect partial failures. Fail-permissive per lib/ pattern (never raises). |
| governance_events import in cycle_state | Import inside try/except inside function body | Matches advance_cycle_phase() pattern at line 119. Avoids circular import risk in hook subprocess context. |
| No agent param in set_cycle_state | Hardcoded "Hephaestus" in log_phase_transition call | Matches justfile recipe behavior; agent is not meaningful for this call site. Can be added later if needed. |
| Advisory A4: verify clear-cycle/set-queue side effects | Confirmed: clear-cycle is pure JSON write only; set-queue is pure JSON write only | Justfile lines 321, 326 confirmed. Neither calls external functions. No side effects beyond JSON write. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| slim file missing for set_cycle_state | Returns False immediately | Test 2 |
| slim file missing for clear_cycle_state | Returns False immediately | (covered by existing session_end_actions tests) |
| session_state key absent for set_active_queue | Returns False | Test 5 |
| session file missing for start_session | Creates it fresh (no headers to preserve) | Test 6 |
| haios-status.json missing for start_session | Creates fresh `{}` then writes session_delta | Test 6 |
| governance_events import fails in start_session | Sets all_ok=False, continues remaining steps | Test 8 (indirect) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| session_end_actions circular import (imports cycle_state which imports governance_events) | M | Both cycle_state and session_end_actions use lazy inside-function imports. No module-level circular imports. |
| Justfile set-cycle silent schema upgrade breaks consumers | L | Consumers only read session_state fields they know about. Adding active_queue/phase_history cannot break existing consumers. Verified: no consumer reads 4-field count. |
| haios-status.json concurrent write race (start_session) | L | Same risk as existing justfile inline code. Not worsened by extraction. |
| test mocking scope for governance_events in session_mgmt | M | Use `unittest.mock.patch` with full module path: `patch("governance_events.log_session_start")`. Tests must add lib_dir to sys.path before patching. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_cycle_state_mgmt.py` (Tests 1-5) and `tests/test_session_mgmt.py` (Tests 6-8) from Layer 1 Tests section. Tests 1-5 import from `cycle_state`; Tests 6-8 import from `session_mgmt`.
- **output:** Both test files exist, all 8 tests fail with ImportError or AttributeError
- **verify:** `pytest tests/test_cycle_state_mgmt.py tests/test_session_mgmt.py --no-header -q 2>&1 | tail -1` shows 8 errors or failures

### Step 2: Add set_cycle_state, clear_cycle_state, set_active_queue to cycle_state.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Append 3 new functions to `.claude/haios/lib/cycle_state.py` per Layer 1 Desired State. No new module-level imports needed.
- **output:** Tests 1-5 pass, Tests 6-8 still fail
- **verify:** `pytest tests/test_cycle_state_mgmt.py -v` shows 5 passed, 0 failed

### Step 3: Create session_mgmt.py (GREEN continued)
- **spec_ref:** Layer 1 > Design > File 2 (CREATE)
- **input:** Step 2 complete
- **action:** Create `.claude/haios/lib/session_mgmt.py` per Layer 1 Desired State
- **output:** All 8 tests pass
- **verify:** `pytest tests/test_cycle_state_mgmt.py tests/test_session_mgmt.py -v` shows 8 passed, 0 failed

### Step 4: Update session_end_actions.py (REFACTOR)
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY)
- **input:** Step 3 complete (all new tests green)
- **action:** Replace `clear_cycle_state` body in `session_end_actions.py` with delegation to `cycle_state.clear_cycle_state`
- **output:** session_end_actions still passes existing tests; delegation is transparent
- **verify:** `pytest tests/test_session_end_actions.py --no-header -q 2>&1 | tail -1` — expect 18 passed, 0 failed

### Step 5: Update justfile recipes
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Step 4 complete
- **action:** Replace inline Python in set-cycle, clear-cycle, set-queue, session-start recipes with lib/ calls per Desired State
- **output:** Recipes call lib/ functions; behavior identical to before
- **verify:** Confirm all 4 import patterns from Ground Truth Deliverables table: `grep "from cycle_state import set_cycle_state" justfile` (1 match), `grep "from cycle_state import clear_cycle_state" justfile` (1 match), `grep "from cycle_state import set_active_queue" justfile` (1 match), `grep "from session_mgmt import start_session" justfile` (1 match)

### Step 6: Full test suite regression check
- **spec_ref:** Layer 0 > Primary Files
- **input:** Step 5 complete
- **action:** Run full pytest suite
- **output:** No new failures vs baseline (1571 passed, 8 skipped)
- **verify:** `pytest tests/ -v 2>&1 | tail -5` — shows 0 new failures

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_cycle_state_mgmt.py -v` | 5 passed, 0 failed |
| `pytest tests/test_session_mgmt.py -v` | 3 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs baseline (1571 passed) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| cycle_state.set_cycle_state exists | `grep "def set_cycle_state" .claude/haios/lib/cycle_state.py` | 1 match |
| cycle_state.clear_cycle_state exists | `grep "def clear_cycle_state" .claude/haios/lib/cycle_state.py` | 1 match |
| cycle_state.set_active_queue exists | `grep "def set_active_queue" .claude/haios/lib/cycle_state.py` | 1 match |
| session_mgmt.start_session exists | `grep "def start_session" .claude/haios/lib/session_mgmt.py` | 1 match |
| Justfile set-cycle updated | `grep "from cycle_state import set_cycle_state" justfile` | 1 match |
| Justfile clear-cycle updated | `grep "from cycle_state import clear_cycle_state" justfile` | 1 match |
| Justfile set-queue updated | `grep "from cycle_state import set_active_queue" justfile` | 1 match |
| Justfile session-start updated | `grep "from session_mgmt import start_session" justfile` | 1 match |
| session_end_actions delegates | `grep "from cycle_state import clear_cycle_state" .claude/haios/lib/session_end_actions.py` | 1 match |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No inline JSON in set-cycle | `grep -A3 "^set-cycle" justfile \| grep "json.load(open"` | 0 matches |
| No inline JSON in clear-cycle | `grep -A2 "^clear-cycle" justfile \| grep "json.load(open"` | 0 matches |
| No inline JSON in set-queue | `grep -A2 "^set-queue" justfile \| grep "json.load(open"` | 0 matches |
| No inline JSON in session-start | `grep -A2 "^session-start" justfile \| grep "json.load(open"` | 0 matches |
| session_end_actions no duplicate impl | `grep -c "slim_file.write_text" .claude/haios/lib/session_end_actions.py` | 0 matches |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 3 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists: justfile recipes call lib/ functions (Consumer Integrity table above)
- [ ] No stale inline JSON in updated recipes (Consumer Integrity table above)
- [ ] session_end_actions.clear_cycle_state delegates to cycle_state.clear_cycle_state
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/haios/lib/cycle_state.py` (extend with 3 new functions)
- `.claude/haios/lib/session_end_actions.py` (delegate clear_cycle_state)
- `.claude/haios/lib/session_event_log.py` (reset_log imported by start_session)
- `.claude/haios/lib/governance_events.py` (log_phase_transition, log_session_start)
- `justfile` lines 299-326 (recipes to update)
- `tests/test_cycle_state.py` (sibling test for import/pattern reference)
- WORK-218 investigation findings (memory 88698-88704) — source of recipe list
- WORK-220 (blocks) — MCP Operations Server Core

---
