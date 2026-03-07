# generated: 2026-02-22
# System Auto: last updated on: 2026-03-07T00:00:00
"""
Tests for UserPromptSubmit hook functions (WORK-195).

Tests _get_session_state_warning and _get_phase_contract with slim dict parameter.
(WORK-247: Removed TestGetContextUsage and TestHandleIntegration — retired functions.)
"""
import sys
from pathlib import Path

import pytest

# Add hooks directory to path for imports (mirrors test_hooks.py pattern)
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

PROJECT_ROOT = Path(__file__).parent.parent
TEST_CWD = str(PROJECT_ROOT)


class TestGetSessionStateWarning:
    """Unit tests for _get_session_state_warning with slim dict parameter (WORK-195)."""

    def test_session_state_warning_no_active_cycle(self):
        """Returns warning when no active governance cycle."""
        from hooks import user_prompt_submit

        slim = {"session_state": {"active_cycle": None}}
        result = user_prompt_submit._get_session_state_warning(TEST_CWD, slim)
        assert result is not None
        assert "No active governance cycle detected" in result

    def test_session_state_warning_with_active_cycle(self):
        """Returns None when active cycle exists (no warning needed)."""
        from hooks import user_prompt_submit

        slim = {
            "session_state": {
                "active_cycle": "implementation-cycle",
                "current_phase": "DO",
                "work_id": "WORK-195",
            }
        }
        result = user_prompt_submit._get_session_state_warning(TEST_CWD, slim)
        assert result is None

    def test_session_state_warning_slim_none(self):
        """Returns None when slim is None (graceful degradation)."""
        from hooks import user_prompt_submit

        result = user_prompt_submit._get_session_state_warning(TEST_CWD, None)
        assert result is None


class TestGetPhaseContract:
    """Unit tests for _get_phase_contract with slim dict parameter (WORK-195)."""

    def test_phase_contract_no_active_cycle(self):
        """Returns None when no active cycle in slim."""
        from hooks import user_prompt_submit

        slim = {"session_state": {"active_cycle": None, "current_phase": None}}
        result = user_prompt_submit._get_phase_contract(TEST_CWD, slim)
        assert result is None
