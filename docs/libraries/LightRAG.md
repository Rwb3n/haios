# generated: 2025-12-04
# System Auto: last updated on: 2025-12-04 23:27:11
# LightRAG - Simple and Fast RAG
## Library Reference for HAIOS

> **Source:** Context7 `/hkuds/lightrag` (Benchmark: 81.6)
> **Extracted:** 2025-12-04
> **Related Report:** @docs/reports/2025-12-04-REPORT-multi-index-architecture.md

---

## Overview

LightRAG is a simple and fast Retrieval-Augmented Generation system that performs entity-relationship extraction from documents. It supports knowledge graphs, multimodal data, and various LLM/storage integrations.

### Relevance to HAIOS
Per the Multi-Index Architecture report, LightRAG (and ApeRAG) patterns inform:
- Graph construction via entity-relation extraction
- Entity normalization (merging duplicates)
- Retrieval fusion (Vector + Graph + Summary)
- Community summaries for context

---

## Installation

```bash
# Basic installation
pip install lightrag-hku

# With API server support
pip install "lightrag-hku[api]"

# With storage backends
pip install "lightrag-hku[api,offline-storage]"

# Full offline package
pip install "lightrag-hku[offline]"
```

---

## Server Configuration

### Environment Setup

```bash
cat > .env << EOF
# LLM Configuration
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your-api-key

# Embedding Configuration
EMBEDDING_BINDING=ollama
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
EMBEDDING_BINDING_HOST=http://localhost:11434

# Server Configuration
PORT=9621
WORKERS=2
WORKING_DIR=./rag_storage

# Storage Configuration (optional)
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=PGGraphStorage

# Authentication (optional)
LIGHTRAG_API_KEY=your-secure-api-key
EOF
```

### Start Server

```bash
# Simple mode
lightrag-server

# Production mode with Gunicorn
lightrag-gunicorn --workers 4

# Access points
# Web UI: http://localhost:9621
# API Docs: http://localhost:9621/docs
# ReDoc: http://localhost:9621/redoc
```

### Docker Compose

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
cp env.example .env
# Edit .env with your LLM/embedding config
docker compose up
```

---

## Architecture Patterns (for HAIOS)

### Multi-Modal Indexing (ApeRAG Pattern)

LightRAG uses a three-index approach that aligns with our Multi-Index Architecture:

1. **Vector Index** - Semantic similarity search
2. **Graph Index** - Entity-relation traversal
3. **Summary Index** - Community/cluster summaries

### Entity-Relation Extraction

LightRAG extracts entities and relations using LLMs, then performs:
- **Entity Normalization** - Merge duplicate entities
- **Relation Typing** - Classify relationship types
- **Graph Construction** - Build knowledge graph

### Retrieval Fusion

Combines results from multiple indices:
1. Vector search (semantic similarity)
2. Graph traversal (neighborhood exploration)
3. Summary lookup (community context)

Uses **Reciprocal Rank Fusion (RRF)** to merge results.

---

## Storage Backends

LightRAG supports multiple storage options:

| Backend | Type | Use Case |
|---------|------|----------|
| `PGKVStorage` | Key-Value | Document storage |
| `PGVectorStorage` | Vector | Embeddings |
| `PGGraphStorage` | Graph | Knowledge graph |

---

## HAIOS Integration Considerations

### What to Adopt

1. **Entity Normalization** - We have duplicates in `entities` table
2. **Graph Construction** - Extend `memory_relationships` for traversal
3. **Community Summaries** - Generate epoch/cluster summaries
4. **Retrieval Fusion** - Combine vector + graph results

### What We Already Have

- Vector storage via `sqlite-vec`
- Entity/concept extraction via `langextract`
- Synthesis pipeline for clustering

### Gap to Bridge

- No graph traversal in current retrieval
- No summary index (epoch summaries)
- No fusion strategy (single-index only)

---

## Evaluation

LightRAG includes RAGAS evaluation:

```bash
pip install ragas datasets
```

Metrics available for measuring RAG quality.

---

## Linux Service (Production)

```bash
sudo cp lightrag.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start lightrag.service
sudo systemctl enable lightrag.service
```

---

## References

- GitHub: https://github.com/HKUDS/LightRAG
- Paper: "LightRAG: Simple and Fast Retrieval-Augmented Generation"
- PyPI: https://pypi.org/project/lightrag-hku/

---

**END OF LIBRARY REFERENCE**
