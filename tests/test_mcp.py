# generated: 2025-11-30
# System Auto: last updated on: 2025-12-14 13:16:34
# MCP Marketplace Tests (Session 17 - PLAN-AGENT-ECOSYSTEM-002)

import pytest
import json
from unittest.mock import patch, MagicMock

from haios_etl.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Returns a DatabaseManager instance using an in-memory database."""
    manager = DatabaseManager(":memory:")
    manager.setup()
    return manager


@pytest.fixture
def populated_db(db_manager):
    """Pre-populated database with test agents."""
    agents = [
        {
            'id': 'agent-interpreter-v1',
            'name': 'Interpreter',
            'version': '1.0.0',
            'description': 'The Front Desk of HAIOS',
            'type': 'subagent',
            'capabilities': ['vision-alignment', 'concept-translation'],
            'tools': ['memory_search'],
        },
        {
            'id': 'agent-ingester-v1',
            'name': 'Ingester',
            'version': '1.0.0',
            'description': 'The Mouth of HAIOS',
            'type': 'subagent',
            'capabilities': ['content-ingestion', 'chunking'],
            'tools': ['extract_content', 'memory_store'],
        },
    ]
    for agent in agents:
        db_manager.register_agent(agent)
    return db_manager


def test_marketplace_list_agents_format(populated_db):
    """Verify marketplace_list_agents returns correct markdown format."""
    from haios_etl import mcp_server

    # Patch the db_manager module-level variable
    with patch.object(mcp_server, 'db_manager', populated_db):
        # Call the actual MCP tool function
        result = mcp_server.marketplace_list_agents()

        # Verify format
        assert "## Available Agents" in result
        assert "**Interpreter**" in result
        assert "**Ingester**" in result
        assert "vision-alignment" in result
        assert "content-ingestion" in result


def test_marketplace_list_agents_filtering(populated_db):
    """Verify capability filtering works correctly."""
    # Filter by vision-alignment
    vision_agents = populated_db.list_agents(capability='vision-alignment')
    assert len(vision_agents) == 1
    assert vision_agents[0]['name'] == 'Interpreter'

    # Filter by content-ingestion
    ingester_agents = populated_db.list_agents(capability='content-ingestion')
    assert len(ingester_agents) == 1
    assert ingester_agents[0]['name'] == 'Ingester'

    # Filter by non-existent capability
    empty = populated_db.list_agents(capability='non-existent')
    assert len(empty) == 0


def test_marketplace_get_agent_json(populated_db):
    """Verify marketplace_get_agent returns valid JSON with full details."""
    agent = populated_db.get_agent('agent-interpreter-v1')

    assert agent is not None

    # Verify JSON serializable
    json_output = json.dumps(agent, indent=2)
    assert json_output is not None

    # Parse and verify structure
    parsed = json.loads(json_output)
    assert parsed['id'] == 'agent-interpreter-v1'
    assert parsed['name'] == 'Interpreter'
    assert parsed['version'] == '1.0.0'
    assert 'capabilities' in parsed
    assert 'tools' in parsed


def test_marketplace_get_agent_not_found(populated_db):
    """Verify correct handling of non-existent agent."""
    agent = populated_db.get_agent('non-existent-agent')
    assert agent is None


# =============================================================================
# MEMORY_STORE TOOL TESTS (Session 17 - PLAN-AGENT-ECOSYSTEM-002)
# =============================================================================

def test_memory_store_basic(db_manager):
    """Verify memory_store stores content and returns confirmation."""
    from haios_etl import mcp_server

    with patch.object(mcp_server, 'db_manager', db_manager):
        result = mcp_server.memory_store(
            content="HAIOS is a Trust Engine for AI agents",
            content_type="episteme",
            source_path="docs/vision.md"
        )

        # Verify success response
        assert "stored" in result.lower() or "success" in result.lower()

        # Verify concept was actually stored
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content, type FROM concepts WHERE content LIKE '%Trust Engine%'")
        row = cursor.fetchone()
        assert row is not None, "Content not found in database"
        assert row[1] == "episteme"


def test_memory_store_with_metadata(db_manager):
    """Verify memory_store handles metadata correctly."""
    from haios_etl import mcp_server

    with patch.object(mcp_server, 'db_manager', db_manager):
        result = mcp_server.memory_store(
            content="Use pytest for testing",
            content_type="techne",
            source_path="docs/testing.md",
            metadata='{"source": "testing_guide", "priority": "high"}'
        )

        assert "stored" in result.lower() or "success" in result.lower()


def test_memory_store_invalid_type(db_manager):
    """Verify memory_store rejects invalid content types."""
    from haios_etl import mcp_server

    with patch.object(mcp_server, 'db_manager', db_manager):
        result = mcp_server.memory_store(
            content="Some content",
            content_type="invalid_type",
            source_path="test.md"
        )

        # Should return error message
        assert "error" in result.lower() or "invalid" in result.lower()


def test_memory_store_deprecation_warning(db_manager):
    """Verify memory_store returns deprecation warning in response (E2-001 TDD)."""
    from haios_etl import mcp_server

    with patch.object(mcp_server, 'db_manager', db_manager):
        result = mcp_server.memory_store(
            content="Test content for deprecation check",
            content_type="techne",
            source_path="test.md"
        )

        # Should contain deprecation notice pointing to ingester_ingest
        assert "deprecated" in result.lower() or "ingester_ingest" in result.lower(), \
            f"Expected deprecation warning, got: {result}"


# =============================================================================
# EXTRACT_CONTENT TOOL TESTS (Session 17 - PLAN-AGENT-ECOSYSTEM-002)
# =============================================================================

def test_extract_content_basic():
    """Verify extract_content extracts entities and concepts."""
    from haios_etl import mcp_server
    from haios_etl.extraction import ExtractionResult, Entity, Concept

    # Mock extraction result
    mock_result = ExtractionResult(
        entities=[Entity(type="Agent", value="Claude")],
        concepts=[Concept(type="Decision", content="Use SQLite", source_adr="ADR-001")]
    )

    # Mock the extraction_manager
    mock_extraction_manager = MagicMock()
    mock_extraction_manager.extract_from_file.return_value = mock_result

    with patch.object(mcp_server, 'extraction_manager', mock_extraction_manager):
        result = mcp_server.extract_content(
            file_path="test/sample.md",
            content="Some test content about Claude and SQLite"
        )

        # Verify extraction was called
        mock_extraction_manager.extract_from_file.assert_called_once()

        # Verify response contains extracted data
        assert "entities" in result.lower() or "extracted" in result.lower()
        assert "Claude" in result or "Agent" in result


def test_extract_content_error_handling():
    """Verify extract_content handles extraction errors gracefully."""
    from haios_etl import mcp_server

    # Mock extraction to raise error
    mock_extraction_manager = MagicMock()
    mock_extraction_manager.extract_from_file.side_effect = Exception("API Error")

    with patch.object(mcp_server, 'extraction_manager', mock_extraction_manager):
        result = mcp_server.extract_content(
            file_path="test/error.md",
            content="Content that causes error"
        )

        # Should return error message, not raise exception
        assert "error" in result.lower()


# =============================================================================
# HYBRID RETRIEVAL MCP TESTS (Session 72 - ADR-037)
# =============================================================================

def test_memory_search_with_experience_accepts_mode():
    """Test 6: MCP tool accepts mode parameter without error."""
    from haios_etl import mcp_server

    # Mock the retrieval service to avoid actual embedding generation
    mock_retrieval = MagicMock()
    mock_retrieval.search_with_experience.return_value = {
        'results': [],
        'reasoning': {'strategy_used': 'test', 'learned_from': 0, 'outcome': 'success'}
    }

    with patch.object(mcp_server, 'retrieval_service', mock_retrieval):
        # This will fail until mode parameter is added to the function signature
        result = mcp_server.memory_search_with_experience(
            query="test query",
            mode="session_recovery"
        )

        # Should not contain error
        assert "error" not in result.lower(), f"Unexpected error: {result}"
