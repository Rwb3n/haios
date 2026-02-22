# generated: 2026-02-22
# System Auto: last updated on: 2026-02-22T15:10:00
"""
Tests for context window usage injection via UserPromptSubmit hook (WORK-189).

Tests the _get_context_usage function that parses transcript JSONL
for API usage metadata to calculate real context window consumption.

Pattern from: github.com/harrymunro/nelson/scripts/count-tokens.py
"""
import json
import sys
from pathlib import Path

import pytest

# Add hooks directory to path for imports (mirrors test_hooks.py pattern)
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

PROJECT_ROOT = Path(__file__).parent.parent
TEST_CWD = str(PROJECT_ROOT)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    """Helper to write JSONL test fixtures."""
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


class TestGetContextUsage:
    """Unit tests for _get_context_usage function."""

    def test_get_context_usage_happy_path(self, tmp_path):
        """Test 1: Usage data extracted and formatted correctly."""
        from hooks import user_prompt_submit

        jsonl_path = tmp_path / "transcript.jsonl"
        records = [
            {
                "type": "assistant",
                "message": {
                    "usage": {
                        "input_tokens": 50000,
                        "cache_creation_input_tokens": 10000,
                        "cache_read_input_tokens": 15000,
                    }
                },
            },
            {
                "type": "assistant",
                "message": {
                    "usage": {
                        "input_tokens": 100000,
                        "cache_creation_input_tokens": 20000,
                        "cache_read_input_tokens": 30000,
                    }
                },
            },
        ]
        _write_jsonl(jsonl_path, records)

        result = user_prompt_submit._get_context_usage(str(jsonl_path))
        # Last message: 100000 + 20000 + 30000 = 150000 / 200000 = 75%
        assert result == "[CONTEXT: 75% used]"

    def test_get_context_usage_missing_file(self):
        """Test 2: Graceful degradation when transcript file doesn't exist."""
        from hooks import user_prompt_submit

        result = user_prompt_submit._get_context_usage("/nonexistent/path.jsonl")
        assert result is None

    def test_get_context_usage_empty_file(self, tmp_path):
        """Test 3: Graceful degradation when transcript is empty."""
        from hooks import user_prompt_submit

        jsonl_path = tmp_path / "transcript.jsonl"
        jsonl_path.write_text("")

        result = user_prompt_submit._get_context_usage(str(jsonl_path))
        assert result is None

    def test_get_context_usage_no_usage_data(self, tmp_path):
        """Test 4: Graceful degradation when assistant messages lack usage."""
        from hooks import user_prompt_submit

        jsonl_path = tmp_path / "transcript.jsonl"
        records = [
            {"type": "assistant", "message": {"content": "Hello"}},
            {"type": "assistant", "message": {"content": "World"}},
        ]
        _write_jsonl(jsonl_path, records)

        result = user_prompt_submit._get_context_usage(str(jsonl_path))
        assert result is None

    def test_get_context_usage_all_zero_returns_none(self, tmp_path):
        """Test 6: All-zero usage fields return None, not false '[CONTEXT: 0% used]'."""
        from hooks import user_prompt_submit

        jsonl_path = tmp_path / "transcript.jsonl"
        records = [
            {
                "type": "assistant",
                "message": {
                    "usage": {
                        "input_tokens": 0,
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 0,
                    }
                },
            },
        ]
        _write_jsonl(jsonl_path, records)

        result = user_prompt_submit._get_context_usage(str(jsonl_path))
        # Should return None (graceful degradation), NOT "[CONTEXT: 0% used]"
        assert result is None


class TestHandleIntegration:
    """Integration test for handle() wiring."""

    def test_handle_includes_context_usage(self, tmp_path, monkeypatch):
        """Test 5: handle() includes context usage in output."""
        from hooks import user_prompt_submit

        monkeypatch.setattr(
            user_prompt_submit,
            "_get_context_usage",
            lambda p: "[CONTEXT: 50% used]",
        )

        hook_data = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
            "transcript_path": str(tmp_path / "transcript.jsonl"),
            "cwd": TEST_CWD,
        }
        result = user_prompt_submit.handle(hook_data)
        assert "[CONTEXT: 50% used]" in result
