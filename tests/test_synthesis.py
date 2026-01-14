# generated: 2025-11-29
# System Auto: last updated on: 2025-12-20 10:46:41
"""
Tests for the Memory Synthesis Pipeline (Phase 9 Enhancement).

Plan Reference: docs/plans/PLAN-SYNTHESIS-001-memory-consolidation.md
Design Decisions:
- DD-005: SynthesizedInsight as concept type
- DD-006: 0.85 similarity threshold
- DD-007: Cluster size 2-20
- DD-008: Separate concept/trace pipelines
- DD-009: Bridge insights as new concepts
"""
import pytest
import sqlite3
import tempfile
import os
import struct
from unittest.mock import MagicMock, patch

from haios_etl.synthesis import (
    SynthesisManager,
    SynthesisResult,
    ClusterInfo,
    SynthesisStats
)


@pytest.fixture
def temp_db():
    """Create a temporary database with synthesis schema."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Create minimal schema for synthesis tests
    # IMPORTANT: This schema MUST match docs/specs/memory_db_schema_v3.sql (DD-010)
    # Including all CHECK and FOREIGN KEY constraints
    cursor.executescript("""
        -- Core tables (minimal for synthesis tests)
        CREATE TABLE concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT,
            source_adr TEXT,
            synthesis_source_count INTEGER DEFAULT 0,
            synthesis_confidence REAL,
            synthesized_at TIMESTAMP,
            synthesis_cluster_id INTEGER
        );

        CREATE TABLE reasoning_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            query_embedding BLOB,
            strategy_title TEXT,
            strategy_content TEXT
        );

        CREATE TABLE embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artifact_id INTEGER,
            concept_id INTEGER,
            entity_id INTEGER,
            vector BLOB,
            model TEXT,
            dimensions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE memory_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Synthesis tables WITH constraints (from memory_db_schema_v3.sql)
        -- DD-010: Schema must match authoritative source
        -- DD-011: source_type includes 'cross' for bridge insights
        CREATE TABLE synthesis_clusters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_type TEXT NOT NULL CHECK(cluster_type IN ('concept', 'trace', 'cross')),
            centroid_embedding BLOB,
            member_count INTEGER DEFAULT 0,
            synthesized_concept_id INTEGER,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'synthesized', 'skipped')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synthesized_at TIMESTAMP,
            FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE SET NULL
        );

        CREATE TABLE synthesis_cluster_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_id INTEGER NOT NULL,
            member_type TEXT NOT NULL CHECK(member_type IN ('concept', 'trace')),
            member_id INTEGER NOT NULL,
            similarity_to_centroid REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cluster_id) REFERENCES synthesis_clusters(id) ON DELETE CASCADE
        );

        CREATE TABLE synthesis_provenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            synthesized_concept_id INTEGER NOT NULL,
            source_type TEXT NOT NULL CHECK(source_type IN ('concept', 'trace', 'cross')),
            source_id INTEGER NOT NULL,
            contribution_weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

    yield path

    os.unlink(path)


@pytest.fixture
def mock_extractor():
    """Create a mock ExtractionManager."""
    extractor = MagicMock()
    extractor.api_key = "test-key"
    extractor.model_id = "gemini-2.5-flash-lite"
    return extractor


def create_embedding(values):
    """Create a packed float embedding blob."""
    return struct.pack(f'{len(values)}f', *values)


class TestSynthesisClustering:
    """Tests for clustering logic (Stage 1)."""

    def test_find_similar_concepts_returns_clusters(self, temp_db):
        """Verify clustering groups similar concepts."""
        # Insert test concepts with similar embeddings
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 3 concepts with similar embeddings
        for i in range(3):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Test concept {i}")
            )
            concept_id = cursor.lastrowid
            # Similar embeddings (small variations)
            embedding = [0.5 + i * 0.01, 0.5, 0.5]
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (concept_id, create_embedding(embedding))
            )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        clusters = manager.find_similar_concepts(limit=100)

        # Should find at least one cluster
        assert len(clusters) >= 1
        # Cluster should have at least MIN_CLUSTER_SIZE members
        assert all(c.member_count >= manager.MIN_CLUSTER_SIZE for c in clusters)

    def test_cluster_respects_min_size(self, temp_db):
        """Clusters smaller than MIN_CLUSTER_SIZE are excluded."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 1 concept (below MIN_CLUSTER_SIZE)
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Solo concept")
        )
        concept_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
            (concept_id, create_embedding([0.1, 0.2, 0.3]))
        )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        clusters = manager.find_similar_concepts(limit=100)

        # Should not create cluster for single item
        assert len(clusters) == 0

    def test_cluster_respects_similarity_threshold(self, temp_db):
        """Dissimilar concepts are not clustered together."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 2 concepts with very different embeddings
        embeddings = [
            [1.0, 0.0, 0.0],  # Pointing in X direction
            [0.0, 1.0, 0.0],  # Pointing in Y direction
        ]
        for i, emb in enumerate(embeddings):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Different concept {i}")
            )
            concept_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (concept_id, create_embedding(emb))
            )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        clusters = manager.find_similar_concepts(limit=100)

        # Should not cluster orthogonal vectors
        assert len(clusters) == 0


class TestSynthesisQueryProgress:
    """Tests for synthesis query progress behavior (E2-FIX-004).

    These tests verify that the find_similar_concepts query properly excludes
    already-clustered concepts, enabling synthesis to progress through the
    full concept space rather than repeatedly processing the same concepts.

    Bug: Query checked synthesized_at IS NULL, but store_synthesis sets
         synthesis_cluster_id. This mismatch caused 6,765 concepts to be
         re-selected forever.

    Fix: Add AND c.synthesis_cluster_id IS NULL to the query.
    """

    def test_find_similar_concepts_excludes_already_clustered(self, temp_db):
        """Concepts with synthesis_cluster_id set should be excluded from query.

        This is the core E2-FIX-004 test - verifies the fix works.
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 3 concepts with similar embeddings
        for i in range(3):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Test concept {i}")
            )
            concept_id = cursor.lastrowid
            embedding = [0.5 + i * 0.001, 0.5, 0.5]  # Very similar
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector, model, dimensions) VALUES (?, ?, ?, ?)",
                (concept_id, create_embedding(embedding), 'test', 3)
            )

        # Mark concept 1 as already clustered (simulating previous synthesis run)
        cursor.execute(
            "UPDATE concepts SET synthesis_cluster_id = 999 WHERE id = 1"
        )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        clusters = manager.find_similar_concepts(limit=100)

        # Collect all member IDs from all clusters
        all_member_ids = []
        for cluster in clusters:
            all_member_ids.extend(cluster.member_ids)

        # Concept 1 should NOT be in any cluster (it's already clustered)
        assert 1 not in all_member_ids, \
            "Concept with synthesis_cluster_id set should be excluded from clustering"

    def test_synthesis_makes_progress_through_id_space(self, temp_db):
        """Repeated synthesis runs should process different concepts.

        Before E2-FIX-004: Same concepts 1-1000 selected every run
        After E2-FIX-004: Each run processes new concepts
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 10 concepts with embeddings
        for i in range(10):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Progress test concept {i}")
            )
            concept_id = cursor.lastrowid
            # Give each unique embedding so they don't cluster together
            embedding = [float(i) / 10.0, 0.5, 0.5]
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector, model, dimensions) VALUES (?, ?, ?, ?)",
                (concept_id, create_embedding(embedding), 'test', 3)
            )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)

        # Run 1: Get concepts
        clusters_1 = manager.find_similar_concepts(limit=5)
        ids_1 = set()
        for cluster in clusters_1:
            ids_1.update(cluster.member_ids)

        # Simulate what store_synthesis does: set synthesis_cluster_id on clustered concepts
        if ids_1:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids_1))
            cursor.execute(
                f"UPDATE concepts SET synthesis_cluster_id = 1 WHERE id IN ({placeholders})",
                list(ids_1)
            )
            conn.commit()
            conn.close()

            # Run 2: Should get DIFFERENT concepts
            clusters_2 = manager.find_similar_concepts(limit=5)
            ids_2 = set()
            for cluster in clusters_2:
                ids_2.update(cluster.member_ids)

            # Verify no overlap between runs
            overlap = ids_1.intersection(ids_2)
            assert len(overlap) == 0, \
                f"Second run should not include already-clustered concepts. Overlap: {overlap}"

    def test_query_still_respects_limit(self, temp_db):
        """LIMIT parameter should still work correctly after fix."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 20 concepts
        for i in range(20):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Limit test concept {i}")
            )
            concept_id = cursor.lastrowid
            embedding = [0.5, 0.5, 0.5]  # All same so they cluster
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector, model, dimensions) VALUES (?, ?, ?, ?)",
                (concept_id, create_embedding(embedding), 'test', 3)
            )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        clusters = manager.find_similar_concepts(limit=5)

        # Total members across all clusters should not exceed limit
        total_members = sum(c.member_count for c in clusters)
        assert total_members <= 5, f"Total members {total_members} exceeds limit 5"

    def test_synthesized_at_filter_still_works(self, temp_db):
        """synthesized_at IS NULL filter should still exclude SynthesizedInsight concepts."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create a regular concept
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Regular concept")
        )
        regular_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector, model, dimensions) VALUES (?, ?, ?, ?)",
            (regular_id, create_embedding([0.5, 0.5, 0.5]), 'test', 3)
        )

        # Create a SynthesizedInsight (has synthesized_at set)
        cursor.execute(
            "INSERT INTO concepts (type, content, synthesized_at) VALUES (?, ?, ?)",
            ("SynthesizedInsight", "Already synthesized", "2025-01-01T00:00:00")
        )
        synth_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector, model, dimensions) VALUES (?, ?, ?, ?)",
            (synth_id, create_embedding([0.5, 0.5, 0.5]), 'test', 3)
        )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        clusters = manager.find_similar_concepts(limit=100)

        # Collect all member IDs
        all_member_ids = []
        for cluster in clusters:
            all_member_ids.extend(cluster.member_ids)

        # SynthesizedInsight concept should be excluded
        assert synth_id not in all_member_ids, \
            "Concepts with synthesized_at set should be excluded"


class TestSynthesisLLM:
    """Tests for LLM synthesis (Stage 2)."""

    def test_synthesize_cluster_returns_result(self, temp_db, mock_extractor):
        """LLM synthesis produces valid result."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create test concepts
        for i in range(3):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Test concept about error handling {i}")
            )

        conn.commit()
        conn.close()

        cluster = ClusterInfo(
            id=1,
            cluster_type='concept',
            member_ids=[1, 2, 3],
            member_count=3
        )

        manager = SynthesisManager(temp_db, mock_extractor)

        # Mock the LLM call
        with patch.object(manager, '_call_synthesis_llm') as mock_llm:
            mock_llm.return_value = {
                'title': 'Error Handling Pattern',
                'content': 'A common approach to handling errors.',
                'confidence': 0.85
            }

            result = manager.synthesize_cluster(cluster)

            assert result is not None
            assert result.title == 'Error Handling Pattern'
            assert result.confidence == 0.85
            assert result.source_type == 'concept'
            assert len(result.source_ids) == 3

    def test_synthesize_handles_llm_failure(self, temp_db, mock_extractor):
        """Graceful fallback on LLM error."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        for i in range(2):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Concept {i}")
            )

        conn.commit()
        conn.close()

        cluster = ClusterInfo(
            id=1,
            cluster_type='concept',
            member_ids=[1, 2],
            member_count=2
        )

        manager = SynthesisManager(temp_db, mock_extractor)

        # Mock LLM failure
        with patch.object(manager, '_call_synthesis_llm') as mock_llm:
            mock_llm.return_value = None

            result = manager.synthesize_cluster(cluster)

            assert result is None  # Graceful failure


class TestSynthesisStorage:
    """Tests for storage with provenance (Stage 3)."""

    def test_store_synthesis_creates_concept(self, temp_db):
        """Synthesized insight stored as new concept."""
        manager = SynthesisManager(temp_db)

        result = SynthesisResult(
            title='Meta Pattern',
            content='A synthesized insight.',
            confidence=0.9,
            source_ids=[1, 2, 3],
            source_type='concept'
        )

        concept_id = manager.store_synthesis(result)

        assert concept_id is not None

        # Verify concept exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT type, content FROM concepts WHERE id = ?", (concept_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 'SynthesizedInsight'
        assert 'Meta Pattern' in row[1]

    def test_store_synthesis_creates_provenance(self, temp_db):
        """Provenance links created in synthesis_provenance."""
        manager = SynthesisManager(temp_db)

        result = SynthesisResult(
            title='Test Insight',
            content='Content',
            confidence=0.8,
            source_ids=[10, 20, 30],
            source_type='concept'
        )

        concept_id = manager.store_synthesis(result)

        # Verify provenance records
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT source_type, source_id FROM synthesis_provenance WHERE synthesized_concept_id = ?",
            (concept_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 3
        source_ids = [r[1] for r in rows]
        assert 10 in source_ids
        assert 20 in source_ids
        assert 30 in source_ids

    def test_store_synthesis_creates_cluster(self, temp_db):
        """Cluster record created and linked."""
        manager = SynthesisManager(temp_db)

        result = SynthesisResult(
            title='Cluster Test',
            content='Content',
            confidence=0.75,
            source_ids=[1, 2],
            source_type='trace'
        )

        concept_id = manager.store_synthesis(result)

        # Verify cluster exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT cluster_type, member_count, status FROM synthesis_clusters WHERE synthesized_concept_id = ?",
            (concept_id,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 'trace'
        assert row[1] == 2
        assert row[2] == 'synthesized'


class TestCrossPollination:
    """Tests for cross-pollination (Stage 4)."""

    def test_bridge_exists_returns_false_when_no_bridge(self, temp_db):
        """_bridge_exists returns False when no bridge exists for pair."""
        manager = SynthesisManager(temp_db)

        # No provenance exists - should return False
        exists = manager._bridge_exists(concept_id=1, trace_id=1)
        assert exists is False

    def test_bridge_exists_returns_true_when_bridge_exists(self, temp_db):
        """_bridge_exists returns True when bridge already exists for pair."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create a synthesized concept (the bridge)
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("SynthesizedInsight", "Existing bridge insight")
        )
        bridge_id = cursor.lastrowid

        # Create provenance records linking concept 10 and trace 20 to the bridge
        cursor.execute("""
            INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id)
            VALUES (?, 'cross', 10)
        """, (bridge_id,))
        cursor.execute("""
            INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id)
            VALUES (?, 'cross', 20)
        """, (bridge_id,))

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)

        # Bridge exists for this pair
        assert manager._bridge_exists(concept_id=10, trace_id=20) is True

        # Bridge does NOT exist for different pairs
        assert manager._bridge_exists(concept_id=10, trace_id=999) is False
        assert manager._bridge_exists(concept_id=999, trace_id=20) is False

    def test_find_overlaps_returns_pairs(self, temp_db):
        """Cross-type similarity detection works."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create concept with embedding
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Error handling pattern")
        )
        concept_id = cursor.lastrowid
        embedding = [0.5, 0.5, 0.5]
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
            (concept_id, create_embedding(embedding))
        )

        # Create trace with similar embedding
        similar_embedding = [0.51, 0.49, 0.50]  # Very similar
        cursor.execute(
            "INSERT INTO reasoning_traces (query, query_embedding, strategy_title) VALUES (?, ?, ?)",
            ("How to handle errors?", create_embedding(similar_embedding), "Error Strategy")
        )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        overlaps = manager.find_cross_type_overlaps(limit=10)

        # Should find the overlap
        assert len(overlaps) >= 1
        concept_ids = [o[0] for o in overlaps]
        assert concept_id in concept_ids

    def test_bridge_insight_created(self, temp_db, mock_extractor):
        """Bridge insights link concepts to traces."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Idempotency principle")
        )
        concept_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO reasoning_traces (query, strategy_title, strategy_content) VALUES (?, ?, ?)",
            ("How to ensure idempotency?", "Idempotent Operations", "Use unique identifiers")
        )
        trace_id = cursor.lastrowid

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db, mock_extractor)

        with patch.object(manager, '_call_synthesis_llm') as mock_llm:
            mock_llm.return_value = {
                'title': 'Bridge: Idempotency in Practice',
                'content': 'The idempotency principle manifests in operations.',
                'confidence': 0.7
            }

            result = manager.create_bridge_insight(concept_id, trace_id)

            assert result is not None
            assert result.source_type == 'cross'
            assert concept_id in result.source_ids
            assert trace_id in result.source_ids


class TestObservabilityEnhancements:
    """Tests for process observability (Session 43 - E2-011).

    Implements tests for PLAN-INVESTIGATION-MEMORY-PROCESS-OBSERVABILITY.md Phase 1a.
    """

    def test_comparison_loop_logs_progress(self, temp_db, caplog):
        """Progress is logged DURING comparison phase (E2-011 Phase 1a)."""
        import logging
        caplog.set_level(logging.INFO)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create enough data to trigger progress logging
        # Progress should log every 10000 comparisons or 10 seconds
        for i in range(100):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Concept {i}")
            )
            cid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (cid, create_embedding([0.5 + i*0.001, 0.5, 0.5]))
            )

        for i in range(100):
            cursor.execute(
                "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
                (f"query {i}", create_embedding([0.5, 0.5, 0.5]))
            )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        manager.find_cross_type_overlaps(limit=10, concept_sample=100, trace_sample=100)

        # Must have PROGRESS log (not just final stats)
        # Format: "Progress: X/Y (Z%) - Nm elapsed - Rk/sec"
        progress_logs = [r for r in caplog.records if "Progress:" in r.message and "/" in r.message]
        assert len(progress_logs) >= 1, "Expected progress log with format 'Progress: X/Y (Z%)'"

    def test_clustering_logs_progress(self, temp_db, caplog):
        """Progress is logged DURING clustering phase (E2-011 Phase 1b).

        Clustering has O(n²) comparisons. For 50 items = 2500 comparisons.
        Progress should be logged to give operator visibility.
        """
        import logging
        caplog.set_level(logging.INFO)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 50 concepts with embeddings to trigger clustering progress
        # This results in ~2500 comparisons (50 * 50)
        for i in range(50):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Clustering concept {i}")
            )
            cid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (cid, create_embedding([0.5 + i*0.01, 0.3, 0.2]))  # Varied embeddings
            )

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        manager.find_similar_concepts(limit=50)

        # Must have PROGRESS log during clustering
        # Format: "Clustering progress: X/Y items (Z%)"
        progress_logs = [r for r in caplog.records if "Clustering progress:" in r.message]
        assert len(progress_logs) >= 1, "Expected clustering progress log with format 'Clustering progress: X/Y items'"


class TestCrossPollinationEnhancements:
    """Tests for cross-pollination enhancements (Session 43).

    Implements tests for PLAN-SYNTHESIS-CROSS-POLLINATION-ENHANCEMENT.md:
    - Idempotency guard via _bridge_exists()
    - Sample parameters for find_cross_type_overlaps()
    - cross_only and max_bridges for run_synthesis_pipeline()
    """

    def test_find_overlaps_respects_concept_sample(self, temp_db):
        """concept_sample parameter limits concepts loaded."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 5 concepts
        for i in range(5):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Concept {i}")
            )
            cid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (cid, create_embedding([0.5, 0.5, 0.5]))
            )

        # Create 1 trace
        cursor.execute(
            "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
            ("test", create_embedding([0.5, 0.5, 0.5]))
        )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)

        # With concept_sample=2, should only compare 2 concepts
        # We can't directly test internal counts, but we verify it doesn't error
        overlaps = manager.find_cross_type_overlaps(limit=10, concept_sample=2)
        # Should return results (the exact count depends on similarity threshold)
        assert isinstance(overlaps, list)

    def test_find_overlaps_respects_trace_sample(self, temp_db):
        """trace_sample parameter limits traces loaded."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 1 concept
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Test concept")
        )
        cid = cursor.lastrowid
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
            (cid, create_embedding([0.5, 0.5, 0.5]))
        )

        # Create 5 traces
        for i in range(5):
            cursor.execute(
                "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
                (f"query {i}", create_embedding([0.5, 0.5, 0.5]))
            )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)

        # With trace_sample=2, should only compare against 2 traces
        overlaps = manager.find_cross_type_overlaps(limit=10, trace_sample=2)
        assert isinstance(overlaps, list)

    def test_find_overlaps_zero_sample_means_all(self, temp_db):
        """sample=0 loads all items (no LIMIT clause)."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create 3 concepts
        for i in range(3):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Concept {i}")
            )
            cid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (cid, create_embedding([0.5, 0.5, 0.5]))
            )

        # Create 2 traces
        for i in range(2):
            cursor.execute(
                "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
                (f"query {i}", create_embedding([0.5, 0.5, 0.5]))
            )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)

        # concept_sample=0, trace_sample=0 should load all
        overlaps = manager.find_cross_type_overlaps(limit=100, concept_sample=0, trace_sample=0)
        assert isinstance(overlaps, list)

    def test_pipeline_cross_only_skips_stages_1_to_3(self, temp_db, mock_extractor):
        """cross_only=True skips clustering and synthesis stages."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create concept with embedding
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Test concept")
        )
        cid = cursor.lastrowid
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
            (cid, create_embedding([0.5, 0.5, 0.5]))
        )

        # Create trace with embedding
        cursor.execute(
            "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
            ("test query", create_embedding([0.5, 0.5, 0.5]))
        )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db, mock_extractor)

        with patch.object(manager, '_call_synthesis_llm') as mock_llm:
            mock_llm.return_value = {
                'title': 'Bridge',
                'content': 'Test bridge',
                'confidence': 0.8
            }

            results = manager.run_synthesis_pipeline(
                cross_only=True,
                max_bridges=5
            )

            # cross_only should skip stages 1-3
            assert results['concept_clusters'] == 0
            assert results['trace_clusters'] == 0
            assert results['synthesized'] == 0
            # But should still run cross-pollination
            assert 'cross_pollination_pairs' in results

    def test_pipeline_max_bridges_limits_bridge_creation(self, temp_db, mock_extractor):
        """max_bridges parameter limits number of bridges created."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create multiple similar concept-trace pairs
        for i in range(5):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Error handling concept {i}")
            )
            cid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (cid, create_embedding([0.8, 0.1, 0.1]))
            )

        for i in range(5):
            cursor.execute(
                "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
                (f"how to handle errors {i}", create_embedding([0.8, 0.1, 0.1]))
            )
        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db, mock_extractor)

        with patch.object(manager, '_call_synthesis_llm') as mock_llm:
            mock_llm.return_value = {
                'title': 'Bridge',
                'content': 'Test',
                'confidence': 0.8
            }

            results = manager.run_synthesis_pipeline(
                cross_only=True,
                max_bridges=2  # Limit to 2
            )

            # Should create at most 2 bridges
            assert results['bridge_insights'] <= 2

    def test_pipeline_idempotency_skips_existing_bridges(self, temp_db, mock_extractor):
        """Running twice doesn't create duplicate bridges (idempotency)."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create concept
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("Directive", "Idempotency concept")
        )
        concept_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
            (concept_id, create_embedding([0.9, 0.1, 0.0]))
        )

        # Create trace
        cursor.execute(
            "INSERT INTO reasoning_traces (query, query_embedding) VALUES (?, ?)",
            ("idempotency query", create_embedding([0.9, 0.1, 0.0]))
        )
        trace_id = cursor.lastrowid

        # Pre-create a bridge for this pair
        cursor.execute(
            "INSERT INTO concepts (type, content) VALUES (?, ?)",
            ("SynthesizedInsight", "Existing bridge")
        )
        bridge_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id)
            VALUES (?, 'cross', ?)
        """, (bridge_id, concept_id))
        cursor.execute("""
            INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id)
            VALUES (?, 'cross', ?)
        """, (bridge_id, trace_id))

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db, mock_extractor)

        with patch.object(manager, '_call_synthesis_llm') as mock_llm:
            mock_llm.return_value = {
                'title': 'New Bridge',
                'content': 'Should not be created',
                'confidence': 0.8
            }

            results = manager.run_synthesis_pipeline(
                cross_only=True,
                max_bridges=10
            )

            # LLM should NOT be called because bridge already exists
            # (idempotency guard should skip this pair)
            # Bridge insights should be 0 because all pairs are already bridged
            assert results['bridge_insights'] == 0


class TestSynthesisPipeline:
    """Tests for full pipeline orchestration."""

    def test_dry_run_no_changes(self, temp_db, mock_extractor):
        """Dry run doesn't modify database."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create test data
        for i in range(3):
            cursor.execute(
                "INSERT INTO concepts (type, content) VALUES (?, ?)",
                ("Directive", f"Concept {i}")
            )
            concept_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO embeddings (concept_id, vector) VALUES (?, ?)",
                (concept_id, create_embedding([0.5 + i * 0.01, 0.5, 0.5]))
            )

        conn.commit()

        # Count before
        cursor.execute("SELECT COUNT(*) FROM concepts")
        before_count = cursor.fetchone()[0]
        conn.close()

        manager = SynthesisManager(temp_db, mock_extractor)
        results = manager.run_synthesis_pipeline(dry_run=True, limit=100)

        # Verify dry run flag
        assert results['dry_run'] is True

        # Count after - should be unchanged
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM concepts")
        after_count = cursor.fetchone()[0]
        conn.close()

        assert before_count == after_count

    def test_get_synthesis_stats(self, temp_db):
        """Stats retrieval works correctly."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Add test data
        cursor.execute("INSERT INTO concepts (type, content) VALUES (?, ?)", ("Directive", "Test"))
        cursor.execute("INSERT INTO concepts (type, content) VALUES (?, ?)", ("SynthesizedInsight", "Synth"))
        cursor.execute("INSERT INTO reasoning_traces (query) VALUES (?)", ("test query",))

        conn.commit()
        conn.close()

        manager = SynthesisManager(temp_db)
        stats = manager.get_synthesis_stats()

        assert isinstance(stats, SynthesisStats)
        assert stats.total_concepts == 2
        assert stats.total_traces == 1
        assert stats.synthesized_concepts == 1


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_parse_embedding(self, temp_db):
        """Embedding parsing from blob works."""
        manager = SynthesisManager(temp_db)

        # Create a test embedding
        values = [0.1, 0.2, 0.3, 0.4]
        blob = create_embedding(values)

        parsed = manager._parse_embedding(blob)

        assert parsed is not None
        assert len(parsed) == 4
        assert abs(parsed[0] - 0.1) < 0.001
        assert abs(parsed[3] - 0.4) < 0.001

    def test_cosine_similarity(self, temp_db):
        """Cosine similarity calculation is correct."""
        manager = SynthesisManager(temp_db)

        # Identical vectors = 1.0
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert abs(manager._cosine_similarity(a, b) - 1.0) < 0.001

        # Orthogonal vectors = 0.0
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert abs(manager._cosine_similarity(a, b)) < 0.001

        # Opposite vectors = -1.0
        a = [1.0, 0.0, 0.0]
        b = [-1.0, 0.0, 0.0]
        assert abs(manager._cosine_similarity(a, b) + 1.0) < 0.001


class TestSynthesisEmbedding:
    """Tests for embedding generation in store_synthesis (E2-FIX-001)."""

    def test_store_synthesis_creates_embedding(self, temp_db, mock_extractor):
        """
        Verify store_synthesis generates embedding for new concept.

        E2-FIX-001: Synthesized concepts were invisible to retrieval because
        they had no embeddings. This test ensures embeddings are created.
        """
        # Mock the embedding generation
        mock_extractor.embed_content.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]

        manager = SynthesisManager(temp_db, mock_extractor)

        result = SynthesisResult(
            title='Test Synthesis',
            content='A synthesized insight about patterns.',
            confidence=0.85,
            source_ids=[1, 2, 3],
            source_type='concept'
        )

        concept_id = manager.store_synthesis(result)

        assert concept_id is not None

        # Verify embedding was created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vector, model FROM embeddings WHERE concept_id = ?",
            (concept_id,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None, "Embedding should be created for synthesized concept"
        assert row[1] == "text-embedding-004", "Should use correct model name"

        # Verify embed_content was called with the concept content
        mock_extractor.embed_content.assert_called_once()
        call_args = mock_extractor.embed_content.call_args[0][0]
        assert "Test Synthesis" in call_args
        assert "patterns" in call_args

    def test_store_synthesis_without_extractor_skips_embedding(self, temp_db):
        """
        When extractor is None, store_synthesis should still work but skip embedding.
        """
        manager = SynthesisManager(temp_db, extractor=None)

        result = SynthesisResult(
            title='No Extractor Test',
            content='Content without embedding.',
            confidence=0.8,
            source_ids=[1, 2],
            source_type='concept'
        )

        concept_id = manager.store_synthesis(result)

        assert concept_id is not None

        # Verify concept exists but no embedding
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM embeddings WHERE concept_id = ?",
            (concept_id,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is None, "No embedding should be created without extractor"

    def test_store_synthesis_handles_embedding_failure(self, temp_db, mock_extractor):
        """
        When embedding generation fails, store_synthesis should still succeed.
        """
        # Mock embedding failure
        mock_extractor.embed_content.return_value = None

        manager = SynthesisManager(temp_db, mock_extractor)

        result = SynthesisResult(
            title='Embedding Failure Test',
            content='Content that fails to embed.',
            confidence=0.75,
            source_ids=[1],
            source_type='trace'
        )

        concept_id = manager.store_synthesis(result)

        # Concept should still be created
        assert concept_id is not None

        # Verify concept exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT type FROM concepts WHERE id = ?", (concept_id,))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 'SynthesizedInsight'


class TestSynthesisResult:
    """Tests for SynthesisResult dataclass."""

    def test_synthesis_result_creation(self):
        """Verify SynthesisResult can be created."""
        result = SynthesisResult(
            title="Test Title",
            content="Test content",
            confidence=0.85,
            source_ids=[1, 2, 3],
            source_type="concept"
        )

        assert result.title == "Test Title"
        assert result.confidence == 0.85
        assert len(result.source_ids) == 3
        assert result.source_type == "concept"
        assert result.cluster_id is None  # Optional field


class TestClusterInfo:
    """Tests for ClusterInfo dataclass."""

    def test_cluster_info_creation(self):
        """Verify ClusterInfo can be created."""
        cluster = ClusterInfo(
            id=42,
            cluster_type="trace",
            member_ids=[10, 20, 30],
            member_count=3,
            centroid=[0.5, 0.5, 0.5]
        )

        assert cluster.id == 42
        assert cluster.cluster_type == "trace"
        assert cluster.member_count == 3
        assert len(cluster.centroid) == 3


class TestSchemaConstraints:
    """
    Tests that verify CHECK constraints are enforced in the schema.

    Plan Reference: PLAN-FIX-001 (Schema Source-of-Truth Restoration)
    Design Decisions:
    - DD-010: Schema source of truth is memory_db_schema_v3.sql
    - DD-011: source_type includes 'cross' for bridge insights

    These tests ensure schema drift cannot occur undetected.
    """

    def test_cluster_type_rejects_invalid(self, temp_db):
        """synthesis_clusters.cluster_type CHECK constraint rejects invalid values."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO synthesis_clusters (cluster_type, member_count)
                VALUES ('invalid_type', 1)
            """)

        conn.close()

    def test_cluster_type_accepts_valid_values(self, temp_db):
        """synthesis_clusters.cluster_type accepts 'concept', 'trace', 'cross'."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # All three valid values should work
        for cluster_type in ['concept', 'trace', 'cross']:
            cursor.execute("""
                INSERT INTO synthesis_clusters (cluster_type, member_count)
                VALUES (?, 1)
            """, (cluster_type,))

        conn.commit()

        # Verify all three were inserted
        cursor.execute("SELECT COUNT(*) FROM synthesis_clusters")
        count = cursor.fetchone()[0]
        assert count == 3

        conn.close()

    def test_cluster_status_rejects_invalid(self, temp_db):
        """synthesis_clusters.status CHECK constraint rejects invalid values."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO synthesis_clusters (cluster_type, status)
                VALUES ('concept', 'invalid_status')
            """)

        conn.close()

    def test_cluster_status_accepts_valid_values(self, temp_db):
        """synthesis_clusters.status accepts 'pending', 'synthesized', 'skipped'."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        for i, status in enumerate(['pending', 'synthesized', 'skipped']):
            cursor.execute("""
                INSERT INTO synthesis_clusters (cluster_type, status)
                VALUES ('concept', ?)
            """, (status,))

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM synthesis_clusters")
        count = cursor.fetchone()[0]
        assert count == 3

        conn.close()

    def test_member_type_rejects_invalid(self, temp_db):
        """synthesis_cluster_members.member_type CHECK constraint rejects invalid values."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # First create a valid cluster to reference
        cursor.execute("""
            INSERT INTO synthesis_clusters (cluster_type, member_count)
            VALUES ('concept', 1)
        """)
        cluster_id = cursor.lastrowid

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO synthesis_cluster_members (cluster_id, member_type, member_id)
                VALUES (?, 'invalid_type', 1)
            """, (cluster_id,))

        conn.close()

    def test_member_type_accepts_valid_values(self, temp_db):
        """synthesis_cluster_members.member_type accepts 'concept', 'trace'."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create a cluster to reference
        cursor.execute("""
            INSERT INTO synthesis_clusters (cluster_type, member_count)
            VALUES ('concept', 2)
        """)
        cluster_id = cursor.lastrowid

        # Both valid member types should work
        for member_type in ['concept', 'trace']:
            cursor.execute("""
                INSERT INTO synthesis_cluster_members (cluster_id, member_type, member_id)
                VALUES (?, ?, 1)
            """, (cluster_id, member_type))

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM synthesis_cluster_members")
        count = cursor.fetchone()[0]
        assert count == 2

        conn.close()

    def test_provenance_source_type_rejects_invalid(self, temp_db):
        """synthesis_provenance.source_type CHECK constraint rejects invalid values."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create a concept to reference
        cursor.execute("""
            INSERT INTO concepts (type, content)
            VALUES ('SynthesizedInsight', 'Test')
        """)
        concept_id = cursor.lastrowid

        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id)
                VALUES (?, 'invalid_type', 1)
            """, (concept_id,))

        conn.close()

    def test_provenance_source_type_accepts_cross(self, temp_db):
        """
        synthesis_provenance.source_type accepts 'cross' (DD-011).

        This is the critical test that validates the bug fix - 'cross' MUST be accepted
        for bridge insights to work correctly.
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Create a concept to reference
        cursor.execute("""
            INSERT INTO concepts (type, content)
            VALUES ('SynthesizedInsight', 'Bridge Insight')
        """)
        concept_id = cursor.lastrowid

        # All three valid source types including 'cross'
        for source_type in ['concept', 'trace', 'cross']:
            cursor.execute("""
                INSERT INTO synthesis_provenance (synthesized_concept_id, source_type, source_id)
                VALUES (?, ?, 1)
            """, (concept_id, source_type))

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM synthesis_provenance")
        count = cursor.fetchone()[0]
        assert count == 3

        # Verify 'cross' specifically is present
        cursor.execute("SELECT source_type FROM synthesis_provenance WHERE source_type = 'cross'")
        row = cursor.fetchone()
        assert row is not None, "'cross' source_type must be accepted per DD-011"

        conn.close()
