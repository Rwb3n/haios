# generated: 2026-02-25
"""Tests for haios-operations MCP server (WORK-220).

16 test functions covering work, queue, and session tool groups
with mocked backends. Tests import haios_ops from .claude/haios/.
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


@patch("haios_ops.mcp_server._engine")
def test_work_get_returns_dict(mock_eng):
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


@patch("haios_ops.mcp_server._engine")
def test_work_get_not_found(mock_eng):
    """Test 3: work_get returns error dict when work item not found."""
    from haios_ops.mcp_server import work_get

    mock_eng.get_work.return_value = None
    result = work_get("WORK-999")

    assert result == {"error": "not found", "work_id": "WORK-999"}


@patch("haios_ops.mcp_server.ceremony_context")
@patch("haios_ops.mcp_server._engine")
def test_work_create_returns_dict(mock_eng, mock_ceremony):
    """Test 4: work_create returns success dict with path."""
    from haios_ops.mcp_server import work_create

    mock_eng.create_work.return_value = Path("/fake/path/WORK.md")
    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)

    result = work_create("WORK-999", "Test Title")

    assert isinstance(result, dict)
    assert result["success"] is True
    assert "path" in result


@patch("haios_ops.mcp_server.ceremony_context")
@patch("haios_ops.mcp_server._engine")
def test_work_close_returns_dict(mock_eng, mock_ceremony):
    """Test 5: work_close returns success dict."""
    from haios_ops.mcp_server import work_close

    mock_eng.close.return_value = Path("/fake/WORK.md")
    mock_ceremony.return_value.__enter__ = MagicMock()
    mock_ceremony.return_value.__exit__ = MagicMock(return_value=False)

    result = work_close("WORK-220")

    assert result == {"success": True, "work_id": "WORK-220"}


@patch("haios_ops.mcp_server.ceremony_context")
@patch("haios_ops.mcp_server._engine")
def test_work_transition_returns_dict(mock_eng, mock_ceremony):
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


@patch("haios_ops.mcp_server._engine")
def test_queue_list_returns_list(mock_eng):
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


@patch("haios_ops.mcp_server._engine")
def test_queue_next_returns_dict(mock_eng):
    """Test 8: queue_next returns single dict for next item."""
    from haios_ops.mcp_server import queue_next

    mock_eng.get_next.return_value = _make_work_state(id="WORK-001")

    result = queue_next()

    assert isinstance(result, dict)
    assert result["id"] == "WORK-001"


@patch("haios_ops.mcp_server._engine")
def test_queue_next_empty(mock_eng):
    """Test 9: queue_next returns null dict for empty queue."""
    from haios_ops.mcp_server import queue_next

    mock_eng.get_next.return_value = None

    result = queue_next()

    assert result == {"next": None, "queue": "default"}


@patch("haios_ops.mcp_server._engine")
def test_queue_ready_returns_list(mock_eng):
    """Test 10: queue_ready returns list of dicts."""
    from haios_ops.mcp_server import queue_ready

    mock_eng.get_ready.return_value = [_make_work_state(id="WORK-001")]

    result = queue_ready()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "WORK-001"


@patch("haios_ops.mcp_server.execute_queue_transition")
def test_queue_commit_returns_dict(mock_transition):
    """Test 11: queue_commit returns success dict."""
    from haios_ops.mcp_server import queue_commit

    mock_transition.return_value = {"success": True, "work": _make_work_state()}

    result = queue_commit("WORK-001")

    assert result == {"success": True}
    mock_transition.assert_called_once()


@patch("haios_ops.mcp_server.execute_queue_transition")
def test_queue_park_unpark(mock_transition):
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


@patch("haios_ops.mcp_server.session_mgmt")
def test_session_start_returns_dict(mock_sess):
    """Test 13: session_start returns success dict with session number."""
    from haios_ops.mcp_server import session_start

    mock_sess.start_session.return_value = True

    result = session_start(451)

    assert result == {"success": True, "session": 451}


@patch("haios_ops.mcp_server.cycle_state")
def test_cycle_set_returns_dict(mock_cs):
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


@patch("haios_ops.mcp_server.cycle_state")
def test_cycle_clear_returns_dict(mock_cs):
    """Test 15: cycle_clear returns success dict."""
    from haios_ops.mcp_server import cycle_clear

    mock_cs.clear_cycle_state.return_value = True

    result = cycle_clear()

    assert result == {"success": True}


def test_cycle_get_returns_dict(tmp_path):
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
