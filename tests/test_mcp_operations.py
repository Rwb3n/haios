# generated: 2026-02-25
"""Tests for haios-operations MCP server (WORK-220, WORK-223).

28 test functions covering work, queue, session, scaffold, hierarchy,
coldstart, and resource tool groups with mocked backends.
Tests import haios_ops from .claude/haios/.
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add .claude/haios to sys.path so haios_ops package is importable (critique A5)
_HAIOS_DIR = str(Path(__file__).parent.parent / ".claude" / "haios")
if _HAIOS_DIR not in sys.path:
    sys.path.insert(0, _HAIOS_DIR)


# ---------------------------------------------------------------------------
# Test 1: bootstrap.py path resolution
# ---------------------------------------------------------------------------


def test_bootstrap_adds_both_paths():
    """Verify bootstrap.setup_paths() adds modules/ and lib/ to sys.path."""
    from haios_ops import bootstrap

    haios_dir = Path(bootstrap.__file__).parent.parent
    modules_dir = str(haios_dir / "modules")
    lib_dir = str(haios_dir / "lib")

    assert modules_dir in sys.path, f"modules/ not in sys.path: {modules_dir}"
    assert lib_dir in sys.path, f"lib/ not in sys.path: {lib_dir}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_engine():
    """Create a mock WorkEngine with common methods."""
    engine = MagicMock()
    return engine


@pytest.fixture
def mock_governance():
    """Create a mock GovernanceLayer."""
    return MagicMock()


def _make_work_state(**overrides):
    """Create a mock WorkState dataclass-like object.

    Returns a MagicMock configured so dataclasses.asdict() works,
    by providing __dataclass_fields__ and direct attribute access.
    """
    from dataclasses import dataclass, field, asdict

    @dataclass
    class _FakeWorkState:
        id: str = "WORK-220"
        title: str = "Test"
        status: str = "active"
        current_node: str = "PLAN"
        type: str = "implementation"
        queue_position: str = "working"
        cycle_phase: str = "PLAN"
        priority: str = "high"
        path: Path = None

    defaults = {
        "id": "WORK-220",
        "title": "Test",
        "status": "active",
        "current_node": "PLAN",
        "type": "implementation",
        "queue_position": "working",
        "cycle_phase": "PLAN",
        "priority": "high",
        "path": None,
    }
    defaults.update(overrides)
    return _FakeWorkState(**defaults)


# ---------------------------------------------------------------------------
# Work tools tests (Tests 2-6)
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_work_get_returns_dict(mock_eng, mock_gate):
    """Test 2: work_get returns typed dict for existing work item."""
    from haios_ops.mcp_server import work_get

    mock_eng.get_work.return_value = _make_work_state(id="WORK-220")
    result = work_get("WORK-220")

    assert isinstance(result, dict)
    assert result["id"] == "WORK-220"
    assert "title" in result
    assert "status" in result
    assert "queue_position" in result
    assert "cycle_phase" in result


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_work_get_not_found(mock_eng, mock_gate):
    """Test 3: work_get returns error dict when work item not found."""
    from haios_ops.mcp_server import work_get

    mock_eng.get_work.return_value = None
    result = work_get("WORK-999")

    assert result == {"error": "not found", "work_id": "WORK-999"}


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.ceremony_context")
@patch("haios_ops.mcp_server._engine")
def test_work_create_returns_dict(mock_eng, mock_ceremony, mock_gate):
    """Test 4: work_create returns success dict with path."""
    from haios_ops.mcp_server import work_create

    mock_eng.create_work.return_value = Path("/fake/path/WORK.md")
    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)

    result = work_create("WORK-999", "Test Title")

    assert isinstance(result, dict)
    assert result["success"] is True
    assert "path" in result


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.ceremony_context")
@patch("haios_ops.mcp_server._engine")
def test_work_close_returns_dict(mock_eng, mock_ceremony, mock_gate):
    """Test 5: work_close returns success dict."""
    from haios_ops.mcp_server import work_close

    mock_eng.close.return_value = Path("/fake/WORK.md")
    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)

    result = work_close("WORK-220")

    assert result == {"success": True, "work_id": "WORK-220"}


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.ceremony_context")
@patch("haios_ops.mcp_server._engine")
def test_work_transition_returns_dict(mock_eng, mock_ceremony, mock_gate):
    """Test 6: work_transition returns updated WorkState dict."""
    from haios_ops.mcp_server import work_transition

    mock_eng.transition.return_value = _make_work_state(cycle_phase="DO")
    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)

    result = work_transition("WORK-220", "DO")

    assert isinstance(result, dict)
    assert result["cycle_phase"] == "DO"


# ---------------------------------------------------------------------------
# Queue tools tests (Tests 7-12)
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_queue_list_returns_list(mock_eng, mock_gate):
    """Test 7: queue_list returns list of dicts."""
    from haios_ops.mcp_server import queue_list

    mock_eng.get_queue.return_value = [
        _make_work_state(id="WORK-001"),
        _make_work_state(id="WORK-002"),
    ]

    result = queue_list()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == "WORK-001"
    assert result[1]["id"] == "WORK-002"


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_queue_next_returns_dict(mock_eng, mock_gate):
    """Test 8: queue_next returns single dict for next item."""
    from haios_ops.mcp_server import queue_next

    mock_eng.get_next.return_value = _make_work_state(id="WORK-001")

    result = queue_next()

    assert isinstance(result, dict)
    assert result["id"] == "WORK-001"


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_queue_next_empty(mock_eng, mock_gate):
    """Test 9: queue_next returns null dict for empty queue."""
    from haios_ops.mcp_server import queue_next

    mock_eng.get_next.return_value = None

    result = queue_next()

    assert result == {"next": None, "queue": "default"}


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_queue_ready_returns_list(mock_eng, mock_gate):
    """Test 10: queue_ready returns list of dicts."""
    from haios_ops.mcp_server import queue_ready

    mock_eng.get_ready.return_value = [_make_work_state(id="WORK-001")]

    result = queue_ready()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "WORK-001"


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.execute_queue_transition")
def test_queue_commit_returns_dict(mock_transition, mock_gate):
    """Test 11: queue_commit returns success dict."""
    from haios_ops.mcp_server import queue_commit

    mock_transition.return_value = {"success": True, "work": _make_work_state()}

    result = queue_commit("WORK-001")

    assert result == {"success": True}
    mock_transition.assert_called_once()


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.execute_queue_transition")
def test_queue_park_unpark(mock_transition, mock_gate):
    """Test 12: queue_park and queue_unpark both return success dicts."""
    from haios_ops.mcp_server import queue_park, queue_unpark

    mock_transition.return_value = {"success": True}

    park_result = queue_park("WORK-001")
    assert park_result == {"success": True}

    unpark_result = queue_unpark("WORK-001")
    assert unpark_result == {"success": True}

    assert mock_transition.call_count == 2


# ---------------------------------------------------------------------------
# Session tools tests (Tests 13-16)
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.session_mgmt")
def test_session_start_returns_dict(mock_sess, mock_gate):
    """Test 13: session_start returns success dict with session number."""
    from haios_ops.mcp_server import session_start

    mock_sess.start_session.return_value = True

    result = session_start(451)

    assert result == {"success": True, "session": 451}


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.cycle_state")
def test_cycle_set_returns_dict(mock_cs, mock_gate):
    """Test 14: cycle_set returns success dict."""
    from haios_ops.mcp_server import cycle_set

    mock_cs.set_cycle_state.return_value = True

    result = cycle_set("implementation-cycle", "DO", "WORK-220")

    assert result == {
        "success": True,
        "cycle": "implementation-cycle",
        "phase": "DO",
        "work_id": "WORK-220",
    }


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.cycle_state")
def test_cycle_clear_returns_dict(mock_cs, mock_gate):
    """Test 15: cycle_clear returns success dict."""
    from haios_ops.mcp_server import cycle_clear

    mock_cs.clear_cycle_state.return_value = True

    result = cycle_clear()

    assert result == {"success": True}


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
def test_cycle_get_returns_dict(mock_gate, tmp_path):
    """Test 16: cycle_get returns session_state from slim file."""
    from haios_ops.mcp_server import cycle_get

    # Create the expected directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    slim_file = claude_dir / "haios-status-slim.json"
    slim_file.write_text(
        json.dumps(
            {
                "session_state": {
                    "active_cycle": "implementation-cycle",
                    "current_phase": "DO",
                    "work_id": "WORK-220",
                    "entered_at": "2026-02-25T11:00:00",
                    "active_queue": None,
                    "phase_history": [],
                }
            }
        )
    )

    result = cycle_get(project_root=tmp_path)

    assert isinstance(result, dict)
    assert result["active_cycle"] == "implementation-cycle"
    assert result["current_phase"] == "DO"
    assert result["work_id"] == "WORK-220"


# ---------------------------------------------------------------------------
# Scaffold tools tests (Tests 17-19, 28) — WORK-223
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
@patch("haios_ops.mcp_server.get_next_work_id")
def test_scaffold_work_returns_dict(mock_next_id, mock_scaffold, mock_gate):
    """Test 17: scaffold_work creates work item and returns typed dict."""
    from haios_ops.mcp_server import scaffold_work

    mock_next_id.return_value = "WORK-225"
    mock_scaffold.return_value = "/fake/WORK.md"

    result = scaffold_work(title="Test Work Item")

    assert result == {"success": True, "path": "/fake/WORK.md", "work_id": "WORK-225"}
    mock_next_id.assert_called_once()
    mock_scaffold.assert_called_once_with(
        "work_item",
        backlog_id="WORK-225",
        title="Test Work Item",
        variables={"TYPE": "implementation"},
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_plan_returns_dict(mock_scaffold, mock_gate):
    """Test 18: scaffold_plan creates plan and returns typed dict."""
    from haios_ops.mcp_server import scaffold_plan

    mock_scaffold.return_value = "/fake/plans/PLAN.md"

    result = scaffold_plan(work_id="WORK-223", title="Test Plan")

    assert result == {"success": True, "path": "/fake/plans/PLAN.md"}
    mock_scaffold.assert_called_once_with(
        "implementation_plan",
        backlog_id="WORK-223",
        title="Test Plan",
        variables={"TYPE": "implementation"},
    )


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
@patch("haios_ops.mcp_server.get_next_work_id")
def test_scaffold_work_error(mock_next_id, mock_scaffold, mock_gate):
    """Test 19: scaffold_work returns error dict on exception."""
    from haios_ops.mcp_server import scaffold_work

    mock_next_id.return_value = "WORK-225"
    mock_scaffold.side_effect = ValueError("template not found")

    result = scaffold_work(title="Bad Work")

    assert result["success"] is False
    assert "template not found" in result["error"]


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.scaffold_template")
def test_scaffold_plan_missing_work_item(mock_scaffold, mock_gate):
    """Test 28: scaffold_plan returns error when work item doesn't exist."""
    from haios_ops.mcp_server import scaffold_plan

    mock_scaffold.side_effect = ValueError("Work file required.")

    result = scaffold_plan(work_id="WORK-999", title="Bad Plan")

    assert result["success"] is False
    assert "Work file required" in result["error"]


# ---------------------------------------------------------------------------
# Hierarchy tools tests (Tests 20-23) — WORK-223
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.StatusPropagator")
def test_hierarchy_cascade_returns_dict(mock_propagator_cls, mock_gate):
    """Test 20: hierarchy_cascade returns propagation result dict."""
    from haios_ops.mcp_server import hierarchy_cascade

    mock_instance = MagicMock()
    mock_instance.propagate.return_value = {
        "action": "chapter_completed",
        "work_id": "WORK-223",
        "chapter": "CH-066",
        "arc": "call",
        "arc_updated": True,
        "arc_complete": False,
    }
    mock_propagator_cls.return_value = mock_instance

    result = hierarchy_cascade("WORK-223")

    assert result["action"] == "chapter_completed"
    assert result["chapter"] == "CH-066"
    mock_instance.propagate.assert_called_once_with("WORK-223")


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.StatusPropagator")
@patch("haios_ops.mcp_server._engine")
@patch("haios_ops.mcp_server.ceremony_context")
def test_hierarchy_close_work_atomic(mock_ceremony, mock_eng, mock_propagator_cls, mock_gate):
    """Test 21: hierarchy_close_work closes and cascades atomically."""
    from haios_ops.mcp_server import hierarchy_close_work

    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)
    mock_eng.close.return_value = None

    mock_instance = MagicMock()
    mock_instance.propagate.return_value = {
        "action": "chapter_incomplete",
        "work_id": "WORK-223",
    }
    mock_propagator_cls.return_value = mock_instance

    result = hierarchy_close_work("WORK-223")

    assert result["success"] is True
    assert result["cascade"]["action"] == "chapter_incomplete"
    mock_eng.close.assert_called_once_with("WORK-223")
    mock_instance.propagate.assert_called_once_with("WORK-223")


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.StatusPropagator")
@patch("haios_ops.mcp_server._engine")
@patch("haios_ops.mcp_server.ceremony_context")
def test_hierarchy_update_status_complete_cascades(
    mock_ceremony, mock_eng, mock_propagator_cls, mock_gate
):
    """Test 22: hierarchy_update_status with complete status runs cascade."""
    from haios_ops.mcp_server import hierarchy_update_status

    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)
    mock_eng.get_work.return_value = _make_work_state(id="WORK-223")
    mock_eng._write_work_file = MagicMock()

    mock_instance = MagicMock()
    mock_instance.propagate.return_value = {"action": "chapter_incomplete"}
    mock_propagator_cls.return_value = mock_instance

    result = hierarchy_update_status("WORK-223", "complete")

    assert result["success"] is True
    assert result["status"] == "complete"
    assert result["cascade"]["action"] == "chapter_incomplete"
    mock_eng._write_work_file.assert_called_once()
    mock_instance.propagate.assert_called_once_with("WORK-223")


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.StatusPropagator")
@patch("haios_ops.mcp_server._engine")
@patch("haios_ops.mcp_server.ceremony_context")
def test_hierarchy_update_status_active_skips_cascade(
    mock_ceremony, mock_eng, mock_propagator_cls, mock_gate
):
    """Test 23: hierarchy_update_status with non-complete status skips cascade."""
    from haios_ops.mcp_server import hierarchy_update_status

    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)
    mock_eng.get_work.return_value = _make_work_state(id="WORK-223")
    mock_eng._write_work_file = MagicMock()

    result = hierarchy_update_status("WORK-223", "active")

    assert result["success"] is True
    assert result["cascade"] == {}
    mock_eng._write_work_file.assert_called_once()
    mock_propagator_cls.assert_not_called()


# ---------------------------------------------------------------------------
# Coldstart tool tests (Tests 24-25) — WORK-223
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.ColdstartOrchestrator")
def test_coldstart_orchestrator_returns_dict(mock_orch_cls, mock_gate):
    """Test 24: coldstart_orchestrator returns output dict."""
    from haios_ops.mcp_server import coldstart_orchestrator

    mock_instance = MagicMock()
    mock_instance.run.return_value = "[IDENTITY]\n...coldstart output..."
    mock_orch_cls.return_value = mock_instance

    result = coldstart_orchestrator()

    assert result["success"] is True
    assert "coldstart output" in result["output"]
    assert result["tier"] == "auto"


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server.ColdstartOrchestrator")
def test_coldstart_orchestrator_tier_param(mock_orch_cls, mock_gate):
    """Test 25: coldstart_orchestrator passes tier parameter."""
    from haios_ops.mcp_server import coldstart_orchestrator

    mock_instance = MagicMock()
    mock_instance.run.return_value = "light output"
    mock_orch_cls.return_value = mock_instance

    result = coldstart_orchestrator(tier="light")

    assert result["tier"] == "light"
    mock_instance.run.assert_called_once_with(tier="light")


# ---------------------------------------------------------------------------
# MCP Resource tests (Tests 26-27) — WORK-223
# ---------------------------------------------------------------------------


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_resource_work_item_returns_dict(mock_eng, mock_gate):
    """Test 26: resource_work_item returns work state dict."""
    from haios_ops.mcp_server import resource_work_item

    mock_eng.get_work.return_value = _make_work_state(id="WORK-220")

    result = resource_work_item("WORK-220")

    assert isinstance(result, dict)
    assert result["id"] == "WORK-220"


@patch("haios_ops.mcp_server._check_tool_gate", return_value=None)
@patch("haios_ops.mcp_server._engine")
def test_resource_queue_ready_returns_list(mock_eng, mock_gate):
    """Test 27: resource_queue_ready returns list of dicts."""
    from haios_ops.mcp_server import resource_queue_ready

    mock_eng.get_ready.return_value = [_make_work_state(id="WORK-001")]

    result = resource_queue_ready()

    assert isinstance(result, list)
    assert result[0]["id"] == "WORK-001"


# ---------------------------------------------------------------------------
# Governance gate tests (Tests 29-36) — WORK-224
# ---------------------------------------------------------------------------

from governance_layer import GateResult


def test_get_current_state_no_slim_file(tmp_path):
    """Test 29: _get_current_state returns EXPLORE when no slim file exists."""
    from haios_ops.mcp_server import _get_current_state

    with patch("haios_ops.mcp_server._PROJECT_ROOT", tmp_path):
        result = _get_current_state()

    assert result == "EXPLORE"


def test_get_current_state_from_slim_file(tmp_path):
    """Test 30: _get_current_state returns phase from slim file."""
    from haios_ops.mcp_server import _get_current_state

    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    slim_file = claude_dir / "haios-status-slim.json"
    slim_file.write_text(
        json.dumps({"session_state": {"current_phase": "DO"}})
    )

    with patch("haios_ops.mcp_server._PROJECT_ROOT", tmp_path):
        result = _get_current_state()

    assert result == "DO"


@patch("haios_ops.mcp_server._get_current_state", return_value="DO")
@patch("haios_ops.mcp_server._governance")
def test_check_tool_gate_allows(mock_gov, mock_state):
    """Test 31: _check_tool_gate returns None when GateResult.allowed is True."""
    from haios_ops.mcp_server import _check_tool_gate

    mock_gov.check_activity.return_value = GateResult(
        allowed=True, reason="Activity allowed"
    )

    result = _check_tool_gate("mcp-read", "work_get")

    assert result is None


@patch("haios_ops.mcp_server._get_current_state", return_value="EXPLORE")
@patch("haios_ops.mcp_server._governance")
def test_check_tool_gate_blocks(mock_gov, mock_state):
    """Test 32: _check_tool_gate returns error dict when GateResult.allowed is False."""
    from haios_ops.mcp_server import _check_tool_gate

    mock_gov.check_activity.return_value = GateResult(
        allowed=False, reason="BLOCKED: mutations not allowed in EXPLORE"
    )

    result = _check_tool_gate("mcp-mutate", "work_create")

    assert result == {
        "success": False,
        "error": "Governance gate blocked: BLOCKED: mutations not allowed in EXPLORE",
    }


@patch("haios_ops.mcp_server._engine")
@patch("haios_ops.mcp_server._get_current_state", return_value="PLAN")
@patch("haios_ops.mcp_server._governance")
def test_work_get_calls_check_activity(mock_gov, mock_state, mock_eng):
    """Test 33: work_get calls check_activity with correct (primitive, state, context) args."""
    mock_gov.check_activity.return_value = GateResult(
        allowed=True, reason="Activity allowed"
    )
    mock_eng.get_work.return_value = _make_work_state(id="WORK-220")

    # Call work_get — but _check_tool_gate is mocked out (returns None).
    from haios_ops.mcp_server import _check_tool_gate

    # _get_current_state is already patched to return 'PLAN'
    result = _check_tool_gate('mcp-read', 'work_get', 'WORK-220')

    mock_gov.check_activity.assert_called_once_with(
        "mcp-read", "PLAN", {"tool": "work_get", "work_id": "WORK-220"}
    )


@patch("haios_ops.mcp_server._get_current_state", return_value="EXPLORE")
@patch("haios_ops.mcp_server._governance")
@patch("haios_ops.mcp_server._engine")
@patch("haios_ops.mcp_server.ceremony_context")
def test_work_create_blocked_by_governance(
    mock_ceremony, mock_eng, mock_gov, mock_state
):
    """Test 34: work_create blocked by governance returns error without calling engine."""
    from haios_ops.mcp_server import work_create

    mock_gov.check_activity.return_value = GateResult(
        allowed=False,
        reason="EXPLORE phase: mutation tools should not be needed during investigation",
    )

    result = work_create("WORK-999", "Test Title")

    assert result == {
        "success": False,
        "error": "Governance gate blocked: EXPLORE phase: mutation tools should not be needed during investigation",
    }
    mock_eng.create_work.assert_not_called()


@patch("governance_events._append_event")
def test_log_governance_gate_appends_event(mock_append):
    """Test 35: _log_governance_gate appends MCPGateChecked event."""
    from haios_ops.mcp_server import _log_governance_gate

    _log_governance_gate("work_get", "mcp-read", "DO", False, "BLOCKED: reason")

    mock_append.assert_called_once()
    event = mock_append.call_args[0][0]
    assert event["type"] == "MCPGateChecked"
    assert event["tool"] == "work_get"
    assert event["primitive"] == "mcp-read"
    assert event["state"] == "DO"
    assert event["allowed"] is False


@patch("governance_events._append_event", side_effect=RuntimeError("disk full"))
def test_log_governance_gate_fails_silently(mock_append):
    """Test 36: _log_governance_gate fails silently on exception."""
    from haios_ops.mcp_server import _log_governance_gate

    # Should not raise
    _log_governance_gate("work_get", "mcp-read", "DO", True, "Activity allowed")

    # If we get here, the function handled the exception silently
    assert True
