# generated: 2025-12-21
# System Auto: last updated on: 2026-01-27T20:57:16
"""
Phase 1b Tests: Retrieval Layer from .claude/haios/lib/

Tests verify retrieval module works from new location.
"""
import sys
from pathlib import Path

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestRetrievalImport:
    """Tests for retrieval module importability."""

    def test_can_import_retrieval_service(self):
        """RetrievalService must be importable from .claude/haios/lib/."""
        from retrieval import RetrievalService
        assert RetrievalService is not None

    def test_can_import_reasoning_aware_retrieval(self):
        """ReasoningAwareRetrieval must be importable."""
        from retrieval import ReasoningAwareRetrieval
        assert ReasoningAwareRetrieval is not None

    def test_retrieval_service_has_required_methods(self):
        """RetrievalService must have core methods."""
        from retrieval import RetrievalService

        required_methods = [
            'search',
            '_generate_embedding',
        ]

        for method in required_methods:
            assert hasattr(RetrievalService, method), f"Missing method: {method}"

    def test_reasoning_aware_has_experience_method(self):
        """ReasoningAwareRetrieval must have search_with_experience."""
        from retrieval import ReasoningAwareRetrieval
        assert hasattr(ReasoningAwareRetrieval, 'search_with_experience')
        assert hasattr(ReasoningAwareRetrieval, 'find_similar_reasoning_traces')
        assert hasattr(ReasoningAwareRetrieval, 'record_reasoning_trace')
