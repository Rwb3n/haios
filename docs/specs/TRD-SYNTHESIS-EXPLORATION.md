---
template: guide
status: draft
date: 2025-11-28
title: "Memory Synthesis Pipeline - Exploration Report"
author: Hephaestus
---
# generated: 2025-11-28
# System Auto: last updated on: 2025-11-28 00:44:57
# Memory Synthesis Pipeline - Codebase Exploration Report

## Purpose

This document captures the exploration of the HAIOS codebase in preparation for designing a Memory Synthesis Pipeline. Generated during Session 15 planning phase.

---

## 1. Key Functions and Signatures

### haios_etl/refinement.py - RefinementManager

```python
class RefinementManager:
    def __init__(self, db_path: str) -> None

    def scan_raw_memories(self, limit: int = 10) -> List[Dict]
        # Find unrefined concepts by checking memory_metadata for refinement_status
        # Returns: [{'id': int, 'type': str, 'content': str}, ...]

    def refine_memory(self, memory_id: int, content: str) -> RefinementResult
        # Mock LLM analysis (TODO: integrate real LLM)
        # Returns RefinementResult with knowledge_type, confidence, concepts, reasoning

    def save_refinement(self, memory_id: int, result: RefinementResult) -> None
        # Persists: metadata (knowledge_type, refinement_status, refinement_confidence)
        # Persists: relationships (derived_from links to Episteme concepts)

    def _get_or_create_episteme(self, content: str) -> int
        # DD-001: Stores Episteme in concepts table (NOT artifacts)
        # Vector search TODO: Currently uses exact match, should switch to similarity > 0.9
        # Returns: concept_id for the (deduplicated) Episteme

    def _link_memories(self, cursor, source_id: int, target_id: int, rel_type: str) -> None
        # Inserts into memory_relationships table
```

### haios_etl/retrieval.py - RetrievalService & ReasoningAwareRetrieval

```python
class RetrievalService:
    def __init__(self, db_manager: DatabaseManager, extraction_manager: ExtractionManager)

    def search(query: str, space_id: Optional[str], filters: Optional[Dict],
               top_k: int = 10) -> List[Dict[str, Any]]
        # Hybrid vector + metadata search

    def _generate_embedding(self, text: str) -> List[float]
        # Delegates to ExtractionManager.embed_content()

class ReasoningAwareRetrieval(RetrievalService):
    def search_with_experience(query: str, space_id: Optional[str],
                               filters: Optional[Dict]) -> Dict[str, Any]
        # Returns: {'results': [...], 'reasoning': {..., 'relevant_strategies': [...]}}

    def find_similar_reasoning_traces(query_embedding: List[float],
                                      space_id: Optional[str] = None,
                                      threshold: float = 0.8) -> List[Dict[str, Any]]
        # DD-002: Uses vec_distance_cosine() directly for MVP
        # DD-003: Converts similarity threshold to distance (0.8 similarity = 0.2 max distance)

    def _determine_strategy(self, past_attempts: List[Dict]) -> Dict[str, Any]
        # DD-004: "First success wins"

    def record_reasoning_trace(...) -> None
        # Calls extractor.extract_strategy() for ReasoningBank alignment
        # Stores: strategy_title, strategy_description, strategy_content
```

### haios_etl/database.py - DatabaseManager

```python
class DatabaseManager:
    def get_connection(self) -> sqlite3.Connection
        # WAL mode enabled for concurrency
        # Loads sqlite-vec extension if available

    def search_memories(self, query_vector: List[float], space_id: Optional[str],
                       filters: Optional[Dict], limit: int = 10) -> List[Dict]
        # Vector search using sqlite-vec vec_distance_cosine()

    def get_stats(self) -> Dict
        # Returns: {artifacts, entities, concepts, embeddings, reasoning_traces}
```

### haios_etl/extraction.py - ExtractionManager

```python
class ExtractionManager:
    def embed_content(self, text: str) -> List[float]
        # Uses Gemini text-embedding-004

    def extract_strategy(self, query: str, approach: str, outcome: str,
                        results_summary: str, error_details: str) -> Dict[str, Any]
        # Returns: {title: str, description: str, content: str}
```

---

## 2. Database Table Structures

### Core Schema (memory_db_schema_v2.sql)

```sql
artifacts (id, file_path, file_hash, last_processed_at, version)
entities (id, type, value)  -- UNIQUE(type, value)
concepts (id, type, content, source_adr)
entity_occurrences (id, artifact_id, entity_id, line_number, context_snippet)
concept_occurrences (id, artifact_id, concept_id, line_number, context_snippet)
processing_log (id, file_path, status, attempt_count, last_attempt_at, error_message, file_hash)
quality_metrics (id, artifact_id, entities_extracted, concepts_extracted, processing_time_seconds, llm_tokens_used, created_at)
```

### Migration 001: Reasoning Traces

```sql
reasoning_traces (
    id, query, query_embedding BLOB, approach_taken, strategy_details JSON,
    outcome IN ('success', 'partial_success', 'failure'),
    failure_reason, success_factors JSON, memories_used JSON, memories_helpful JSON,
    context_snapshot JSON, execution_time_ms, model_used, space_id, timestamp,
    similar_to_trace_id (FK to reasoning_traces)
)
```

### Migration 002: Embeddings

```sql
embeddings (
    id, artifact_id, concept_id, entity_id,
    vector BLOB (sqlite-vec format), model, dimensions, created_at
)
```

### Migration 004: Refinement Tables

```sql
memory_metadata (
    id, memory_id (FK), key, value, created_at
)
-- Keys: knowledge_type, refinement_status, refinement_confidence, refinement_model

memory_relationships (
    id, source_id (FK), target_id (FK),
    relationship_type IN ('implements', 'justifies', 'derived_from', 'supports', 'contradicts', 'related'),
    created_at
)
```

### Migration 006: Strategy Columns

```sql
ALTER TABLE reasoning_traces ADD COLUMN (
    strategy_title, strategy_description, strategy_content, extraction_model
)
```

---

## 3. Existing Batch Processing Patterns

### Idempotent Processing Model
- Hash-based change detection: SHA256 in `artifacts.file_hash`
- Status tracking: `processing_log` table with status enum
- Resume capability: Restart failed batches without reprocessing
- Side-effect cleanup: Deletes old occurrences on re-processing

### Error Handling Pattern
```python
try:
    # Process
except Exception as e:
    db.update_processing_status(file_path, "error", str(e))
    # Continue with next file
```

---

## 4. Gaps and Hooks for Synthesis Pipeline

### Identified Gaps

| Gap | Current State | Required For Synthesis |
|-----|---------------|------------------------|
| LLM Integration | `refine_memory()` is MOCKED | Real classification |
| Vector Deduplication | Exact match in `_get_or_create_episteme()` | Similarity > 0.9 |
| Clustering | No clustering logic exists | Batch deduplication |
| Quality Reports | TODO in quality.py | Synthesis metrics |

### Integration Hooks

| Hook | Location | Purpose |
|------|----------|---------|
| Metadata Storage | `memory_metadata` table | Store synthesis results |
| Relationship Storage | `memory_relationships` table | Store `synthesized_from` links |
| Batch Pattern | `scan_raw_memories()` | Cursor-based iteration |
| CLI | `cli.py` | Add `synthesis` command |
| MCP | `mcp_server.py` | Add `memory_synthesis_run` tool |

---

## 5. Design Decisions Reference

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-001 | Episteme in `concepts` table | Has `content` column |
| DD-002 | Direct vec_distance_cosine() | Simpler than vec0 for MVP |
| DD-003 | Similarity threshold = 0.8 | 80% semantic match |
| DD-004 | "First success wins" strategy | Simple learning |

---

## 6. User Requirements (Session 15)

| Question | Answer |
|----------|--------|
| Input Source | Both Concepts (34k) + Reasoning Traces (200+), cross-pollinate |
| Goal | All: Dedupe + Meta-patterns + Knowledge Graph |
| Trigger | On-demand CLI |

---

## 7. Synthesis Pipeline Architecture (Proposed)

```
                 Existing Memories
                 (34k concepts, 200+ traces)
                          |
                          v
        +----------------------------------+
        |     1. CLUSTER                   |
        |  - Generate embeddings           |
        |  - Group by similarity (>0.85)   |
        |  - Separate: concepts vs traces  |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     2. SYNTHESIZE                |
        |  - LLM: "Common insight?"        |
        |  - Output: meta-pattern          |
        |  - Type: Episteme (principle)    |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     3. STORE                     |
        |  - New concept (SynthesizedInsight) |
        |  - memory_relationships links    |
        |  - memory_metadata tags          |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     4. CROSS-POLLINATE           |
        |  - Find concept<->trace overlaps |
        |  - Generate bridge insights      |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     5. PRUNE (Optional)          |
        |  - Archive low-value duplicates  |
        |  - Merge near-identical concepts |
        +----------------------------------+
```

---

## References

- @docs/VISION_ANCHOR.md - Core vision
- @docs/epistemic_state.md - Current state
- @haios_etl/refinement.py - Existing refinement layer
- @haios_etl/retrieval.py - Vector search patterns
