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
