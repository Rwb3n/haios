import pytest
from unittest.mock import patch, MagicMock
from haios_etl.extraction import ExtractionManager, ExtractionResult, ExtractionError

@pytest.fixture
def mock_langextract():
    # Patch where it is imported in haios_etl.extraction
    with patch('haios_etl.extraction.lx.extract') as mock:
        yield mock

@pytest.fixture
def extraction_manager():
    return ExtractionManager(api_key="dummy_key")

def test_extract_from_file_success(extraction_manager, mock_langextract):
    """Verify successful extraction of entities and concepts."""
    # Mock response from langextract
    mock_response = MagicMock()
    mock_response.extractions = [
        MagicMock(extraction_class="entity", extraction_text="Ruben", attributes={"entity_type": "User"}),
        MagicMock(extraction_class="entity", extraction_text="Antigravity", attributes={"entity_type": "Agent"}),
        MagicMock(extraction_class="concept", extraction_text="Use SQLite", attributes={"concept_type": "Decision"}),
    ]
    mock_langextract.return_value = mock_response

    result = extraction_manager.extract_from_file("test/file.md", "File content")

    assert isinstance(result, ExtractionResult)
    assert len(result.entities) == 2
    assert result.entities[0].type == "User"
    assert result.entities[0].value == "Ruben"
    assert len(result.concepts) == 1
    assert result.concepts[0].type == "Decision"
    assert result.concepts[0].content == "Use SQLite"
    
    # Verify langextract was called correctly
    mock_langextract.assert_called_once()
    call_kwargs = mock_langextract.call_args[1]
    assert "prompt_description" in call_kwargs
    assert "examples" in call_kwargs
    assert call_kwargs["api_key"] == "dummy_key"

def test_extract_from_file_api_error(extraction_manager, mock_langextract):
    """Verify handling of API errors."""
    mock_langextract.side_effect = Exception("API Error")

    with pytest.raises(ExtractionError):
        extraction_manager.extract_from_file("test/file.md", "content")

def test_extract_from_file_empty(extraction_manager, mock_langextract):
    """Verify handling of empty results."""
    mock_response = MagicMock()
    mock_response.extractions = []
    mock_langextract.return_value = mock_response

    result = extraction_manager.extract_from_file("test/file.md", "content")

    assert len(result.entities) == 0
    assert len(result.concepts) == 0

def test_extract_with_retry_success(extraction_manager, mock_langextract):
    """Verify retry succeeds after transient error."""
    # First call fails with rate limit, second succeeds
    mock_response = MagicMock()
    mock_response.extractions = [
        MagicMock(extraction_class="entity", extraction_text="User", attributes={"entity_type": "User"}),
    ]
    
    mock_langextract.side_effect = [
        Exception("Rate limit exceeded (429)"),
        mock_response
    ]
    
    # Should succeed after 1 retry
    with patch('time.sleep'):  # Mock sleep to speed up test
        result = extraction_manager.extract_from_file("test/file.md", "content")
    
    assert isinstance(result, ExtractionResult)
    assert len(result.entities) == 1
    assert mock_langextract.call_count == 2

def test_extract_with_retry_permanent_error(extraction_manager, mock_langextract):
    """Verify permanent errors fail immediately without retry."""
    mock_langextract.side_effect = Exception("Invalid API key (401)")
    
    # Should NOT retry on permanent error
    with pytest.raises(ExtractionError):
        extraction_manager.extract_from_file("test/file.md", "content")
    
    assert mock_langextract.call_count == 1

def test_extract_with_retry_exhausted(extraction_manager, mock_langextract):
    """Verify failure after max retries exhausted."""
    mock_langextract.side_effect = Exception("Timeout")
    
    # Should retry 3 times then fail
    with patch('time.sleep'):
        with pytest.raises(ExtractionError):
            extraction_manager.extract_from_file("test/file.md", "content")
    
    assert mock_langextract.call_count == 3
