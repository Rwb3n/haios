# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21T22:33:50
"""
Tests for error capture module (E2-130).

TDD tests written BEFORE implementation.
Tests verify:
1. Bash error detection (exit_code != 0)
2. False positive prevention for Read/Edit/Write
3. Real error detection
4. Storage with dedicated type
"""
import sys
from pathlib import Path

import pytest

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestIsActualError:
    """Test error detection logic."""

    def test_bash_failure_detected(self):
        """Bash with non-zero exit code is an error."""
        from error_capture import is_actual_error

        response = {"exit_code": 1, "stderr": "command not found"}
        assert is_actual_error("Bash", response) is True

    def test_bash_success_not_captured(self):
        """Bash with exit_code 0 is NOT an error, even if output contains 'error'."""
        from error_capture import is_actual_error

        response = {"exit_code": 0, "stdout": "error handling complete"}
        assert is_actual_error("Bash", response) is False

    def test_read_success_not_captured(self):
        """Successful Read response should NOT be captured as error."""
        from error_capture import is_actual_error

        response = {
            "type": "text",
            "file": {"filePath": "/path/to/file.py", "content": "has error in code"},
        }
        assert is_actual_error("Read", response) is False

    def test_edit_success_not_captured(self):
        """Successful Edit response should NOT be captured as error."""
        from error_capture import is_actual_error

        response = {
            "filePath": "/path/to/file.py",
            "oldString": "error handling",
            "newString": "exception handling",
        }
        assert is_actual_error("Edit", response) is False

    def test_real_error_captured(self):
        """Real error response IS captured."""
        from error_capture import is_actual_error

        response = {"error": "File not found: /path/to/missing.txt"}
        assert is_actual_error("Read", response) is True

    def test_write_success_not_captured(self):
        """Successful Write response should NOT be captured."""
        from error_capture import is_actual_error

        response = {"type": "create", "filePath": "/path/to/new.py"}
        assert is_actual_error("Write", response) is False


class TestStoreError:
    """Test error storage functionality."""

    def test_store_error_uses_tool_error_type(self):
        """Errors stored with type='tool_error' for queryability."""
        from error_capture import store_error, _get_db

        # Store an error
        result = store_error("Bash", "command not found", "git foo")

        assert result["success"] is True
        assert "concept_id" in result

        # Verify in DB
        conn = _get_db()
        row = conn.execute(
            "SELECT type, content FROM concepts WHERE id = ?",
            (result["concept_id"],),
        ).fetchone()

        assert row[0] == "tool_error"
        assert "Bash" in row[1]
        assert "command not found" in row[1]


class TestIntegration:
    """Integration tests for error capture flow."""

    def test_capture_errors_returns_none_on_success(self):
        """_capture_errors returns None for successful tool use."""
        pytest.skip("Requires _capture_errors implementation in post_tool_use.py")

    def test_capture_errors_stores_on_failure(self):
        """_capture_errors stores error and returns message on failure."""
        pytest.skip("Requires _capture_errors implementation in post_tool_use.py")
