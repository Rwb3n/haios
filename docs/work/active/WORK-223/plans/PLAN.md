---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-223
title: "MCP Operations Extended Tools Phase 2"
author: Hephaestus
lifecycle_phase: plan
session: 452
generated: 2026-02-25
last_updated: 2026-02-25T12:22:05

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-223/WORK.md"
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
# Implementation Plan: MCP Operations Extended Tools Phase 2

---

## Goal

Extend `.claude/haios/haios_ops/mcp_server.py` with scaffold tools (scaffold_work, scaffold_plan), hierarchy tools (cascade, update_status, close_work), a coldstart tool (coldstart_orchestrator), and MCP Resources for read-only CQRS queries, completing the CH-066 exit criterion that the haios-operations MCP server exposes work/hierarchy/session/scaffold tools.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No unresolved operator decisions | — | — | operator_decisions field is empty in WORK.md |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/haios_ops/mcp_server.py` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_mcp_operations.py` | imports and tests mcp_server tools | 98-336 | UPDATE (append new test groups) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_mcp_operations.py` | UPDATE | Append scaffold, hierarchy, coldstart, and resource test groups |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files — all additions go into existing mcp_server.py |
| Files to modify | 1 | mcp_server.py (primary) |
| Test files to update | 1 | test_mcp_operations.py (append new test groups) |
| Total blast radius | 2 | mcp_server.py + test_mcp_operations.py |

---

## Layer 1: Specification

### Current State

```python
# .claude/haios/haios_ops/mcp_server.py — top-level imports (lines 17-31)
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import bootstrap  # noqa: F401
from mcp.server.fastmcp import FastMCP
from governance_layer import GovernanceLayer, ceremony_context
from work_engine import WorkEngine, WorkState, WorkNotFoundError, InvalidTransitionError
from queue_ceremonies import execute_queue_transition
import cycle_state
import session_mgmt

# End of file (line 376)
if __name__ == "__main__":
    mcp.run()
```

**Behavior:** Server exposes 15 tools across work, queue, and session groups. No scaffold, hierarchy, coldstart, or resource endpoints exist.

**Problem:** Agents still invoke `just` recipes for scaffold, cascade, close-work, update-status, and coldstart. The CH-066 exit criterion requires these to be MCP tools. CQRS pattern (resources for reads) is not implemented.

### Desired State

```python
# .claude/haios/haios_ops/mcp_server.py — new imports appended after existing imports
# Intentional direct import of scaffold.py (not GovernanceLayer.scaffold_template)
# because MCP server is a self-governing boundary (WORK-218 F3).
from scaffold import scaffold_template, get_next_work_id
from status_propagator import StatusPropagator
from coldstart_orchestrator import ColdstartOrchestrator

# ---------------------------------------------------------------------------
# Scaffold tools
# ---------------------------------------------------------------------------

@mcp.tool()
def scaffold_work(
    title: str,
    work_id: Optional[str] = None,
    work_type: str = "implementation",
) -> Dict[str, Any]:
    """Scaffold a new work item from template.

    Args:
        title: Human-readable title for the work item
        work_id: Optional explicit ID (e.g., "WORK-225"). If omitted, auto-incremented.
        work_type: Template TYPE variable: implementation | investigation | etc. (default: implementation)

    Returns:
        {"success": True, "path": "<work_md_path>", "work_id": "<id>"} or {"success": False, "error": "..."}
    """
    try:
        backlog_id = work_id or get_next_work_id()
        path = scaffold_template(
            "work_item",
            backlog_id=backlog_id,
            title=title,
            variables={"TYPE": work_type},
        )
        return {"success": True, "path": path, "work_id": backlog_id}
    except Exception as e:
        logger.error(f"scaffold_work failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_plan(
    work_id: str,
    title: str,
    plan_type: str = "implementation",
) -> Dict[str, Any]:
    """Scaffold an implementation plan for an existing work item.

    Args:
        work_id: Work item ID the plan belongs to (e.g., "WORK-223")
        title: Plan title
        plan_type: Plan template variant: implementation | design | cleanup (default: implementation)

    Returns:
        {"success": True, "path": "<plan_md_path>"} or {"success": False, "error": "..."}
    """
    try:
        path = scaffold_template(
            "implementation_plan",
            backlog_id=work_id,
            title=title,
            variables={"TYPE": plan_type},
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_plan failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Hierarchy tools
# ---------------------------------------------------------------------------

@mcp.tool()
def hierarchy_cascade(work_id: str) -> Dict[str, Any]:
    """Propagate work item closure status up to chapter and arc.

    Runs StatusPropagator.propagate() which:
    1. Checks if all chapter work items are complete
    2. Updates chapter row status in ARC.md
    3. Checks if entire arc is complete
    4. Logs StatusPropagation governance event

    Args:
        work_id: Closed work item ID (e.g., "WORK-223")

    Returns:
        Dict with keys: action, work_id, chapter, arc, arc_updated, arc_complete.
        action is one of: no_hierarchy | chapter_incomplete | chapter_completed | arc_completed
    """
    try:
        propagator = StatusPropagator()
        return propagator.propagate(work_id)
    except Exception as e:
        logger.error(f"hierarchy_cascade failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def hierarchy_update_status(
    work_id: str,
    status: str,
) -> Dict[str, Any]:
    """Update work item status field and optionally cascade to chapter/arc.

    Uses get_work() + direct mutation + _write_work_file() because
    WorkEngine has no public set_status() method.

    Args:
        work_id: Work item ID (e.g., "WORK-223")
        status: New status value (e.g., "complete", "active", "blocked")

    Returns:
        {"success": True, "work_id": ..., "status": ..., "cascade": <propagate result>}
        or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("update-status"):
            work = _engine.get_work(work_id)
            if work is None:
                raise WorkNotFoundError(f"Work item {work_id} not found")
            work.status = status
            _engine._write_work_file(work)
        cascade_result = {}
        if status in ("complete", "completed", "done", "closed"):
            propagator = StatusPropagator()
            cascade_result = propagator.propagate(work_id)
        return {
            "success": True,
            "work_id": work_id,
            "status": status,
            "cascade": cascade_result,
        }
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"hierarchy_update_status failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def hierarchy_close_work(work_id: str) -> Dict[str, Any]:
    """Close a work item and cascade status to chapter/arc atomically.

    Combines WorkEngine.close() + StatusPropagator.propagate() in one call,
    replacing the 3-subprocess just close-work recipe (WORK-218 F6).

    Args:
        work_id: Work item ID to close (e.g., "WORK-223")

    Returns:
        {"success": True, "work_id": ..., "cascade": <propagate result>}
        or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("close-work"):
            _engine.close(work_id)
        propagator = StatusPropagator()
        cascade_result = propagator.propagate(work_id)
        return {
            "success": True,
            "work_id": work_id,
            "cascade": cascade_result,
        }
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"hierarchy_close_work failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Coldstart tool
# ---------------------------------------------------------------------------

@mcp.tool()
def coldstart_orchestrator(tier: str = "auto") -> Dict[str, Any]:
    """Run the coldstart orchestrator and return its output.

    Wraps ColdstartOrchestrator().run(tier=tier). Tier controls which
    loaders are included: full | light | minimal | auto.

    Args:
        tier: Coldstart tier: auto | full | light | minimal (default: auto)

    Returns:
        {"success": True, "output": "<coldstart text>", "tier": "<resolved tier>"}
        or {"success": False, "error": "..."}
    """
    try:
        orch = ColdstartOrchestrator()
        output = orch.run(tier=tier)
        return {"success": True, "output": output, "tier": tier}
    except Exception as e:
        logger.error(f"coldstart_orchestrator failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# MCP Resources (CQRS read pattern — WORK-218 F4)
# ---------------------------------------------------------------------------

@mcp.resource("work://{work_id}")
def resource_work_item(work_id: str) -> Dict[str, Any]:
    """Read-only work item state by URI (CQRS pattern).

    URI: work://WORK-223
    Returns typed WorkState dict or {"error": "not found"} if not found.
    """
    work = _engine.get_work(work_id)
    if work is None:
        return {"error": "not found", "work_id": work_id}
    return _work_to_dict(work)


@mcp.resource("haios://queue/ready")
def resource_queue_ready() -> List[Dict[str, Any]]:
    """Read-only list of ready queue items (CQRS pattern).

    URI: haios://queue/ready
    Returns list of WorkState dicts for all unblocked active items.
    """
    items = _engine.get_ready()
    return [_work_to_dict(w) for w in items]


@mcp.resource("haios://queue/{queue_name}")
def resource_queue(queue_name: str) -> List[Dict[str, Any]]:
    """Read-only ordered list of items from a named queue (CQRS pattern).

    URI: haios://queue/default
    Returns ordered list of WorkState dicts.
    """
    items = _engine.get_queue(queue_name)
    return [_work_to_dict(w) for w in items]


if __name__ == "__main__":
    mcp.run()
```

**Behavior:** mcp_server.py gains scaffold_work, scaffold_plan, hierarchy_cascade, hierarchy_update_status, hierarchy_close_work, coldstart_orchestrator tools, and 3 MCP Resources.

**Result:** Agents can scaffold work items, run cascade propagation, close work atomically, and run coldstart — all via typed MCP tool calls. Work item and queue state are URI-addressable read-only resources.

### Tests

#### Test 17: scaffold_work creates work item
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_work_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server.scaffold_template")` + `@patch("haios_ops.mcp_server.get_next_work_id")` returning `"WORK-225"` and `"/fake/WORK.md"` respectively
- **assertion:** `result == {"success": True, "path": "/fake/WORK.md", "work_id": "WORK-225"}`

#### Test 18: scaffold_plan creates plan
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_plan_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server.scaffold_template")` returning `"/fake/plans/PLAN.md"`
- **assertion:** `result == {"success": True, "path": "/fake/plans/PLAN.md"}`

#### Test 19: scaffold_work handles exception
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_work_error()`
- **setup:** `@patch("haios_ops.mcp_server.scaffold_template")` raising `ValueError("template not found")`
- **assertion:** `result["success"] is False` and `"template not found" in result["error"]`

#### Test 20: hierarchy_cascade returns propagation result
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_hierarchy_cascade_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server.StatusPropagator")` returning mock with `propagate.return_value = {"action": "chapter_completed", "work_id": "WORK-223", "chapter": "CH-066", "arc": "call", "arc_updated": True, "arc_complete": False}`
- **assertion:** `result["action"] == "chapter_completed"` and `result["chapter"] == "CH-066"`

#### Test 21: hierarchy_close_work closes and cascades atomically
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_hierarchy_close_work_atomic()`
- **setup:** `@patch("haios_ops.mcp_server.ceremony_context")` + `@patch("haios_ops.mcp_server._engine")` + `@patch("haios_ops.mcp_server.StatusPropagator")`. Mock engine.close returns None. Mock propagator.propagate returns `{"action": "chapter_incomplete", "work_id": "WORK-223"}`.
- **assertion:** `result["success"] is True` and `result["cascade"]["action"] == "chapter_incomplete"`. Both `_engine.close` and `StatusPropagator().propagate` called once.

#### Test 22: hierarchy_update_status with complete status runs cascade
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_hierarchy_update_status_complete_cascades()`
- **setup:** `@patch("haios_ops.mcp_server.ceremony_context")` + `@patch("haios_ops.mcp_server._engine")` + `@patch("haios_ops.mcp_server.StatusPropagator")`. Mock `_engine.get_work` returns `_make_work_state(id="WORK-223")`. Mock `_engine._write_work_file` as no-op. Mock propagator returns `{"action": "chapter_incomplete"}`.
- **assertion:** `result["success"] is True`, `result["status"] == "complete"`, `result["cascade"]["action"] == "chapter_incomplete"`. `_engine._write_work_file` called once.

#### Test 23: hierarchy_update_status with non-complete status skips cascade
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_hierarchy_update_status_active_skips_cascade()`
- **setup:** `@patch("haios_ops.mcp_server.ceremony_context")` + `@patch("haios_ops.mcp_server._engine")` + `@patch("haios_ops.mcp_server.StatusPropagator")`. Mock `_engine.get_work` returns `_make_work_state(id="WORK-223")`. Mock `_engine._write_work_file` as no-op. Propagator should NOT be called.
- **assertion:** `result["success"] is True`, `result["cascade"] == {}`, `StatusPropagator` mock NOT called. `_engine._write_work_file` called once.

#### Test 28: scaffold_plan handles missing work item
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_scaffold_plan_missing_work_item()`
- **setup:** `@patch("haios_ops.mcp_server.scaffold_template")` raising `ValueError("Work file required.")`
- **assertion:** `result["success"] is False` and `"Work file required" in result["error"]`

#### Test 24: coldstart_orchestrator returns output dict
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_coldstart_orchestrator_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server.ColdstartOrchestrator")` returning mock with `run.return_value = "[IDENTITY]\n...coldstart output..."`
- **assertion:** `result["success"] is True`, `"coldstart output" in result["output"]`, `result["tier"] == "auto"`

#### Test 25: coldstart_orchestrator passes tier parameter
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_coldstart_orchestrator_tier_param()`
- **setup:** `@patch("haios_ops.mcp_server.ColdstartOrchestrator")` with mock run returning short string
- **assertion:** `result["tier"] == "light"` and `mock_orch_instance.run.call_args[1]["tier"] == "light"`

#### Test 26: resource_work_item returns work state dict
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_resource_work_item_returns_dict()`
- **setup:** `@patch("haios_ops.mcp_server._engine")` with `get_work.return_value = _make_work_state(id="WORK-220")`
- **assertion:** `result["id"] == "WORK-220"` — confirms resource uses same _work_to_dict helper

#### Test 27: resource_queue_ready returns list
- **file:** `tests/test_mcp_operations.py`
- **function:** `test_resource_queue_ready_returns_list()`
- **setup:** `@patch("haios_ops.mcp_server._engine")` with `get_ready.return_value = [_make_work_state(id="WORK-001")]`
- **assertion:** `isinstance(result, list)` and `result[0]["id"] == "WORK-001"`

### Design

#### File 1 (MODIFY): `.claude/haios/haios_ops/mcp_server.py`

**Step A — Append new imports after existing import block (after line 31, before line 33 `logging.basicConfig`):**

**Current Code (lines 17-32):**
```python
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
```

**Target Code (lines 17-35):**
```python
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
# Intentional direct import of scaffold.py (not GovernanceLayer.scaffold_template)
# because MCP server is a self-governing boundary (WORK-218 F3) — GovernanceLayer
# wrapper adds ceremony context overhead that the MCP server handles itself.
from scaffold import scaffold_template, get_next_work_id
from status_propagator import StatusPropagator
from coldstart_orchestrator import ColdstartOrchestrator
```

**Step B — Replace `if __name__ == "__main__":` block with all new tool groups + resources + original block:**

The `if __name__ == "__main__":` block at line 375-376 is the insertion point. All new code is inserted before it.

**Complete new sections to insert before `if __name__ == "__main__":`:**

```python
# ---------------------------------------------------------------------------
# Scaffold tools
# ---------------------------------------------------------------------------

@mcp.tool()
def scaffold_work(
    title: str,
    work_id: Optional[str] = None,
    work_type: str = "implementation",
) -> Dict[str, Any]:
    """Scaffold a new work item from template.

    Args:
        title: Human-readable title for the work item
        work_id: Optional explicit ID (e.g., "WORK-225"). If omitted, auto-incremented.
        work_type: Template TYPE variable: implementation | investigation | etc. (default: implementation)

    Returns:
        {"success": True, "path": "<work_md_path>", "work_id": "<id>"}
        or {"success": False, "error": "..."}
    """
    try:
        backlog_id = work_id or get_next_work_id()
        path = scaffold_template(
            "work_item",
            backlog_id=backlog_id,
            title=title,
            variables={"TYPE": work_type},
        )
        return {"success": True, "path": path, "work_id": backlog_id}
    except Exception as e:
        logger.error(f"scaffold_work failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_plan(
    work_id: str,
    title: str,
    plan_type: str = "implementation",
) -> Dict[str, Any]:
    """Scaffold an implementation plan for an existing work item.

    Args:
        work_id: Work item ID the plan belongs to (e.g., "WORK-223")
        title: Plan title
        plan_type: Plan template variant: implementation | design | cleanup (default: implementation)

    Returns:
        {"success": True, "path": "<plan_md_path>"} or {"success": False, "error": "..."}
    """
    try:
        path = scaffold_template(
            "implementation_plan",
            backlog_id=work_id,
            title=title,
            variables={"TYPE": plan_type},
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_plan failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Hierarchy tools
# ---------------------------------------------------------------------------

@mcp.tool()
def hierarchy_cascade(work_id: str) -> Dict[str, Any]:
    """Propagate work item closure status up to chapter and arc.

    Args:
        work_id: Closed work item ID (e.g., "WORK-223")

    Returns:
        Dict with keys: action, work_id, chapter, arc, arc_updated, arc_complete.
        action: no_hierarchy | chapter_incomplete | chapter_completed | arc_completed
    """
    try:
        propagator = StatusPropagator()
        return propagator.propagate(work_id)
    except Exception as e:
        logger.error(f"hierarchy_cascade failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def hierarchy_update_status(
    work_id: str,
    status: str,
) -> Dict[str, Any]:
    """Update work item status field and optionally cascade to chapter/arc.

    Uses WorkEngine.get_work() + direct status mutation + _write_work_file()
    because WorkEngine has no public set_status() method. This follows the
    same pattern as WorkEngine.close() (lines 587-607 of work_engine.py).

    Cascade runs automatically when status is complete/done/closed.

    Args:
        work_id: Work item ID (e.g., "WORK-223")
        status: New status value (e.g., "complete", "active", "blocked")

    Returns:
        {"success": True, "work_id": ..., "status": ..., "cascade": <propagate result>}
        or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("update-status"):
            work = _engine.get_work(work_id)
            if work is None:
                raise WorkNotFoundError(f"Work item {work_id} not found")
            work.status = status
            _engine._write_work_file(work)
        cascade_result: Dict[str, Any] = {}
        if status in ("complete", "completed", "done", "closed"):
            propagator = StatusPropagator()
            cascade_result = propagator.propagate(work_id)
        return {
            "success": True,
            "work_id": work_id,
            "status": status,
            "cascade": cascade_result,
        }
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"hierarchy_update_status failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def hierarchy_close_work(work_id: str) -> Dict[str, Any]:
    """Close a work item and cascade status to chapter/arc atomically.

    Replaces the 3-subprocess just close-work recipe (WORK-218 F6).
    Combines WorkEngine.close() + StatusPropagator.propagate() in one call.

    Args:
        work_id: Work item ID to close (e.g., "WORK-223")

    Returns:
        {"success": True, "work_id": ..., "cascade": <propagate result>}
        or {"success": False, "error": "..."}
    """
    try:
        with ceremony_context("close-work"):
            _engine.close(work_id)
        propagator = StatusPropagator()
        cascade_result = propagator.propagate(work_id)
        return {
            "success": True,
            "work_id": work_id,
            "cascade": cascade_result,
        }
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"hierarchy_close_work failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Coldstart tool
# ---------------------------------------------------------------------------

@mcp.tool()
def coldstart_orchestrator(tier: str = "auto") -> Dict[str, Any]:
    """Run the coldstart orchestrator and return its output as a typed dict.

    Note: Function name 'coldstart_orchestrator' does not collide with
    the imported class 'ColdstartOrchestrator' (Python is case-sensitive).

    Args:
        tier: Coldstart tier: auto | full | light | minimal (default: auto)

    Returns:
        {"success": True, "output": "<coldstart text>", "tier": "<tier>"}
        or {"success": False, "error": "..."}
    """
    try:
        orch = ColdstartOrchestrator()
        output = orch.run(tier=tier)
        return {"success": True, "output": output, "tier": tier}
    except Exception as e:
        logger.error(f"coldstart_orchestrator failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# MCP Resources (CQRS read pattern — WORK-218 F4)
# ---------------------------------------------------------------------------

@mcp.resource("work://{work_id}")
def resource_work_item(work_id: str) -> Dict[str, Any]:
    """Read-only work item state addressed by URI.

    URI pattern: work://WORK-223
    Returns typed WorkState dict or {"error": "not found", "work_id": ...}.
    """
    work = _engine.get_work(work_id)
    if work is None:
        return {"error": "not found", "work_id": work_id}
    return _work_to_dict(work)


@mcp.resource("haios://queue/ready")
def resource_queue_ready() -> List[Dict[str, Any]]:
    """Read-only list of ready queue items.

    URI pattern: haios://queue/ready
    Returns list of WorkState dicts for all unblocked active items.
    """
    items = _engine.get_ready()
    return [_work_to_dict(w) for w in items]


@mcp.resource("haios://queue/{queue_name}")
def resource_queue(queue_name: str) -> List[Dict[str, Any]]:
    """Read-only ordered list of items from a named queue.

    URI pattern: haios://queue/default
    Returns ordered list of WorkState dicts.
    """
    items = _engine.get_queue(queue_name)
    return [_work_to_dict(w) for w in items]
```

**Diff summary:**
```diff
  import session_mgmt
+ from scaffold import scaffold_template, get_next_work_id
+ from status_propagator import StatusPropagator
+ from coldstart_orchestrator import ColdstartOrchestrator

  logging.basicConfig(level=logging.INFO)
  ...
  # (all new tool + resource functions inserted before if __name__ block)
```

### Call Chain

```
Agent calls mcp__haios-operations__scaffold_work(title="...")
    |
    +-> scaffold_work()          # mcp_server.py
    |       calls get_next_work_id()     # lib/scaffold.py
    |       calls scaffold_template()    # lib/scaffold.py
    |       Returns: {"success": True, "path": "...", "work_id": "..."}

Agent calls mcp__haios-operations__hierarchy_close_work(work_id="WORK-223")
    |
    +-> hierarchy_close_work()    # mcp_server.py
    |       calls _engine.close(work_id)         # work_engine.py
    |       creates StatusPropagator()            # lib/status_propagator.py
    |       calls propagator.propagate(work_id)  # -> ARC.md update + event log
    |       Returns: {"success": True, "cascade": {...}}

Agent reads resource work://WORK-223
    |
    +-> resource_work_item("WORK-223")   # mcp_server.py
    |       calls _engine.get_work(work_id)
    |       calls _work_to_dict(work)
    |       Returns: typed WorkState dict (cacheable)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tool name for coldstart | `coldstart_orchestrator` (not `coldstart_orchestrator_tool`) | No name collision — Python is case-sensitive: class `ColdstartOrchestrator` vs function `coldstart_orchestrator`. Matches WORK.md AC naming. Avoids unnecessary `_tool` suffix. |
| scaffold_template imported at module level | `from scaffold import scaffold_template, get_next_work_id` | Consistent with all other imports in mcp_server.py (module-level). Matches sibling pattern (cycle_state, session_mgmt already module-level). Aligns with E2-255 sibling pattern verification. |
| StatusPropagator instantiated per call | `StatusPropagator()` inside each tool function | StatusPropagator has no shared mutable state across calls; instantiating per call avoids stale path state. Same pattern as governance_events.log_session_end (inline import per call in session_end). |
| ColdstartOrchestrator instantiated per call | `ColdstartOrchestrator()` inside coldstart_orchestrator_tool | ColdstartOrchestrator reads config on init; per-call ensures fresh config read. Consistent with modules/cli.py:304 `orch = ColdstartOrchestrator()` pattern. |
| hierarchy_update_status uses get_work + _write_work_file | Direct status mutation following WorkEngine.close() pattern (lines 587-607) | WorkEngine has no public set_status(). Using get_work() + mutate + _write_work_file() matches the canonical close() pattern. _write_work_file is private but is the L4 invariant single-writer path. |
| CQRS resource URIs | `work://{work_id}`, `haios://queue/ready`, `haios://queue/{queue_name}` | Directly from WORK-218 F4 spec: "work://WORK-218" for work items, "haios://queue/ready" for queue state. Uses investigative spec as source of truth. |
| Resources read from _engine directly | Resources call `_engine.get_work()` / `_engine.get_ready()` — same as tools | No duplicate code. Resources are read-only (CQRS), tools are mutations. Resources are naturally idempotent. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| scaffold_work with no work_id | Calls get_next_work_id() for auto-increment | Test 17 |
| scaffold_work with explicit work_id | Skips get_next_work_id(), uses provided ID | (covered by Test 17 mock pattern) |
| hierarchy_cascade on work with no chapter/arc | StatusPropagator returns {"action": "no_hierarchy"} | Test 20 |
| hierarchy_update_status with "active" status | cascade dict is empty `{}`, no propagation | Test 23 |
| hierarchy_close_work on missing work item | WorkNotFoundError caught, returns {"success": False, "error": "..."} | Test 21 error path |
| coldstart_orchestrator failure | Any exception caught, returns {"success": False, "error": str(e)} | Test 24 error path |
| resource_work_item not found | Returns {"error": "not found", "work_id": ...} — same as work_get | Test 26 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| _write_work_file is a private method | Med | WorkEngine._write_work_file() is the L4 invariant single-writer. Using it from MCP server is necessary because no public set_status() exists. If WorkEngine adds a public API in future, migrate to it. Document the coupling in a code comment. |
| scaffold_template PRIORITY variable | Low | RESOLVED: work_item.md template has no {{PRIORITY}} placeholder. Removed priority param from scaffold_work to avoid silent no-op. Priority defaults to 'medium' in template; callers update after scaffold. |
| FastMCP @mcp.resource return type annotation | Low | RESOLVED: `hasattr(FastMCP, 'resource')` confirmed True. If resource requires str return, wrap with json.dumps(). Smoke test during Step 7. |
| ColdstartOrchestrator output is very long | Low | Output truncation is caller's problem (agent decides how much to read). Tool returns full string — consistent with how cmd_coldstart prints full output. |
| StatusPropagator imported at module level collides with lazy import inside status_propagator.py | Low | StatusPropagator uses lazy `from hierarchy_engine import HierarchyQueryEngine` inside __init__. This is fine — module-level import of StatusPropagator class is safe; lazy sub-import is inside instance init. |

---

## Layer 2: Implementation Steps

### Step 1: Verify WorkEngine._write_work_file() accessibility (PRE-CHECK)
- **spec_ref:** Layer 1 > Key Design Decisions > hierarchy_update_status
- **input:** WorkEngine source available at `.claude/haios/modules/work_engine.py`
- **action:** Confirm `_write_work_file` method exists and is callable from MCP server via `_engine._write_work_file(work)`. WorkEngine has no public set_status() — hierarchy_update_status uses get_work() + direct mutation + _write_work_file() pattern (same as WorkEngine.close()).
- **output:** Confirmed _write_work_file callable on _engine instance
- **verify:** `grep "def _write_work_file" .claude/haios/modules/work_engine.py` returns 1 match

### Step 2: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests (Tests 17-27)
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Append test groups for scaffold (Tests 17-19), hierarchy (Tests 20-23), coldstart (Tests 24-25), and resources (Tests 26-27) to `tests/test_mcp_operations.py`
- **output:** Test file updated, all 12 new tests fail (ImportError or AttributeError — tool functions don't exist yet)
- **verify:** `pytest tests/test_mcp_operations.py -k "scaffold_work or scaffold_plan or hierarchy or coldstart or resource" -v 2>&1 | grep -c "FAILED\|ERROR"` equals 12

### Step 3: Add imports to mcp_server.py
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) > Step A
- **input:** Step 2 complete
- **action:** Append 3 import lines after `import session_mgmt` in mcp_server.py: `from scaffold import scaffold_template, get_next_work_id`, `from status_propagator import StatusPropagator`, `from coldstart_orchestrator import ColdstartOrchestrator`
- **output:** Imports added, no import errors at module load
- **verify:** `python -c "import sys; sys.path.insert(0, '.claude/haios'); sys.path.insert(0, '.claude/haios/lib'); sys.path.insert(0, '.claude/haios/modules'); from haios_ops import mcp_server"` exits 0

### Step 4: Implement scaffold tool group (GREEN partial)
- **spec_ref:** Layer 1 > Design > File 1 > scaffold tools section
- **input:** Step 3 complete (imports work)
- **action:** Insert scaffold_work and scaffold_plan tool functions before `if __name__ == "__main__":` in mcp_server.py
- **output:** scaffold_work and scaffold_plan callable; Tests 17-19, 28 pass
- **verify:** `pytest tests/test_mcp_operations.py -k "scaffold" -v` exits 0, 4 passed

### Step 5: Implement hierarchy tool group (GREEN partial)
- **spec_ref:** Layer 1 > Design > File 1 > hierarchy tools section
- **input:** Step 4 complete
- **action:** Insert hierarchy_cascade, hierarchy_update_status, hierarchy_close_work tool functions before `if __name__ == "__main__":`
- **output:** Hierarchy tools callable; Tests 20-23 pass
- **verify:** `pytest tests/test_mcp_operations.py -k "hierarchy" -v` exits 0, 4 passed

### Step 6: Implement coldstart tool (GREEN partial)
- **spec_ref:** Layer 1 > Design > File 1 > coldstart tool section
- **input:** Step 5 complete
- **action:** Insert coldstart_orchestrator function before `if __name__ == "__main__":`
- **output:** Coldstart tool callable; Tests 24-25 pass
- **verify:** `pytest tests/test_mcp_operations.py -k "coldstart" -v` exits 0, 2 passed

### Step 7: Implement MCP Resources (GREEN partial)
- **spec_ref:** Layer 1 > Design > File 1 > MCP Resources section
- **input:** Step 6 complete
- **action:** Insert resource_work_item, resource_queue_ready, resource_queue resource functions before `if __name__ == "__main__":`
- **output:** Resource functions defined; Tests 26-27 pass
- **verify:** `pytest tests/test_mcp_operations.py -k "resource" -v` exits 0, 2 passed

### Step 8: Full test suite regression check
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Steps 4-7 complete (all new tests green)
- **action:** Run full test suite to check for regressions
- **output:** All prior tests still pass, 12 new tests pass
- **verify:** `pytest tests/test_mcp_operations.py -v` shows 28 passed, 0 failed

### Step 9: Run full project test suite
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 8 complete
- **action:** Run full pytest suite to confirm no regressions outside mcp_operations tests
- **output:** Full suite green (no new failures)
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures vs baseline (1571 passed)

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_mcp_operations.py -v` | 28 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -3` | 0 new failures vs pre-WORK-223 baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Scaffold tools added (scaffold_work, scaffold_plan) | `grep "def scaffold_work\|def scaffold_plan" .claude/haios/haios_ops/mcp_server.py` | 2 matches |
| Hierarchy tools added (cascade, update_status, close_work) | `grep "def hierarchy_cascade\|def hierarchy_update_status\|def hierarchy_close_work" .claude/haios/haios_ops/mcp_server.py` | 3 matches |
| Coldstart tool added | `grep "def coldstart_orchestrator" .claude/haios/haios_ops/mcp_server.py` | 1 match |
| MCP Resources added | `grep "@mcp.resource" .claude/haios/haios_ops/mcp_server.py` | 3 matches |
| All new tools return typed JSON dicts | `pytest tests/test_mcp_operations.py -k "scaffold or hierarchy or coldstart or resource" -v` | 12 passed |
| Tests cover all new tool groups | `grep "def test_scaffold\|def test_hierarchy\|def test_coldstart\|def test_resource" tests/test_mcp_operations.py` | 12 matches |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No missing imports at load time | `python -c "import sys; sys.path.insert(0,'.claude/haios'); sys.path.insert(0,'.claude/haios/lib'); sys.path.insert(0,'.claude/haios/modules'); from haios_ops import mcp_server"` | exits 0, no ImportError |
| Phase 1 tools unaffected | `pytest tests/test_mcp_operations.py -k "work_get or work_create or queue_list or session_start or cycle_set" -v` | All 16 original tests still pass |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 8 verify: 28 passed)
- [ ] All WORK.md deliverables verified (Deliverables table above)
- [ ] Runtime consumer exists — scaffold_work, hierarchy_close_work, coldstart_orchestrator defined in mcp_server.py
- [ ] No stale references (original Phase 1 tools unchanged)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/haios/haios_ops/mcp_server.py` — Phase 1 server to extend
- `.claude/haios/lib/scaffold.py:504` — scaffold_template() signature
- `.claude/haios/lib/status_propagator.py` — StatusPropagator.propagate()
- `.claude/haios/lib/coldstart_orchestrator.py` — ColdstartOrchestrator().run(tier=)
- `.claude/haios/modules/cli.py:280` — cmd_coldstart() usage pattern
- `tests/test_mcp_operations.py` — existing test patterns to follow
- `docs/work/active/WORK-218/investigations/INVESTIGATION-WORK-218.md` — F4 (Resources/CQRS spec), F5 (naming), F6 (atomic ops)
- `docs/ADR/ADR-045-three-tier-entry-point-architecture.md` — Tier 2 MCP pattern
- `docs/work/active/WORK-220/WORK.md` — Phase 1 prerequisite

---
