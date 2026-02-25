"""Tests for session_mgmt.start_session function (WORK-219).

Tests 6-8 per plan Layer 1 Tests section.
Uses tmp_path for filesystem isolation (S340 pattern).
Mocks governance_events and session_event_log to isolate unit behavior.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure lib/ is importable
_lib_dir = str(Path(__file__).parent.parent / ".claude" / "haios" / "lib")
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)

from session_mgmt import start_session


def _setup_session_files(tmp_path: Path, session_content: str, status: dict = None):
    """Helper: create .claude/session and .claude/haios-status.json."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    haios_dir = claude_dir / "haios"
    haios_dir.mkdir(parents=True, exist_ok=True)

    session_file = claude_dir / "session"
    session_file.write_text(session_content, encoding="utf-8")

    status_file = claude_dir / "haios-status.json"
    status_file.write_text(
        json.dumps(status or {}, indent=2), encoding="utf-8"
    )


class TestStartSession:
    """Test 6-8: start_session."""

    @patch("governance_events.log_session_start", return_value=None)
    @patch("session_event_log.reset_log", return_value=None)
    def test_start_session_writes_files(self, mock_reset, mock_log, tmp_path):
        """Test 6: start_session writes session file and status delta."""
        _setup_session_files(tmp_path, "# generated: test\n449\n")

        result = start_session(451, project_root=tmp_path)
        assert result is True

        # Check session file
        session_file = tmp_path / ".claude" / "session"
        content = session_file.read_text(encoding="utf-8")
        assert "451" in content
        assert "# generated: test" in content

        # Check status file
        status_file = tmp_path / ".claude" / "haios-status.json"
        status = json.loads(status_file.read_text(encoding="utf-8"))
        assert status["session_delta"]["current_session"] == 451
        assert status["session_delta"]["prior_session"] == 450

    @patch("governance_events.log_session_start", return_value=None)
    @patch("session_event_log.reset_log", return_value=None)
    def test_start_session_preserves_headers(self, mock_reset, mock_log, tmp_path):
        """Test 7: start_session preserves session file headers."""
        headers = "# generated: 2026-01-21\n# System Auto: last updated on: 2026-01-21T11:26:51\n"
        _setup_session_files(tmp_path, headers + "450\n")

        start_session(451, project_root=tmp_path)

        session_file = tmp_path / ".claude" / "session"
        content = session_file.read_text(encoding="utf-8")
        assert content.startswith(headers)
        assert content.endswith("451\n")

    @patch("governance_events.log_session_start", return_value=None)
    @patch("session_event_log.reset_log", return_value=None)
    def test_start_session_returns_true(self, mock_reset, mock_log, tmp_path):
        """Test 8: start_session returns True on success."""
        _setup_session_files(tmp_path, "450\n")

        result = start_session(451, project_root=tmp_path)
        assert result is True
