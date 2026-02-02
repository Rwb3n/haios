# generated: 2025-12-20
# System Auto: last updated on: 2026-02-01T22:11:23
"""
Tests for Python hook dispatcher (E2-085).

Test categories:
1. Dispatcher routing
2. UserPromptSubmit vitals injection
3. PreToolUse SQL blocking
4. PostToolUse timestamp injection
5. Stop hook extraction
6. Backward compatibility
"""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

# Test data directory - use project root for haios-status-slim.json
PROJECT_ROOT = Path(__file__).parent.parent
TEST_CWD = str(PROJECT_ROOT)


class TestDispatcherRouting:
    """Test 1: Dispatcher routes to correct handler."""

    def test_dispatcher_routes_user_prompt_submit(self):
        """Verify dispatcher routes UserPromptSubmit to correct handler."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
            "cwd": TEST_CWD
        }
        result = dispatch_hook(hook_input)
        # Should return string with date/time
        assert result is not None
        assert isinstance(result, str)
        assert "Today is" in result

    def test_dispatcher_routes_pre_tool_use(self):
        """Verify dispatcher routes PreToolUse to correct handler."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls"}
        }
        result = dispatch_hook(hook_input)
        # WORK-064: Now returns context on allow (non-SQL bash should be allowed)
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
        assert "additionalContext" in result["hookSpecificOutput"]

    def test_dispatcher_routes_post_tool_use(self):
        """Verify dispatcher routes PostToolUse to correct handler."""
        from hook_dispatcher import dispatch_hook

        # Create a temp file to test timestamp injection
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
            f.write("# original content\n")
            temp_path = f.name

        try:
            hook_input = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Edit",
                "tool_response": {"filePath": temp_path}
            }
            result = dispatch_hook(hook_input)
            # PostToolUse returns status message or None
            assert result is None or isinstance(result, str)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_dispatcher_routes_stop(self):
        """Verify dispatcher routes Stop to correct handler."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "transcript_path": "/nonexistent/path.jsonl"
        }
        result = dispatch_hook(hook_input)
        # Should return None for non-existent transcript
        assert result is None

    def test_dispatcher_handles_unknown_event(self):
        """Verify unknown events don't crash."""
        from hook_dispatcher import dispatch_hook

        hook_input = {"hook_event_name": "UnknownEvent"}
        result = dispatch_hook(hook_input)
        assert result is None


class TestUserPromptSubmitVitals:
    """Test 2: UserPromptSubmit vitals injection."""

    def test_vitals_disabled_session_179(self):
        """Verify vitals are disabled per Session 179 (E2.2 chapter redesign)."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
            "cwd": TEST_CWD
        }
        result = dispatch_hook(hook_input)
        # Vitals disabled in Session 179 - should NOT contain HAIOS Vitals
        # Instead, should contain session state warning (E2-287)
        assert "HAIOS Vitals" not in result
        # But should have date
        assert "Today is" in result

    def test_vitals_graceful_fail_no_slim(self):
        """Verify no crash if slim.json missing."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
            "cwd": "/nonexistent/path"
        }
        result = dispatch_hook(hook_input)
        # Should still output date
        assert "Today is" in result

    def test_date_time_always_present(self):
        """Verify date/time is always in output."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test",
            "cwd": ""
        }
        result = dispatch_hook(hook_input)
        assert "Today is" in result
        # Should have day of week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert any(day in result for day in days)


class TestSessionStateWarning:
    """E2-287: Session state warning injection tests."""

    def test_session_state_warning_when_no_cycle(self, tmp_path):
        """E2-287: Inject warning when session_state.active_cycle is null."""
        # Add hooks directory to path
        hooks_path = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
        if str(hooks_path) not in sys.path:
            sys.path.insert(0, str(hooks_path))

        from user_prompt_submit import _get_session_state_warning

        # Create slim status with null active_cycle
        slim = {"session_state": {"active_cycle": None}}
        slim_dir = tmp_path / ".claude"
        slim_dir.mkdir(parents=True)
        slim_path = slim_dir / "haios-status-slim.json"
        slim_path.write_text(json.dumps(slim))

        warning = _get_session_state_warning(str(tmp_path))

        assert warning is not None
        assert "No active governance cycle" in warning
        assert "skill" in warning.lower()

    def test_no_warning_when_cycle_active(self, tmp_path):
        """E2-287: No warning when session_state.active_cycle is set."""
        hooks_path = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
        if str(hooks_path) not in sys.path:
            sys.path.insert(0, str(hooks_path))

        from user_prompt_submit import _get_session_state_warning

        # Create slim status with active cycle
        slim = {"session_state": {"active_cycle": "implementation-cycle"}}
        slim_dir = tmp_path / ".claude"
        slim_dir.mkdir(parents=True)
        slim_path = slim_dir / "haios-status-slim.json"
        slim_path.write_text(json.dumps(slim))

        warning = _get_session_state_warning(str(tmp_path))

        assert warning is None

    def test_no_warning_when_session_state_missing(self, tmp_path):
        """E2-287: Handle missing session_state gracefully (backward compat)."""
        hooks_path = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
        if str(hooks_path) not in sys.path:
            sys.path.insert(0, str(hooks_path))

        from user_prompt_submit import _get_session_state_warning

        # Create slim status without session_state (old format)
        slim = {"generated": "2026-01-14"}
        slim_dir = tmp_path / ".claude"
        slim_dir.mkdir(parents=True)
        slim_path = slim_dir / "haios-status-slim.json"
        slim_path.write_text(json.dumps(slim))

        warning = _get_session_state_warning(str(tmp_path))

        # Should not crash, should return None (no warning for old format)
        assert warning is None


class TestPreToolUseSqlBlocking:
    """Test 3: PreToolUse SQL blocking."""

    def test_pretooluse_blocks_direct_sql(self):
        """Verify SQL queries are blocked without schema-verifier."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "sqlite3 db.sqlite 'SELECT * FROM concepts'"}
        }
        result = dispatch_hook(hook_input)
        assert result is not None
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "schema-verifier" in result["hookSpecificOutput"]["permissionDecisionReason"]

    def test_pretooluse_allows_safe_sql(self):
        """Verify safe patterns like PRAGMA are allowed."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "sqlite3 db.sqlite 'PRAGMA table_info(concepts)'"}
        }
        result = dispatch_hook(hook_input)
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_pretooluse_allows_pytest(self):
        """Verify pytest commands are allowed."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/ -v"}
        }
        result = dispatch_hook(hook_input)
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_pretooluse_allows_non_bash(self):
        """Verify non-Bash tools are allowed."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "/some/file.py"}
        }
        result = dispatch_hook(hook_input)
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"


class TestPreToolUseScaffoldBlocking:
    """Test: PreToolUse scaffold recipe blocking (E2-305, refined Session 253/257).

    Note: Only 'just work' and 'just scaffold work_item' are blocked.
    Other scaffold types (plan, inv) are allowed as they chain to governed commands.
    """

    def test_blocks_just_work_recipe(self):
        """Verify 'just work WORK-XXX' is blocked with redirect to /new-work."""
        from hooks.pre_tool_use import handle
        # Pattern requires WORK-XXX or quoted title after 'just work'
        result = handle({"tool_name": "Bash", "tool_input": {"command": "just work WORK-999 'test'"}})
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "/new-work" in result["hookSpecificOutput"]["permissionDecisionReason"]

    def test_blocks_just_scaffold_work_item_recipe(self):
        """Verify 'just scaffold work_item' is blocked."""
        from hooks.pre_tool_use import handle
        result = handle({"tool_name": "Bash", "tool_input": {"command": "just scaffold work_item E2-999 'test'"}})
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_allows_just_plan_recipe(self):
        """Verify 'just plan' is allowed (Session 253 refinement)."""
        from hooks.pre_tool_use import handle
        result = handle({"tool_name": "Bash", "tool_input": {"command": "just plan E2-999 'test'"}})
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_allows_just_inv_recipe(self):
        """Verify 'just inv' is allowed (Session 253 refinement)."""
        from hooks.pre_tool_use import handle
        result = handle({"tool_name": "Bash", "tool_input": {"command": "just inv INV-999 'test'"}})
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_allows_non_scaffold_just_commands(self):
        """Verify 'just ready' is not blocked."""
        from hooks.pre_tool_use import handle
        result = handle({"tool_name": "Bash", "tool_input": {"command": "just ready"}})
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_allows_just_scaffold_observations(self):
        """Verify 'just scaffold-observations' is not blocked (hyphenated, different recipe)."""
        from hooks.pre_tool_use import handle
        result = handle({"tool_name": "Bash", "tool_input": {"command": "just scaffold-observations E2-305"}})
        # WORK-064: Now returns context on allow
        assert result is not None
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"


class TestPostToolUseTimestamps:
    """Test 4: PostToolUse timestamp injection."""

    def test_posttooluse_adds_timestamp(self):
        """Verify timestamps are added to edited files."""
        from hook_dispatcher import dispatch_hook

        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as f:
            f.write("# original content\nprint('hello')\n")
            temp_path = f.name

        try:
            hook_input = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Edit",
                "tool_response": {"filePath": temp_path}
            }
            dispatch_hook(hook_input)
            content = Path(temp_path).read_text()
            assert "System Auto: last updated on:" in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_posttooluse_skips_json(self):
        """Verify JSON files are skipped (no comment syntax)."""
        from hook_dispatcher import dispatch_hook

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode='w') as f:
            f.write('{"key": "value"}\n')
            temp_path = f.name

        try:
            hook_input = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": temp_path}
            }
            dispatch_hook(hook_input)
            content = Path(temp_path).read_text()
            # JSON should not have timestamp added
            assert "System Auto" not in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_posttooluse_handles_nonexistent_file(self):
        """Verify no crash on nonexistent file."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_response": {"filePath": "/nonexistent/file.py"}
        }
        result = dispatch_hook(hook_input)
        # Should not crash, return None
        assert result is None


class TestStopHook:
    """Test 5: Stop hook extraction."""

    def test_stop_hook_prevents_infinite_loop(self):
        """Verify stop_hook_active=True causes early exit."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "Stop",
            "stop_hook_active": True
        }
        result = dispatch_hook(hook_input)
        assert result is None

    def test_stop_hook_handles_missing_transcript(self):
        """Verify no crash if transcript missing."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "transcript_path": "/nonexistent/transcript.jsonl"
        }
        result = dispatch_hook(hook_input)
        # Should return None, not crash
        assert result is None

    def test_stop_hook_handles_no_transcript_path(self):
        """Verify no crash if transcript_path not provided."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "Stop",
            "stop_hook_active": False
        }
        result = dispatch_hook(hook_input)
        assert result is None


class TestBackwardCompatibility:
    """Test 6: Backward compatibility - JSON output format."""

    def test_pretooluse_json_output_format(self):
        """Verify PreToolUse returns exact JSON structure expected by Claude Code."""
        from hook_dispatcher import dispatch_hook

        # Test with governed path (should block)
        hook_input = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "docs/checkpoints/new-file.md"}
        }
        result = dispatch_hook(hook_input)

        # Should have correct structure
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
        assert result["hookSpecificOutput"]["permissionDecision"] in ["allow", "deny", "ask"]
        assert "permissionDecisionReason" in result["hookSpecificOutput"]

    def test_pretooluse_allows_existing_file_edit(self):
        """Verify editing existing governed files is allowed."""
        from hook_dispatcher import dispatch_hook

        # Create temp file in governed-like path (simulated)
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w') as f:
            f.write("# Test\n")
            temp_path = f.name

        try:
            hook_input = {
                "hook_event_name": "PreToolUse",
                "tool_name": "Edit",
                "tool_input": {"file_path": temp_path}
            }
            result = dispatch_hook(hook_input)
            # WORK-064: Now returns context on allow
            assert result is not None
            assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestLifecycleGuidance:
    """Test lifecycle and RFC2119 features."""

    def test_lifecycle_guidance_for_plan_intent(self):
        """Verify lifecycle guidance triggers for plan creation."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "/new-plan E2-999 Test Feature",
            "cwd": TEST_CWD
        }
        result = dispatch_hook(hook_input)
        # Should include lifecycle guidance since no investigation exists
        assert "Today is" in result  # Always has date

    def test_rfc2119_discovery_trigger(self):
        """Verify RFC2119 reminder for discovery keywords."""
        from hook_dispatcher import dispatch_hook

        hook_input = {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "I found a bug in the system",
            "cwd": TEST_CWD
        }
        result = dispatch_hook(hook_input)
        # Should trigger discovery reminder
        assert "RFC 2119" in result or "Today is" in result


class TestContextThreshold:
    """Test E2-210: Context threshold auto-checkpoint warning."""

    def test_estimate_context_usage_calculates_percentage(self):
        """Estimate context from transcript file size."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            # Write ~4000 chars ≈ 1000 tokens ≈ 0.5% of 200k
            for _ in range(100):
                f.write(json.dumps({"type": "user", "content": "a" * 40}) + "\n")
            f.flush()
            temp_path = f.name

        try:
            from hooks.user_prompt_submit import _estimate_context_usage
            pct = _estimate_context_usage(temp_path)
            assert 0 < pct < 5  # Should be small percentage
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_check_context_threshold_warns_above_80(self):
        """Warning returned when context > 80%."""
        with patch('hooks.user_prompt_submit._estimate_context_usage', return_value=85.0):
            from hooks.user_prompt_submit import _check_context_threshold
            warning = _check_context_threshold("/fake/path")
            assert warning is not None
            assert "CONTEXT:" in warning
            assert "85%" in warning
            assert "checkpoint" in warning.lower()

    def test_check_context_threshold_silent_below_80(self):
        """No warning when context < 80%."""
        with patch('hooks.user_prompt_submit._estimate_context_usage', return_value=50.0):
            from hooks.user_prompt_submit import _check_context_threshold
            warning = _check_context_threshold("/fake/path")
            assert warning is None


class TestYamlTimestampNestedStructures:
    """Test E2-172: YAML timestamp injection preserves nested structures."""

    def test_yaml_timestamp_preserves_node_history(self, tmp_path):
        """Verify node_history arrays survive timestamp injection."""
        from hooks.post_tool_use import _add_yaml_timestamp

        test_file = tmp_path / "test.md"
        content = """---
current_node: plan
node_history:
  - node: backlog
    entered: 2025-12-24T10:00:00
    exited: 2025-12-24T11:00:00
  - node: plan
    entered: 2025-12-24T11:00:00
    exited: null
---
# Content"""
        test_file.write_text(content)
        lines = content.split("\n")

        _add_yaml_timestamp(test_file, lines, 10, "2025-12-24", "2025-12-24T12:00:00")

        result = test_file.read_text()
        # Both node entries should be preserved
        assert "node: backlog" in result
        assert "node: plan" in result
        assert result.count("- node:") == 2

    def test_yaml_timestamp_flat_fields_still_work(self, tmp_path):
        """Verify simple flat YAML fields still work correctly."""
        from hooks.post_tool_use import _add_yaml_timestamp

        test_file = tmp_path / "test.md"
        content = """---
template: checkpoint
status: active
---
# Content"""
        test_file.write_text(content)
        lines = content.split("\n")

        _add_yaml_timestamp(test_file, lines, 3, "2025-12-24", "2025-12-24T12:00:00")

        result = test_file.read_text()
        assert "template: checkpoint" in result
        assert "status: active" in result
        # yaml.dump may quote date strings, so check for the value, not exact format
        assert "2025-12-24" in result and "generated" in result
        assert "2025-12-24T12:00:00" in result and "last_updated" in result


class TestPreToolUseAdditionalContext:
    """Test WORK-064: PreToolUse additionalContext for state visibility."""

    def test_additional_context_on_allow(self, mocker):
        """WORK-064: additionalContext should be present even when tool is allowed."""
        import subprocess
        from hooks.pre_tool_use import handle

        # Mock subprocess.run to simulate DO state
        mock_result = mocker.Mock()
        mock_result.stdout = "implementation-cycle/DO/WORK-064"
        mock_result.returncode = 0
        mocker.patch.object(subprocess, "run", return_value=mock_result)

        hook_data = {"tool_name": "Read", "tool_input": {"file_path": "/some/file.py"}}
        result = handle(hook_data)

        # Read is allowed in DO - should have additionalContext
        assert result is not None
        assert "hookSpecificOutput" in result
        assert "additionalContext" in result["hookSpecificOutput"]

    def test_additional_context_includes_state_and_blocked(self, mocker):
        """WORK-064: additionalContext should contain current state and blocked primitives."""
        import subprocess
        from hooks.pre_tool_use import handle

        mock_result = mocker.Mock()
        mock_result.stdout = "implementation-cycle/DO/WORK-064"
        mock_result.returncode = 0
        mocker.patch.object(subprocess, "run", return_value=mock_result)

        hook_data = {"tool_name": "Read", "tool_input": {}}
        result = handle(hook_data)

        context = result["hookSpecificOutput"].get("additionalContext", "")
        assert "[STATE: DO]" in context
        assert "Blocked:" in context
        # DO state blocks: user-query, web-fetch, web-search, memory-search, memory-store
        assert "user-query" in context

    def test_deny_behavior_preserved_with_context(self, mocker):
        """WORK-064: Deny responses should still block with reason AND include context."""
        import subprocess
        from hooks.pre_tool_use import handle

        mock_result = mocker.Mock()
        mock_result.stdout = "implementation-cycle/DO/WORK-064"
        mock_result.returncode = 0
        mocker.patch.object(subprocess, "run", return_value=mock_result)

        # AskUserQuestion is blocked in DO state
        hook_data = {"tool_name": "AskUserQuestion", "tool_input": {}}
        result = handle(hook_data)

        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "permissionDecisionReason" in result["hookSpecificOutput"]
        assert "additionalContext" in result["hookSpecificOutput"]

    def test_graceful_degradation_on_governance_failure(self, mocker):
        """WORK-064: When subprocess fails, default to EXPLORE state (fail-permissive)."""
        import subprocess
        from hooks.pre_tool_use import handle

        # Make subprocess.run raise exception - GovernanceLayer.get_activity_state()
        # catches this and returns "EXPLORE" as default (fail-permissive)
        mocker.patch.object(subprocess, "run", side_effect=Exception("Simulated failure"))

        hook_data = {"tool_name": "Read", "tool_input": {}}
        result = handle(hook_data)

        # Should default to EXPLORE state and still provide context
        assert result is not None
        assert "hookSpecificOutput" in result
        assert "[STATE: EXPLORE]" in result["hookSpecificOutput"]["additionalContext"]


class TestMemoryRefsAutoLink:
    """Test E2-238: PostToolUse memory_refs auto-linking."""

    def test_extract_work_id_from_active_path(self):
        """Extract work_id from docs/work/active/{id}/... paths."""
        from hooks.post_tool_use import _extract_work_id_from_source_path

        source_path = "docs/work/active/E2-238/plans/PLAN.md"
        work_id = _extract_work_id_from_source_path(source_path)
        assert work_id == "E2-238"

    def test_extract_work_id_from_archive_path(self):
        """Extract work_id from docs/work/archive/{id}/... paths."""
        from hooks.post_tool_use import _extract_work_id_from_source_path

        source_path = "docs/work/archive/INV-052/WORK.md"
        work_id = _extract_work_id_from_source_path(source_path)
        assert work_id == "INV-052"

    def test_extract_work_id_from_closure_prefix(self):
        """Extract work_id from closure:{id} source_path."""
        from hooks.post_tool_use import _extract_work_id_from_source_path

        source_path = "closure:E2-269"
        work_id = _extract_work_id_from_source_path(source_path)
        assert work_id == "E2-269"

    def test_extract_work_id_returns_none_for_invalid_path(self):
        """Return None when source_path has no work_id."""
        from hooks.post_tool_use import _extract_work_id_from_source_path

        source_path = "some/random/path.md"
        work_id = _extract_work_id_from_source_path(source_path)
        assert work_id is None

    def test_auto_link_skips_when_no_concept_ids(self):
        """Auto-link returns None when response has no concept_ids."""
        from hooks.post_tool_use import _auto_link_memory_refs

        hook_data = {
            "tool_name": "mcp__haios-memory__ingester_ingest",
            "tool_input": {"source_path": "docs/work/active/E2-238/WORK.md"},
            "tool_response": {"classification": "techne"}  # No concept_ids
        }

        result = _auto_link_memory_refs(hook_data)
        assert result is None

    def test_auto_link_skips_invalid_source_path(self):
        """Auto-link returns None when source_path has no work_id."""
        from hooks.post_tool_use import _auto_link_memory_refs

        hook_data = {
            "tool_name": "mcp__haios-memory__ingester_ingest",
            "tool_input": {"source_path": "some/random/path.md"},
            "tool_response": {"concept_ids": [80001], "classification": "techne"}
        }

        result = _auto_link_memory_refs(hook_data)
        assert result is None

    def test_auto_link_calls_work_engine(self, tmp_path, monkeypatch):
        """Auto-link calls WorkEngine.add_memory_refs when valid response."""
        from hooks.post_tool_use import _auto_link_memory_refs

        # Create mock work file structure
        work_dir = tmp_path / "docs" / "work" / "active" / "E2-238"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        work_file.write_text("""---
id: E2-238
title: Test
status: active
current_node: backlog
memory_refs: []
node_history: []
---
# Test""")

        # Change to tmp_path so WorkEngine finds the file
        monkeypatch.chdir(tmp_path)

        hook_data = {
            "tool_name": "mcp__haios-memory__ingester_ingest",
            "tool_input": {"source_path": "docs/work/active/E2-238/plans/PLAN.md"},
            "tool_response": {"concept_ids": [80001, 80002], "classification": "techne"}
        }

        result = _auto_link_memory_refs(hook_data)

        # Should return status message
        assert result is not None
        assert "E2-238" in result
        assert "80001" in result or "80002" in result

        # Verify work file was updated
        content = work_file.read_text()
        assert "80001" in content or "80002" in content
