---
template: investigation
status: complete
date: 2025-12-14
backlog_id: INV-015
title: "Investigation: Retrieval Algorithm Intelligence"
author: Hephaestus
lifecycle_phase: conclude
version: "1.1"
session: 73
closed_session: 102
closure_note: "Research consolidated into INV-023. Option A (E2-063 Query Rewriting) complete. Options B-E research preserved in INV-023. Feedback loop (Option D) is INV-023's focus."
generated: 2025-12-23
last_updated: 2025-12-23T11:01:23
---
# Investigation: Retrieval Algorithm Intelligence

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 73 observation: E2-059 completed the mechanism (memory retrieval pipeline works), but the algorithm is lacking. The memory system successfully:
- Fires on user prompt
- Generates embeddings
- Queries database with session_recovery mode
- Injects TOON-formatted context

But the INTELLIGENCE of retrieval is naive - pure cosine similarity with no contextual understanding. Operator feedback: "the mechanism input output is there, the algorithm is lacking."

**Related investigations:**
- INV-014: Memory context injection architecture (truncation, format)
- INV-010: Memory retrieval architecture (CLOSED - led to ADR-037)

This investigation goes deeper: not just WHAT to filter, but HOW to make retrieval actually intelligent.

---

## Objective

Determine what algorithmic improvements would transform memory retrieval from a search engine into a learning system that provides actionable, contextually-relevant insights.

---

## Scope

### In Scope
- Query formulation strategy (raw prompt vs. extracted intent)
- Ranking algorithms (similarity + contextual weighting)
- Strategy applicability matching (not just pattern similarity)
- Result framing (actionable guidance vs. raw dumps)
- Task-type awareness (debugging vs. implementing vs. reviewing)

### Out of Scope
- Mechanism changes (hooks, MCP tools) - already working
- UI/UX changes - focus on algorithm
- New data sources - work with existing memory content

---

## Hypotheses

1. **H1:** Raw user prompts are poor queries - conversational text doesn't map well to stored technical content. Need intent extraction.

2. **H2:** Pure cosine similarity misses contextual relevance - a strategy about "debugging" might be 0.6 similar but highly applicable vs. 0.8 similar but irrelevant.

3. **H3:** Strategies are matched by embedding similarity, not by task applicability. Need task-type classification.

4. **H4:** Results are dumped without framing - agent doesn't know HOW to use them. Need actionable presentation.

5. **H5:** No feedback loop - system doesn't learn which retrieved content was actually useful. ReasoningBank records attempts but doesn't improve selection.

---

## Investigation Steps

1. [x] Analyze current query path: prompt -> embedding -> search -> results
2. [x] Examine strategy matching logic in ReasoningAwareRetrieval
3. [ ] Review what metadata exists for task-type classification
4. [x] Identify where "applicability" could be computed vs. pure similarity
5. [x] Research: How do RAG systems add contextual relevance? (Context7)
6. [ ] Prototype: Intent extraction from conversational prompts (E2-063)
7. [ ] Prototype: Task-type classification (debug/implement/review/plan) (E2-066)

---

## Findings

### Preliminary (Session 73)

**Current algorithm (memory_retrieval.py + retrieval.py):**
1. User prompt -> embed as-is
2. Search concepts table by cosine similarity
3. Search reasoning_traces for strategies by similarity
4. Return top-N above threshold
5. Format as TOON and inject

**Gap analysis:**
- No query preprocessing or intent extraction
- No task-type awareness
- Similarity is only ranking signal
- Strategies selected by pattern match, not applicability
- No feedback on what was useful

### External Research (Session 73 - Context7)

Researched RAG patterns from: nirdiamant/rag_techniques, sentence-transformers, LlamaIndex, dsRAG.

**Technique 1: Query Transformation**
- **Query Rewriting:** LLM reformulates conversational query to be more specific for retrieval
- **Step-back Prompting:** Generate broader context query alongside original
- **Sub-query Decomposition:** Break complex queries into 2-4 simpler sub-queries
- **Maps to H1:** Raw prompts ARE poor queries - industry solution is LLM preprocessing

**Technique 2: Two-Stage Retrieval (Bi-Encoder + Cross-Encoder)**
- Stage 1: Fast bi-encoder (embedding similarity) gets top-K candidates
- Stage 2: Cross-encoder reranks candidates with query-document pair scoring
- Cross-encoder is slower but more accurate (sees both query and doc together)
- **Maps to H2:** Pure similarity misses context - cross-encoder adds contextual relevance

**Technique 3: Contextual Retrieval**
- Incorporate user context into query reformulation
- LLM ranks document relevance considering user context
- dsRAG "AutoContext" adds contextual headers to chunks
- **Maps to H3:** Task-type could be user context for retrieval

**Technique 4: Feedback Loops**
- Collect relevance/quality ratings on retrieved content
- Adjust document relevance scores based on feedback
- Periodically fine-tune vector index with high-quality responses
- **Maps to H5:** Industry has established patterns for retrieval feedback

**Technique 5: Time-Weighted Reranking**
- LlamaIndex `TimeWeightedPostprocessor` with decay factor
- Recent content prioritized via exponential decay on timestamps
- **Already have:** ADR-037 modes, but not decay-based ranking

### Algorithm Options for HAIOS

| Option | Complexity | Impact | Addresses |
|--------|------------|--------|-----------|
| **A: Query Rewriting** | Low | High | H1 |
| **B: Cross-Encoder Rerank** | Medium | High | H2 |
| **C: Task-Type Classification** | Medium | Medium | H3, H4 |
| **D: Feedback Loop** | High | High | H5 |
| **E: Time-Decay Ranking** | Low | Medium | Recency bias |

**Recommended Sequence:**
1. **A (Query Rewriting)** - Highest ROI, one LLM call to improve query quality
2. **E (Time-Decay)** - Low effort, adds recency signal to existing similarity
3. **B (Cross-Encoder)** - Significant accuracy boost, requires model loading
4. **C (Task-Type)** - Enables "show me debugging strategies" queries
5. **D (Feedback)** - Long-term learning, needs UI/storage infrastructure

---

## Spawned Work Items

**From INV-014:**
- [ ] E2-060: Intent extraction preprocessing
- [ ] E2-061: Strategy quality audit

**From INV-015 (this investigation):**
- [ ] E2-063: Query Rewriting Layer (Option A) - LLM reformulates prompts before embedding
- [ ] E2-064: Time-Decay Ranking (Option E) - Add recency weighting to similarity scores
- [ ] E2-065: Cross-Encoder Reranking (Option B) - Two-stage retrieval with sentence-transformers
- [ ] E2-066: Task-Type Classification (Option C) - Classify queries for contextual retrieval
- [ ] E2-067: Retrieval Feedback Loop (Option D) - Store and learn from retrieval usefulness

---

## Expected Deliverables

- [x] Problem articulation (this document)
- [x] Algorithm design options (A/B/C/D/E analysis)
- [ ] Prototype of at least one improvement (E2-063 recommended first)
- [ ] ADR if architectural decision needed
- [ ] Memory storage of findings

---

## References

**HAIOS Internal:**
- INV-010: Memory Retrieval Architecture Mismatch (CLOSED)
- INV-014: Memory Context Injection Architecture
- ADR-037: Hybrid Retrieval Architecture
- `haios_etl/retrieval.py`: ReasoningAwareRetrieval class
- `.claude/hooks/memory_retrieval.py`: Hook implementation

**External Research (Context7):**
- nirdiamant/rag_techniques - Query transformations, feedback loops, contextual retrieval
- huggingface/sentence-transformers - Cross-encoder reranking patterns
- run-llama/llama_index - TimeWeightedPostprocessor, SentenceTransformerRerank
- d-star-ai/dsrag - AutoContext, Relevant Segment Extraction (RSE)

---
