"""
Tests for WORK-248: Hook Infrastructure Cleanup — Dead Code and Stale Gates.

Verifies removal of disabled code, dead functions, orphaned scripts,
and session-scoping of the process review gate.
"""
import importlib
import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

# Resolve project root and hook paths
PROJECT_ROOT = Path(__file__).parent.parent
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks" / "hooks"
USER_PROMPT_SUBMIT = HOOKS_DIR / "user_prompt_submit.py"
PRE_TOOL_USE = HOOKS_DIR / "pre_tool_use.py"
ORPHAN_MEMORY_RETRIEVAL = PROJECT_ROOT / ".claude" / "hooks" / "memory_retrieval.py"
ORPHAN_REASONING_EXTRACTION = PROJECT_ROOT / ".claude" / "hooks" / "reasoning_extraction.py"


# --- AC1: Disabled vitals/thresholds code removed ---


class TestAC1DisabledCodeRemoved:
    """AC1: Remove disabled vitals and thresholds code from user_prompt_submit.py."""

    def test_vitals_block_not_in_handle(self):
        """Disabled S179 vitals block must be removed from handle()."""
        source = USER_PROMPT_SUBMIT.read_text(encoding="utf-8")
        assert "DISABLED Session 179" not in source, (
            "Disabled S179 vitals block still present in user_prompt_submit.py"
        )
        assert "_refresh_slim_status" not in source, (
            "_refresh_slim_status reference still present in user_prompt_submit.py"
        )

    def test_thresholds_block_not_in_handle(self):
        """Disabled S259 thresholds block must be removed from handle()."""
        source = USER_PROMPT_SUBMIT.read_text(encoding="utf-8")
        assert "DISABLED Session 259" not in source, (
            "Disabled S259 thresholds block still present in user_prompt_submit.py"
        )
        assert "_get_thresholds" not in source, (
            "_get_thresholds reference still present in user_prompt_submit.py"
        )
        assert "_get_vitals" not in source, (
            "_get_vitals reference still present in user_prompt_submit.py"
        )

    def test_dead_functions_removed(self):
        """Dead function definitions must not exist in module."""
        source = USER_PROMPT_SUBMIT.read_text(encoding="utf-8")
        assert "def _refresh_slim_status" not in source, (
            "_refresh_slim_status function definition still present"
        )
        assert "def _get_vitals" not in source, (
            "_get_vitals function definition still present"
        )
        assert "def _get_thresholds" not in source, (
            "_get_thresholds function definition still present"
        )


# --- AC2: batch_work_bypass dead code removed ---


class TestAC2BatchBypassRemoved:
    """AC2: Remove .batch_work_bypass dead code from pre_tool_use.py."""

    def test_batch_bypass_removed(self):
        """batch_work_bypass check must be removed from pre_tool_use.py."""
        source = PRE_TOOL_USE.read_text(encoding="utf-8")
        assert ".batch_work_bypass" not in source, (
            ".batch_work_bypass reference still present in pre_tool_use.py"
        )
        assert "Session 297" not in source, (
            "Session 297 bypass comment still present in pre_tool_use.py"
        )


# --- AC3: Orphaned hook scripts deleted ---


class TestAC3OrphanedScriptsDeleted:
    """AC3: Orphaned memory_retrieval.py and reasoning_extraction.py deleted."""

    def test_orphaned_scripts_deleted(self):
        """Orphaned memory_retrieval.py must not exist on disk.

        Note: reasoning_extraction.py is NOT orphaned — it has a live consumer
        in memory_bridge.py (extract_learnings -> parse_transcript). Kept.
        """
        assert not ORPHAN_MEMORY_RETRIEVAL.exists(), (
            f"Orphaned script still exists: {ORPHAN_MEMORY_RETRIEVAL}"
        )


# --- AC4: Process review gate scoped to current session ---


class TestAC4ProcessReviewGateSessionScoped:
    """AC4: Process review gate must scope to current session only."""

    def test_process_review_gate_session_scoped(self):
        """Cross-session ProcessReviewApproved must NOT unlock the gate."""
        # Load pre_tool_use module
        hooks_str = str(HOOKS_DIR)
        lib_dir = str(PROJECT_ROOT / ".claude" / "haios" / "lib")

        if hooks_str not in sys.path:
            sys.path.insert(0, hooks_str)
        if lib_dir not in sys.path:
            sys.path.insert(0, lib_dir)

        # Import the module (use unique name to avoid conflicts)
        spec = importlib.util.spec_from_file_location(
            "pre_tool_use_test", PRE_TOOL_USE
        )
        assert spec is not None, f"Could not load spec from {PRE_TOOL_USE}"
        ptu = importlib.util.module_from_spec(spec)
        assert spec.loader is not None, "Module spec has no loader"
        spec.loader.exec_module(ptu)

        # Mock: event from session 999, but current session is 474
        mock_events = [
            {
                "type": "ProcessReviewApproved",
                "session_id": 999,
                "timestamp": "2026-01-01T00:00:00",
            }
        ]

        with patch("governance_events.read_events", return_value=mock_events), \
             patch("governance_events._read_session_id", return_value=474):
            result = ptu._check_process_review_gate(
                "D:\\PROJECTS\\haios\\.claude\\haios\\manifesto\\L3\\some.md"
            )

        # Gate should DENY because the approval is from a different session
        assert result is not None, (
            "Process review gate should deny cross-session approval"
        )
        # _deny() returns {'hookSpecificOutput': {'permissionDecision': 'deny', ...}}
        hook_output = result.get("hookSpecificOutput", {})
        assert hook_output.get("permissionDecision") == "deny", (
            f"Expected deny, got: {result}"
        )
