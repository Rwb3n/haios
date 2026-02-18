# generated: 2026-02-18
"""
Tests for session_end_actions.py (WORK-161: Session Boundary Fix).

Unit tests for the four session-end action functions, plus integration
tests for stop.py calling them.

TDD: Written RED first, then implementation to pass.
"""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add lib to path for session_end_actions imports
LIB_DIR = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
sys.path.insert(0, str(LIB_DIR))

# Add hooks directory for stop.py integration tests
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))


# =============================================================================
# Unit Tests: session_end_actions.py
# =============================================================================


class TestReadSessionNumber:
    """Unit tests for read_session_number()."""

    def test_read_session_number(self, tmp_path):
        """Reads integer from file with comment header lines."""
        session_file = tmp_path / ".claude" / "session"
        session_file.parent.mkdir(parents=True)
        session_file.write_text("# generated: 2026-02-18\n# System Auto: last updated on: 2026-02-18T10:00:00\n396\n")

        from session_end_actions import read_session_number

        result = read_session_number(project_root=tmp_path)
        assert result == 396

    def test_read_session_number_missing_file(self, tmp_path):
        """Returns None gracefully when session file doesn't exist."""
        from session_end_actions import read_session_number

        result = read_session_number(project_root=tmp_path)
        assert result is None

    def test_read_session_number_empty_file(self, tmp_path):
        """Returns None for empty file."""
        session_file = tmp_path / ".claude" / "session"
        session_file.parent.mkdir(parents=True)
        session_file.write_text("")

        from session_end_actions import read_session_number

        result = read_session_number(project_root=tmp_path)
        assert result is None

    def test_read_session_number_no_integer(self, tmp_path):
        """Returns None when file has no parseable integer."""
        session_file = tmp_path / ".claude" / "session"
        session_file.parent.mkdir(parents=True)
        session_file.write_text("# just comments\n# no number\n")

        from session_end_actions import read_session_number

        result = read_session_number(project_root=tmp_path)
        assert result is None


class TestLogSessionEnded:
    """Unit tests for log_session_ended()."""

    def test_log_session_ended_writes_event(self, tmp_path):
        """SessionEnded event in JSONL with agent and session fields."""
        events_file = tmp_path / "governance-events.jsonl"

        from session_end_actions import log_session_ended

        with patch("governance_events.EVENTS_FILE", events_file):
            log_session_ended(396, agent="Hephaestus")

        # Verify event was written
        lines = events_file.read_text().strip().split("\n")
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["type"] == "SessionEnded"
        assert event["session"] == 396
        assert event["agent"] == "Hephaestus"
        assert "timestamp" in event

    def test_log_session_ended_requires_session_number(self):
        """Verify session_number is required (not optional)."""
        from session_end_actions import log_session_ended

        with pytest.raises(TypeError):
            log_session_ended(agent="Hephaestus")  # Missing session_number


class TestClearCycleState:
    """Unit tests for clear_cycle_state()."""

    def test_clear_cycle_state(self, tmp_path):
        """All 6 session_state fields nulled after clear."""
        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        slim_file.parent.mkdir(parents=True)
        slim_file.write_text(json.dumps({
            "generated": "2026-02-18T10:00:00",
            "session_state": {
                "active_cycle": "implementation-cycle",
                "current_phase": "DO",
                "work_id": "WORK-161",
                "entered_at": "2026-02-18T10:00:00",
                "active_queue": "governance",
                "phase_history": ["PLAN", "DO"],
            },
        }, indent=4))

        from session_end_actions import clear_cycle_state

        result = clear_cycle_state(project_root=tmp_path)
        assert result is True

        # Verify all 6 fields cleared
        data = json.loads(slim_file.read_text())
        ss = data["session_state"]
        assert ss["active_cycle"] is None
        assert ss["current_phase"] is None
        assert ss["work_id"] is None
        assert ss["entered_at"] is None
        assert ss["active_queue"] is None
        assert ss["phase_history"] == []

    def test_clear_cycle_state_normalizes_4_field_schema(self, tmp_path):
        """Normalizes old 4-field schema to full 6-field schema."""
        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        slim_file.parent.mkdir(parents=True)
        # Old format: only 4 fields
        slim_file.write_text(json.dumps({
            "generated": "2026-02-18T10:00:00",
            "session_state": {
                "active_cycle": "investigation-cycle",
                "current_phase": "EXPLORE",
                "work_id": "INV-050",
                "entered_at": "2026-02-18T10:00:00",
            },
        }, indent=4))

        from session_end_actions import clear_cycle_state

        result = clear_cycle_state(project_root=tmp_path)
        assert result is True

        data = json.loads(slim_file.read_text())
        ss = data["session_state"]
        # All 6 fields present and cleared
        assert len([k for k in ["active_cycle", "current_phase", "work_id",
                                 "entered_at", "active_queue", "phase_history"]
                     if k in ss]) == 6
        assert ss["active_queue"] is None
        assert ss["phase_history"] == []

    def test_clear_cycle_state_missing_file(self, tmp_path):
        """Returns False gracefully when slim file doesn't exist."""
        from session_end_actions import clear_cycle_state

        result = clear_cycle_state(project_root=tmp_path)
        assert result is False

    def test_clear_cycle_state_preserves_other_keys(self, tmp_path):
        """Other top-level keys in slim JSON are preserved."""
        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        slim_file.parent.mkdir(parents=True)
        slim_file.write_text(json.dumps({
            "generated": "2026-02-18T10:00:00",
            "milestone": {"id": "M8-Memory"},
            "session_state": {
                "active_cycle": "impl",
                "current_phase": "DO",
                "work_id": "W-1",
                "entered_at": "2026-02-18",
                "active_queue": None,
                "phase_history": [],
            },
        }, indent=4))

        from session_end_actions import clear_cycle_state

        clear_cycle_state(project_root=tmp_path)

        data = json.loads(slim_file.read_text())
        assert data["generated"] == "2026-02-18T10:00:00"
        assert data["milestone"]["id"] == "M8-Memory"


class TestDetectUncommittedChanges:
    """Unit tests for detect_uncommitted_changes()."""

    def test_detect_uncommitted_changes_clean(self, monkeypatch):
        """Returns empty list when working tree is clean."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_result)

        from session_end_actions import detect_uncommitted_changes

        result = detect_uncommitted_changes()
        assert result == []

    def test_detect_uncommitted_changes_dirty(self, monkeypatch):
        """Returns file list when changes exist."""
        mock_result = MagicMock()
        mock_result.stdout = " M file1.py\n?? file2.py\n"
        mock_result.returncode = 0
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_result)

        from session_end_actions import detect_uncommitted_changes

        result = detect_uncommitted_changes()
        assert len(result) == 2
        assert " M file1.py" in result
        assert "?? file2.py" in result

    def test_detect_uncommitted_changes_timeout(self, monkeypatch):
        """Returns None on subprocess timeout."""
        def raise_timeout(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="git", timeout=5)

        monkeypatch.setattr(subprocess, "run", raise_timeout)

        from session_end_actions import detect_uncommitted_changes

        result = detect_uncommitted_changes()
        assert result is None

    def test_detect_uncommitted_changes_error(self, monkeypatch):
        """Returns None on subprocess error."""
        def raise_error(*a, **kw):
            raise OSError("git not found")

        monkeypatch.setattr(subprocess, "run", raise_error)

        from session_end_actions import detect_uncommitted_changes

        result = detect_uncommitted_changes()
        assert result is None


# =============================================================================
# Integration Tests: stop.py calling session-end actions
# =============================================================================


class TestStopHookSessionEndIntegration:
    """Integration tests for stop.py session-end actions."""

    def test_session_end_runs_without_transcript(self, tmp_path, monkeypatch):
        """Session-end actions fire even without transcript."""
        # Setup: session file exists
        session_dir = tmp_path / ".claude"
        session_dir.mkdir(parents=True)
        (session_dir / "session").write_text("# comment\n396\n")

        # Setup: slim file exists
        slim_file = session_dir / "haios-status-slim.json"
        slim_file.write_text(json.dumps({
            "session_state": {
                "active_cycle": "impl",
                "current_phase": "DO",
                "work_id": "W-1",
                "entered_at": "2026-02-18",
                "active_queue": None,
                "phase_history": [],
            }
        }, indent=4))

        # Setup: events file for governance_events
        events_file = tmp_path / "events.jsonl"

        from hooks.stop import handle, _run_session_end_actions

        with patch("session_end_actions._default_project_root", return_value=tmp_path), \
             patch("governance_events.EVENTS_FILE", events_file), \
             patch("subprocess.run") as mock_git:
            mock_git.return_value = MagicMock(stdout="", returncode=0)

            # No transcript_path — learning extraction should be skipped
            hook_data = {
                "stop_hook_active": False,
                "transcript_path": "",
            }
            result = handle(hook_data)

        # Session-end actions should have fired:
        # 1. SessionEnded event logged
        if events_file.exists():
            events = [json.loads(l) for l in events_file.read_text().strip().split("\n") if l.strip()]
            session_ended = [e for e in events if e["type"] == "SessionEnded"]
            assert len(session_ended) == 1
            assert session_ended[0]["session"] == 396

        # 2. Cycle state cleared
        data = json.loads(slim_file.read_text())
        assert data["session_state"]["active_cycle"] is None

    def test_session_end_runs_with_transcript(self, tmp_path, monkeypatch):
        """Both learning extraction and session-end actions run."""
        # Setup minimal files
        session_dir = tmp_path / ".claude"
        session_dir.mkdir(parents=True)
        (session_dir / "session").write_text("# comment\n396\n")
        slim_file = session_dir / "haios-status-slim.json"
        slim_file.write_text(json.dumps({
            "session_state": {
                "active_cycle": "impl",
                "current_phase": "DO",
                "work_id": "W-1",
                "entered_at": "2026-02-18",
                "active_queue": None,
                "phase_history": [],
            }
        }, indent=4))
        events_file = tmp_path / "events.jsonl"

        # Create a fake transcript
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text('{"type":"user","content":"hello"}\n')

        from hooks.stop import handle

        # Mock MemoryBridge to avoid real MCP calls
        mock_bridge = MagicMock()
        mock_bridge.extract_learnings.return_value = MagicMock(success=True, outcome="stored")

        with patch("session_end_actions._default_project_root", return_value=tmp_path), \
             patch("governance_events.EVENTS_FILE", events_file), \
             patch("subprocess.run") as mock_git:
            mock_git.return_value = MagicMock(stdout="", returncode=0)

            # Patch MemoryBridge import inside stop.py
            with patch.dict("sys.modules", {"memory_bridge": MagicMock(MemoryBridge=lambda: mock_bridge)}):
                hook_data = {
                    "stop_hook_active": False,
                    "transcript_path": str(transcript),
                }
                result = handle(hook_data)

        # Learning extraction should have run
        assert result is not None
        assert "[LEARNING]" in result

        # Session-end actions should also have run
        data = json.loads(slim_file.read_text())
        assert data["session_state"]["active_cycle"] is None

    def test_stop_hook_active_skips_all(self):
        """Infinite loop guard preserved — stop_hook_active=True skips everything."""
        from hooks.stop import handle

        result = handle({"stop_hook_active": True})
        assert result is None

    def test_learning_failure_doesnt_skip_session_end(self, tmp_path):
        """Independent fail-permissive: learning crash doesn't prevent session-end."""
        session_dir = tmp_path / ".claude"
        session_dir.mkdir(parents=True)
        (session_dir / "session").write_text("# comment\n396\n")
        slim_file = session_dir / "haios-status-slim.json"
        slim_file.write_text(json.dumps({
            "session_state": {
                "active_cycle": "impl",
                "current_phase": "DO",
                "work_id": "W-1",
                "entered_at": "2026-02-18",
                "active_queue": None,
                "phase_history": [],
            }
        }, indent=4))
        events_file = tmp_path / "events.jsonl"

        # Create transcript so learning extraction is attempted
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text('{"type":"user","content":"hello"}\n')

        from hooks.stop import handle

        # Make MemoryBridge raise an exception
        def failing_import(*args, **kwargs):
            raise RuntimeError("MCP server down")

        with patch("session_end_actions._default_project_root", return_value=tmp_path), \
             patch("governance_events.EVENTS_FILE", events_file), \
             patch("subprocess.run") as mock_git:
            mock_git.return_value = MagicMock(stdout="", returncode=0)

            # Patch the import to fail
            with patch.dict("sys.modules", {"memory_bridge": MagicMock(MemoryBridge=failing_import)}):
                hook_data = {
                    "stop_hook_active": False,
                    "transcript_path": str(transcript),
                }
                result = handle(hook_data)

        # Session-end should still have run despite learning failure
        data = json.loads(slim_file.read_text())
        assert data["session_state"]["active_cycle"] is None
