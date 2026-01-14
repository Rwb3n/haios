---
template: implementation_plan
status: complete
date: 2025-12-13
backlog_id: E2-FIX-002
title: "Ingester Embedding Fix"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 16:03:05
# Implementation Plan: Ingester Embedding Fix

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Make ingested concepts (via `ingester_ingest` MCP tool) visible to memory retrieval by generating embeddings at ingestion time.

---

## Problem Statement

**Root Cause:** `haios_etl/agents/ingester.py` inserts concepts via `db_manager.insert_concept()` but does NOT generate embeddings afterward.

**Investigation:** INVESTIGATION-E2-FIX-002-ingester-embedding-gap.md (complete)

**Evidence:**
- Concepts 70696-70715 (ingested E2-009 learnings): NO embeddings
- Concepts 70716+ (synthesized): YES embeddings (E2-FIX-001 fixed synthesis.py)
- Total gap: 3,177 concepts (4.5%), 75% Critique/Directive types

**Impact:** Recently ingested session learnings invisible to retrieval. Memory queries miss recent context.

---

## Methodology: TDD

1. Write test for embedding generation in `ingest()` method
2. Implement fix
3. Verify with existing concepts

---

## Proposed Changes

### 1. Add ExtractionManager to Ingester (ingester.py)

- [x] Add `extractor` parameter to `Ingester.__init__()`
- [x] Store as `self.extractor`
- [x] ~~Create default if not provided~~ (MCP server passes extraction_manager)

```python
def __init__(
    self,
    db_manager=None,
    config: Optional[IngesterConfig] = None,
    api_key: Optional[str] = None,
    extractor: Optional['ExtractionManager'] = None  # NEW
):
    self.db_manager = db_manager
    self.config = config or IngesterConfig()
    self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
    self.extractor = extractor  # NEW
```

### 2. Generate Embeddings After Concept Insert (ingester.py lines 160-170)

- [x] After `concept_ids.append(concept_id)`, call embedding generation
- [x] Mirror synthesis.py pattern (E2-FIX-001)
- [x] Graceful failure (log warning, continue without embedding)

```python
# Store concepts
for concept in extraction_result.get("concepts", []):
    try:
        concept_id = self.db_manager.insert_concept(
            type=concept.get("type", classification),
            name=concept.get("content", "")[:100],
            description=concept.get("content", "")
        )
        concept_ids.append(concept_id)

        # NEW: Generate embedding for semantic search (E2-FIX-002)
        if self.extractor:
            try:
                content = concept.get("content", "")[:8000]
                embedding = self.extractor.embed_content(content)
                if embedding:
                    self.db_manager.insert_embedding(
                        concept_id=concept_id,
                        vector=embedding,
                        model="text-embedding-004",
                        dimensions=len(embedding)
                    )
            except Exception as embed_err:
                logger.warning(f"Failed to generate embedding for concept {concept_id}: {embed_err}")

    except Exception as e:
        logger.warning(f"Failed to store concept: {e}")
```

### 3. Update MCP Server (mcp_server.py)

- [x] Ensure `ingester_ingest` tool passes extractor or allows Ingester to create one
- [x] Check current wiring in `haios_etl/mcp_server.py`

### 4. Tests

- [x] `test_ingest_creates_embedding()` - verify new concepts get embedded
- [x] `test_ingest_without_extractor_skips_embedding()` - graceful when no extractor
- [x] `test_ingest_handles_embedding_failure()` - graceful when API fails
- [x] `test_ingest_creates_embedding_for_each_concept()` - verify batch behavior

---

## Verification

- [x] Tests pass (`pytest tests/test_ingester.py -v` - 23 passed)
- [x] New ingestion creates embeddings (concept 70891 has 768-dim embedding after server restart)
- [x] Retrieval returns recently ingested concepts (verified in database)
- [x] Documentation updated (plan complete, backlog updated)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits during bulk ingestion | Medium | Same pattern as synthesis - batch internally if needed |
| Embedding cost ($) | Low | ~$0.01 per 1000 concepts, minimal |
| ExtractionManager not available | Low | Graceful fallback - log warning, skip embedding |
| db_manager.insert_embedding signature mismatch | Low | Check signature before implementing |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 64 | 2025-12-13 | - | investigation_complete | Root cause verified |
| 64 | 2025-12-13 | - | plan_created | This plan |
| 64 | 2025-12-13 | - | complete | Implementation + tests done |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (23 ingester tests, 196 total)
- [x] WHY captured (concepts 70882-70890, source: closure:E2-FIX-002)
- [x] Documentation current (plan updated)
- [x] All traced files complete

**Note:** Concepts 70882-70890 were stored WITHOUT embeddings because the running MCP server had not reloaded the code changes. After server restart, new ingestions will have embeddings. Tests confirm the code is correct.

---

## Out of Scope

- Backfill of existing 3,177 unembedded concepts (separate script, can reuse E2-FIX-001 pattern)
- Entity embeddings (E2-018 scope)

---

## References

- **Investigation:** INVESTIGATION-E2-FIX-002-ingester-embedding-gap.md
- **E2-FIX-001:** Synthesis embedding gap (same pattern, already fixed)
- **PLAN-E2-FIX-001:** Original fix plan with working code pattern
- **synthesis.py:482-503:** Working embedding pattern
- **collaboration.py:239-254:** Working artifact embedding pattern

---
