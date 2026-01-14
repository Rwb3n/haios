# generated: 2026-01-03
# System Auto: last updated on: 2026-01-04T20:40:44
"""
Tests for MemoryBridge module (E2-241).

Tests L4 functional requirements:
- query(query, mode) -> QueryResult
- store(content, source_path) -> StoreResult
- auto_link(work_id, concept_ids) -> None

Tests L4 invariants:
- MUST handle MCP timeout gracefully (retry once, then warn)
- MUST parse work_id from source_path for auto-linking
- MUST NOT block on MCP failure (degrade gracefully)
"""
import sys
from pathlib import Path

import pytest

# Add module path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestQuery:
    """Tests for query function (L4 requirement)."""

    def test_query_returns_query_result(self, mocker):
        """L4: query(query, mode) returns QueryResult with concepts and reasoning."""
        from memory_bridge import MemoryBridge, QueryResult

        bridge = MemoryBridge()
        # Mock _call_mcp to return valid response
        mocker.patch.object(
            bridge,
            "_call_mcp",
            return_value={"results": [{"id": 1, "content": "test"}], "reasoning": {"outcome": "success"}},
        )

        result = bridge.query("test query", mode="semantic")

        assert isinstance(result, QueryResult)
        assert hasattr(result, "concepts")
        assert hasattr(result, "reasoning")
        assert len(result.concepts) == 1

    def test_query_supports_all_modes(self, mocker):
        """L4: Query modes (semantic, session_recovery, knowledge_lookup)."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mocker.patch.object(bridge, "_call_mcp", return_value={"results": [], "reasoning": {}})

        for mode in ["semantic", "session_recovery", "knowledge_lookup"]:
            result = bridge.query("test", mode=mode)
            assert result is not None

    def test_query_invalid_mode_defaults_to_semantic(self, mocker):
        """Invalid mode defaults to semantic with warning."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mock_call = mocker.patch.object(bridge, "_call_mcp", return_value={"results": [], "reasoning": {}})

        bridge.query("test", mode="invalid_mode")

        # Should have called with semantic mode
        call_args = mock_call.call_args
        assert call_args[0][1]["mode"] == "semantic"


class TestStore:
    """Tests for store function (L4 requirement)."""

    def test_store_returns_store_result(self, mocker):
        """L4: store(content, source_path) returns StoreResult with concept IDs."""
        from memory_bridge import MemoryBridge, StoreResult

        bridge = MemoryBridge()
        mocker.patch.object(
            bridge, "_call_mcp", return_value={"concept_ids": [12345], "classification": "techne"}
        )

        result = bridge.store("Test content", "docs/test.md")

        assert isinstance(result, StoreResult)
        assert result.concept_ids == [12345]
        assert result.classification == "techne"

    def test_store_triggers_auto_link_when_work_id_found(self, mocker):
        """Store calls auto_link when work_id can be parsed from path."""
        from memory_bridge import MemoryBridge

        mock_callback = mocker.Mock()
        bridge = MemoryBridge(work_engine_callback=mock_callback)
        mocker.patch.object(
            bridge, "_call_mcp", return_value={"concept_ids": [123], "classification": "techne"}
        )

        bridge.store("Test content", "docs/work/active/E2-241/plans/PLAN.md")

        mock_callback.assert_called_once_with("E2-241", [123])


class TestAutoLink:
    """Tests for auto_link and _parse_work_id (L4 requirement)."""

    def test_parse_work_id_from_active_path(self):
        """L4: auto_link parses work_id from source_path - active work."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()

        work_id = bridge._parse_work_id("docs/work/active/E2-241/plans/PLAN.md")
        assert work_id == "E2-241"

    def test_parse_work_id_from_archive_path(self):
        """Parse work_id from archive path."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()

        work_id = bridge._parse_work_id("docs/work/archive/INV-023/WORK.md")
        assert work_id == "INV-023"

    def test_parse_work_id_returns_none_for_non_work_path(self):
        """Parse returns None for paths without work IDs."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()

        work_id = bridge._parse_work_id("docs/specs/some-spec.md")
        assert work_id is None

    def test_auto_link_calls_callback(self, mocker):
        """auto_link invokes work_engine_callback with correct args."""
        from memory_bridge import MemoryBridge

        mock_callback = mocker.Mock()
        bridge = MemoryBridge(work_engine_callback=mock_callback)

        bridge.auto_link("E2-241", [100, 101, 102])

        mock_callback.assert_called_once_with("E2-241", [100, 101, 102])

    def test_auto_link_no_callback_no_error(self):
        """auto_link with no callback does not error."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()  # No callback

        # Should not raise
        bridge.auto_link("E2-241", [100])


class TestInvariants:
    """Tests for L4 invariants."""

    def test_timeout_returns_empty_not_error(self, mocker):
        """L4 Invariant: MUST NOT block on MCP failure (degrade gracefully)."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mocker.patch.object(bridge, "_call_mcp", side_effect=TimeoutError("MCP timeout"))

        result = bridge.query("test")

        assert result.concepts == []
        assert result.reasoning.get("degraded") is True

    def test_retry_once_on_timeout(self, mocker):
        """L4 Invariant: MUST handle MCP timeout gracefully (retry once, then warn)."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mock_mcp = mocker.patch.object(
            bridge, "_call_mcp", side_effect=[TimeoutError("first"), {"results": [], "reasoning": {}}]
        )

        result = bridge.query("test")

        assert mock_mcp.call_count == 2  # One retry
        assert result.concepts == []

    def test_memory_bridge_is_stateless(self):
        """L4 Invariant: Same input produces same output across instances."""
        from memory_bridge import MemoryBridge

        bridge1 = MemoryBridge()
        bridge2 = MemoryBridge()

        # Both instances should have identical initial state
        assert bridge1._handlers == bridge2._handlers == {}
        assert bridge1._work_engine_callback is None
        assert bridge2._work_engine_callback is None

    def test_store_error_returns_store_result_with_error(self, mocker):
        """Store failure returns StoreResult with error, not exception."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mocker.patch.object(bridge, "_call_mcp", side_effect=Exception("MCP error"))

        result = bridge.store("content", "path.md")

        assert result.concept_ids == []
        assert result.error is not None


class TestCallMcpDispatch:
    """Tests for E2-253: _call_mcp implementation."""

    def test_call_mcp_search_dispatches_correctly(self, mocker):
        """_call_mcp with memory_search_with_experience calls _search_with_experience."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mock_search = mocker.patch.object(
            bridge, "_search_with_experience", return_value={"results": [], "reasoning": {}}
        )

        bridge._call_mcp("memory_search_with_experience", {"query": "test"})

        mock_search.assert_called_once_with({"query": "test"})

    def test_call_mcp_ingest_dispatches_correctly(self, mocker):
        """_call_mcp with ingester_ingest calls _ingest."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        mock_ingest = mocker.patch.object(
            bridge, "_ingest", return_value={"concept_ids": [], "classification": "unknown"}
        )

        bridge._call_mcp("ingester_ingest", {"content": "test", "source_path": "test.md"})

        mock_ingest.assert_called_once()

    def test_call_mcp_unknown_tool_raises(self):
        """_call_mcp with unknown tool raises ValueError."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()

        with pytest.raises(ValueError, match="Unknown tool"):
            bridge._call_mcp("nonexistent_tool", {})


class TestQueryRewriting:
    """Tests for E2-253: Query rewriting feature."""

    def test_query_applies_rewriting_when_enabled(self, mocker):
        """query() applies rewriting when enable_rewriting=True."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge(enable_rewriting=True)
        mock_rewrite = mocker.patch.object(bridge, "_rewrite_query", return_value="rewritten")
        mocker.patch.object(bridge, "_call_mcp", return_value={"results": [], "reasoning": {}})

        bridge.query("original query")

        mock_rewrite.assert_called_once_with("original query")

    def test_query_skips_rewriting_when_disabled(self, mocker):
        """query() skips rewriting when enable_rewriting=False."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge(enable_rewriting=False)
        mock_rewrite = mocker.patch.object(bridge, "_rewrite_query")
        mocker.patch.object(bridge, "_call_mcp", return_value={"results": [], "reasoning": {}})

        bridge.query("original query")

        mock_rewrite.assert_not_called()

    def test_rewrite_short_query_passthrough(self):
        """Queries shorter than threshold pass through unchanged."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        result = bridge._rewrite_query("hi")
        assert result == "hi"

    def test_rewrite_falls_back_on_api_error(self, mocker):
        """Rewriting falls back to original on API error."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        # Mock genai to raise exception
        mocker.patch("memory_bridge.genai.configure", side_effect=Exception("API error"))

        result = bridge._rewrite_query("longer query that should be rewritten")
        assert result == "longer query that should be rewritten"


# =============================================================================
# E2-261: Error Capture Tests
# =============================================================================


class TestErrorCapture:
    """Tests for error capture methods (E2-261)."""

    def test_is_actual_error_bash_failure(self):
        """is_actual_error returns True for bash exit code != 0."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        result = bridge.is_actual_error("Bash", {"exit_code": 1})
        assert result is True

    def test_is_actual_error_bash_success(self):
        """is_actual_error returns False for bash exit code 0."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        result = bridge.is_actual_error("Bash", {"exit_code": 0})
        assert result is False

    def test_capture_error_returns_dict(self, mocker):
        """capture_error returns result dict."""
        from memory_bridge import MemoryBridge

        # Mock store_error to avoid DB access
        mocker.patch(
            "error_capture.store_error",
            return_value={"success": True, "concept_id": 123, "tool": "Bash"},
        )
        bridge = MemoryBridge()
        result = bridge.capture_error("Bash", "Command failed")
        assert result["success"] is True


# =============================================================================
# E2-262: Learning Extraction Tests
# =============================================================================


class TestLearningExtraction:
    """Tests for learning extraction method (E2-262)."""

    def test_extract_learnings_returns_result_type(self):
        """extract_learnings returns LearningExtractionResult."""
        from memory_bridge import MemoryBridge, LearningExtractionResult

        bridge = MemoryBridge()
        # Non-existent file should return error result
        result = bridge.extract_learnings("/nonexistent/path.jsonl")
        assert isinstance(result, LearningExtractionResult)

    def test_extract_learnings_handles_missing_file(self):
        """extract_learnings handles missing transcript file."""
        from memory_bridge import MemoryBridge

        bridge = MemoryBridge()
        result = bridge.extract_learnings("/nonexistent/transcript.jsonl")
        assert result.success is False
        assert result.reason == "error"
        assert result.error is not None

    def test_extract_learnings_delegates_to_reasoning_extraction(self, mocker, tmp_path):
        """extract_learnings delegates to reasoning_extraction functions."""
        from memory_bridge import MemoryBridge

        # Create a real temporary file so os.path.exists returns True
        transcript_file = tmp_path / "transcript.jsonl"
        transcript_file.write_text('{"type": "user", "message": {"content": [{"type": "text", "text": "test"}]}}')

        # Import reasoning_extraction first so we can mock it
        import sys
        hooks_path = str(Path(__file__).parent.parent / ".claude" / "hooks")
        if hooks_path not in sys.path:
            sys.path.insert(0, hooks_path)

        # Now mock the functions after they're importable
        import reasoning_extraction
        mock_parse = mocker.patch.object(
            reasoning_extraction, "parse_transcript",
            return_value={"initial_query": "test", "tool_count": 5, "message_count": 10, "tools_used": ["Bash"]}
        )
        mocker.patch.object(
            reasoning_extraction, "should_extract",
            return_value=(True, "qualified")
        )
        mocker.patch.object(
            reasoning_extraction, "determine_outcome",
            return_value="success"
        )
        mocker.patch.object(
            reasoning_extraction, "extract_and_store",
            return_value=True
        )
        mocker.patch.object(reasoning_extraction, "load_env")

        bridge = MemoryBridge()
        result = bridge.extract_learnings(str(transcript_file))

        assert result.success is True
        assert result.reason == "qualified"
        mock_parse.assert_called_once()
