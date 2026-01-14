# generated: 2025-12-14
# System Auto: last updated on: 2025-12-14 20:10:16
"""
Tests for Query Rewriting Layer (E2-063)

TDD tests for rewrite_query_for_retrieval() function that transforms
conversational user prompts into technical, retrieval-optimized queries.
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add hooks directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / '.claude' / 'hooks'))


class TestQueryRewriter:
    """Tests for rewrite_query_for_retrieval function."""

    def test_rewrite_conversational_to_technical(self, monkeypatch):
        """Test 1: Conversational prompt becomes technical query."""
        from memory_retrieval import rewrite_query_for_retrieval

        # Set API key so function doesn't short-circuit
        monkeypatch.setenv('GOOGLE_API_KEY', 'test-key')

        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "HAIOS coldstart session initialization command"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('memory_retrieval.genai') as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model

            result = rewrite_query_for_retrieval("okay sure, lets revisit coldstart")

            assert "coldstart" in result.lower() or "HAIOS" in result
            assert result != "okay sure, lets revisit coldstart"  # Was transformed

    def test_short_query_passthrough(self):
        """Test 2: Queries under 10 chars are not rewritten (save API calls)."""
        from memory_retrieval import rewrite_query_for_retrieval

        # Short queries pass through unchanged
        assert rewrite_query_for_retrieval("test") == "test"
        assert rewrite_query_for_retrieval("schema") == "schema"
        assert rewrite_query_for_retrieval("ADR-033") == "ADR-033"

    def test_empty_query_passthrough(self):
        """Test 2b: Empty queries pass through unchanged."""
        from memory_retrieval import rewrite_query_for_retrieval

        assert rewrite_query_for_retrieval("") == ""
        assert rewrite_query_for_retrieval("   ") == "   "

    def test_rewriter_fallback_on_error(self, monkeypatch):
        """Test 3: If Gemini fails, return original query."""
        from memory_retrieval import rewrite_query_for_retrieval

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error")

        with patch('memory_retrieval.genai') as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model

            original = "some conversational query text here"
            result = rewrite_query_for_retrieval(original)

            # Should fall back to original on error
            assert result == original

    def test_rewriter_strips_whitespace(self, monkeypatch):
        """Test 3b: Rewritten query should be stripped of extra whitespace."""
        from memory_retrieval import rewrite_query_for_retrieval

        # Set API key so function doesn't short-circuit
        monkeypatch.setenv('GOOGLE_API_KEY', 'test-key')

        mock_response = MagicMock()
        mock_response.text = "  HAIOS coldstart query  \n"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('memory_retrieval.genai') as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model

            result = rewrite_query_for_retrieval("lets check the coldstart thing")

            assert not result.startswith(" ")
            assert not result.endswith(" ")
            assert not result.endswith("\n")


class TestQueryRewriterIntegration:
    """Integration tests for query rewriting in retrieval pipeline."""

    def test_search_memory_uses_rewritten_query(self, monkeypatch, tmp_path):
        """Test 4: search_memory() calls rewrite before retrieval."""
        # This test verifies the integration point
        # We'll check that rewrite is called when search_memory is invoked

        from memory_retrieval import search_memory

        rewrite_called = []

        def mock_rewrite(query):
            rewrite_called.append(query)
            return f"rewritten: {query}"

        # Set required env var
        monkeypatch.setenv('GOOGLE_API_KEY', 'test-key')

        # Create mock db file
        db_path = tmp_path / 'haios_memory.db'
        db_path.touch()

        # Mock at the source locations (where they're imported from)
        with patch('memory_retrieval.rewrite_query_for_retrieval', mock_rewrite):
            with patch('haios_etl.database.DatabaseManager') as mock_db:
                with patch('haios_etl.extraction.ExtractionManager') as mock_ext:
                    with patch('haios_etl.retrieval.ReasoningAwareRetrieval') as mock_retrieval:
                        mock_instance = MagicMock()
                        mock_instance.search_with_experience.return_value = {
                            'results': [],
                            'reasoning': {}
                        }
                        mock_retrieval.return_value = mock_instance

                        with patch('memory_retrieval.PROJECT_ROOT', tmp_path):
                            search_memory("conversational query here")

                        # Verify rewrite was called
                        assert len(rewrite_called) == 1
                        assert rewrite_called[0] == "conversational query here"

                        # Verify retrieval used rewritten query
                        call_args = mock_instance.search_with_experience.call_args
                        assert call_args is not None
                        # Check if 'query' is in kwargs or args
                        if call_args.kwargs and 'query' in call_args.kwargs:
                            assert "rewritten:" in call_args.kwargs['query']
                        elif call_args.args:
                            assert "rewritten:" in call_args.args[0]
