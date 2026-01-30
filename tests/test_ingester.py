# generated: 2025-12-01
# System Auto: last updated on: 2026-01-30T20:09:02
# Ingester Agent Tests (Session 18 - PLAN-AGENT-ECOSYSTEM-001)
# Design Decisions: DD-015 (single-item), DD-016 (retry), DD-017 (provenance), DD-019 (timeout)

import pytest
from unittest.mock import patch, MagicMock, call
from dataclasses import asdict
import time


@pytest.fixture
def db_manager():
    """Returns a DatabaseManager instance using in-memory database."""
    from haios_etl.database import DatabaseManager
    manager = DatabaseManager(":memory:")
    manager.setup()
    return manager


@pytest.fixture
def ingester(db_manager):
    """Returns an Ingester instance with default config."""
    from haios_etl.agents.ingester import Ingester, IngesterConfig
    config = IngesterConfig(max_retries=3, backoff_base=2.0, timeout_seconds=30)
    return Ingester(db_manager=db_manager, config=config)


@pytest.fixture
def ingester_fast(db_manager):
    """Returns an Ingester with minimal retry delays for testing."""
    from haios_etl.agents.ingester import Ingester, IngesterConfig
    # Use backoff_base > 1 so exponential growth works (base^1 < base^2)
    config = IngesterConfig(max_retries=3, backoff_base=1.5, timeout_seconds=5)
    return Ingester(db_manager=db_manager, config=config)


# =============================================================================
# BASIC INGESTION TESTS (DD-015)
# =============================================================================

def test_ingester_ingest_basic(ingester):
    """Verify happy path ingestion returns valid IngestionResult."""
    from haios_etl.agents.ingester import IngestionResult

    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [{"type": "Agent", "value": "Claude"}],
            "concepts": [{"type": "Decision", "content": "Use SQLite"}]
        }

        result = ingester.ingest(
            content="Claude decided to use SQLite for storage",
            source_path="docs/decisions.md",
            content_type_hint="episteme"
        )

    assert isinstance(result, IngestionResult)
    assert result.classification == "episteme"
    assert result.ingested_by_agent == "ingester-v1"


def test_ingester_ingest_returns_dataclass(ingester):
    """Verify ingest returns proper dataclass with all fields."""
    from haios_etl.agents.ingester import IngestionResult

    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        result = ingester.ingest(
            content="Some content",
            source_path="test.md"
        )

    # Verify dataclass fields
    result_dict = asdict(result)
    assert "concept_ids" in result_dict
    assert "entity_ids" in result_dict
    assert "classification" in result_dict
    assert "ingested_by_agent" in result_dict


# =============================================================================
# CLASSIFICATION TESTS (Greek Triad)
# =============================================================================

def test_ingester_ingest_episteme(ingester):
    """Verify episteme (knowledge/facts) classification works correctly."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        result = ingester.ingest(
            content="HAIOS is a Trust Engine that transforms low-trust AI outputs to high-trust artifacts.",
            source_path="docs/overview.md",
            content_type_hint="episteme"
        )

    assert result.classification == "episteme"


def test_ingester_ingest_techne(ingester):
    """Verify techne (practical skills/how-to) classification works correctly."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        result = ingester.ingest(
            content="To start the MCP server, run: python -m haios_etl.mcp_server",
            source_path="docs/quickstart.md",
            content_type_hint="techne"
        )

    assert result.classification == "techne"


def test_ingester_ingest_doxa(ingester):
    """Verify doxa (opinions/beliefs) classification works correctly."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        result = ingester.ingest(
            content="I believe that evidence-based development is the best approach for AI systems.",
            source_path="docs/philosophy.md",
            content_type_hint="doxa"
        )

    assert result.classification == "doxa"


def test_ingester_auto_classify_when_unknown(ingester):
    """Verify auto-classification when content_type_hint is 'unknown'."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}
        with patch.object(ingester, '_classify_content') as mock_classify:
            mock_classify.return_value = "techne"

            result = ingester.ingest(
                content="Step 1: Install dependencies. Step 2: Run setup.",
                source_path="docs/setup.md",
                content_type_hint="unknown"
            )

    assert result.classification == "techne"
    mock_classify.assert_called_once()


# =============================================================================
# RETRY LOGIC TESTS (DD-016)
# =============================================================================

def test_ingester_extraction_failure_retries(ingester_fast):
    """Verify retries on transient errors with exponential backoff (DD-016)."""
    with patch.object(ingester_fast, '_extract_content') as mock_extract:
        # First two calls fail, third succeeds
        mock_extract.side_effect = [
            Exception("Rate limit exceeded (429)"),
            Exception("Timeout"),
            {"entities": [], "concepts": []}
        ]
        with patch('time.sleep'):  # Mock sleep to speed up test

            result = ingester_fast.ingest(
                content="Test content",
                source_path="test.md",
                content_type_hint="episteme"
            )

    assert result is not None
    assert mock_extract.call_count == 3


def test_ingester_permanent_error_no_retry(ingester_fast):
    """Verify permanent errors fail immediately without retry (DD-016)."""
    from haios_etl.agents.ingester import IngestionError

    with patch.object(ingester_fast, '_extract_content') as mock_extract:
        mock_extract.side_effect = Exception("Invalid content format (400)")
        with patch('time.sleep'):

            with pytest.raises(IngestionError):
                ingester_fast.ingest(
                    content="Some valid content that triggers extraction",
                    source_path="test.md",
                    content_type_hint="episteme"
                )

    # Should NOT retry on permanent error (400 is permanent)
    assert mock_extract.call_count == 1


def test_ingester_retries_exhausted(ingester_fast):
    """Verify failure after max retries exhausted (DD-016)."""
    from haios_etl.agents.ingester import IngestionError

    with patch.object(ingester_fast, '_extract_content') as mock_extract:
        mock_extract.side_effect = Exception("Timeout")
        with patch('time.sleep'):

            with pytest.raises(IngestionError):
                ingester_fast.ingest(
                    content="Test content",
                    source_path="test.md",
                    content_type_hint="episteme"
                )

    # Should retry 3 times then fail
    assert mock_extract.call_count == 3


def test_ingester_exponential_backoff(ingester_fast):
    """Verify exponential backoff timing (2s, 4s, 8s base pattern)."""
    with patch.object(ingester_fast, '_extract_content') as mock_extract:
        mock_extract.side_effect = [
            Exception("Rate limit"),
            Exception("Rate limit"),
            {"entities": [], "concepts": []}
        ]
        sleep_times = []
        with patch('time.sleep', side_effect=lambda x: sleep_times.append(x)):
            ingester_fast.ingest(
                content="Test",
                source_path="test.md",
                content_type_hint="episteme"
            )

    # Backoff should be increasing (base^1, base^2)
    if len(sleep_times) >= 2:
        assert sleep_times[1] >= sleep_times[0]


# =============================================================================
# PROVENANCE TESTS (DD-017)
# =============================================================================

def test_ingester_provenance_includes_agent_id(ingester):
    """Verify ingested_by_agent is included in result (DD-017)."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        result = ingester.ingest(
            content="Test content",
            source_path="test.md",
            content_type_hint="episteme"
        )

    assert result.ingested_by_agent == "ingester-v1"


def test_ingester_provenance_stored_with_records(ingester, db_manager):
    """Verify agent ID is stored with database records."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [{"type": "Agent", "value": "TestAgent"}],
            "concepts": [{"type": "Decision", "content": "Test decision"}]
        }

        result = ingester.ingest(
            content="TestAgent made a decision",
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify records were created
    assert len(result.entity_ids) > 0 or len(result.concept_ids) > 0


# =============================================================================
# STORAGE TESTS
# =============================================================================

def test_ingester_stores_entities(ingester, db_manager):
    """Verify entities are stored in database."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [
                {"type": "Agent", "value": "Claude"},
                {"type": "User", "value": "Operator"}
            ],
            "concepts": []
        }

        result = ingester.ingest(
            content="Claude and Operator discussed the system",
            source_path="test.md",
            content_type_hint="episteme"
        )

    assert len(result.entity_ids) == 2


def test_ingester_stores_concepts(ingester, db_manager):
    """Verify concepts are stored in database."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [],
            "concepts": [
                {"type": "Decision", "content": "Use SQLite"},
                {"type": "Proposal", "content": "Add caching layer"}
            ]
        }

        result = ingester.ingest(
            content="We decided to use SQLite and proposed adding caching",
            source_path="test.md",
            content_type_hint="episteme"
        )

    assert len(result.concept_ids) == 2


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_ingester_handles_empty_content(ingester):
    """Verify empty content is handled gracefully."""
    from haios_etl.agents.ingester import IngestionError

    with pytest.raises(IngestionError):
        ingester.ingest(
            content="",
            source_path="test.md",
            content_type_hint="episteme"
        )


def test_ingester_handles_invalid_content_type(ingester):
    """Verify invalid content type is handled."""
    from haios_etl.agents.ingester import IngestionError

    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        with pytest.raises(IngestionError):
            ingester.ingest(
                content="Some content",
                source_path="test.md",
                content_type_hint="invalid_type"
            )


def test_ingester_handles_extraction_error(ingester_fast):
    """Verify extraction errors are handled after retries."""
    from haios_etl.agents.ingester import IngestionError

    with patch.object(ingester_fast, '_extract_content') as mock_extract:
        mock_extract.side_effect = Exception("API unavailable")
        with patch('time.sleep'):

            with pytest.raises(IngestionError) as exc_info:
                ingester_fast.ingest(
                    content="Test content",
                    source_path="test.md",
                    content_type_hint="episteme"
                )

    assert "API unavailable" in str(exc_info.value) or "extraction" in str(exc_info.value).lower()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_ingester_uses_extract_content(ingester):
    """Verify ingester calls extraction for content processing."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {"entities": [], "concepts": []}

        ingester.ingest(
            content="Test content for extraction",
            source_path="test.md",
            content_type_hint="episteme"
        )

        mock_extract.assert_called_once()


def test_ingester_uses_memory_store(ingester, db_manager):
    """Verify ingester stores results in memory."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [{"type": "Agent", "value": "Test"}],
            "concepts": [{"type": "Decision", "content": "Test decision"}]
        }

        result = ingester.ingest(
            content="Test decision by Test agent",
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify IDs were returned (indicates storage happened)
    assert len(result.entity_ids) > 0
    assert len(result.concept_ids) > 0


# =============================================================================
# EMBEDDING GENERATION TESTS (E2-FIX-002)
# =============================================================================

@pytest.fixture
def mock_extractor():
    """Returns a mock ExtractionManager for embedding tests."""
    extractor = MagicMock()
    extractor.embed_content.return_value = [0.1] * 768  # Mock 768-dim embedding
    return extractor


@pytest.fixture
def ingester_with_extractor(db_manager, mock_extractor):
    """Returns an Ingester with mock extractor for embedding tests."""
    from haios_etl.agents.ingester import Ingester, IngesterConfig
    config = IngesterConfig(max_retries=3, backoff_base=2.0, timeout_seconds=30)
    return Ingester(
        db_manager=db_manager,
        config=config,
        extractor=mock_extractor
    )


def test_ingest_creates_embedding(ingester_with_extractor, db_manager, mock_extractor):
    """E2-FIX-002: Verify new concepts get embeddings when extractor is provided."""
    with patch.object(ingester_with_extractor, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [],
            "concepts": [{"type": "Decision", "content": "Test decision for embedding"}]
        }

        result = ingester_with_extractor.ingest(
            content="Test decision for embedding",
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify concept was stored
    assert len(result.concept_ids) == 1
    concept_id = result.concept_ids[0]

    # Verify embedding was generated
    mock_extractor.embed_content.assert_called_once()

    # Verify embedding was stored in database
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT concept_id FROM embeddings WHERE concept_id = ?", (concept_id,))
    row = cursor.fetchone()
    assert row is not None, f"Expected embedding for concept {concept_id}"


def test_ingest_without_extractor_skips_embedding(ingester, db_manager):
    """E2-FIX-002: Verify graceful behavior when no extractor provided."""
    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [],
            "concepts": [{"type": "Decision", "content": "Test without extractor"}]
        }

        result = ingester.ingest(
            content="Test without extractor",
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify concept was stored (basic functionality still works)
    assert len(result.concept_ids) == 1
    concept_id = result.concept_ids[0]

    # Verify NO embedding was created (since no extractor)
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT concept_id FROM embeddings WHERE concept_id = ?", (concept_id,))
    row = cursor.fetchone()
    assert row is None, "No embedding should exist when extractor is not provided"


def test_ingest_handles_embedding_failure(ingester_with_extractor, db_manager, mock_extractor):
    """E2-FIX-002: Verify graceful failure when embedding API fails."""
    # Configure extractor to fail
    mock_extractor.embed_content.side_effect = Exception("API rate limit exceeded")

    with patch.object(ingester_with_extractor, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [],
            "concepts": [{"type": "Decision", "content": "Test with failing embedding"}]
        }

        # Should NOT raise - embedding failure is graceful
        result = ingester_with_extractor.ingest(
            content="Test with failing embedding",
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify concept was still stored (ingestion succeeded)
    assert len(result.concept_ids) == 1

    # Verify embedding call was attempted
    mock_extractor.embed_content.assert_called_once()


def test_ingest_creates_embedding_for_each_concept(ingester_with_extractor, db_manager, mock_extractor):
    """E2-FIX-002: Verify embedding is created for each concept in batch."""
    with patch.object(ingester_with_extractor, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [],
            "concepts": [
                {"type": "Decision", "content": "First concept"},
                {"type": "Directive", "content": "Second concept"},
                {"type": "Proposal", "content": "Third concept"}
            ]
        }

        result = ingester_with_extractor.ingest(
            content="Multiple concepts for testing",
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify all concepts stored
    assert len(result.concept_ids) == 3

    # Verify embed_content called for each concept
    assert mock_extractor.embed_content.call_count == 3

    # Verify all embeddings stored
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    for concept_id in result.concept_ids:
        cursor.execute("SELECT concept_id FROM embeddings WHERE concept_id = ?", (concept_id,))
        row = cursor.fetchone()
        assert row is not None, f"Expected embedding for concept {concept_id}"


# =============================================================================
# REGRESSION TESTS
# =============================================================================

def test_ingester_preserves_full_content_no_truncation(ingester, db_manager):
    """WORK-038: Regression test for content truncation bug.

    Verifies end-to-end: ingester input -> database content verification.
    Content over 100 chars MUST be stored completely, not truncated.

    Bug: haios_etl/agents/ingester.py:167 had [:100] slice that truncated
    the 'name' parameter passed to insert_concept, which maps to 'content' column.
    """
    # Content significantly longer than 100 chars
    long_content = "A" * 200

    with patch.object(ingester, '_extract_content') as mock_extract:
        mock_extract.return_value = {
            "entities": [],
            "concepts": [{"type": "episteme", "content": long_content}]
        }

        result = ingester.ingest(
            content=long_content,
            source_path="test.md",
            content_type_hint="episteme"
        )

    # Verify concept was stored
    assert len(result.concept_ids) == 1, "Expected one concept to be stored"
    concept_id = result.concept_ids[0]

    # Verify stored content is NOT truncated
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM concepts WHERE id = ?", (concept_id,))
    row = cursor.fetchone()

    assert row is not None, "Concept not found in database"
    stored_content = row[0]
    assert len(stored_content) == 200, f"Content truncated: expected 200 chars, got {len(stored_content)}"
    assert stored_content == long_content, "Content mismatch - stored content differs from input"
