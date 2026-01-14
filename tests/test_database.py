# generated: 2025-11-30
# System Auto: last updated on: 2025-12-27T16:42:25
import pytest
import sqlite3
import os
from haios_etl.database import DatabaseManager

# Fixture for in-memory database
@pytest.fixture
def db_manager():
    """Returns a DatabaseManager instance using an in-memory database."""
    # Use :memory: for fast, isolated testing
    manager = DatabaseManager(":memory:")
    manager.setup()
    return manager

def test_setup_database(db_manager):
    """Verify that all tables are created correctly."""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Check for existence of all 7 tables
    tables = [
        "artifacts", "entities", "entity_occurrences", 
        "concepts", "concept_occurrences", "processing_log", "quality_metrics"
    ]
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        assert cursor.fetchone() is not None, f"Table {table} not created"

def test_insert_artifact(db_manager):
    """Verify artifact insertion."""
    artifact_id = db_manager.insert_artifact(
        file_path="test/file.md",
        file_hash="abc123hash",
        size_bytes=100
    )
    assert artifact_id is not None
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, file_hash FROM artifacts WHERE id=?", (artifact_id,))
    row = cursor.fetchone()
    assert row[0] == "test/file.md"
    assert row[1] == "abc123hash"

def test_insert_artifact_duplicate(db_manager):
    """Verify handling of duplicate artifacts."""
    id1 = db_manager.insert_artifact("test/dup.md", "hash1", 100)
    
    # Insert same path, different hash (simulating file update)
    id2 = db_manager.insert_artifact("test/dup.md", "hash2", 120)
    
    assert id1 == id2 # Should return same ID
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_hash, version FROM artifacts WHERE id=?", (id1,))
    row = cursor.fetchone()
    assert row[0] == "hash2" # Hash updated
    assert row[1] == 2 # Version incremented

def test_insert_entity(db_manager):
    """Verify entity insertion."""
    entity_id = db_manager.insert_entity("User", "Ruben")
    assert entity_id is not None
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type, value FROM entities WHERE id=?", (entity_id,))
    row = cursor.fetchone()
    assert row[0] == "User"
    assert row[1] == "Ruben"

def test_insert_entity_duplicate(db_manager):
    """Verify handling of duplicate entities."""
    id1 = db_manager.insert_entity("Agent", "Claude")
    id2 = db_manager.insert_entity("Agent", "Claude")
    
    assert id1 == id2 # Should be idempotent

def test_insert_concept(db_manager):
    """Verify concept insertion."""
    concept_id = db_manager.insert_concept("Decision", "Use SQLite", "Because it is fast")
    assert concept_id is not None
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT type, content FROM concepts WHERE id=?", (concept_id,))
    row = cursor.fetchone()
    assert row[0] == "Decision"
    assert row[1] == "Use SQLite"

def test_insert_occurrences(db_manager):
    """Verify linking entities/concepts to artifacts."""
    art_id = db_manager.insert_artifact("test/link.md", "hash", 10)
    ent_id = db_manager.insert_entity("User", "Ruben")
    
    db_manager.record_entity_occurrence(ent_id, art_id, "Ruben said hello")
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT context_snippet FROM entity_occurrences WHERE entity_id=? AND artifact_id=?", (ent_id, art_id))
    row = cursor.fetchone()
    assert row[0] == "Ruben said hello"

def test_get_processing_status(db_manager):
    """Verify status retrieval."""
    # Should be None for unknown file
    status = db_manager.get_processing_status("unknown.md")
    assert status is None
    
    # Insert artifact first
    db_manager.insert_artifact("known.md", "hash", 10)
    # Initialize status
    db_manager.update_processing_status("known.md", "pending")
    
    status = db_manager.get_processing_status("known.md")
    assert status == "pending"

def test_insert_quality_metrics(db_manager):
    """Verify quality metrics insertion."""
    art_id = db_manager.insert_artifact("test/metrics.md", "hash", 100)
    
    db_manager.insert_quality_metrics(
        artifact_id=art_id,
        entities_extracted=5,
        concepts_extracted=2,
        processing_time=1.5,
        tokens_used=100
    )
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT entities_extracted, concepts_extracted, processing_time_seconds, llm_tokens_used 
        FROM quality_metrics WHERE artifact_id=?
    """, (art_id,))
    row = cursor.fetchone()
    
    assert row[0] == 5
    assert row[1] == 2
    assert row[2] == 1.5
    assert row[3] == 100

def test_duplicate_occurrence_prevention(db_manager):
    """Test that recording same occurrence twice doesn't create duplicates."""
    artifact_id = db_manager.insert_artifact("test/dup_occ.md", "hash123", 100)
    entity_id = db_manager.insert_entity("User", "Alice")
    concept_id = db_manager.insert_concept("Decision", "Test", "Context")

    # Record same entity occurrence twice
    db_manager.record_entity_occurrence(entity_id, artifact_id, "context1")
    db_manager.record_entity_occurrence(entity_id, artifact_id, "context2")

    # Record same concept occurrence twice
    db_manager.record_concept_occurrence(concept_id, artifact_id, "context1")
    db_manager.record_concept_occurrence(concept_id, artifact_id, "context2")

    # Verify only one occurrence exists for each
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM entity_occurrences WHERE entity_id = ? AND artifact_id = ?",
                   (entity_id, artifact_id))
    count = cursor.fetchone()[0]
    assert count == 1, f"Expected 1 entity occurrence, found {count}"

    cursor.execute("SELECT COUNT(*) FROM concept_occurrences WHERE concept_id = ? AND artifact_id = ?",
                   (concept_id, artifact_id))
    count = cursor.fetchone()[0]
    assert count == 1, f"Expected 1 concept occurrence, found {count}"


# =============================================================================
# AGENT REGISTRY TESTS (Session 17 - PLAN-AGENT-ECOSYSTEM-002)
# =============================================================================

def test_register_agent(db_manager):
    """Verify agent registration and idempotent update."""
    agent_card = {
        'id': 'agent-test-v1',
        'name': 'TestAgent',
        'version': '1.0.0',
        'description': 'A test agent',
        'type': 'subagent',
        'capabilities': ['test-capability', 'another-capability'],
        'tools': ['memory_search'],
        'input_schema': {'type': 'object', 'properties': {'query': {'type': 'string'}}},
        'output_schema': {'type': 'object', 'properties': {'result': {'type': 'string'}}},
        'status': 'active'
    }

    # Register agent
    db_manager.register_agent(agent_card)

    # Verify via direct SQL
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, version, type FROM agent_registry WHERE id = ?", ('agent-test-v1',))
    row = cursor.fetchone()

    assert row is not None, "Agent not found in registry"
    assert row[0] == 'TestAgent'
    assert row[1] == '1.0.0'
    assert row[2] == 'subagent'

    # Update agent (idempotent)
    agent_card['version'] = '1.1.0'
    agent_card['description'] = 'Updated description'
    db_manager.register_agent(agent_card)

    cursor.execute("SELECT version, description FROM agent_registry WHERE id = ?", ('agent-test-v1',))
    row = cursor.fetchone()
    assert row[0] == '1.1.0', "Version not updated"
    assert row[1] == 'Updated description', "Description not updated"


def test_get_agent(db_manager):
    """Verify agent retrieval by ID with JSON field parsing."""
    agent_card = {
        'id': 'agent-retrieval-test',
        'name': 'RetrievalTest',
        'version': '2.0.0',
        'description': 'Test retrieval',
        'type': 'worker',
        'capabilities': ['cap1', 'cap2'],
        'tools': ['tool1', 'tool2'],
        'input_schema': {'type': 'string'},
        'output_schema': {'type': 'boolean'},
    }

    db_manager.register_agent(agent_card)

    # Retrieve via method
    retrieved = db_manager.get_agent('agent-retrieval-test')

    assert retrieved is not None, "Agent not retrieved"
    assert retrieved['name'] == 'RetrievalTest'
    assert retrieved['version'] == '2.0.0'
    assert retrieved['type'] == 'worker'
    assert retrieved['capabilities'] == ['cap1', 'cap2'], "Capabilities not parsed correctly"
    assert retrieved['tools'] == ['tool1', 'tool2'], "Tools not parsed correctly"
    assert retrieved['input_schema'] == {'type': 'string'}, "Input schema not parsed"
    assert retrieved['output_schema'] == {'type': 'boolean'}, "Output schema not parsed"

    # Test non-existent agent
    missing = db_manager.get_agent('non-existent-agent')
    assert missing is None, "Should return None for missing agent"


def test_list_agents(db_manager):
    """Verify agent listing with capability filtering."""
    # Register multiple agents with different capabilities
    agents = [
        {
            'id': 'agent-a',
            'name': 'AgentA',
            'version': '1.0.0',
            'type': 'subagent',
            'capabilities': ['vision-alignment', 'concept-translation'],
        },
        {
            'id': 'agent-b',
            'name': 'AgentB',
            'version': '1.0.0',
            'type': 'subagent',
            'capabilities': ['content-ingestion', 'chunking'],
        },
        {
            'id': 'agent-c',
            'name': 'AgentC',
            'version': '1.0.0',
            'type': 'worker',
            'capabilities': ['vision-alignment', 'quality-check'],
            'status': 'active'
        },
        {
            'id': 'agent-deprecated',
            'name': 'DeprecatedAgent',
            'version': '0.9.0',
            'type': 'subagent',
            'capabilities': ['legacy'],
            'status': 'deprecated'
        }
    ]

    for agent in agents:
        db_manager.register_agent(agent)

    # List all active agents
    all_active = db_manager.list_agents()
    assert len(all_active) == 3, f"Expected 3 active agents, got {len(all_active)}"

    # Filter by capability
    vision_agents = db_manager.list_agents(capability='vision-alignment')
    assert len(vision_agents) == 2, f"Expected 2 agents with vision-alignment, got {len(vision_agents)}"

    agent_names = [a['name'] for a in vision_agents]
    assert 'AgentA' in agent_names
    assert 'AgentC' in agent_names
    assert 'AgentB' not in agent_names

    # Filter by non-existent capability
    empty = db_manager.list_agents(capability='non-existent')
    assert len(empty) == 0, "Should return empty list for non-existent capability"


# =============================================================================
# HYBRID RETRIEVAL TESTS (Session 72 - ADR-037)
# =============================================================================

@pytest.fixture
def db_with_concepts(db_manager):
    """Database with test concepts for retrieval testing."""
    # Insert old concepts (simulating older content)
    for i in range(5):
        db_manager.insert_concept(
            type="SynthesizedInsight",
            name=f"Old synthesis {i}",
            description=f"Generic philosophical insight about HAIOS number {i}"
        )

    # Insert recent concepts (simulating session work)
    for i in range(5):
        db_manager.insert_concept(
            type="Decision",
            name=f"Recent decision {i}",
            description=f"Session 70 work item E2-04{i} decision"
        )

    # Insert knowledge concepts
    db_manager.insert_concept(
        type="episteme",
        name="Knowledge fact",
        description="A factual piece of knowledge"
    )
    db_manager.insert_concept(
        type="techne",
        name="How-to guide",
        description="Practical instructions for doing something"
    )

    return db_manager


def test_search_memories_accepts_mode(db_with_concepts):
    """Test 1: Mode parameter is accepted without error."""
    # This test will fail until mode parameter is implemented
    import struct
    dummy_vector = [0.1] * 768
    vector_bytes = struct.pack(f'{len(dummy_vector)}f', *dummy_vector)

    # Should not raise an error
    results = db_with_concepts.search_memories(
        query_vector=dummy_vector,
        mode='session_recovery'
    )
    assert results is not None


def test_session_recovery_excludes_synthesis(db_with_concepts):
    """Test 3: Session recovery mode excludes SynthesizedInsight."""
    import struct
    dummy_vector = [0.1] * 768

    results = db_with_concepts.search_memories(
        query_vector=dummy_vector,
        mode='session_recovery'
    )

    types = [r['type'] for r in results]
    assert 'SynthesizedInsight' not in types, f"SynthesizedInsight found in results: {types}"


def test_knowledge_lookup_filters_types(db_with_concepts):
    """Test 4: Knowledge lookup mode filters to episteme/techne types."""
    import struct
    dummy_vector = [0.1] * 768

    results = db_with_concepts.search_memories(
        query_vector=dummy_vector,
        mode='knowledge_lookup'
    )

    allowed_types = ['episteme', 'techne', 'Critique', 'Decision', 'Directive', 'Proposal']
    types = [r['type'] for r in results]
    for t in types:
        assert t in allowed_types, f"Unexpected type {t} in knowledge lookup results"


def test_semantic_mode_backward_compatible(db_with_concepts):
    """Test 5: Semantic mode (default) behaves same as no mode."""
    import struct
    dummy_vector = [0.1] * 768

    # With explicit mode='semantic'
    results_with_mode = db_with_concepts.search_memories(
        query_vector=dummy_vector,
        mode='semantic'
    )

    # Without mode (default behavior)
    results_default = db_with_concepts.search_memories(
        query_vector=dummy_vector
    )

    # Results should be identical
    assert len(results_with_mode) == len(results_default)
    # Content should match (comparing IDs)
    ids_with_mode = [r['id'] for r in results_with_mode]
    ids_default = [r['id'] for r in results_default]
    assert ids_with_mode == ids_default, "Mode='semantic' should match default behavior"


# =============================================================================
# BUSY_TIMEOUT TESTS (Session 128 - E2-211 / INV-027)
# =============================================================================

def test_database_busy_timeout_is_set():
    """Verify busy_timeout PRAGMA is configured on connection (E2-211).

    Fixes INV-027: Concurrent access crash when ingester runs while synthesis active.
    Without explicit busy_timeout, SQLite may default to 0ms or a low value like 5000ms.
    Synthesis operations can take 10+ seconds, so we need at least 30s.
    """
    import sys
    sys.path.insert(0, '.claude/lib')
    from database import DatabaseManager

    db = DatabaseManager(":memory:")
    conn = db.get_connection()
    cursor = conn.execute("PRAGMA busy_timeout")
    timeout = cursor.fetchone()[0]
    # Must be at least 30 seconds to handle synthesis operations
    assert timeout >= 30000, f"Expected busy_timeout >= 30000ms, got {timeout}ms"
