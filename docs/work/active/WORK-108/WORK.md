---
template: work_item
id: WORK-108
title: Fix Embedding Model Migration (text-embedding-004 to gemini-embedding-001)
type: bug
status: active
owner: Hephaestus
created: 2026-02-08
spawned_by: null
chapter: null
arc: null
closed: null
priority: high
effort: small
traces_to:
- REQ-MEMORY-001
requirement_refs: []
source_files:
- haios_etl/extraction.py
- haios_etl/agents/ingester.py
- haios_etl/agents/collaboration.py
- scripts/backfill_synthesis_embeddings.py
- scripts/complete_concept_embeddings.py
acceptance_criteria:
- AC1: memory_search_with_experience returns results (not embedding 404)
- AC2: All references to text-embedding-004 replaced with gemini-embedding-001
- AC3: Embedding generation test passes with live API
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-08 23:24:21
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-08
last_updated: '2026-02-08T23:25:09'
---
# WORK-108: Fix Embedding Model Migration (text-embedding-004 to gemini-embedding-001)

---

## Context

Google retired the `text-embedding-004` model from the Gemini API (v1beta endpoint returns 404). The replacement is `gemini-embedding-001` (confirmed via `genai.list_models()`). This breaks all semantic search in the memory system — `memory_search_with_experience` fails with "Embedding generation failed: 404 models/text-embedding-004 is not found for API version v1beta". Ingestion still works (doesn't require embeddings), but search is fully broken.

**Root cause:** Hardcoded model name `models/text-embedding-004` in 5 files across haios_etl and scripts.
**Fix:** Replace with `models/gemini-embedding-001` in all locations. Consider making the model name configurable via env var or config.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] Replace `text-embedding-004` with `gemini-embedding-001` in haios_etl/extraction.py
- [ ] Replace `text-embedding-004` with `gemini-embedding-001` in haios_etl/agents/ingester.py
- [ ] Replace `text-embedding-004` with `gemini-embedding-001` in haios_etl/agents/collaboration.py
- [ ] Replace `text-embedding-004` in scripts (backfill_synthesis_embeddings.py, complete_concept_embeddings.py)
- [ ] Verify memory_search_with_experience returns results (not 404)
- [ ] Consider: make embedding model name configurable via env var or haios.yaml

---

## History

### 2026-02-08 - Created (Session 324)
- Discovered during WORK-107 when memory_search_with_experience returned 404
- Confirmed: text-embedding-004 retired, gemini-embedding-001 is replacement
- 5 files need model name update

---

## References

- @haios_etl/extraction.py (line 368: embedding_model = "models/text-embedding-004")
- @haios_etl/agents/ingester.py (line 182)
- @haios_etl/agents/collaboration.py (line 248)
