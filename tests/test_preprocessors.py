"""
Unit tests for the preprocessor architecture.
"""

import pytest
from haios_etl.preprocessors import Preprocessor, GeminiDumpPreprocessor, get_preprocessors


def test_gemini_dump_preprocessor_detection():
    """Test that GeminiDumpPreprocessor correctly identifies Gemini session dumps."""
    preprocessor = GeminiDumpPreprocessor()
    
    # Should detect dumps with runSettings
    gemini_content = '{"runSettings": {}, "text": "Hello"}'
    assert preprocessor.can_handle(gemini_content) is True
    
    # Should detect dumps with chunkedPrompt
    gemini_content2 = '{"chunkedPrompt": [], "content": "World"}'
    assert preprocessor.can_handle(gemini_content2) is True
    
    # Should not detect regular markdown
    markdown_content = "# Regular Markdown\nSome text here"
    assert preprocessor.can_handle(markdown_content) is False


def test_gemini_dump_preprocessor_extraction():
    """Test that GeminiDumpPreprocessor correctly extracts text fields."""
    preprocessor = GeminiDumpPreprocessor()
    
    # Simple case
    content = '{"runSettings": {}, "text": "Hello World"}'
    result = preprocessor.preprocess(content)
    assert "Hello World" in result
    
    # Multiple fields
    content2 = '{"runSettings": {}, "text": "First", "content": "Second"}'
    result2 = preprocessor.preprocess(content2)
    assert "First" in result2
    assert "Second" in result2


def test_gemini_dump_preprocessor_literal_newlines():
    """Test that preprocessor handles literal newlines (the bug we fixed)."""
    preprocessor = GeminiDumpPreprocessor()
    
    # Content with literal newline (not \n)
    content_with_newline = '{"runSettings": {}, "text": "Line 1\nLine 2"}'
    result = preprocessor.preprocess(content_with_newline)
    
    # Should extract both lines
    assert "Line 1" in result
    assert "Line 2" in result


def test_preprocessor_registry():
    """Test that get_preprocessors returns the expected preprocessors."""
    preprocessors = get_preprocessors()
    
    assert len(preprocessors) > 0
    assert any(isinstance(p, GeminiDumpPreprocessor) for p in preprocessors)


def test_preprocessor_base_interface():
    """Test that the Preprocessor base class defines the expected interface."""
    assert hasattr(Preprocessor, 'can_handle')
    assert hasattr(Preprocessor, 'preprocess')
