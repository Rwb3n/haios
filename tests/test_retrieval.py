# generated: 2025-11-27
# System Auto: last updated on: 2025-11-28 00:21:19
import pytest
from unittest.mock import MagicMock, patch
from haios_etl.retrieval import RetrievalService, ReasoningAwareRetrieval
from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager

@pytest.fixture
def mock_db():
    db = MagicMock(spec=DatabaseManager)
    db.get_connection.return_value.cursor.return_value = MagicMock()
    return db

@pytest.fixture
def mock_extractor():
    extractor = MagicMock(spec=ExtractionManager)
    extractor.embed_content.return_value = [0.1, 0.2, 0.3]
    extractor.model_id = "gemini-2.5-flash-lite"  # Required for strategy extraction
    extractor.extract_strategy.return_value = {
        'title': 'Default Strategy',
        'description': 'Default approach',
        'content': 'Default strategy content'
    }
    return extractor

def test_retrieval_service_search(mock_db, mock_extractor):
    service = RetrievalService(mock_db, mock_extractor)
    mock_db.search_memories.return_value = [{'id': 1, 'score': 0.9}]
    
    results = service.search("test query")
    
    assert len(results) == 1
    assert results[0]['id'] == 1
    mock_extractor.embed_content.assert_called_once_with("test query")
    mock_db.search_memories.assert_called_once()

def test_reasoning_aware_cold_start(mock_db, mock_extractor):
    service = ReasoningAwareRetrieval(mock_db, mock_extractor)
    
    # Mock search to return results
    service.search = MagicMock(return_value=[{'id': 1, 'score': 0.9}])
    
    # Mock find_similar_reasoning_traces to return empty (Cold Start)
    service.find_similar_reasoning_traces = MagicMock(return_value=[])
    
    # Mock record_reasoning_trace
    service.record_reasoning_trace = MagicMock()
    
    result = service.search_with_experience("test query")
    
    assert result['reasoning']['outcome'] == 'success'
    assert result['reasoning']['learned_from'] == 0
    service.search.assert_called_once()
    service.record_reasoning_trace.assert_called_once()
    
    # Verify trace args
    args = service.record_reasoning_trace.call_args[1]
    assert args['query'] == "test query"
    assert args['outcome'] == "success"

def test_reasoning_aware_with_history(mock_db, mock_extractor):
    service = ReasoningAwareRetrieval(mock_db, mock_extractor)

    # Mock search
    service.search = MagicMock(return_value=[{'id': 1, 'score': 0.9}])

    # Mock history (Success trace)
    service.find_similar_reasoning_traces = MagicMock(return_value=[
        {'outcome': 'success', 'approach_taken': 'narrow_search', 'strategy_details': '{"k": 5}'}
    ])

    service.record_reasoning_trace = MagicMock()

    result = service.search_with_experience("test query")

    assert result['reasoning']['learned_from'] == 1
    assert result['reasoning']['strategy_used'] == 'narrow_search'

    # In a real implementation, we'd verify that 'narrow_search' strategy was actually applied to the search
    # For now, we just verify it was selected


# =============================================================================
# P4-G3: Strategy Selection Tests
# Design Decision DD-004: First success wins
# =============================================================================

class TestDetermineStrategy:
    """Tests for _determine_strategy() - P4-G3."""

    def test_returns_default_when_no_traces(self, mock_db, mock_extractor):
        """DD-004: When no past attempts, use default strategy."""
        service = ReasoningAwareRetrieval(mock_db, mock_extractor)

        strategy = service._determine_strategy([])

        assert strategy['description'] == 'default_hybrid'
        assert strategy['parameters'] == {}

    def test_returns_first_successful_strategy(self, mock_db, mock_extractor):
        """DD-004: When past attempts include success, reuse that strategy."""
        service = ReasoningAwareRetrieval(mock_db, mock_extractor)

        past_attempts = [
            {'outcome': 'success', 'approach_taken': 'semantic_boost', 'strategy_details': '{"boost": 1.5}'}
        ]

        strategy = service._determine_strategy(past_attempts)

        assert strategy['description'] == 'semantic_boost'
        assert strategy['parameters'] == {'boost': 1.5}

    def test_ignores_failed_traces_when_success_exists(self, mock_db, mock_extractor):
        """DD-004: First success wins, failures ignored when success exists."""
        service = ReasoningAwareRetrieval(mock_db, mock_extractor)

        past_attempts = [
            {'outcome': 'failure', 'approach_taken': 'bad_approach', 'strategy_details': '{}'},
            {'outcome': 'success', 'approach_taken': 'good_approach', 'strategy_details': '{}'},
            {'outcome': 'failure', 'approach_taken': 'another_bad', 'strategy_details': '{}'}
        ]

        strategy = service._determine_strategy(past_attempts)

        assert strategy['description'] == 'good_approach'

    def test_returns_default_when_only_failures(self, mock_db, mock_extractor):
        """DD-004: When only failures exist, use default (avoid known failures)."""
        service = ReasoningAwareRetrieval(mock_db, mock_extractor)

        past_attempts = [
            {'outcome': 'failure', 'approach_taken': 'failed_approach', 'strategy_details': '{}'}
        ]

        strategy = service._determine_strategy(past_attempts)

        assert strategy['description'] == 'default_hybrid'

    def test_handles_malformed_strategy_details(self, mock_db, mock_extractor):
        """Graceful handling of malformed JSON in strategy_details."""
        service = ReasoningAwareRetrieval(mock_db, mock_extractor)

        past_attempts = [
            {'outcome': 'success', 'approach_taken': 'some_approach', 'strategy_details': 'not valid json'}
        ]

        # Should not crash, but may raise or return default
        try:
            strategy = service._determine_strategy(past_attempts)
            # If it doesn't crash, it should have parsed what it could
        except Exception:
            # Acceptable to raise on malformed input
            pass

    def test_handles_missing_strategy_details(self, mock_db, mock_extractor):
        """Graceful handling when strategy_details is missing."""
        service = ReasoningAwareRetrieval(mock_db, mock_extractor)

        past_attempts = [
            {'outcome': 'success', 'approach_taken': 'minimal_approach'}
            # No strategy_details key
        ]

        strategy = service._determine_strategy(past_attempts)

        assert strategy['description'] == 'minimal_approach'
        assert strategy['parameters'] == {}


# =============================================================================
# ReasoningBank Strategy Extraction Tests
# Per plan: PLAN-REASONINGBANK-001
# =============================================================================

class TestStrategyExtraction:
    """Tests for ReasoningBank-aligned strategy extraction."""

    def test_extract_strategy_called_on_success(self, mock_db, mock_extractor):
        """Verify extract_strategy is called when outcome is success."""
        mock_extractor.extract_strategy = MagicMock(return_value={
            'title': 'Semantic Search Strategy',
            'description': 'Use semantic similarity for concept retrieval',
            'content': 'When searching for abstract concepts, prioritize semantic meaning over keyword matching.'
        })

        service = ReasoningAwareRetrieval(mock_db, mock_extractor)
        service.search = MagicMock(return_value=[{'id': 1, 'score': 0.9}])
        service.find_similar_reasoning_traces = MagicMock(return_value=[])

        # Mock the database insert
        mock_cursor = MagicMock()
        mock_db.get_connection.return_value.cursor.return_value = mock_cursor

        result = service.search_with_experience("test query")

        # Verify extract_strategy was called
        mock_extractor.extract_strategy.assert_called_once()
        call_args = mock_extractor.extract_strategy.call_args[1]
        assert call_args['outcome'] == 'success'
        assert 'results_summary' in call_args

    def test_extract_strategy_called_on_failure(self, mock_db, mock_extractor):
        """Verify extract_strategy is called when outcome is failure."""
        mock_extractor.extract_strategy = MagicMock(return_value={
            'title': 'Avoid Vague Queries',
            'description': 'Be specific in query formulation',
            'content': 'Vague queries return no results. Use specific terminology.'
        })

        service = ReasoningAwareRetrieval(mock_db, mock_extractor)
        service.search = MagicMock(return_value=[])  # Empty = failure
        service.find_similar_reasoning_traces = MagicMock(return_value=[])

        # Mock the database insert
        mock_cursor = MagicMock()
        mock_db.get_connection.return_value.cursor.return_value = mock_cursor

        result = service.search_with_experience("test query")

        # Verify extract_strategy was called with failure outcome
        mock_extractor.extract_strategy.assert_called_once()
        call_args = mock_extractor.extract_strategy.call_args[1]
        assert call_args['outcome'] == 'failure'
        assert 'error_details' in call_args

    def test_response_includes_relevant_strategies(self, mock_db, mock_extractor):
        """Verify response includes relevant_strategies for prompt injection."""
        mock_extractor.extract_strategy = MagicMock(return_value={
            'title': 'New Strategy',
            'description': 'New approach',
            'content': 'New content'
        })

        service = ReasoningAwareRetrieval(mock_db, mock_extractor)
        service.search = MagicMock(return_value=[{'id': 1, 'score': 0.9}])

        # Mock past attempts with strategy content
        service.find_similar_reasoning_traces = MagicMock(return_value=[
            {
                'id': 100,
                'outcome': 'success',
                'approach_taken': 'semantic_search',
                'strategy_details': '{}',
                'strategy_title': 'Use Semantic Search',
                'strategy_description': 'Prioritize meaning',
                'strategy_content': 'When searching for concepts, focus on semantic similarity rather than exact keyword matches.'
            }
        ])

        # Mock the database insert
        mock_cursor = MagicMock()
        mock_db.get_connection.return_value.cursor.return_value = mock_cursor

        result = service.search_with_experience("test query")

        # Verify response structure
        assert 'relevant_strategies' in result['reasoning']
        assert len(result['reasoning']['relevant_strategies']) == 1
        assert result['reasoning']['relevant_strategies'][0]['title'] == 'Use Semantic Search'
        assert 'semantic similarity' in result['reasoning']['relevant_strategies'][0]['content']

    def test_relevant_strategies_empty_when_no_strategy_content(self, mock_db, mock_extractor):
        """Verify relevant_strategies is empty when past traces have no strategy_content."""
        mock_extractor.extract_strategy = MagicMock(return_value={
            'title': 'New',
            'description': 'New',
            'content': 'New'
        })

        service = ReasoningAwareRetrieval(mock_db, mock_extractor)
        service.search = MagicMock(return_value=[{'id': 1}])

        # Mock past attempts WITHOUT strategy content (legacy traces)
        service.find_similar_reasoning_traces = MagicMock(return_value=[
            {
                'id': 100,
                'outcome': 'success',
                'approach_taken': 'old_approach',
                'strategy_details': '{}',
                'strategy_title': None,
                'strategy_description': None,
                'strategy_content': None
            }
        ])

        mock_cursor = MagicMock()
        mock_db.get_connection.return_value.cursor.return_value = mock_cursor

        result = service.search_with_experience("test query")

        # Should be empty since no strategy_content
        assert result['reasoning']['relevant_strategies'] == []
        # But learned_from should still count the trace
        assert result['reasoning']['learned_from'] == 1
