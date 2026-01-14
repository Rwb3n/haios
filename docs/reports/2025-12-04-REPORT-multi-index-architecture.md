# Investigation Report: Multi-Index Architecture

**Date:** 2025-12-04
**Author:** Hephaestus (Builder)
**Status:** Draft

## 1. Executive Summary
HAIOS currently relies on a single-index architecture (Vector Search via `sqlite-vec`) with rudimentary relational data stored in SQL tables. To enable the "Transformation Engine" vision, we propose a **Multi-Index Architecture** inspired by ApeRAG, comprising three distinct indices generated from the same source data:
1.  **Vector Index:** For semantic similarity search (existing).
2.  **Graph Index:** For relational and multi-hop reasoning (new).
3.  **Summary Index:** For high-level context and hierarchical understanding (new).

## 2. Current Architecture Audit
*   **Vector Index:** Implemented using `sqlite-vec`. Stores embeddings for artifacts, entities, and concepts.
    *   *Gap:* No fusion strategy; search is purely cosine similarity.
*   **Relational Data:** `memory_relationships` table exists but is not optimized for traversal.
    *   *Gap:* No recursive query capability (e.g., "Find all concepts derived from this ADR").
*   **Summary Data:** `concepts` table has `synthesis_cluster_id` but no dedicated summary artifacts.
    *   *Gap:* No "Global Summary" or "Epoch Summary" to ground the agent.

## 3. ApeRAG Pattern Analysis
ApeRAG (and LightRAG) uses a "Multi-Modal Indexing" approach:
*   **Graph Construction:** Extracts entities and relations using LLMs, then performs **Entity Normalization** (merging duplicates).
*   **Retrieval Fusion:** Combines results from Vector (similarity) and Graph (neighborhood) searches.
*   **Summary Index:** Generates summaries for clusters of nodes to provide "community" context.

## 4. HAIOS Graph Index Design
We will implement a **Lightweight Graph Index** backed by SQLite, but structured for export to NetworkX/JSON-LD for complex analysis.

### Schema
**Nodes:**
- `Artifact`: Source file (e.g., `ADR-001.md`)
- `Entity`: Extracted noun (e.g., `DatabaseManager`)
- `Concept`: Extracted idea (e.g., `Idempotency`)
- `Epoch`: Version marker (e.g., `Epoch 1`)

**Edges:**
- `EXTRACTED_FROM` (Entity -> Artifact)
- `MENTIONS` (Artifact -> Entity)
- `RELATES_TO` (Entity <-> Entity)
- `IMPLEMENTS` (Artifact -> Concept)
- `DERIVED_FROM` (Concept -> Concept)

### Storage
Extend `memory_relationships` table to act as the edge list.
```sql
-- Enhanced Edge Table
CREATE TABLE graph_edges (
    source_id INTEGER,
    source_type TEXT,
    target_id INTEGER,
    target_type TEXT,
    relation TEXT,
    weight REAL
);
```

## 5. HAIOS Summary Index Design
We will implement a **Hierarchical Summary Index**.

### Levels
1.  **Artifact Summary:** One-liner per file (already in `concepts`?).
2.  **Cluster Summary:** Summary of a synthesis cluster (e.g., "All DB-related patterns").
3.  **Epoch Summary:** High-level narrative of the entire epoch.

### Storage
```sql
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY,
    target_type TEXT, -- 'artifact', 'cluster', 'epoch'
    target_id INTEGER,
    content TEXT,
    embedding BLOB -- For retrieval
);
```

## 6. Multi-Index Retrieval Strategy
**Query Router:**
1.  **Classify Query:** Is it specific ("What is X?"), relational ("How does X relate to Y?"), or broad ("Tell me about Z")?
2.  **Route:**
    *   Specific -> Vector Index
    *   Relational -> Graph Index (Traversal)
    *   Broad -> Summary Index
3.  **Fuse:** Use Reciprocal Rank Fusion (RRF) to combine results.

## 7. Implementation Plan
1.  **Phase 1 (Graph):** Populate `graph_edges` from existing `entity_occurrences`.
2.  **Phase 2 (Summary):** Implement `EpochSummary` generation at the end of `synthesis.py`.
3.  **Phase 3 (Fusion):** Update `search_memories` to query all indices and fuse.

## 8. Recommendation
Adopt this architecture. It aligns perfectly with the "Transformation Engine" vision and solves the "context fragmentation" problem by providing connected and summarized views of the memory.
