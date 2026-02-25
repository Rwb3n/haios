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
    # Path fields need str() conversion for JSON serialization
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
    if result.get("success"):
        return {"success": True}
    return {"success": False, "error": result.get("error")}


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
    if result.get("success"):
        return {"success": True}
    return {"success": False, "error": result.get("error")}


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
    if result.get("success"):
        return {"success": True}
    return {"success": False, "error": result.get("error")}


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
    if result.get("success"):
        return {"success": True}
    return {"success": False, "error": result.get("error")}


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
