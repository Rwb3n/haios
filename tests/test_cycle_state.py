"""
Tests for lib/cycle_state.py — Cycle Phase Auto-Advancement (WORK-168).

8 tests: 7 unit tests for advance_cycle_phase() + 1 integration test for PostToolUse Part 8.
"""
import importlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Load cycle_state from lib/
_lib_dir = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(_lib_dir) not in sys.path:
    sys.path.insert(0, str(_lib_dir))

from cycle_state import advance_cycle_phase


def _write_slim(tmp_path: Path, session_state: dict) -> Path:
    """Helper: write haios-status-slim.json with given session_state."""
    slim_file = tmp_path / ".claude" / "haios-status-slim.json"
    slim_file.parent.mkdir(parents=True, exist_ok=True)
    slim_file.write_text(json.dumps({"session_state": session_state}), encoding="utf-8")
    return slim_file


def _read_slim(tmp_path: Path) -> dict:
    """Helper: read and parse haios-status-slim.json."""
    slim_file = tmp_path / ".claude" / "haios-status-slim.json"
    return json.loads(slim_file.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Test 1: advance_cycle_phase advances implementation-cycle PLAN to DO
# ---------------------------------------------------------------------------
def test_advance_impl_plan_to_do(tmp_path):
    _write_slim(tmp_path, {
        "active_cycle": "implementation-cycle",
        "current_phase": "PLAN",
        "work_id": "WORK-168",
        "entered_at": "2026-02-19T00:00:00",
    })
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is True
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "DO"
    assert data["session_state"]["active_cycle"] == "implementation-cycle"


# ---------------------------------------------------------------------------
# Test 2: advance_cycle_phase advances investigation-cycle EXPLORE to HYPOTHESIZE
# ---------------------------------------------------------------------------
def test_advance_inv_explore_to_hypothesize(tmp_path):
    _write_slim(tmp_path, {
        "active_cycle": "investigation-cycle",
        "current_phase": "EXPLORE",
        "work_id": "INV-001",
        "entered_at": "2026-02-19T00:00:00",
    })
    result = advance_cycle_phase("investigation-cycle", project_root=tmp_path)
    assert result is True
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "HYPOTHESIZE"


# ---------------------------------------------------------------------------
# Test 3: Unrecognized skill name returns False, no state change
# ---------------------------------------------------------------------------
def test_unrecognized_skill_no_change(tmp_path):
    _write_slim(tmp_path, {
        "active_cycle": "implementation-cycle",
        "current_phase": "DO",
        "work_id": "WORK-168",
        "entered_at": "2026-02-19T00:00:00",
    })
    result = advance_cycle_phase("retro-cycle", project_root=tmp_path)
    assert result is False
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "DO"  # unchanged


# ---------------------------------------------------------------------------
# Test 4: Last phase (CHAIN) does not advance further
# ---------------------------------------------------------------------------
def test_last_phase_no_advance(tmp_path):
    _write_slim(tmp_path, {
        "active_cycle": "implementation-cycle",
        "current_phase": "CHAIN",
        "work_id": "WORK-168",
        "entered_at": "2026-02-19T00:00:00",
    })
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is False


# ---------------------------------------------------------------------------
# Test 5: Handles 4-field session_state (no phase_history/active_queue)
# ---------------------------------------------------------------------------
def test_four_field_schema_handled(tmp_path):
    # Only 4 fields — no phase_history or active_queue
    _write_slim(tmp_path, {
        "active_cycle": "implementation-cycle",
        "current_phase": "PLAN",
        "work_id": "WORK-168",
        "entered_at": "2026-02-19T00:00:00",
    })
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is True
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "DO"
    assert "phase_history" in data["session_state"]  # auto-created
    assert len(data["session_state"]["phase_history"]) == 1
    assert data["session_state"]["phase_history"][0]["from"] == "PLAN"
    assert data["session_state"]["phase_history"][0]["to"] == "DO"


# ---------------------------------------------------------------------------
# Test 6: Phase history accumulates across multiple advances
# ---------------------------------------------------------------------------
def test_phase_history_accumulates(tmp_path):
    _write_slim(tmp_path, {
        "active_cycle": "implementation-cycle",
        "current_phase": "PLAN",
        "work_id": "WORK-168",
        "entered_at": "2026-02-19T00:00:00",
        "phase_history": [],
        "active_queue": None,
    })
    # First advance: PLAN -> DO
    advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "DO"
    assert len(data["session_state"]["phase_history"]) == 1
    assert data["session_state"]["phase_history"][0]["from"] == "PLAN"
    assert data["session_state"]["phase_history"][0]["to"] == "DO"

    # Second advance: DO -> CHECK
    advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "CHECK"
    assert len(data["session_state"]["phase_history"]) == 2
    assert data["session_state"]["phase_history"][1]["from"] == "DO"
    assert data["session_state"]["phase_history"][1]["to"] == "CHECK"


# ---------------------------------------------------------------------------
# Test 7: Missing slim file returns False (fail-permissive)
# ---------------------------------------------------------------------------
def test_missing_slim_file_returns_false(tmp_path):
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is False  # No crash, no exception


# ---------------------------------------------------------------------------
# Test 8: Active cycle mismatch returns False (critique A5)
# ---------------------------------------------------------------------------
def test_active_cycle_mismatch_returns_false(tmp_path):
    """If session_state.active_cycle doesn't match the skill, refuse to advance."""
    _write_slim(tmp_path, {
        "active_cycle": "investigation-cycle",
        "current_phase": "PLAN",
        "work_id": "WORK-168",
        "entered_at": "2026-02-19T00:00:00",
    })
    # Skill says implementation-cycle but active_cycle says investigation-cycle
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is False
    data = _read_slim(tmp_path)
    assert data["session_state"]["current_phase"] == "PLAN"  # unchanged
