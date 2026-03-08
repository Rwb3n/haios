"""
Tests for retro_gate.py — Mechanical retro-before-close enforcement (WORK-253).

Verifies check_retro_gate() correctly blocks close-work-cycle when no
RetroCycleCompleted event exists for the work item in the current session.
"""
import json
import sys
from pathlib import Path

import pytest

# Insert lib/ into sys.path for import
_lib_dir = str(Path(__file__).parent.parent / ".claude" / "haios" / "lib")
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)

from retro_gate import check_retro_gate


def _write_session(tmp_path: Path, session_number: int) -> None:
    """Write a .claude/session file with the given session number."""
    session_dir = tmp_path / ".claude"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "session").write_text(str(session_number), encoding="utf-8")


def _write_events(tmp_path: Path, events: list[dict]) -> None:
    """Write governance-events.jsonl with the given events."""
    events_dir = tmp_path / ".claude" / "haios"
    events_dir.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(e) for e in events]
    (events_dir / "governance-events.jsonl").write_text(
        "\n".join(lines), encoding="utf-8"
    )


class TestCheckRetroGate:
    """Tests for check_retro_gate() function."""

    def test_blocks_when_no_retro(self, tmp_path: Path) -> None:
        """Test 1: Block when no retro event exists for work_id in session."""
        _write_session(tmp_path, 479)
        _write_events(
            tmp_path,
            [
                {
                    "type": "SessionStarted",
                    "session_id": 479,
                    "timestamp": "2026-03-08T10:00:00",
                },
            ],
        )

        result = check_retro_gate("WORK-253", project_root=tmp_path)

        assert result["blocked"] is True
        assert "retro-cycle must complete" in result["reason"]
        assert result["retro_found"] is False

    def test_allows_when_retro_completed(self, tmp_path: Path) -> None:
        """Test 2: Allow when retro completed this session."""
        _write_session(tmp_path, 479)
        _write_events(
            tmp_path,
            [
                {
                    "type": "RetroCycleCompleted",
                    "work_id": "WORK-253",
                    "session_id": 479,
                    "timestamp": "2026-03-08T11:00:00",
                },
            ],
        )

        result = check_retro_gate("WORK-253", project_root=tmp_path)

        assert result["blocked"] is False
        assert result["retro_found"] is True

    def test_warns_when_events_file_missing(self, tmp_path: Path) -> None:
        """Test 3: Fail-permissive when events file missing."""
        _write_session(tmp_path, 479)
        # Do NOT create governance-events.jsonl

        result = check_retro_gate("WORK-253", project_root=tmp_path)

        assert result["blocked"] is False
        assert "governance-events.jsonl not found" in result["warning"]
        assert result["retro_found"] is False

    def test_warns_when_work_id_empty(self, tmp_path: Path) -> None:
        """Test 4: Warn when work_id is empty string."""
        _write_session(tmp_path, 479)
        _write_events(tmp_path, [])

        result = check_retro_gate("", project_root=tmp_path)

        assert result["blocked"] is False
        assert "work_id could not be determined" in result["warning"]
        assert result["retro_found"] is False

    def test_blocks_when_retro_from_different_session(self, tmp_path: Path) -> None:
        """Test 5: Block ignores retro from a different session."""
        _write_session(tmp_path, 479)
        _write_events(
            tmp_path,
            [
                {
                    "type": "RetroCycleCompleted",
                    "work_id": "WORK-253",
                    "session_id": 400,  # Prior session
                    "timestamp": "2026-03-07T10:00:00",
                },
            ],
        )

        result = check_retro_gate("WORK-253", project_root=tmp_path)

        assert result["blocked"] is True
        assert result["retro_found"] is False


# =============================================================================
# WORK-291: Round-trip test — log_retro_completed then check_retro_gate
# =============================================================================


class TestRetroGateRoundTrip:
    """WORK-291: Verify log_retro_completed produces events that check_retro_gate accepts."""

    def test_retro_gate_passes_after_log_retro_completed(self, tmp_path: Path) -> None:
        """Round-trip: emit event via lib function, then gate passes."""
        import sys as _sys
        _lib = str(Path(__file__).parent.parent / ".claude" / "haios" / "lib")
        if _lib not in _sys.path:
            _sys.path.insert(0, _lib)

        from unittest.mock import patch
        from governance_events import log_retro_completed

        _write_session(tmp_path, 482)
        # Create events dir and file
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True, exist_ok=True)
        events_file = events_dir / "governance-events.jsonl"
        events_file.write_text("", encoding="utf-8")

        # Emit event via lib function (patches EVENTS_FILE to tmp_path)
        with patch("governance_events.EVENTS_FILE", events_file), \
             patch("governance_events.SLIM_FILE", tmp_path / "nonexistent-slim.json"), \
             patch("governance_events.SESSION_FILE", tmp_path / ".claude" / "session"):
            log_retro_completed(
                work_id="WORK-291",
                scaling="substantial",
                reflect_count=5,
                kss_count=3,
                extract_count=2,
            )

        # Now check gate — uses project_root to find events file
        result = check_retro_gate("WORK-291", project_root=tmp_path)

        assert result["blocked"] is False, f"Gate should pass after log_retro_completed: {result}"
        assert result["retro_found"] is True

    def test_retro_gate_blocks_without_retro_completed(self, tmp_path: Path) -> None:
        """Confirm gate blocks when no event exists (regression guard)."""
        _write_session(tmp_path, 482)
        _write_events(tmp_path, [])  # Empty events file

        result = check_retro_gate("WORK-291", project_root=tmp_path)

        assert result["blocked"] is True
        assert result["retro_found"] is False
