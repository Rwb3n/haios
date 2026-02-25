"""Tests for cycle_state set/clear/queue management functions (WORK-219).

Tests 1-5 per plan Layer 1 Tests section.
Uses tmp_path for filesystem isolation (S340 pattern).
"""
import json
import sys
from pathlib import Path

import pytest

# Ensure lib/ is importable
_lib_dir = str(Path(__file__).parent.parent / ".claude" / "haios" / "lib")
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)

from cycle_state import clear_cycle_state, set_active_queue, set_cycle_state


def _write_slim(tmp_path: Path, session_state: dict) -> Path:
    """Helper: write haios-status-slim.json with given session_state."""
    slim_dir = tmp_path / ".claude"
    slim_dir.mkdir(parents=True, exist_ok=True)
    slim_file = slim_dir / "haios-status-slim.json"
    data = {"session_state": session_state}
    slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
    return slim_file


class TestSetCycleState:
    """Test 1-2: set_cycle_state."""

    def test_set_cycle_state_writes_session_state(self, tmp_path, monkeypatch):
        """Test 1: set_cycle_state writes 6-field session_state."""
        _write_slim(tmp_path, {})

        # Mock sync_work_md_phase and log_phase_transition to no-ops
        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "DO", "WORK-219", project_root=tmp_path
        )
        assert result is True

        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        ss = data["session_state"]

        assert ss["active_cycle"] == "implementation-cycle"
        assert ss["current_phase"] == "DO"
        assert ss["work_id"] == "WORK-219"
        assert ss["active_queue"] is None
        assert ss["phase_history"] == []
        assert "entered_at" in ss

    def test_set_cycle_state_missing_file(self, tmp_path):
        """Test 2: set_cycle_state returns False on missing file."""
        result = set_cycle_state(
            "implementation-cycle", "DO", "WORK-219", project_root=tmp_path
        )
        assert result is False


class TestClearCycleState:
    """Test 3: clear_cycle_state."""

    def test_clear_cycle_state_zeroes_fields(self, tmp_path):
        """Test 3: clear_cycle_state zeroes all 6 fields."""
        _write_slim(tmp_path, {
            "active_cycle": "implementation-cycle",
            "current_phase": "DO",
            "work_id": "WORK-219",
            "entered_at": "2026-02-25T10:00:00",
            "active_queue": "governance",
            "phase_history": [{"from": "PLAN", "to": "DO", "at": "2026-02-25T10:00:00"}],
        })

        result = clear_cycle_state(project_root=tmp_path)
        assert result is True

        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        ss = data["session_state"]

        assert ss["active_cycle"] is None
        assert ss["current_phase"] is None
        assert ss["work_id"] is None
        assert ss["entered_at"] is None
        assert ss["active_queue"] is None
        assert ss["phase_history"] == []


class TestSetActiveQueue:
    """Test 4-5: set_active_queue."""

    def test_set_active_queue_mutates_field(self, tmp_path):
        """Test 4: set_active_queue mutates only active_queue field."""
        _write_slim(tmp_path, {
            "active_cycle": "implementation-cycle",
            "current_phase": "DO",
            "work_id": "WORK-219",
            "entered_at": "2026-02-25T10:00:00",
            "active_queue": None,
            "phase_history": [],
        })

        result = set_active_queue("governance", project_root=tmp_path)
        assert result is True

        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        ss = data["session_state"]

        assert ss["active_queue"] == "governance"
        # Other fields unchanged
        assert ss["active_cycle"] == "implementation-cycle"
        assert ss["current_phase"] == "DO"
        assert ss["work_id"] == "WORK-219"

    def test_set_active_queue_missing_session_state(self, tmp_path):
        """Test 5: set_active_queue returns False on missing session_state key."""
        slim_dir = tmp_path / ".claude"
        slim_dir.mkdir(parents=True, exist_ok=True)
        slim_file = slim_dir / "haios-status-slim.json"
        slim_file.write_text(json.dumps({}, indent=4), encoding="utf-8")

        result = set_active_queue("governance", project_root=tmp_path)
        assert result is False
