---
template: investigation
status: complete
date: 2025-12-13
backlog_id: E2-FIX-002
title: "Investigation: Ingester Embedding Gap"
author: Hephaestus
lifecycle_phase: discovery
version: "1.0"
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 15:51:28
# Investigation: Ingester Embedding Gap

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 63 completed E2-FIX-001 (synthesis embedding gap) and ran overnight synthesis. Morning verification discovered that recently ingested concepts (via `ingester_ingest` MCP tool) were NOT appearing in retrieval. A search for "lifecycle sequence enforcement" returned old concepts, not the E2-009 learnings just stored.

This investigation verifies whether `haios_etl/agents/ingester.py` has the same embedding gap that was fixed in `synthesis.py`.

---

## Objective

1. Verify that ingester.py does not generate embeddings after concept insertion
2. Confirm affected concept scope (which concepts are invisible)
3. Identify the fix pattern from synthesis.py

---

## Scope

### In Scope
- `haios_etl/agents/ingester.py` embedding behavior
- Concepts 70696-70715 (E2-009 session learnings)
- Comparison with synthesis.py fix

### Out of Scope
- Historical embedding gap (E2-017) - separate backfill effort
- Entity embeddings (E2-018) - separate initiative
- Collaboration.py artifact embeddings (already working)

---

## Hypotheses

1. **H1:** `ingester.py` inserts concepts via `db_manager.insert_concept()` but does NOT call embedding generation afterward - **CONFIRMED**
2. **H2:** `synthesis.py` was fixed (E2-FIX-001) to embed after concept creation; ingester.py was not - **CONFIRMED**
3. **H3:** Recently ingested concepts (70696-70715) have no embeddings - **CONFIRMED**

---

## Investigation Steps

1. [x] Read `haios_etl/agents/ingester.py` - check `ingest()` method
2. [x] Read `haios_etl/synthesis.py` - check `store_synthesis()` fix
3. [x] Read `haios_etl/agents/collaboration.py` - check working pattern (artifact embeddings)
4. [x] Query database: concepts 70696-70715 embedding status
5. [x] Quantify total embedding gap by type

---

## Findings

### Finding 1: Root Cause Confirmed

`ingester.py` lines 160-170 insert concepts WITHOUT embedding generation:

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
    except Exception as e:
        logger.warning(f"Failed to store concept: {e}")
# NO EMBEDDING GENERATION HERE
```

### Finding 2: Working Pattern Exists

`synthesis.py` lines 482-503 (after E2-FIX-001):
```python
# 5. Generate embedding for the synthesized concept (E2-FIX-001)
if self.extractor:
    try:
        content = f"[{result.title}] {result.content}"
        embedding = self.extractor.embed_content(content[:8000])
        if embedding:
            cursor.execute("""
                INSERT INTO embeddings (concept_id, vector, model, dimensions)
                VALUES (?, ?, ?, ?)
            """, (new_concept_id, struct.pack(...), "text-embedding-004", len(embedding)))
```

### Finding 3: Database Verification

| Concept ID Range | Type | Has Embedding |
|------------------|------|---------------|
| 70696-70715 | Decision/Critique/Directive/Proposal (ingested) | **NO** |
| 70716+ | SynthesizedInsight (synthesis.py) | **YES** |

**Pattern:** Same ID boundary as synthesis overnight run. All ingested = no embedding. All synthesized = has embedding.

### Finding 4: Total Impact

- 3,177 concepts missing embeddings (4.5% of total)
- 75% of gap from Critique (1,194) and Directive (1,193) types
- These are common ingestion types from session learnings

---

## Root Cause

`Ingester.ingest()` (used by `ingester_ingest` MCP tool) stores concepts but skips embedding generation. The `Ingester` class has NO reference to `ExtractionManager` for embedding calls.

Contrast with:
- `synthesis.py` - Has `self.extractor` and uses it in `store_synthesis()`
- `collaboration.py:_handle_ingester()` - Creates artifacts with embeddings (lines 239-254)

---

## Recommended Fix

Add embedding generation after concept insertion in `ingester.py`, mirroring the synthesis.py pattern:

```python
# After concept_ids.append(concept_id):
if hasattr(self, 'extractor') and self.extractor:
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
    except Exception as e:
        logger.warning(f"Failed to generate embedding: {e}")
```

**Also required:** Pass `ExtractionManager` to `Ingester.__init__()` or create it internally.

---

## Spawned Work Items

- [x] E2-FIX-002 - Fix ingester.py embedding gap (this investigation)
- [ ] Backfill script for 3,177 unembedded concepts (can reuse E2-FIX-001 script pattern)

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Root cause identification
- [ ] Implementation plan (can proceed directly - pattern known)
- [ ] Memory storage (after fix implementation)

---

## References

- **E2-FIX-001:** Synthesis embedding gap (same pattern, synthesis.py side)
- **PLAN-E2-FIX-001:** Original fix plan with working code pattern
- **collaboration.py:239-254:** Working artifact embedding pattern
- **Session 63 checkpoint:** Discovery of this gap during verification

---
