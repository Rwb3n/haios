# generated: 2025-11-25
# System Auto: last updated on: 2025-12-09 23:05:18
# HAIOS ETL Package

> **Navigation:** [Quick Reference](../docs/README.md) | [Strategic Overview](../docs/epistemic_state.md) | [Operations](../docs/OPERATIONS.md) | [MCP Integration](../docs/MCP_INTEGRATION.md)

The `haios_etl` package implements the Extract, Transform, Load pipeline for the HAIOS Cognitive Memory System.

**Status:** Phase 9 Complete - Memory Synthesis + MCP Schema Abstraction (Session 53)

---

## Modules Overview

| Module | Role | Phase |
|--------|------|-------|
| `extraction.py` | LLM extraction + embeddings | 3 |
| `processing.py` | Batch orchestration | 3 |
| `database.py` | SQLite + vector storage | 3-4 |
| `retrieval.py` | ReasoningBank search + strategy extraction | 4 |
| `refinement.py` | Knowledge refinement + LLM classification | 7 |
| `synthesis.py` | Memory consolidation + clustering | 9 |
| `agents/` | Interpreter, Ingester, Collaboration | 8 |
| `mcp_server.py` | Agent ecosystem interface | 4-5 |
| `cli.py` | Command-line interface | 3 |
| `migrations/` | Schema version control (001-008) | 4-9 |
| `preprocessors/` | Format transformation | 3 |
| `quality.py` | Metrics collection | 3 |
| `errors.py` | Custom exceptions | 3 |

---

## Module Details

### Phase 3: ETL Core

#### `extraction.py` (The "Eyes")
-   **Role:** Interfaces with the LLM (Gemini) to extract structured data.
-   **Key Class:** `ExtractionManager`
-   **Features:**
    -   Uses `langextract` library for schema-constrained generation.
    -   Implements retry logic for API stability.
    -   Handles model configuration (currently `gemini-2.5-flash-lite`).
    -   **`embed_content()`**: Generates embeddings via Gemini text-embedding-004.

#### `processing.py` (The "Brain")
-   **Role:** Orchestrates the batch processing of files.
-   **Key Class:** `BatchProcessor`
-   **Features:**
    -   **Idempotency:** Checks file hashes against DB to skip unchanged files.
    -   **Safety:** Handles binary files, encoding errors, and empty files.
    -   **Atomic Updates:** Updates database status per file.

#### `database.py` (The "Memory")
-   **Role:** Manages SQLite interactions.
-   **Key Class:** `DatabaseManager`
-   **Features:**
    -   Stores `Artifacts`, `Entities`, `Concepts`, `Embeddings`, `Reasoning Traces`.
    -   Prevents duplicate occurrences via `DELETE BEFORE INSERT` strategy.
    -   **WAL Mode:** Write-Ahead Logging for concurrent access.
    -   **`get_stats()`**: Returns counts for all tables.
    -   **`search_memories()`**: Vector similarity search (requires sqlite-vec).
    -   **`insert_embedding()`**: Stores vector embeddings.

#### `cli.py` (The "Hands")
-   **Role:** Command-line interface.
-   **Commands:**
    -   `process <dir>`: Run ETL on a directory.
    -   `status`: Show system statistics.
    -   `reset`: Wipe the database.

#### `preprocessors/` (The "Translators")
-   **Role:** Adapts non-standard file formats for extraction.
-   **Handlers:**
    -   `GeminiDumpPreprocessor`: Parses raw Gemini API JSON dumps.
    -   `BasePreprocessor`: Interface for future handlers (e.g., PDF, HTML).

#### `quality.py` + `errors.py`
-   **Role:** Supporting modules for metrics and error handling.

---

### Phase 4: Retrieval & Reasoning (COMPLETE)

#### `retrieval.py` (The "Recall")
-   **Role:** Implements ReasoningBank-style experience learning.
-   **Key Classes:**
    -   `RetrievalService`: Base vector search.
    -   `ReasoningAwareRetrieval`: Records and learns from reasoning traces.
-   **Features:**
    -   **`search_with_experience()`**: Main entry point for retrieval with strategy injection.
    -   **`find_similar_reasoning_traces()`**: Finds past successful strategies.
    -   **`record_reasoning_trace()`**: Logs attempts with outcomes.
    -   **`extract_strategy_from_trace()`**: LLM-based strategy extraction.
-   **Status:** ReasoningBank loop closed (Session 32-33).

#### `mcp_server.py` (The "Interface")
-   **Role:** Exposes memory system to agent ecosystem via MCP.
-   **Server:** FastMCP named `haios-memory`
-   **Tools (13 total):**
    -   `memory_search_with_experience(query, space_id)`: Search with learning.
    -   `memory_stats()`: Database statistics.
    -   `ingester_ingest(content, source_path, content_type_hint)`: Primary ingest method.
    -   `interpreter_translate(intent)`: Natural language to directive.
    -   `extract_content(file_path, content, extraction_mode)`: LLM extraction.
    -   `marketplace_list_agents(capability)`: Agent registry.
    -   `marketplace_get_agent(agent_id)`: Agent details.
    -   `schema_info(table_name)`: **NEW** - DB schema introspection (Session 53).
    -   `db_query(sql)`: **NEW** - Read-only SQL queries (Session 53).
    -   `memory_store(...)`: **DEPRECATED** - Use ingester_ingest.
-   **See:** [MCP Integration Guide](../docs/MCP_INTEGRATION.md)

---

## Configuration

Environment variables (in `.env`):
-   `GOOGLE_API_KEY`: Required for Gemini API access.
-   `DB_PATH`: Optional path to database (default: `haios_memory.db`).

## Usage

### CLI Usage
```bash
# Process files
python -m haios_etl.cli process HAIOS-RAW

# Check status
python -m haios_etl.cli status

# Reset database
python -m haios_etl.cli reset
```

### MCP Server

Exposes 13 tools for retrieving memories, checking system status, and schema introspection.
Integrated with Epoch 2 Governance Suite via system diagnostics.
**New in Session 53:** `schema_info` and `db_query` tools provide database abstraction layer.

```bash
python -m haios_etl.mcp_server
```

### Programmatic Usage
```python
from haios_etl.processing import BatchProcessor
from haios_etl.database import DatabaseManager
from haios_etl.extraction import ExtractionManager
from haios_etl.retrieval import ReasoningAwareRetrieval
import os

# Initialize
db = DatabaseManager("haios_memory.db")
extractor = ExtractionManager(api_key=os.getenv("GOOGLE_API_KEY"))

# ETL Processing
processor = BatchProcessor(db, extractor)
processor.process_file("path/to/document.md")

# Retrieval with Learning
retrieval = ReasoningAwareRetrieval(db, extractor)
results = retrieval.search_with_experience("find authentication patterns")
```

---

## Schema Migrations

Located in `migrations/`:
-   `001_add_reasoning_traces.sql`: ReasoningBank table
-   `002_add_embeddings.sql`: Vector storage table
-   `003_add_space_id_to_artifacts.sql`: Scoped retrieval support
-   `004_add_refinement_tables.sql`: Knowledge refinement tables
-   `005_add_reasoning_traces_vec.sql`: Vector embeddings for traces
-   `006_add_strategy_columns.sql`: Strategy extraction columns
-   `007_add_synthesis_tables.sql`: Memory synthesis tables
-   `008_add_synthesis_constraints.sql`: Synthesis schema constraints

Apply with: `python scripts/apply_migration.py`

---

### Phase 6: Refinement

#### sqlite-vec Integration
-   **Role:** High-performance vector similarity search
-   **Version:** v0.1.6
-   **Features:**
    -   Loaded automatically in `get_connection()`
    -   `vec_distance_cosine()` for similarity scoring
    -   Graceful fallback if extension unavailable

#### space_id Filtering
-   **Role:** Scoped retrieval for multi-tenant queries
-   **Column:** `artifacts.space_id` (added via migration 003)
-   **Index:** `idx_artifacts_space_id` for query performance

#### Embedding Generation
-   **Script:** `scripts/generate_embeddings.py`
-   **Model:** Gemini text-embedding-004
-   **Coverage:** Complete (all concepts have embeddings)

---

### Phase 7: Knowledge Refinement

#### `refinement.py` (The "Refiner")
-   **Role:** LLM-based classification and knowledge upgrading.
-   **Key Class:** `RefinementManager`
-   **Features:**
    -   **`scan_raw_memories()`**: Find unrefined concepts.
    -   **`classify_concept()`**: LLM classification (episteme/techne/doxa).
    -   **`create_episteme()`**: Upgrade high-confidence concepts to episteme.
-   **Greek Triad:** episteme (knowledge), techne (skills), doxa (beliefs)

---

### Phase 8: Agent Ecosystem

#### `agents/` (The "Workers")
-   **Role:** Subagent implementations for the HAIOS ecosystem.
-   **Modules:**
    -   `interpreter.py`: Translates operator intent to system directives (DD-012 to DD-014)
    -   `ingester.py`: Classifies and stores content in memory (DD-015 to DD-019)
    -   `collaboration.py`: Agent-to-agent handoff protocol (DD-018, DD-020)
-   **Key Classes:**
    -   `Interpreter`: Intent translation with grounding.
    -   `Ingester`: Content classification and storage.
    -   `Collaborator`: Handoff orchestration.
-   **Reference:** [PLAN-AGENT-ECOSYSTEM-001](../docs/plans/PLAN-AGENT-ECOSYSTEM-001.md)

---

### Phase 9: Memory Synthesis

#### `synthesis.py` (The "Consolidator")
-   **Role:** Memory consolidation and pattern extraction.
-   **Key Class:** `SynthesisPipeline`
-   **5-Stage Pipeline:**
    1. **CLUSTER** - Group similar memories by vector similarity
    2. **SYNTHESIZE** - Extract meta-patterns using LLM
    3. **STORE** - Save synthesized concepts with provenance
    4. **CROSS-POLLINATE** - Bridge concepts and reasoning traces
    5. **PRUNE** - Archive redundant entries (optional)
-   **Reference:** [PLAN-SYNTHESIS-001](../docs/plans/PLAN-SYNTHESIS-001-memory-consolidation.md)

---

## Navigation

-   [Quick Reference](../docs/README.md) - Documentation map
-   [Strategic Overview](../docs/epistemic_state.md) - Current system state
-   [Operations Manual](../docs/OPERATIONS.md) - ETL runbook
-   [MCP Integration](../docs/MCP_INTEGRATION.md) - Agent connection
-   [Test Suite](../tests/README.md) - Test documentation

---

**Last Updated:** 2025-12-09 (Session 54 - README sync)
**Status:** Phase 9 Complete - Memory Synthesis + MCP Schema Abstraction
