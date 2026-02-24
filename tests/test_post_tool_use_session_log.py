# generated: 2026-02-23
"""
Tests for PostToolUse session event detection (WORK-206).

Tests 5-7, 10-11: Event detection for phase transitions, pytest results,
git commits, work spawns, and work closures.
TDD RED phase: written before implementation.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add lib path for imports — hooks live at .claude/hooks/hooks/
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
LIB_DIR = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))


class TestPhaseTransitionDetection:
    """Test 5: PostToolUse detects phase transition in WORK.md Edit."""

    def test_post_tool_use_detects_phase_transition(self, tmp_path):
        """_append_session_event detects cycle_phase change in WORK.md Edit."""
        from post_tool_use import _append_session_event

        log_file = tmp_path / "session-log.jsonl"
        work_path = str(tmp_path / "docs" / "work" / "active" / "WORK-206" / "WORK.md")

        hook_data = {
            "tool_name": "Edit",
            "tool_input": {
                "old_string": "cycle_phase: PLAN",
                "new_string": "cycle_phase: DO",
            },
            "tool_response": {"filePath": work_path},
        }

        with patch("session_event_log.get_log_path", return_value=log_file):
            _append_session_event("Edit", hook_data, work_path)

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["t"] == "phase"
        assert event["v"] == "PLAN->DO"


class TestPytestResultDetection:
    """Test 6: PostToolUse detects pytest result."""

    def test_post_tool_use_detects_pytest_result(self, tmp_path):
        """_append_session_event detects pytest pass/fail counts from Bash stdout."""
        from post_tool_use import _append_session_event

        log_file = tmp_path / "session-log.jsonl"

        hook_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/ -v"},
            "tool_response": {"stdout": "42 passed, 0 failed in 3.2s"},
        }

        with patch("session_event_log.get_log_path", return_value=log_file):
            _append_session_event("Bash", hook_data, "")

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["t"] == "test"
        assert event["v"] == "42p/0f"


class TestGitCommitDetection:
    """Test 7: PostToolUse detects git commit."""

    def test_post_tool_use_detects_git_commit(self, tmp_path):
        """_append_session_event detects git commit from Bash command."""
        from post_tool_use import _append_session_event

        log_file = tmp_path / "session-log.jsonl"

        hook_data = {
            "tool_name": "Bash",
            "tool_input": {"command": 'git commit -m "Session 434: WORK-206 impl"'},
            "tool_response": {"stdout": "[main abc1234] Session 434: WORK-206 impl"},
        }

        with patch("session_event_log.get_log_path", return_value=log_file):
            _append_session_event("Bash", hook_data, "")

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["t"] == "commit"
        assert event["v"].startswith("Session 434")


class TestWorkSpawnDetection:
    """Test 10: PostToolUse detects work spawn."""

    def test_post_tool_use_detects_work_spawn(self, tmp_path):
        """_append_session_event detects Write to a new WORK.md in docs/work/active/."""
        from post_tool_use import _append_session_event

        log_file = tmp_path / "session-log.jsonl"
        work_path = str(tmp_path / "docs" / "work" / "active" / "WORK-207" / "WORK.md")

        hook_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": work_path,
                "content": "---\nid: WORK-207\n---",
            },
            "tool_response": {"filePath": work_path},
        }

        with patch("session_event_log.get_log_path", return_value=log_file):
            _append_session_event("Write", hook_data, work_path)

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["t"] == "spawn"
        assert event["v"] == "WORK-207"


class TestWorkClosureDetection:
    """Test 11: PostToolUse detects work closure."""

    def test_post_tool_use_detects_work_closure(self, tmp_path):
        """_append_session_event detects Bash with cli.py close command."""
        from post_tool_use import _append_session_event

        log_file = tmp_path / "session-log.jsonl"

        hook_data = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "python .claude/haios/modules/cli.py close WORK-206"
            },
            "tool_response": {"stdout": "WORK-206 closed"},
        }

        with patch("session_event_log.get_log_path", return_value=log_file):
            _append_session_event("Bash", hook_data, "")

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["t"] == "close"
        assert event["v"] == "WORK-206"
