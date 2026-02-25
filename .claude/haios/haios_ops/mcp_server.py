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

Phase 2 (WORK-223): scaffold, hierarchy, coldstart tools + MCP resources.
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
# Intentional direct import of scaffold.py (not GovernanceLayer.scaffold_template)
# because MCP server is a self-governing boundary (WORK-218 F3).
from scaffold import scaffold_template, get_next_work_id
from status_propagator import StatusPropagator
from coldstart_orchestrator import ColdstartOrchestrator

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


def _get_current_state() -> str:
    """Get current governance state from haios-status-slim.json.

    Reads directly from haios-status-slim.json (NOT get_activity_state() which
    shells out to `just get-cycle` — unavailable inside MCP server process).
    Fail-open: returns EXPLORE when no cycle is active (per CH-003).
    """
    try:
        slim_file = _PROJECT_ROOT / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "EXPLORE"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        session_state = data.get("session_state", {})
        phase = session_state.get("current_phase")
        return phase if phase else "EXPLORE"
    except Exception:
        return "EXPLORE"


def _check_tool_gate(
    primitive: str,
    tool_name: str,
    work_id: str = "unknown",
) -> Optional[Dict[str, Any]]:
    """Check governance gate for an MCP tool invocation.

    Returns None if allowed (caller proceeds normally).
    Returns error dict if blocked (caller returns this immediately).

    Args:
        primitive: MCP primitive type (e.g., "mcp-read", "mcp-mutate")
        tool_name: Tool function name for context/logging (e.g., "work_get")
        work_id: Work item ID if available, else "unknown"
    """
    state = _get_current_state()
    context = {"tool": tool_name, "work_id": work_id}
    result = _governance.check_activity(primitive, state, context)
    # Only log non-trivial gate decisions (blocked or warned) to avoid
    # unbounded governance-events.jsonl growth from always-allowed reads.
    if not result.allowed or result.reason != "Activity allowed":
        _log_governance_gate(tool_name, primitive, state, result.allowed, result.reason)
    if not result.allowed:
        return {"success": False, "error": f"Governance gate blocked: {result.reason}"}
    return None


def _log_governance_gate(
    tool_name: str,
    primitive: str,
    state: str,
    allowed: bool,
    reason: str,
) -> None:
    """Log MCP governance gate decision to governance-events.jsonl."""
    try:
        from governance_events import _append_event
        _append_event({
            "type": "MCPGateChecked",
            "tool": tool_name,
            "primitive": primitive,
            "state": state,
            "allowed": allowed,
            "reason": reason,
        })
    except Exception:
        pass  # Fail-permissive — gate logging must not break tool execution


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
    blocked = _check_tool_gate("mcp-read", "work_get", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-mutate", "work_create", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-mutate", "work_close", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-mutate", "work_transition", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-read", "queue_ready")
    if blocked:
        return []
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
    blocked = _check_tool_gate("mcp-read", "queue_list")
    if blocked:
        return []
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
    blocked = _check_tool_gate("mcp-read", "queue_next")
    if blocked:
        return {"error": "governance gate blocked", "queue": queue_name}
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
    blocked = _check_tool_gate("mcp-queue", "queue_prioritize", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-queue", "queue_commit", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-queue", "queue_park", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-queue", "queue_unpark", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-session", "session_start")
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-session", "session_end")
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-session", "cycle_set", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-read", "cycle_get")
    if blocked:
        return {"error": "governance gate blocked"}
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
    blocked = _check_tool_gate("mcp-session", "cycle_clear")
    if blocked:
        return blocked
    ok = cycle_state.clear_cycle_state()
    if ok:
        return {"success": True}
    return {"success": False, "error": "clear_cycle_state failed — check haios-status-slim.json"}


# ---------------------------------------------------------------------------
# Scaffold tools (WORK-223)
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
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_work")
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_plan", work_id)
    if blocked:
        return blocked
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
# Scaffold tools (WORK-226) — Phase 4: checkpoint, investigation, adr
# ---------------------------------------------------------------------------


@mcp.tool()
def scaffold_checkpoint(
    session_number: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold a checkpoint file for the current session.

    Args:
        session_number: Session number used as backlog_id (e.g., "455")
        title: Checkpoint title (e.g., "pre-compact")

    Returns:
        {"success": True, "path": "<checkpoint_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_checkpoint")
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "checkpoint",
            backlog_id=session_number,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_checkpoint failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_investigation(
    work_id: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold an investigation document inside a work item directory.

    Args:
        work_id: Work item ID the investigation belongs to (e.g., "WORK-226")
        title: Investigation title

    Returns:
        {"success": True, "path": "<investigation_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_investigation", work_id)
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "investigation",
            backlog_id=work_id,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_investigation failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def scaffold_adr(
    adr_number: str,
    title: str,
) -> Dict[str, Any]:
    """Scaffold an Architecture Decision Record (ADR) file.

    Args:
        adr_number: ADR number used as backlog_id (e.g., "049")
        title: ADR title (e.g., "Event Sourcing for Audit Trail")

    Returns:
        {"success": True, "path": "<adr_md_path>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-scaffold", "scaffold_adr")
    if blocked:
        return blocked
    try:
        path = scaffold_template(
            "architecture_decision_record",
            backlog_id=adr_number,
            title=title,
        )
        return {"success": True, "path": path}
    except Exception as e:
        logger.error(f"scaffold_adr failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Document link and spawn query tools (WORK-226) — Phase 4
# ---------------------------------------------------------------------------


@mcp.tool()
def link_document(
    work_id: str,
    doc_type: str,
    doc_path: str,
) -> Dict[str, Any]:
    """Link a document to a work item (plan, investigation, checkpoint).

    Updates cycle_docs and documents section of WORK.md.

    Args:
        work_id: Work item ID (e.g., "WORK-226")
        doc_type: Document type: plan | investigation | checkpoint
        doc_path: Path to the document being linked

    Returns:
        {"success": True, "work_id": ..., "doc_type": ..., "doc_path": ...}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-mutate", "link_document", work_id)
    if blocked:
        return blocked
    try:
        _engine.add_document_link(work_id, doc_type, doc_path)
        return {"success": True, "work_id": work_id, "doc_type": doc_type, "doc_path": doc_path}
    except WorkNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"link_document failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def spawn_tree(
    root_id: str,
    max_depth: int = 5,
) -> Dict[str, Any]:
    """Return spawn tree for a work item as formatted ASCII art and raw dict.

    Read-only query — no mutations. Scans active and archive WORK.md files
    for spawned_by relationships.

    Args:
        root_id: Root work item ID (e.g., "WORK-220")
        max_depth: Maximum recursion depth (default: 5)

    Returns:
        {"success": True, "root_id": ..., "tree": <nested dict>, "formatted": "<ascii art>"}
        or {"success": False, "error": "..."}
    """
    blocked = _check_tool_gate("mcp-read", "spawn_tree", root_id)
    if blocked:
        return blocked
    try:
        tree = _engine.spawn_tree(root_id, max_depth=max_depth)
        formatted = _engine.format_tree(tree, use_ascii=True)
        return {
            "success": True,
            "root_id": root_id,
            "tree": tree,
            "formatted": formatted,
        }
    except Exception as e:
        logger.error(f"spawn_tree failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Hierarchy tools (WORK-223)
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
    blocked = _check_tool_gate("mcp-cascade", "hierarchy_cascade", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-mutate", "hierarchy_update_status", work_id)
    if blocked:
        return blocked
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
    blocked = _check_tool_gate("mcp-mutate", "hierarchy_close_work", work_id)
    if blocked:
        return blocked
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
# Coldstart tool (WORK-223)
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
    blocked = _check_tool_gate("mcp-cascade", "coldstart_orchestrator")
    if blocked:
        return blocked
    try:
        orch = ColdstartOrchestrator()
        output = orch.run(tier=tier)
        return {"success": True, "output": output, "tier": tier}
    except Exception as e:
        logger.error(f"coldstart_orchestrator failed: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# MCP Resources (CQRS read pattern — WORK-218 F4, WORK-223)
# ---------------------------------------------------------------------------

@mcp.resource("work://{work_id}")
def resource_work_item(work_id: str) -> Dict[str, Any]:
    """Read-only work item state addressed by URI.

    URI pattern: work://WORK-223
    Returns typed WorkState dict or {"error": "not found", "work_id": ...}.
    """
    blocked = _check_tool_gate("mcp-read", "resource_work_item", work_id)
    if blocked:
        return {"error": "governance gate blocked", "work_id": work_id}
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
    blocked = _check_tool_gate("mcp-read", "resource_queue_ready")
    if blocked:
        return []
    items = _engine.get_ready()
    return [_work_to_dict(w) for w in items]


@mcp.resource("haios://queue/{queue_name}")
def resource_queue(queue_name: str) -> List[Dict[str, Any]]:
    """Read-only ordered list of items from a named queue.

    URI pattern: haios://queue/default
    Returns ordered list of WorkState dicts.
    """
    blocked = _check_tool_gate("mcp-read", "resource_queue")
    if blocked:
        return []
    items = _engine.get_queue(queue_name)
    return [_work_to_dict(w) for w in items]


if __name__ == "__main__":
    mcp.run()
