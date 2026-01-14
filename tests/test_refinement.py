# generated: 2025-11-27
# System Auto: last updated on: 2025-12-03 21:30:55
"""
Tests for the Knowledge Refinement Layer (Phase 8).

Design Decision Reference: docs/plans/25-11-27-01-phase-integration/S4-specification-deliverable.md
- DD-001: Episteme storage in concepts table
- INV-001: Existing metadata rows must remain valid

GAP-B3 (Session 21): Added LLM classification tests
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch, MagicMock

from haios_etl.refinement import RefinementManager, RefinementResult


@pytest.fixture
def temp_db():
    """Create a temporary database with required schema."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Create minimal schema for refinement tests
    cursor.executescript("""
        CREATE TABLE concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT,
            source_adr TEXT
        );

        CREATE TABLE memory_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE memory_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            relationship_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

    yield path

    os.unlink(path)


class TestGetOrCreateEpisteme:
    """Tests for _get_or_create_episteme() - P8-G1 regression tests."""

    def test_creates_episteme_without_crash(self, temp_db):
        """
        P8-T1: Verify Episteme creation uses correct table.

        Regression test for P8-G1: Previously referenced non-existent
        artifacts.content column, causing sqlite3.OperationalError.
        """
        mgr = RefinementManager(temp_db)

        # Should NOT raise sqlite3.OperationalError
        episteme_id = mgr._get_or_create_episteme("Test Principle")

        assert episteme_id > 0

    def test_creates_episteme_in_concepts_table(self, temp_db):
        """Verify DD-001: Episteme stored in concepts table, not artifacts."""
        mgr = RefinementManager(temp_db)

        episteme_id = mgr._get_or_create_episteme("Idempotency Principle")

        # Verify in concepts table
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT type, content, source_adr FROM concepts WHERE id = ?", (episteme_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "Episteme"
        assert row[1] == "Idempotency Principle"
        assert row[2] == "virtual:episteme"

    def test_creates_metadata_for_episteme(self, temp_db):
        """Verify metadata is created with knowledge_type=episteme."""
        mgr = RefinementManager(temp_db)

        episteme_id = mgr._get_or_create_episteme("Test Principle")

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM memory_metadata WHERE memory_id = ? AND key = 'knowledge_type'",
            (episteme_id,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "episteme"

    def test_deduplicates_existing_episteme(self, temp_db):
        """Verify existing Episteme is returned, not duplicated."""
        mgr = RefinementManager(temp_db)

        # Create first
        first_id = mgr._get_or_create_episteme("Unique Principle")

        # Should return same ID, not create new
        second_id = mgr._get_or_create_episteme("Unique Principle")

        assert first_id == second_id

        # Verify only one concept exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM concepts WHERE content = 'Unique Principle'")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1


class TestRefinementResult:
    """Tests for RefinementResult dataclass."""

    def test_refinement_result_creation(self):
        """Verify RefinementResult can be created."""
        result = RefinementResult(
            knowledge_type="episteme",
            confidence=0.95,
            concepts=["Concept A", "Concept B"],
            reasoning="Test reasoning"
        )

        assert result.knowledge_type == "episteme"
        assert result.confidence == 0.95
        assert len(result.concepts) == 2


class TestSaveRefinement:
    """Tests for save_refinement()."""

    def test_saves_metadata(self, temp_db):
        """Verify save_refinement creates correct metadata entries."""
        mgr = RefinementManager(temp_db)

        # First create a concept to refine
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO concepts (type, content) VALUES (?, ?)", ("Directive", "Test content"))
        concept_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Create refinement result
        result = RefinementResult(
            knowledge_type="doxa",
            confidence=0.85,
            concepts=[],
            reasoning="Test"
        )

        # Save refinement
        mgr.save_refinement(concept_id, result)

        # Verify metadata
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM memory_metadata WHERE memory_id = ?", (concept_id,))
        rows = cursor.fetchall()
        conn.close()

        metadata = {row[0]: row[1] for row in rows}
        assert metadata.get("knowledge_type") == "doxa"
        assert metadata.get("refinement_status") == "processed"
        assert metadata.get("refinement_confidence") == "0.85"


class TestLLMClassification:
    """Tests for LLM-based classification (GAP-B3)."""

    def test_classify_with_llm_episteme(self, temp_db):
        """Test LLM classifies factual content as episteme."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        # Patch the module-level genai in refinement.py
        with patch('haios_etl.refinement.genai') as mock_genai, \
             patch('haios_etl.refinement.GENAI_AVAILABLE', True):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "episteme"
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            result = mgr._classify_with_llm("The architecture consists of three layers.")

            assert result == "episteme"
            mock_genai.configure.assert_called_once_with(api_key="test-key")

    def test_classify_with_llm_techne(self, temp_db):
        """Test LLM classifies how-to content as techne."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        with patch('haios_etl.refinement.genai') as mock_genai, \
             patch('haios_etl.refinement.GENAI_AVAILABLE', True):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "techne"
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            result = mgr._classify_with_llm("Step 1: Install the package. Step 2: Configure.")

            assert result == "techne"

    def test_classify_with_llm_doxa(self, temp_db):
        """Test LLM classifies opinion content as doxa."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        with patch('haios_etl.refinement.genai') as mock_genai, \
             patch('haios_etl.refinement.GENAI_AVAILABLE', True):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "doxa"
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            result = mgr._classify_with_llm("I believe this approach is better.")

            assert result == "doxa"

    def test_classify_with_llm_fallback_no_api_key(self, temp_db):
        """Test fallback to heuristic when api_key is None."""
        mgr = RefinementManager(temp_db, api_key=None)

        result = mgr._classify_with_llm("Some content")

        assert result is None

    def test_classify_with_llm_fallback_on_exception(self, temp_db):
        """Test fallback to heuristic when LLM fails."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        with patch('haios_etl.refinement.genai') as mock_genai, \
             patch('haios_etl.refinement.GENAI_AVAILABLE', True):
            mock_genai.configure.side_effect = Exception("API Error")

            result = mgr._classify_with_llm("Some content")

            assert result is None

    def test_classify_with_llm_invalid_response(self, temp_db):
        """Test returns None when LLM response is invalid."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        with patch('haios_etl.refinement.genai') as mock_genai, \
             patch('haios_etl.refinement.GENAI_AVAILABLE', True):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "unknown_type"  # Invalid classification
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            result = mgr._classify_with_llm("Some content")

            assert result is None

    def test_refine_memory_uses_llm_first(self, temp_db):
        """Test refine_memory uses LLM classification when available."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        with patch.object(mgr, '_classify_with_llm', return_value="techne"):
            result = mgr.refine_memory(1, "How to do something")

            assert result.knowledge_type == "techne"
            assert result.confidence == 0.9
            assert "LLM classification" in result.reasoning

    def test_refine_memory_fallback_to_heuristic(self, temp_db):
        """Test refine_memory falls back to heuristic when LLM unavailable."""
        mgr = RefinementManager(temp_db, api_key=None)

        result = mgr.refine_memory(1, "This Directive must be followed")

        assert result.knowledge_type == "doxa"
        assert result.confidence == 0.6  # Heuristic confidence
        assert "Heuristic" in result.reasoning

    def test_confidence_reflects_source(self, temp_db):
        """Test confidence score differs between LLM and heuristic."""
        mgr = RefinementManager(temp_db, api_key="test-key")

        # LLM path
        with patch.object(mgr, '_classify_with_llm', return_value="episteme"):
            llm_result = mgr.refine_memory(1, "Content")
            assert llm_result.confidence == 0.9

        # Heuristic path (no api_key)
        mgr_no_key = RefinementManager(temp_db, api_key=None)
        heuristic_result = mgr_no_key.refine_memory(1, "Some content")
        assert heuristic_result.confidence == 0.5  # Default heuristic
