# generated: 2025-12-14
# System Auto: last updated on: 2025-12-14 13:24:40
import pytest
import json
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from haios_etl.mcp_server import memory_search_with_experience, memory_stats
from haios_etl.database import DatabaseManager

@pytest.fixture
def mock_db_env(monkeypatch):
    # Use a test database
    test_db = "test_integration.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Initialize DB
    db = DatabaseManager(test_db)
    db.setup()
    
    # Mock DB_PATH and db_manager in mcp_server
    monkeypatch.setenv("DB_PATH", test_db)
    # We need to re-initialize db_manager in mcp_server or mock it
    # Since mcp_server initializes db_manager at module level, we might need to patch it
    from haios_etl import mcp_server
    mcp_server.db_manager = db
    mcp_server.DB_PATH = test_db
    
    yield db
    
    # Cleanup
    if db.conn:
        db.conn.close()
        
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            print(f"Warning: Could not remove {test_db}")

def test_memory_stats(mock_db_env):
    """Test memory_stats endpoint."""
    result = memory_stats()
    data = json.loads(result)
    
    assert data['status'] == 'online'
    assert 'artifacts' in data
    assert data['artifacts'] == 0
    assert data['db_path'] == "test_integration.db"

def test_memory_search_with_experience(mock_db_env, monkeypatch):
    """Test search endpoint with mocked embedding."""

    # Mock ExtractionManager.embed_content to avoid API call
    def mock_embed(self, text):
        return [0.1] * 768

    from haios_etl.extraction import ExtractionManager
    monkeypatch.setattr(ExtractionManager, "embed_content", mock_embed)

    # Mock TOON_AVAILABLE to False to get JSON output for testing
    from haios_etl import mcp_server
    monkeypatch.setattr(mcp_server, "TOON_AVAILABLE", False)

    # Perform search
    result_json = memory_search_with_experience("test query")
    result = json.loads(result_json)
    
    assert 'results' in result
    assert 'reasoning' in result
    # With sqlite-vec installed, outcome should be 'success' (empty results but query succeeded)
    # Without sqlite-vec, outcome is 'failure' (graceful fallback)
    assert result['reasoning']['outcome'] in ('success', 'failure')
    assert result['reasoning']['strategy_used'] == 'default_hybrid'
