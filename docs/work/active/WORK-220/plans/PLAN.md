---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-220
title: "MCP Operations Server Core"
author: Hephaestus
lifecycle_phase: plan
session: 451
generated: 2026-02-25
last_updated: 2026-02-25T12:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-220/WORK.md"
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
# Implementation Plan: MCP Operations Server Core

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Create the `haios-operations` FastMCP server package at `.claude/haios/haios_ops/` that wraps WorkEngine, queue_ceremonies, cycle_state, and session_mgmt as ~15 typed MCP tools across work, queue, and session groups, registered in `.mcp.json` as the ADR-045 Tier 2 agent-native operations interface.

---

## Open Decisions

<!-- No operator_decisions in WORK.md frontmatter — no open decisions. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Package location | project root vs .claude/haios/ | .claude/haios/haios_ops/ | Operator directive Session 450 — portability, mirrors haios_etl pattern under .claude/haios/ |
| GovernanceLayer integration | Phase 1 vs deferred | Deferred to Phase 3 | WORK-218 F3: governance deferred; Phase 1 tools execute without in-server governance check |
| MCP Resources (CQRS reads) | Phase 1 vs deferred | Deferred to Phase 2 | WORK-218 design output: resources are a separate innovation phase, not blocking Phase 1 |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/haios_ops/__init__.py` | CREATE | 2 |
| `.claude/haios/haios_ops/bootstrap.py` | CREATE | 2 |
| `.claude/haios/haios_ops/mcp_server.py` | CREATE | 2 |
| `.mcp.json` | MODIFY | 2 |

### Consumer Files

<!-- Files that reference primary files and need updating.
     .mcp.json is the only existing consumer — it registers MCP servers.
     No existing code imports haios_ops (new package). -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.mcp.json` | Registers MCP servers | 1-11 | UPDATE — add haios-operations entry |
| `.claude/haios/README.md` | Package documentation | N/A | UPDATE if exists, else SKIP |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_mcp_operations.py` | CREATE | New test file — all tool groups with mocked backends |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 4 | Primary Files table (CREATE rows: __init__.py, bootstrap.py, mcp_server.py, test file) |
| Files to modify | 1 | Primary Files table (MODIFY rows: .mcp.json) |
| Tests to write | 16 | Test Files table (see Layer 1 Tests section — ~16 test functions) |
| Total blast radius | 5 | Sum of all unique files above |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

```python
# .mcp.json — what exists now
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": ["-m", "haios_etl.mcp_server"],
      "env": {
        "DB_PATH": "haios_memory.db"
      }
    }
  }
}
```

```
# .claude/haios/haios_ops/ — does not exist
# No haios_ops package exists. The directory is absent.
```

**Behavior:** Only haios-memory MCP server is registered. Agents access HAIOS operations via `just` recipes (Bash tool calls), which are Tier 3 — opaque, untyped, shell-overhead.

**Problem:** Agents call `just ready`, `just commit`, `just set-cycle` via Bash — these are string-in/string-out with no type safety, no structured returns, and violate REQ-DISCOVER-002 (ADR-045 Tier 2 not populated for operations).

### Desired State

```python
# .mcp.json — after change
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": ["-m", "haios_etl.mcp_server"],
      "env": {
        "DB_PATH": "haios_memory.db"
      }
    },
    "haios-operations": {
      "command": "python",
      "args": ["-m", "haios_ops.mcp_server"],
      "env": {
        "PYTHONPATH": ".claude/haios"
      }
    }
  }
}
```

```
# .claude/haios/haios_ops/ — after creation
haios_ops/
  __init__.py         # package marker
  bootstrap.py        # dual sys.path setup for modules/ and lib/
  mcp_server.py       # FastMCP("haios-operations") with ~15 @mcp.tool() functions
```

**Behavior:** `mcp__haios-operations__work_get(work_id="WORK-220")` returns typed JSON WorkState dict. Queue tools return lists of WorkState dicts. Session tools return `{success: bool}`.

**Note (critique A4):** Uses `PYTHONPATH` env var instead of `cwd` with `${workspaceFolder}` — avoids reliance on variable expansion by MCP host. `PYTHONPATH=.claude/haios` makes `haios_ops` discoverable as a package. bootstrap.py derives paths from `__file__` (not cwd), so this is safe.

**Result:** Agents call operations as MCP tools — auto-discovered in system prompt, typed returns, no Bash overhead. ADR-045 Tier 2 interface for operations satisfied.

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 1: bootstrap.py path resolution
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_bootstrap_adds_both_paths()`
- **setup:** Add `sys.path.insert(0, str(Path(__file__).parent.parent / ".claude/haios"))` at top of test module (before any `haios_ops` import) so `haios_ops` is importable in pytest context. Import bootstrap from `haios_ops` package; capture sys.path before and after
- **assertion:** After bootstrap import, both `.claude/haios/modules` and `.claude/haios/lib` are in `sys.path`; WorkEngine importable without ImportError

#### Test 2: work_get returns typed dict
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_get_returns_dict()`
- **setup:** Mock WorkEngine.get_work to return WorkState(id="WORK-220", title="Test", status="active", current_node="PLAN", type="implementation", queue_position="working", cycle_phase="PLAN", priority="high")
- **assertion:** `work_get("WORK-220")` returns dict with keys `id`, `title`, `status`, `queue_position`, `cycle_phase`; value `id == "WORK-220"`

#### Test 3: work_get not found
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_get_not_found()`
- **setup:** Mock WorkEngine.get_work to return None
- **assertion:** `work_get("WORK-999")` returns `{"error": "not found", "work_id": "WORK-999"}`

#### Test 4: work_create returns path dict
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_create_returns_dict()`
- **setup:** Mock WorkEngine.create_work to return Path("/fake/path/WORK.md"); mock ceremony_context as no-op
- **assertion:** `work_create("WORK-999", "Test Title")` returns dict with keys `success`, `path`; `success == True`

#### Test 5: work_close returns success dict
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_close_returns_dict()`
- **setup:** Mock WorkEngine.close to return Path("/fake/WORK.md"); mock ceremony_context as no-op
- **assertion:** `work_close("WORK-220")` returns `{"success": True, "work_id": "WORK-220"}`

#### Test 6: work_transition returns updated state
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_work_transition_returns_dict()`
- **setup:** Mock WorkEngine.transition to return WorkState with cycle_phase="DO"; mock ceremony_context
- **assertion:** `work_transition("WORK-220", "DO")` returns dict with `cycle_phase == "DO"`

#### Test 7: queue_list returns list of dicts
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_queue_list_returns_list()`
- **setup:** Mock WorkEngine.get_queue to return [WorkState(id="WORK-001", ...), WorkState(id="WORK-002", ...)]
- **assertion:** `queue_list()` returns list of 2 dicts, each with key `id`

#### Test 8: queue_next returns single dict or null
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_queue_next_returns_dict()`
- **setup:** Mock WorkEngine.get_next to return WorkState(id="WORK-001", ...)
- **assertion:** `queue_next()` returns dict with `id == "WORK-001"`

#### Test 9: queue_next empty queue
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_queue_next_empty()`
- **setup:** Mock WorkEngine.get_next to return None
- **assertion:** `queue_next()` returns `{"next": null, "queue": "default"}`

#### Test 10: queue_ready returns list
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_queue_ready_returns_list()`
- **setup:** Mock WorkEngine.get_ready to return [WorkState(id="WORK-001", ...)]
- **assertion:** `queue_ready()` returns list of 1 dict with key `id`

#### Test 11: queue_commit transitions to working
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_queue_commit_returns_dict()`
- **setup:** Mock execute_queue_transition to return `{"success": True, "work": WorkState(...)}`
- **assertion:** `queue_commit("WORK-001")` returns dict with `success == True`

#### Test 12: queue_park and queue_unpark
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_queue_park_unpark()`
- **setup:** Mock execute_queue_transition for both park and unpark operations
- **assertion:** `queue_park("WORK-001")` and `queue_unpark("WORK-001")` each return `{"success": True}`

#### Test 13: session_start success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_session_start_returns_dict()`
- **setup:** Mock session_mgmt.start_session to return True
- **assertion:** `session_start(451)` returns `{"success": True, "session": 451}`

#### Test 14: cycle_set success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_cycle_set_returns_dict()`
- **setup:** Mock cycle_state.set_cycle_state to return True
- **assertion:** `cycle_set("implementation-cycle", "DO", "WORK-220")` returns `{"success": True}`

#### Test 15: cycle_clear success
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_cycle_clear_returns_dict()`
- **setup:** Mock cycle_state.clear_cycle_state to return True
- **assertion:** `cycle_clear()` returns `{"success": True}`

#### Test 16: cycle_get returns current state
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_cycle_get_returns_dict()`
- **setup:** `cycle_get` accepts optional `project_root: Path = None` parameter (defaults to `_PROJECT_ROOT`); test passes `tmp_path` as project_root, writes known `session_state` to `tmp_path / ".claude" / "haios-status-slim.json"`
- **assertion:** `cycle_get(project_root=tmp_path)` returns dict with `active_cycle`, `current_phase`, `work_id` keys

### Design

<!-- Per file in Layer 0 Primary Files table. -->

#### File 1 (NEW): `.claude/haios/haios_ops/__init__.py`

```python
# generated: 2026-02-25
"""haios_ops — HAIOS Operations MCP Server package."""
```

#### File 2 (NEW): `.claude/haios/haios_ops/bootstrap.py`

```python
# generated: 2026-02-25
"""
Bootstrap module for haios_ops MCP server.

Sets up dual sys.path so modules/ and lib/ are importable
from the server location inside .claude/haios/haios_ops/.

Pattern from .claude/haios/modules/cli.py:19-26.
"""
import sys
from pathlib import Path


def setup_paths() -> None:
    """Insert modules/ and lib/ dirs into sys.path.

    Anchored from this file's location:
      haios_ops/bootstrap.py
        -> haios_ops/ (package dir)
        -> haios/ (parent = .claude/haios/)
        -> modules/ (.claude/haios/modules/)
        -> lib/     (.claude/haios/lib/)

    Idempotent — only inserts if not already present.
    """
    haios_dir = Path(__file__).parent.parent  # .claude/haios/
    modules_dir = haios_dir / "modules"
    lib_dir = haios_dir / "lib"

    for p in (str(modules_dir), str(lib_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)


# Run at import time so that `import bootstrap` in mcp_server.py
# is sufficient to prepare the path.
setup_paths()
```

#### File 3 (NEW): `.claude/haios/haios_ops/mcp_server.py`

```python
# generated: 2026-02-25
"""
haios-operations MCP Server (WORK-220, Phase 1).

FastMCP server providing agent-native operations as typed MCP tools.
ADR-045 Tier 2 implementation for HAIOS operational interface.

Tool groups:
  work:    work_get, work_create, work_close, work_transition
  queue:   queue_ready, queue_list, queue_next, queue_prioritize,
           queue_commit, queue_park, queue_unpark
  session: session_start, session_end, cycle_set, cycle_get, cycle_clear

Phase 2 (resources): @mcp.resource decorators — deferred.
Phase 3 (governance): GovernanceLayer in-server check — deferred.
"""
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Bootstrap sys.path FIRST — before any module imports
from . import bootstrap  # noqa: F401  (side-effect: setup_paths() runs)

from mcp.server.fastmcp import FastMCP
from governance_layer import GovernanceLayer, ceremony_context
from work_engine import WorkEngine, WorkState, WorkNotFoundError, InvalidTransitionError
from queue_ceremonies import execute_queue_transition
import cycle_state
import session_mgmt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server init
# ---------------------------------------------------------------------------
mcp = FastMCP("haios-operations")

# Project root derived from file location (not cwd):
#   haios_ops/mcp_server.py -> haios_ops/ -> haios/ -> .claude/ -> project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Module-level engine — shared across tool calls (single process lifetime)
_governance = GovernanceLayer()
_engine = WorkEngine(governance=_governance, base_path=_PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _work_to_dict(work: WorkState) -> Dict[str, Any]:
    """Convert WorkState dataclass to JSON-serializable dict."""
    d = asdict(work)
    # path is a Path object — serialize to string or remove
    if d.get("path") is not None:
        d["path"] = str(d["path"])
    return d


# ---------------------------------------------------------------------------
# Work tools
# ---------------------------------------------------------------------------

@mcp.tool()
def work_get(work_id: str) -> Dict[str, Any]:
    """Get work item state by ID.

    Args:
        work_id: Work item ID (e.g., "WORK-220")

    Returns:
        Typed dict of WorkState fields, or {"error": ..., "work_id": ...} if not found.
    """
    work = _engine.get_work(work_id)
    if work is None:
        return {"error": "not found", "work_id": work_id}
    return _work_to_dict(work)


@mcp.tool()
def work_create(
    work_id: str,
    title: str,
    priority: str = "medium",
    category: str = "implementation",
) -> Dict[str, Any]:
    """Create a new work item with directory structure.

    Args:
        work_id: New work item ID (e.g., "WORK-221")
        title: Human-readable title
        priority: low | medium | high (default: medium)
        category: implementation | investigation | etc. (default: implementation)

    Returns:
        {"success": True, "path": "<work_md_path>"} or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("create-work"):
            path = _engine.create_work(
                id=work_id,
                title=title,
                priority=priority,
                category=category,
            )
        return {"success": True, "path": str(path)}
    except Exception as e:
        logger.error(f"work_create failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def work_close(work_id: str) -> Dict[str, Any]:
    """Close a work item (set status=complete, queue_position=done).

    Args:
        work_id: Work item ID to close

    Returns:
        {"success": True, "work_id": "..."} or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("close-work"):
            _engine.close(work_id)
        return {"success": True, "work_id": work_id}
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"work_close failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def work_transition(work_id: str, to_node: str) -> Dict[str, Any]:
    """Transition a work item to a new lifecycle node.

    Args:
        work_id: Work item ID
        to_node: Target node (e.g., "DO", "CHECK", "DONE")

    Returns:
        Updated WorkState dict, or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("transition-work"):
            work = _engine.transition(work_id, to_node)
        return _work_to_dict(work)
    except (WorkNotFoundError, InvalidTransitionError) as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"work_transition failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Queue tools
# ---------------------------------------------------------------------------

@mcp.tool()
def queue_ready() -> List[Dict[str, Any]]:
    """Get all unblocked, non-parked active work items.

    Returns:
        List of WorkState dicts (may be empty).
    """
    items = _engine.get_ready()
    return [_work_to_dict(w) for w in items]


@mcp.tool()
def queue_list(queue_name: str = "default") -> List[Dict[str, Any]]:
    """Get ordered work items from a named queue.

    Args:
        queue_name: Queue name from work_queues.yaml (default: "default")

    Returns:
        Ordered list of WorkState dicts.
    """
    items = _engine.get_queue(queue_name)
    return [_work_to_dict(w) for w in items]


@mcp.tool()
def queue_next(queue_name: str = "default") -> Dict[str, Any]:
    """Get the next work item from queue head.

    Args:
        queue_name: Queue name (default: "default")

    Returns:
        WorkState dict of next item, or {"next": null, "queue": "<name>"} if empty.
    """
    work = _engine.get_next(queue_name)
    if work is None:
        return {"next": None, "queue": queue_name}
    return _work_to_dict(work)


@mcp.tool()
def queue_prioritize(work_id: str, rationale: str = "") -> Dict[str, Any]:
    """Move work item from backlog to ready (Prioritize ceremony).

    Args:
        work_id: Work item ID
        rationale: Optional reason for prioritization

    Returns:
        {"success": True} or {"success": False, "error": "..."}
    """
    result = execute_queue_transition(
        _engine, work_id, "ready", "Prioritize", rationale=rationale or None
    )
    return {"success": result.get("success", False), "error": result.get("error")} if not result.get("success") else {"success": True}


@mcp.tool()
def queue_commit(work_id: str, rationale: str = "") -> Dict[str, Any]:
    """Move work item from ready to working (Commit ceremony).

    Args:
        work_id: Work item ID
        rationale: Optional commit rationale

    Returns:
        {"success": True} or {"success": False, "error": "..."}
    """
    result = execute_queue_transition(
        _engine, work_id, "working", "Commit", rationale=rationale or None
    )
    return {"success": True} if result.get("success") else {"success": False, "error": result.get("error")}


@mcp.tool()
def queue_park(work_id: str, rationale: str = "") -> Dict[str, Any]:
    """Move work item to parked (Park ceremony).

    Args:
        work_id: Work item ID
        rationale: Optional reason for parking

    Returns:
        {"success": True} or {"success": False, "error": "..."}
    """
    result = execute_queue_transition(
        _engine, work_id, "parked", "Park", rationale=rationale or None
    )
    return {"success": True} if result.get("success") else {"success": False, "error": result.get("error")}


@mcp.tool()
def queue_unpark(work_id: str, rationale: str = "") -> Dict[str, Any]:
    """Move work item from parked to backlog (Unpark ceremony).

    Args:
        work_id: Work item ID
        rationale: Optional reason for unparking

    Returns:
        {"success": True} or {"success": False, "error": "..."}
    """
    result = execute_queue_transition(
        _engine, work_id, "backlog", "Unpark", rationale=rationale or None
    )
    return {"success": True} if result.get("success") else {"success": False, "error": result.get("error")}


# ---------------------------------------------------------------------------
# Session tools
# ---------------------------------------------------------------------------

@mcp.tool()
def session_start(session_number: int, agent: str = "Hephaestus") -> Dict[str, Any]:
    """Start a new session (writes session number, session_delta, logs governance event).

    Args:
        session_number: New session number (e.g., 452)
        agent: Agent name for governance event (default: Hephaestus)

    Returns:
        {"success": True, "session": <n>} or {"success": False, "error": "..."}
    """
    ok = session_mgmt.start_session(session_number, agent=agent)
    if ok:
        return {"success": True, "session": session_number}
    return {"success": False, "error": "session_start failed — check logs"}


@mcp.tool()
def session_end(session_number: int, agent: str = "Hephaestus") -> Dict[str, Any]:
    """Mark session end in governance events log.

    Args:
        session_number: Session number to end
        agent: Agent name for governance event (default: Hephaestus)

    Returns:
        {"success": True, "session": <n>} or {"success": False, "error": "..."}
    """
    try:
        from governance_events import log_session_end
        log_session_end(session_number, agent)
        return {"success": True, "session": session_number}
    except Exception as e:
        logger.error(f"session_end failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def cycle_set(cycle: str, phase: str, work_id: str) -> Dict[str, Any]:
    """Set session_state for a new lifecycle cycle phase.

    Args:
        cycle: Lifecycle cycle name (e.g., "implementation-cycle")
        phase: Phase name (e.g., "DO", "PLAN")
        work_id: Work item ID (e.g., "WORK-220")

    Returns:
        {"success": True} or {"success": False, "error": "..."}
    """
    ok = cycle_state.set_cycle_state(cycle, phase, work_id)
    if ok:
        return {"success": True, "cycle": cycle, "phase": phase, "work_id": work_id}
    return {"success": False, "error": "set_cycle_state failed — check haios-status-slim.json"}


@mcp.tool()
def cycle_get(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Get current session_state from haios-status-slim.json.

    Args:
        project_root: Optional project root path (defaults to _PROJECT_ROOT).
                      Exposed for testability — tests pass tmp_path.

    Returns:
        Session state dict with keys: active_cycle, current_phase, work_id,
        entered_at, active_queue, phase_history. Or {"error": "..."} on failure.
    """
    try:
        root = project_root or _PROJECT_ROOT
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return {"error": "haios-status-slim.json not found"}
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        return data.get("session_state", {"error": "session_state key missing"})
    except Exception as e:
        logger.error(f"cycle_get failed: {e}")
        return {"error": str(e)}


@mcp.tool()
def cycle_clear() -> Dict[str, Any]:
    """Zero out session_state in haios-status-slim.json (all fields set to null/empty).

    Returns:
        {"success": True} or {"success": False, "error": "..."}
    """
    ok = cycle_state.clear_cycle_state()
    if ok:
        return {"success": True}
    return {"success": False, "error": "clear_cycle_state failed — check haios-status-slim.json"}


if __name__ == "__main__":
    mcp.run()
```

#### File 4 (MODIFY): `.mcp.json`

**Location:** Full file replacement (11 lines → 16 lines)

**Current Code:**
```json
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": ["-m", "haios_etl.mcp_server"],
      "env": {
        "DB_PATH": "haios_memory.db"
      }
    }
  }
}
```

**Target Code:**
```json
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": ["-m", "haios_etl.mcp_server"],
      "env": {
        "DB_PATH": "haios_memory.db"
      }
    },
    "haios-operations": {
      "command": "python",
      "args": ["-m", "haios_ops.mcp_server"],
      "env": {
        "PYTHONPATH": ".claude/haios"
      }
    }
  }
}
```

**Rationale for `PYTHONPATH`:** `PYTHONPATH=.claude/haios` makes `haios_ops` discoverable as a package when running `python -m haios_ops.mcp_server` from project root (default cwd). Avoids `${workspaceFolder}` variable expansion dependency (critique A4). bootstrap.py derives module paths from `__file__` location, not cwd — safe regardless of where the process starts.

**Diff:**
```diff
   "mcpServers": {
     "haios-memory": {
       "command": "python",
       "args": ["-m", "haios_etl.mcp_server"],
       "env": {
         "DB_PATH": "haios_memory.db"
       }
-    }
+    },
+    "haios-operations": {
+      "command": "python",
+      "args": ["-m", "haios_ops.mcp_server"],
+      "env": {
+        "PYTHONPATH": ".claude/haios"
+      }
+    }
   }
```

### Call Chain

```
Agent calls: mcp__haios-operations__work_get(work_id="WORK-220")
    |
    +-> work_get(work_id) in mcp_server.py
    |       |
    |       +-> _engine.get_work("WORK-220")   # WorkEngine.get_work()
    |               Returns: WorkState dataclass
    |
    +-> _work_to_dict(work)
    |       Returns: Dict[str, Any]  (JSON-serializable)
    |
    Returns: {"id": "WORK-220", "title": "...", "status": "active", ...}

Agent calls: mcp__haios-operations__queue_commit(work_id="WORK-220")
    |
    +-> queue_commit(work_id) in mcp_server.py
    |       |
    |       +-> execute_queue_transition(_engine, "WORK-220", "working", "Commit")
    |               |
    |               +-> _engine.set_queue_position("WORK-220", "working")
    |               +-> log_queue_ceremony("Commit", ["WORK-220"], ...)
    |               Returns: {success: True, work: WorkState}
    |
    Returns: {"success": True}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package location: `.claude/haios/haios_ops/` vs project root | `.claude/haios/haios_ops/` | Operator directive S450. Portability — the whole `.claude/haios/` subtree is self-contained. Mirrors logic of haios_etl living under its own directory. |
| Package discovery in .mcp.json | `env: { PYTHONPATH: .claude/haios }` with `-m haios_ops.mcp_server` | Avoids `${workspaceFolder}` expansion risk in `cwd` field. PYTHONPATH makes `haios_ops` discoverable as package from project root. Relative path follows same convention as `DB_PATH: haios_memory.db` in haios-memory entry. bootstrap.py derives module paths from `__file__`, not cwd. |
| bootstrap.py as separate module vs inline in mcp_server.py | Separate bootstrap.py | Testable in isolation (critique A2). `from . import bootstrap` in mcp_server.py is one line. cli.py precedent (same pattern). |
| Module-level WorkEngine instance vs per-tool instantiation | Module-level `_engine` | Single process — shared state reduces overhead. Mirrors haios_etl/mcp_server.py pattern (module-level db_manager, retrieval_service). |
| `dataclasses.asdict()` for WorkState serialization | `asdict()` + Path→str fix | WorkState is a dataclass; asdict() is the canonical conversion. Path fields need str() conversion for JSON. Avoids manual field enumeration that would miss new fields. |
| GovernanceLayer: deferred vs inline | Deferred to Phase 3 | WORK-218 explicit decision. Phase 1 tools use `ceremony_context` for ceremony boundaries but do not call `check_activity()`. Governance gap is documented, not ignored. |
| `session_end` implementation | Calls `governance_events.log_session_end` directly | session_mgmt.py only has `start_session`. end_session would be symmetric but is a one-liner — implement inline in mcp_server.py rather than adding to session_mgmt.py out of WORK-219 scope. |
| Return type annotation: `Dict[str, Any]` vs `str` | `Dict[str, Any]` | Typed JSON dicts, not prose strings. FastMCP serializes dict returns to JSON automatically. WORK-218 F4: "structured return eliminates prose-to-struct extraction". |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| work_get: work_id not found | Return `{"error": "not found", "work_id": "..."}` | Test 3 |
| work_transition: invalid node | Return `{"success": False, "error": "Invalid transition: ..."}` | Test 6 (mock raises InvalidTransitionError) |
| queue_next: empty queue | Return `{"next": null, "queue": "<name>"}` | Test 9 |
| queue_commit: already at `working` | execute_queue_transition returns `{success: False, error: "... already at 'working'"}` — propagated | Test 11 (mock returns failure) |
| session_start: partial failure | start_session returns False — return `{"success": False, "error": "..."}` | Test 13 |
| cycle_get: slim file missing | Return `{"error": "haios-status-slim.json not found"}` | Test 16 (slim_file.exists() = False) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| bootstrap.py path derivation fails if package moves | H | bootstrap.py uses `Path(__file__).parent.parent` — anchored to file location, not cwd. Test 1 verifies both paths are in sys.path after import. |
| `bootstrap` name collision with other bootstrap.py | L | Resolved by `from . import bootstrap` (explicit relative import, PEP 328). No risk of shadowing — scoped to haios_ops package. |
| `dataclasses.asdict()` fails on non-dataclass WorkState | L | WorkState is decorated with `@dataclass` at line 90 of work_engine.py. Confirmed. |
| ceremony_context import fails in server context | M | work_engine.py uses try/except ImportError for all sibling imports (confirmed pattern). mcp_server.py uses same pattern for governance_layer import (covered by bootstrap). |
| `PYTHONPATH=.claude/haios` is relative — requires MCP host to run from project root | M | Same convention as `DB_PATH: haios_memory.db` in haios-memory entry. Verify in Step 4: `python -c "import sys; sys.path.insert(0,'.claude/haios'); import haios_ops; print('ok')"` from project root. |
| governance_events.log_session_end missing (WORK-219 scope boundary) | M | Grep governance_events.py for `log_session_end` before DO phase. If absent, implement inline in session_end tool with governance_events.log_* call pattern. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_mcp_operations.py` with all 16 test functions from Layer 1 Tests section; use `unittest.mock.patch` to mock WorkEngine, execute_queue_transition, cycle_state, session_mgmt
- **output:** Test file exists, all 16 tests fail (ImportError or AssertionError — haios_ops not yet created)
- **verify:** `pytest tests/test_mcp_operations.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 16

### Step 2: Create Package Scaffold (haios_ops/)
- **spec_ref:** Layer 1 > Design > File 1 (NEW) + File 2 (NEW)
- **input:** Step 1 complete
- **action:** Create `.claude/haios/haios_ops/__init__.py` and `.claude/haios/haios_ops/bootstrap.py` from Layer 1 Design specs exactly
- **output:** Package directory exists with both files
- **verify:** `python -c "import sys; sys.path.insert(0, '.claude/haios'); import haios_ops.bootstrap; print('ok')"` prints `ok`; Test 1 passes: `pytest tests/test_mcp_operations.py::test_bootstrap_adds_both_paths -v` exits 0

### Step 3: Implement MCP Server (GREEN)
- **spec_ref:** Layer 1 > Design > File 3 (NEW)
- **input:** Step 2 complete (bootstrap works)
- **action:** Create `.claude/haios/haios_ops/mcp_server.py` from Layer 1 Design spec exactly; verify all 16 tests pass
- **output:** All 16 tests pass
- **verify:** `pytest tests/test_mcp_operations.py -v` exits 0, `16 passed` in output

### Step 4: Register in .mcp.json
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Step 3 complete (server implemented and tested)
- **action:** Update `.mcp.json` per Layer 1 Design diff — add `haios-operations` entry with `env.PYTHONPATH=.claude/haios` and `-m haios_ops.mcp_server` args
- **output:** `.mcp.json` has both server entries
- **verify:** `grep "haios-operations" .mcp.json` returns 1 match; `python -c "import json; d=json.load(open('.mcp.json')); print(list(d['mcpServers'].keys()))"` prints `['haios-memory', 'haios-operations']`; `python -c "import sys; sys.path.insert(0,'.claude/haios'); import haios_ops; print('ok')"` prints `ok`

### Step 5: Full Test Suite Regression Check
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Step 4 complete
- **action:** Run full pytest suite to verify no regressions
- **output:** 0 new failures vs baseline (1571 passed, 0 failed, 8 skipped)
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows same or more passed count, 0 new failures

---

## Ground Truth Verification

<!-- Computable verification protocol. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_mcp_operations.py -v` | 16 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs baseline (1571 passed pre-WORK-220) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| haios_ops package created | `ls .claude/haios/haios_ops/` | Shows `__init__.py bootstrap.py mcp_server.py` |
| bootstrap.py imports workable | `python -c "import sys; sys.path.insert(0,'.claude/haios'); import haios_ops.bootstrap; from work_engine import WorkEngine; print('ok')"` | `ok` |
| FastMCP server defined | `grep "FastMCP.*haios-operations" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| work tools present | `grep -c "@mcp.tool" .claude/haios/haios_ops/mcp_server.py` | 15 (matches ~15 @mcp.tool decorators) |
| queue tools named correctly | `grep "def queue_" .claude/haios/haios_ops/mcp_server.py` | 7 matches (queue_ready, queue_list, queue_next, queue_prioritize, queue_commit, queue_park, queue_unpark) |
| session tools named correctly | `grep "def session_\|def cycle_" .claude/haios/haios_ops/mcp_server.py` | 5 matches (session_start, session_end, cycle_set, cycle_get, cycle_clear) |
| .mcp.json updated | `grep "haios-operations" .mcp.json` | 1 match |
| JSON valid after update | `python -m json.tool .mcp.json` | No error |
| Test file created | `ls tests/test_mcp_operations.py` | File exists |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| haios-memory entry preserved | `grep "haios-memory" .mcp.json` | 1 match |
| No old pattern broken | `grep "haios_etl.mcp_server" .mcp.json` | 1 match (still present) |
| bootstrap path anchor correct | `python -c "from pathlib import Path; import sys; sys.path.insert(0,'.claude/haios'); import haios_ops.bootstrap as b; print(b.haios_dir if hasattr(b,'haios_dir') else 'anchored')"` | no ImportError |

### Completion Criteria (DoD)

- [ ] All 16 tests pass (Layer 2 Step 3 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] `.mcp.json` has both server entries and is valid JSON
- [ ] No stale references (haios-memory entry preserved)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- @docs/work/active/WORK-218/investigations/INVESTIGATION-WORK-218.md (source investigation — F1/F2/F5, tool taxonomy, architecture design)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (Tier model — this server IS Tier 2 for operations)
- @haios_etl/mcp_server.py (pattern: FastMCP init, module-level services, @mcp.tool decorators)
- @.mcp.json (registration target — add haios-operations entry)
- @.claude/haios/modules/work_engine.py (WorkEngine API: get_work, create_work, close, transition, get_ready, get_queue, get_next, set_queue_position)
- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition, log_queue_ceremony)
- @.claude/haios/lib/cycle_state.py (set_cycle_state, clear_cycle_state, set_active_queue — WORK-219 extractions)
- @.claude/haios/lib/session_mgmt.py (start_session — WORK-219 extraction)
- @.claude/haios/modules/cli.py (bootstrap pattern: dual sys.path setup from file location)
- Memory: 88698-88704 (WORK-218 investigation findings), 85949 (MCP tools auto-discovered), 85950 (Tier model), 85951 (operator vision)

---
