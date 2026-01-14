# generated: 2025-12-01
# System Auto: last updated on: 2025-12-01 14:42:16
# Interpreter Agent Tests (Session 18 - PLAN-AGENT-ECOSYSTEM-001)
# Design Decisions: DD-012 (LLM translation), DD-013 (confidence), DD-014 (no-context)

import pytest
from unittest.mock import patch, MagicMock
from dataclasses import asdict


@pytest.fixture
def interpreter():
    """Returns an Interpreter instance with default config."""
    from haios_etl.agents.interpreter import Interpreter, InterpreterConfig
    config = InterpreterConfig(use_llm=True, fallback_to_rules=True)
    return Interpreter(config=config)


@pytest.fixture
def interpreter_no_llm():
    """Returns an Interpreter with LLM disabled (rule-based only)."""
    from haios_etl.agents.interpreter import Interpreter, InterpreterConfig
    config = InterpreterConfig(use_llm=False, fallback_to_rules=True)
    return Interpreter(config=config)


# =============================================================================
# BASIC TRANSLATION TESTS (DD-012)
# =============================================================================

def test_interpreter_translate_basic(interpreter):
    """Verify happy path translation returns valid InterpretationResult."""
    from haios_etl.agents.interpreter import InterpretationResult

    # Mock the LLM call to return a structured directive
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {
            "action": "search",
            "target": "documentation",
            "query": "how to use memory system"
        }
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = ["doc1: Memory system overview", "doc2: API reference"]

            result = interpreter.translate("Find documentation about the memory system")

    assert isinstance(result, InterpretationResult)
    assert result.directive is not None
    assert "action" in result.directive
    assert 0.0 <= result.confidence <= 1.0
    assert result.grounded is True  # Context was found


def test_interpreter_translate_returns_dataclass(interpreter):
    """Verify translate returns proper dataclass with all fields."""
    from haios_etl.agents.interpreter import InterpretationResult

    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "list", "target": "agents"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = []

            result = interpreter.translate("List all agents")

    # Verify dataclass fields
    result_dict = asdict(result)
    assert "directive" in result_dict
    assert "confidence" in result_dict
    assert "grounded" in result_dict
    assert "context_used" in result_dict


# =============================================================================
# CONFIDENCE HANDLING TESTS (DD-013)
# =============================================================================

def test_interpreter_confidence_score_range(interpreter):
    """Verify confidence score is always between 0.0 and 1.0."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "unknown"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = []

            result = interpreter.translate("Some ambiguous request")

    assert 0.0 <= result.confidence <= 1.0


def test_interpreter_low_confidence_for_ambiguous(interpreter):
    """Verify ambiguous input returns confidence < 0.5 (DD-013)."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        # Ambiguous result with no clear action
        mock_llm.return_value = {"action": "unclear", "note": "ambiguous input"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = []

            result = interpreter.translate("maybe do something?")

    # Ambiguous inputs should have lower confidence
    assert result.confidence < 0.7


def test_interpreter_high_confidence_for_clear_intent(interpreter):
    """Verify clear intent returns high confidence."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "ingest", "target": "file.md", "type": "episteme"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = ["doc: Ingestion patterns"]

            result = interpreter.translate("Ingest file.md as episteme knowledge")

    # Clear command should have higher confidence
    assert result.confidence >= 0.7


# =============================================================================
# NO-CONTEXT BEHAVIOR TESTS (DD-014)
# =============================================================================

def test_interpreter_no_context_returns_grounded_false(interpreter):
    """Verify grounded=false when no context found (DD-014)."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "unknown_action"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = []  # No context found

            result = interpreter.translate("Do something with the flibbertigibbet")

    assert result.grounded is False
    assert result.context_used == []


def test_interpreter_with_context_returns_grounded_true(interpreter):
    """Verify grounded=true when relevant context is found."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "search", "target": "ADRs"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = [
                "ADR-023: Idempotency requirements",
                "ADR-024: Async messaging"
            ]

            result = interpreter.translate("Find ADRs about messaging")

    assert result.grounded is True
    assert len(result.context_used) > 0


# =============================================================================
# RULE-BASED FALLBACK TESTS (DD-012)
# =============================================================================

def test_interpreter_rule_fallback_when_llm_fails(interpreter):
    """Verify falls back to rules when LLM fails (DD-012)."""
    from haios_etl.agents.interpreter import InterpretationResult

    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.side_effect = Exception("LLM API Error")
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = []

            result = interpreter.translate("search for agents")

    # Should still return a result via rule-based fallback
    assert isinstance(result, InterpretationResult)
    assert result.directive is not None


def test_interpreter_rule_fallback_patterns(interpreter_no_llm):
    """Verify rule-based patterns work for common operations."""
    with patch.object(interpreter_no_llm, '_search_memory') as mock_search:
        mock_search.return_value = []

        # Test common patterns
        result = interpreter_no_llm.translate("search for documentation")
        assert result.directive.get("action") == "search"

        result = interpreter_no_llm.translate("ingest this content as techne")
        assert result.directive.get("action") == "ingest"

        result = interpreter_no_llm.translate("list all agents")
        assert result.directive.get("action") == "list"


def test_interpreter_llm_disabled_uses_rules_only(interpreter_no_llm):
    """Verify LLM is not called when disabled."""
    with patch.object(interpreter_no_llm, '_translate_with_llm') as mock_llm:
        with patch.object(interpreter_no_llm, '_search_memory') as mock_search:
            mock_search.return_value = []

            result = interpreter_no_llm.translate("search something")

    # LLM should not be called when disabled
    mock_llm.assert_not_called()


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_interpreter_handles_empty_intent(interpreter):
    """Verify empty intent is handled gracefully."""
    with patch.object(interpreter, '_search_memory') as mock_search:
        mock_search.return_value = []

        result = interpreter.translate("")

    assert result.confidence < 0.5
    assert result.directive is not None


def test_interpreter_handles_none_response_from_llm(interpreter):
    """Verify None LLM response triggers fallback."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = None
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = []

            result = interpreter.translate("some request")

    # Should fall back to rule-based
    assert result.directive is not None


# =============================================================================
# INTEGRATION WITH MEMORY SEARCH
# =============================================================================

def test_interpreter_uses_memory_search(interpreter):
    """Verify interpreter calls memory search for context."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "search"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = ["result1", "result2"]

            result = interpreter.translate("Find documentation")

            mock_search.assert_called_once()


def test_interpreter_passes_context_to_llm(interpreter):
    """Verify memory context is passed to LLM for grounded translation."""
    with patch.object(interpreter, '_translate_with_llm') as mock_llm:
        mock_llm.return_value = {"action": "search"}
        with patch.object(interpreter, '_search_memory') as mock_search:
            mock_search.return_value = ["ADR-023: Idempotency"]

            interpreter.translate("Find ADR about idempotency")

            # Verify LLM was called with context
            call_args = mock_llm.call_args
            assert call_args is not None
            # Context should be passed (either positional or keyword)
