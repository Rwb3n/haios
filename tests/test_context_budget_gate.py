# generated: 2026-03-07
"""
Tests for context budget gate (WORK-247).

Tests _check_context_budget and _inject_context_warning in pre_tool_use.py,
and statusline.py::main() context_remaining file writing.
"""
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))


class TestCheckContextBudget:
    """Tests for _check_context_budget in pre_tool_use.py."""

    def test_check_context_budget_no_file(self, tmp_path):
        """Returns None when .claude/context_remaining file is missing."""
        from hooks.pre_tool_use import _check_context_budget

        result = _check_context_budget(str(tmp_path))
        assert result is None

    def test_check_context_budget_safe(self, tmp_path):
        """Returns None when remaining context is above 20%."""
        from hooks.pre_tool_use import _check_context_budget

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context_remaining").write_text("45.0", encoding="utf-8")

        result = _check_context_budget(str(tmp_path))
        assert result is None

    def test_check_context_budget_low(self, tmp_path):
        """Returns LOW warning at exactly 20% remaining."""
        from hooks.pre_tool_use import _check_context_budget

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context_remaining").write_text("20.0", encoding="utf-8")

        result = _check_context_budget(str(tmp_path))
        assert result is not None
        assert "[CONTEXT LOW" in result
        assert "20.0%" in result

    def test_check_context_budget_session_end(self, tmp_path):
        """Returns SESSION-END warning at exactly 15% remaining."""
        from hooks.pre_tool_use import _check_context_budget

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context_remaining").write_text("15.0", encoding="utf-8")

        result = _check_context_budget(str(tmp_path))
        assert result is not None
        assert "[CONTEXT SESSION-END" in result
        assert "15.0%" in result

    def test_check_context_budget_critical(self, tmp_path):
        """Returns CRITICAL warning at exactly 10% remaining."""
        from hooks.pre_tool_use import _check_context_budget

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context_remaining").write_text("10.0", encoding="utf-8")

        result = _check_context_budget(str(tmp_path))
        assert result is not None
        assert "[CONTEXT CRITICAL" in result
        assert "10.0%" in result

    def test_check_context_budget_very_critical(self, tmp_path):
        """Returns CRITICAL warning below 10% (e.g., 5%)."""
        from hooks.pre_tool_use import _check_context_budget

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context_remaining").write_text("5.0", encoding="utf-8")

        result = _check_context_budget(str(tmp_path))
        assert result is not None
        assert "[CONTEXT CRITICAL" in result

    def test_check_context_budget_malformed(self, tmp_path):
        """Returns None gracefully when file contains non-numeric text."""
        from hooks.pre_tool_use import _check_context_budget

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "context_remaining").write_text("not_a_number", encoding="utf-8")

        result = _check_context_budget(str(tmp_path))
        assert result is None


class TestInjectContextWarning:
    """Tests for _inject_context_warning in pre_tool_use.py."""

    def test_inject_context_warning_merge(self):
        """Merges warning into existing result's additionalContext."""
        from hooks.pre_tool_use import _inject_context_warning

        existing_result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "additionalContext": "[STATE: DO] Blocked: none",
            }
        }
        warning = "[CONTEXT LOW: 18.5% remaining] Finish current step."

        result = _inject_context_warning(existing_result, warning)
        assert result is not None
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "[STATE: DO]" in ctx
        assert "[CONTEXT LOW" in ctx

    def test_inject_context_warning_create(self):
        """Creates a new allow result when input result is None."""
        from hooks.pre_tool_use import _inject_context_warning

        warning = "[CONTEXT LOW: 18.5% remaining] Finish current step."

        result = _inject_context_warning(None, warning)
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
        assert "[CONTEXT LOW" in result["hookSpecificOutput"]["additionalContext"]


class TestStatuslineWritesContextRemaining:
    """Tests for statusline.py::main() writing context_remaining file."""

    def test_statusline_writes_context_remaining(self, tmp_path, monkeypatch):
        """statusline.main() writes remaining_percentage to .claude/context_remaining."""
        # Create .claude dir in tmp_path
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Mock stdin with JSON containing workspace.current_dir = tmp_path
        stdin_data = json.dumps({
            "model": {"display_name": "Claude"},
            "workspace": {"current_dir": str(tmp_path)},
            "context_window": {
                "used_percentage": 57.5,
                "remaining_percentage": 42.5,
                "total_input_tokens": 100000,
                "total_output_tokens": 50000,
            },
        })
        monkeypatch.setattr("sys.stdin", StringIO(stdin_data))

        # Capture stdout
        captured = StringIO()
        monkeypatch.setattr("sys.stdout", captured)

        # Import and run
        import statusline
        statusline.main()

        # Verify file written with correct value
        remaining_file = claude_dir / "context_remaining"
        assert remaining_file.exists()
        assert remaining_file.read_text(encoding="utf-8").strip() == "42.5"

        # Verify stdout contains usage info
        output = captured.getvalue()
        assert "57.5% used" in output
