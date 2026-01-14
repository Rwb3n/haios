import pytest
from unittest.mock import MagicMock, patch, call
# Import to-be-implemented classes
from haios_etl.processing import BatchProcessor
from haios_etl.extraction import ExtractionResult, Entity, Concept, ExtractionError

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_extractor():
    return MagicMock()

@pytest.fixture
def processor(mock_db, mock_extractor):
    return BatchProcessor(mock_db, mock_extractor)

def test_process_file_success(processor, mock_db, mock_extractor):
    """Verify successful processing of a new file."""
    # Setup
    file_path = "test/doc.md"
    content = "Hello World"
    file_hash = "hash123"
    
    # Mocks
    mock_db.get_processing_status.return_value = None # Not processed yet
    mock_extractor.extract_from_file.return_value = ExtractionResult(
        entities=[Entity("User", "Ruben")],
        concepts=[Concept("Directive", "Do X")]
    )
    mock_db.insert_artifact.return_value = 1
    mock_db.insert_entity.return_value = 10
    mock_db.insert_concept.return_value = 20

    # Action
    # We mock reading file content to avoid disk I/O
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = content
        # We also mock os.path.getsize and hashing if implemented in processor
        # For now assuming processor takes path and handles reading
        
        # Wait, processor needs to calculate hash. 
        # Let's assume processor.process_file(path) does everything.
        # We need to patch the hashing function or file reading inside it.
        # Let's assume we pass content for unit testing `process_content`?
        # No, `process_file` is the API.
        # Let's patch `haios_etl.processing.calculate_file_hash` if we had it.
        # Or just patch `open` as done above.
        
        # Also need to patch os.path.getsize for artifact insertion
        with patch("os.path.getsize", return_value=100):
             # And patch hashlib or whatever is used for hashing
             with patch("haios_etl.processing.compute_file_hash", return_value=file_hash):
                processor.process_file(file_path)

    # Assertions
    mock_db.get_processing_status.assert_called_with(file_path)
    mock_extractor.extract_from_file.assert_called_with(file_path, content)
    
    # DB calls
    mock_db.insert_artifact.assert_called_with(file_path, file_hash, 100)
    mock_db.insert_entity.assert_called()
    mock_db.insert_concept.assert_called()
    mock_db.record_entity_occurrence.assert_called()
    mock_db.record_concept_occurrence.assert_called()
    
    # Quality metrics
    mock_db.insert_quality_metrics.assert_called()
    
    # Status update
    mock_db.update_processing_status.assert_called_with(file_path, "success")

def test_process_file_skip(processor, mock_db, mock_extractor):
    """Verify skipping of already processed file with same hash."""
    file_path = "test/doc.md"
    file_hash = "hash123"
    
    # Setup: DB says success
    mock_db.get_processing_status.return_value = "success"
    # And DB says hash matches
    mock_db.get_artifact_hash.return_value = file_hash
    
    with patch("haios_etl.processing.compute_file_hash", return_value=file_hash):
        processor.process_file(file_path)
        
    # Assertions
    mock_extractor.extract_from_file.assert_not_called()
    # Status might be updated to 'skipped' or just left alone?
    # Let's say we log 'skipped'
    mock_db.update_processing_status.assert_called_with(file_path, "skipped")

def test_process_file_skip_when_already_skipped(processor, mock_db, mock_extractor):
    """Verify skipping of file that was already marked as skipped in previous run."""
    file_path = "test/doc.md"
    file_hash = "hash123"
    
    # Setup: DB says skipped (from previous run)
    mock_db.get_processing_status.return_value = "skipped"
    # And DB says hash matches
    mock_db.get_artifact_hash.return_value = file_hash
    
    with patch("haios_etl.processing.compute_file_hash", return_value=file_hash):
        processor.process_file(file_path)
        
    # Assertions
    # Should NOT extract
    mock_extractor.extract_from_file.assert_not_called()
    # Should update status to skipped (or keep it)
    mock_db.update_processing_status.assert_called_with(file_path, "skipped")

def test_process_file_extraction_error(processor, mock_db, mock_extractor):
    """Verify handling of extraction errors."""
    file_path = "test/doc.md"
    
    mock_db.get_processing_status.return_value = None
    mock_extractor.extract_from_file.side_effect = ExtractionError("API Error")
    
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "content"
        with patch("os.path.getsize", return_value=100):
             with patch("haios_etl.processing.compute_file_hash", return_value="hash"):
                processor.process_file(file_path)
    
    # Assertions
    mock_db.update_processing_status.assert_called_with(file_path, "error", "API Error")
    # Should NOT insert entities
    mock_db.insert_entity.assert_not_called()

# Tests for read_file_safely function
def test_read_file_safely_utf8(tmp_path):
    """Test reading a UTF-8 encoded file."""
    from haios_etl.processing import read_file_safely
    
    # Create test file
    test_file = tmp_path / "utf8.txt"
    test_file.write_text("Hello World", encoding="utf-8")
    
    content = read_file_safely(str(test_file))
    assert content == "Hello World"

def test_read_file_safely_latin1_fallback(tmp_path):
    """Test fallback to latin-1 encoding."""
    from haios_etl.processing import read_file_safely
    
    # Create file with latin-1 encoding
    test_file = tmp_path / "latin1.txt"
    test_file.write_bytes("Café résumé".encode("latin-1"))
    
    content = read_file_safely(str(test_file))
    assert content is not None
    assert "Caf" in content

def test_read_file_safely_binary_file(tmp_path):
    """Test that binary files return None."""
    from haios_etl.processing import read_file_safely
    
    # Create binary file
    test_file = tmp_path / "image.jpg"
    test_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")
    
    content = read_file_safely(str(test_file))
    assert content is None

def test_read_file_safely_permission_error():
    """Test handling of permission errors."""
    from haios_etl.processing import read_file_safely
    
    with patch("builtins.open", side_effect=PermissionError("Access denied")):
        content = read_file_safely("restricted.txt")
        assert content is None

def test_read_file_safely_null_bytes(tmp_path):
    """Test detection of null bytes (binary content)."""
    from haios_etl.processing import read_file_safely
    
    test_file = tmp_path / "binary.dat"
    test_file.write_bytes(b"Text\x00with\x00nulls")
    
    content = read_file_safely(str(test_file))
    assert content is None

def test_read_file_safely_empty_file(tmp_path):
    """Test that empty files return None."""
    from haios_etl.processing import read_file_safely
    
    # Create empty file
    test_file = tmp_path / "empty.txt"
    test_file.write_text("")
    
    content = read_file_safely(str(test_file))
    assert content is None

    # Create whitespace only file
    test_file_ws = tmp_path / "whitespace.txt"
    test_file_ws.write_text("   \n  ")
    
    content = read_file_safely(str(test_file_ws))
    assert content is None

