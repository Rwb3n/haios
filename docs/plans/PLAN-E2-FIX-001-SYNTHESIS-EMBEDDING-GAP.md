---
template: implementation_plan
status: complete
date: 2025-12-11
backlog_id: E2-FIX-001
title: "Synthesis Embedding Gap"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-11
# System Auto: last updated on: 2025-12-11 20:43:20
# Implementation Plan: Synthesis Embedding Gap

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Make synthesized concepts (2,265 SynthesizedInsight type) visible to memory retrieval by generating embeddings for them.

---

## Problem Statement

**Root Cause:** `synthesis.py:store_synthesis()` creates concepts but never generates embeddings.

**Evidence:**
- 2,265 SynthesizedInsight concepts exist
- 2 have embeddings (0.09%)
- 2,263 missing embeddings (99.91%)

**Impact:** Cross-pollination runs but produces invisible results. Vector search cannot find synthesized insights.

**Working Pattern:** `collaboration.py:_handle_ingester()` (lines 239-254) correctly embeds ingested content.

---

## Methodology: TDD

1. Write test for embedding generation in `store_synthesis()`
2. Implement fix
3. Write backfill script
4. Verify retrieval

---

## Proposed Changes

### 1. Fix Forward Path (synthesis.py)
- [x] Add `ExtractionManager` dependency to `SynthesisManager.__init__()` (already exists)
- [x] In `store_synthesis()`, after concept insert, generate embedding:
  ```python
  if self.extractor:
      content = f"[{result.title}] {result.content}"
      embedding = self.extractor.embed_content(content[:8000])
      if embedding:
          self.db.insert_embedding(
              concept_id=new_concept_id,
              vector=embedding,
              model="text-embedding-004",
              dimensions=len(embedding)
          )
  ```

### 2. Backfill Existing Concepts (script)
- [x] Create `scripts/backfill_synthesis_embeddings.py`
- [x] Query: `SELECT id, content FROM concepts WHERE type='SynthesizedInsight'`
- [x] Left join embeddings to find those without
- [x] Batch embed and insert (50 at a time to respect rate limits)
- [x] Report progress: X/2263 embedded

### 3. Tests
- [x] `test_store_synthesis_creates_embedding()` - verify new concepts get embedded
- [x] `test_store_synthesis_without_extractor_skips_embedding()` - graceful when no extractor
- [x] `test_store_synthesis_handles_embedding_failure()` - graceful when embedding fails

### 4. Verification
- [ ] Run backfill script
- [ ] Query `memory_search_with_experience` for synthesized content
- [ ] Confirm SynthesizedInsight concepts appear in results

---

## Verification

- [ ] Tests pass (`pytest tests/test_synthesis.py -v`)
- [ ] Backfill complete (0 concepts without embeddings)
- [ ] Retrieval works (SynthesizedInsight in search results)
- [ ] Documentation updated (epistemic_state.md - synthesis gap RESOLVED)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits during backfill | Medium | Batch 50 at a time with delay |
| Embedding cost ($) | Low | 2,263 concepts @ ~100 tokens each = ~$0.02 |
| Existing synthesis_clusters orphaned | None | Concepts already linked, just invisible |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 59 | 2025-12-11 | - | plan_created | INV-005 complete, fix designed |

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] All traced files complete

---

## References

- **Investigation:** PLAN-INV-005-MEMORY-SYSTEM-REALITY-CHECK.md (complete)
- **Working Pattern:** `haios_etl/agents/collaboration.py:239-254`
- **Target:** `haios_etl/synthesis.py:store_synthesis()`
- **Memory:** Concepts 65070-65071 (INV-005 findings)

---
