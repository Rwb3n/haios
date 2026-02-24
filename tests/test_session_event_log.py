# generated: 2026-02-23
"""
Tests for session_event_log module (WORK-206).

Tests 1-4: Core module functions (reset_log, append_event, read_events).
TDD RED phase: written before implementation.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add lib path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestResetLog:
    """Test 1: reset_log truncates existing file."""

    def test_reset_log_truncates_existing_file(self, tmp_path):
        """reset_log() creates an empty file, truncating any existing content."""
        from session_event_log import reset_log, get_log_path

        log_file = tmp_path / "session-log.jsonl"
        log_file.write_text('{"t":"phase","v":"old"}\n', encoding="utf-8")

        with patch("session_event_log.get_log_path", return_value=log_file):
            reset_log()

        assert log_file.exists()
        assert log_file.read_text(encoding="utf-8") == ""


class TestAppendEvent:
    """Test 2: append_event writes valid JSONL."""

    def test_append_event_writes_jsonl(self, tmp_path):
        """append_event() writes a single valid JSONL line with correct fields."""
        from session_event_log import append_event

        log_file = tmp_path / "session-log.jsonl"

        with patch("session_event_log.get_log_path", return_value=log_file):
            append_event("phase", "PLAN->DO", "WORK-206")

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

        event = json.loads(lines[0])
        assert event["t"] == "phase"
        assert event["v"] == "PLAN->DO"
        assert event["w"] == "WORK-206"
        # ts should be HH:MM format
        assert len(event["ts"]) == 5
        assert ":" in event["ts"]


class TestReadEvents:
    """Tests 3-4: read_events returns parsed list or empty list."""

    def test_read_events_returns_list(self, tmp_path):
        """read_events() returns a list of parsed dicts from JSONL file."""
        from session_event_log import read_events

        log_file = tmp_path / "session-log.jsonl"
        log_file.write_text(
            '{"t":"phase","v":"PLAN->DO","w":"WORK-206","ts":"15:03"}\n'
            '{"t":"commit","v":"Session 434","w":"WORK-206","ts":"15:10"}\n',
            encoding="utf-8",
        )

        with patch("session_event_log.get_log_path", return_value=log_file):
            events = read_events()

        assert len(events) == 2
        assert events[0]["t"] == "phase"
        assert events[1]["t"] == "commit"

    def test_read_events_missing_file(self, tmp_path):
        """read_events() returns [] for non-existent file without raising."""
        from session_event_log import read_events

        log_file = tmp_path / "nonexistent" / "session-log.jsonl"

        with patch("session_event_log.get_log_path", return_value=log_file):
            events = read_events()

        assert events == []
