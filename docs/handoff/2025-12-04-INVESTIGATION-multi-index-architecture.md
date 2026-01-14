---
template: handoff
version: 1.0
type: investigation
date: 2025-12-04
author: Hephaestus (Builder)
status: ready
priority: medium
estimated_effort: 8 hours
source: "@docs/libraries/research-2025-12-04/05-apecloud-aperag.md"
generated: 2025-12-04
last_updated: 2025-12-04T21:06:17
---

# Investigation Handoff: Multi-Index Architecture for Epoch Artifacts

## Objective

Design a Multi-Index output architecture for HAIOS epochs, producing Vector, Graph, and Summary indices from the same source data. Enables different query types (similarity, relational, high-level).

---

## Background

**Source:** https://github.com/apecloud/ApeRAG

**Key Concepts:**
- **Multi-Modal Indexing:** Same data -> multiple specialized indices
- **GraphRAG:** Entity-relation graphs for complex queries
- **Entity Normalization:** Merge duplicates during graph construction
- **Summary Index:** Compressed representation for high-level context

**Current State:**
- HAIOS has: sqlite-vec for vectors, entities/concepts tables
- No graph structure (entities not linked to each other)
- No summary layer
- Single retrieval path (vector similarity only)

---

## Investigation Spec

### 1. Current Architecture Audit

**Questions to Answer:**
- [ ] What index types does HAIOS currently support?
- [ ] How are entities/concepts currently related (if at all)?
- [ ] What queries fail or underperform with current architecture?
- [ ] What is the schema for `haios_memory.db`?

**Actions:**
- Review `docs/specs/memory_db_schema_v3.sql`
- Analyze `haios_etl/database.py` retrieval methods
- Document current query patterns and limitations

### 2. ApeRAG Architecture Analysis

**Questions to Answer:**
- [ ] What are the 5 index types in ApeRAG? (Vector, Full-text, Graph, Summary, Vision)
- [ ] How does LightRAG construct the knowledge graph?
- [ ] What is the entity normalization algorithm?
- [ ] How are the indices queried together (fusion)?

**Actions:**
- Deep-read ApeRAG source code (focus on index construction)
- Extract graph schema (node types, edge types)
- Document the retrieval fusion strategy

### 3. Graph Index Design for HAIOS

**Questions to Answer:**
- [ ] What node types should HAIOS graph have?
- [ ] What edge types (relations) are meaningful?
- [ ] How to construct graph from existing entities/concepts?
- [ ] Storage: Separate graph DB or extend SQLite?

**Proposed Node Types:**
```
- Artifact (source file)
- Entity (extracted thing: ADR, Person, System)
- Concept (extracted idea: Strategy, Principle, Pattern)
- Epoch (version marker)
```

**Proposed Edge Types:**
```
- EXTRACTED_FROM: Entity/Concept -> Artifact
- RELATES_TO: Entity <-> Entity
- IMPLEMENTS: Concept -> Concept
- SUPERSEDES: Epoch -> Epoch
```

**Storage Options:**
| Option | Pros | Cons |
|--------|------|------|
| SQLite (edges table) | Simple, single file | No graph queries (Cypher) |
| NetworkX (in-memory) | Python native, algorithms | Not persistent |
| Neo4j | Full graph DB | Heavy dependency |
| JSON-LD export | Portable | Query overhead |

### 4. Summary Index Design for HAIOS

**Questions to Answer:**
- [ ] What level of summarization? (per-artifact, per-epoch, global)
- [ ] How to generate summaries? (LLM, extractive, hybrid)
- [ ] How to index summaries for retrieval?

**Proposed Levels:**
```
Global Summary: "HAIOS is a Trust Engine for AI agents..."
  |
Epoch Summary: "Epoch 2 focused on ETL pipeline completion..."
  |
Artifact Summary: "ADR-023 defines idempotency requirements..."
```

### 5. Multi-Index Retrieval Strategy

**Questions to Answer:**
- [ ] How to route queries to appropriate index?
- [ ] How to fuse results from multiple indices?
- [ ] What is the ranking/scoring strategy?

**Proposed Flow:**
```
Query: "How does HAIOS handle authentication?"
    |
    v
[Query Classifier]
    - Similarity query? -> Vector Index
    - Relational query? -> Graph Index
    - Overview query? -> Summary Index
    - Hybrid? -> All + Fusion
    |
    v
[Retrieval]
    - Vector: Top-K similar chunks
    - Graph: Subgraph around "authentication" entity
    - Summary: Relevant epoch/artifact summaries
    |
    v
[Fusion]
    - RRF (Reciprocal Rank Fusion)
    - or LLM-based reranking
    |
    v
[Result]
```

### 6. Integration Points

**Where Multi-Index connects to HAIOS:**

| Component | Integration |
|-----------|-------------|
| `haios_etl/database.py` | Add graph storage methods |
| `haios_etl/extraction.py` | Extract relations for graph edges |
| `haios-memory-mcp` | Expose graph queries as tools |
| Epoch artifacts | Export `graph.json`, `summaries.json` |

---

## Acceptance Criteria

- [ ] Current architecture limitations documented
- [ ] ApeRAG index construction patterns extracted
- [ ] Graph schema design for HAIOS (nodes, edges, storage)
- [ ] Summary index design (levels, generation, storage)
- [ ] Multi-index retrieval strategy spec
- [ ] Migration path from current to multi-index architecture
- [ ] Effort estimate for full implementation

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Scope creep (too ambitious) | Phase implementation: Graph first, Summary second |
| Graph construction quality | Start with explicit relations, add LLM-inferred later |
| Query routing complexity | Start with manual routing, add classifier later |
| Performance regression | Benchmark current vs new on same queries |

---

## Key References

- @docs/libraries/research-2025-12-04/05-apecloud-aperag.md
- @docs/libraries/research-2025-12-04/07-cognee.md
- @docs/libraries/research-2025-12-04/SUMMARY-output-pipeline.md
- @docs/specs/memory_db_schema_v3.sql
- @haios_etl/database.py
- @haios_etl/extraction.py
- https://github.com/apecloud/ApeRAG
- https://github.com/topoteretes/cognee

---

## Output Expected

Investigation report containing:
1. Current architecture audit (capabilities, gaps)
2. ApeRAG pattern extraction (what to adopt)
3. Graph index design spec (schema, storage, construction)
4. Summary index design spec (levels, generation)
5. Multi-index retrieval strategy
6. Phased implementation plan
7. Effort estimate and recommendation

---

## Vision Alignment

From `docs/VISION_ANCHOR.md`:
> "We store WHAT HAPPENED, not WHAT WE LEARNED"

Multi-Index is the architectural answer:
- **Vector Index:** WHAT HAPPENED (raw similarity)
- **Graph Index:** HOW THINGS RELATE (learned structure)
- **Summary Index:** WHAT WE LEARNED (distilled knowledge)

This transforms storage into knowledge.
