---
template: investigation
status: complete
date: 2025-12-14
backlog_id: INV-010
title: "Investigation: Memory Retrieval Architecture Mismatch"
author: Hephaestus
lifecycle_phase: discovery
version: "1.0"
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-14 13:27:57
# Investigation: Memory Retrieval Architecture Mismatch

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 71 coldstart consumed ~60k tokens. After reducing PM bloat (ADR-036), memory injection via `memory_search_with_experience` is now the dominant context consumer.

Initial observation: The memory system returns verbose results that are semantically related but not task-relevant. Coldstart needs "what was I working on?" but gets "philosophical concepts about what HAIOS is."

---

## Objective

Determine why memory retrieval fails to surface recent, actionable context and identify architectural changes to align retrieval with use-case needs.

---

## Scope

### In Scope
- Coldstart memory query effectiveness
- Retrieval algorithm (semantic similarity vs temporal/task relevance)
- TOON encoding efficiency
- Query formulation patterns
- Connection to INV-003 (strategy quality)

### Out of Scope
- Storage/ingestion architecture (separate concern)
- Memory MCP server implementation details
- Synthesis algorithm changes

---

## Hypotheses

1. **H1:** Static query formulation - Coldstart uses hardcoded "HAIOS session context initialization" regardless of recent work
2. **H2:** Semantic similarity bias - Embedding similarity favors philosophical/synthesized concepts over specific/recent ones
3. **H3:** No temporal weighting - Retrieval algorithm doesn't factor recency
4. **H4:** Synthesis dilution - Synthesis creates generic concepts that outrank specific session content
5. **H5:** Query-use case mismatch - Different use cases need different retrieval modes (session-recovery vs knowledge-lookup)

---

## Investigation Steps

### Initial Recon (Session 71 - COMPLETE)

1. [x] Examine coldstart.md query formulation
2. [x] Run memory stats to verify data exists
3. [x] Test specific query ("Session 70 work items E2-041...")
4. [x] Compare relevance scores between generic and specific queries

### Deep Investigation (Session 72 - COMPLETE)

5. [x] Analyze retrieval code (`haios_etl/mcp_server.py` search implementation)
6. [x] Examine embedding similarity distribution for recent vs old concepts
7. [x] Test temporal weighting hypothesis with date-bounded queries
8. [x] Evaluate TOON encoding overhead vs compression benefit
9. [x] Map use cases to retrieval requirements

---

## Findings

### Initial Recon Results (Session 71)

**Evidence 1: Static Query**
```markdown
# From coldstart.md line 19:
Query `mcp__haios-memory__memory_search_with_experience` with query "HAIOS session context initialization"
```
Hardcoded, doesn't adapt to session context.

**Evidence 2: Specific Query Failure**
Query: "Session 70 work items E2-041 E2-042 E2-043 E2-044"

| Rank | Score | Content |
|------|-------|---------|
| 1 | 0.64 | "comprehensive list of protocols from this session" (generic) |
| 2 | 0.64 | "Add Session 17 implementation status" (wrong session) |
| 3 | 0.64 | "Implementing Task T2" (irrelevant) |

Session 70 content (concepts 71291-71321 stored yesterday) **not in top 10**.

**Evidence 3: Score Comparison**

| Query Type | Top Score |
|------------|-----------|
| Generic "HAIOS session context initialization" | 0.84 |
| Specific "Session 70 work items E2-041..." | 0.64 |

Generic philosophical queries score HIGHER than specific actionable queries.

**Evidence 4: Memory Volume**
- 71,322 concepts stored
- 1,164 reasoning traces
- Data EXISTS but retrieval doesn't surface it

### Confirmed Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| H1: Static query | **CONFIRMED** | coldstart.md line 19 |
| H2: Semantic bias | **CONFIRMED** | 0.64 vs 0.84 scores |
| H3: No temporal weighting | **CONFIRMED** | database.py:305-371 - pure vector search |
| H4: Synthesis dilution | **CONFIRMED** | 98.6% of this_week embeddings are SynthesizedInsight |
| H5: Query-use case mismatch | **CONFIRMED** | Different use cases need different retrieval modes |

### Information Architecture Principle Violated

**Relevance is context-dependent.** The memory system optimizes for semantic similarity (what matches the query) but coldstart needs temporal recency + actionability (what's relevant to resuming work).

---

## Deep Investigation Findings (Session 72)

### Finding 1: Retrieval Architecture is Pure Semantic

Code path: `mcp_server.py:55` → `retrieval.py:106` → `database.py:305`

```python
# database.py:322-350 - NO temporal weighting
sql = """
    SELECT id, type, content, source, distance FROM (
        -- Concept embeddings
        SELECT c.id, 'concept' as type, c.content, c.source_adr as source,
               vec_distance_cosine(e.vector, ?) as distance
        FROM embeddings e JOIN concepts c ON e.concept_id = c.id
    )
    ORDER BY distance ASC
    LIMIT ?
"""
```

Key issues:
- `filters` parameter exists in function signature but **NOT USED** in SQL
- Strategy learning records traces but **TODO not implemented** (retrieval.py:103-105)
- No date filtering, no recency boost, no concept type filtering

### Finding 2: Embedding Distribution is Heavily Skewed

| Age Bucket | Embeddings | Percentage |
|------------|------------|------------|
| oldest (<50000) | 49,484 | 73% |
| older (50000-64999) | 12,486 | 18% |
| this_week (65000-70999) | 5,848 | 9% |
| **recent (71000+)** | **371** | **0.5%** |

Recent session content is 0.5% of the embedding space. Semantic search statistically favors the 99.5% older content.

### Finding 3: Synthesis Dominates Recent Embeddings

| Age | Dominant Type | Count | Insight |
|-----|---------------|-------|---------|
| older | Critique, Directive, Proposal | 54,436 | Extracted from documents |
| this_week | **SynthesizedInsight** | **5,764 (98.6%)** | Synthesis dominates |
| recent | SynthesizedInsight | 216 (58%) | Still mostly synthesis |

SynthesizedInsight concepts are abstract, cross-topic summaries - semantically "central" to everything. They score high on ANY query, crowding out specific session content.

### Finding 4: Specific Content EXISTS but Doesn't Surface

Session 70 concepts 71291-71321 contain exactly what coldstart needs:
- `71291`: "PROBLEM: haios-status.json bloated to 1,365 lines..."
- `71294`: "DECISION: Remove cached indexes..."
- `71296`: "SPAWNED WORK: E2-041, E2-042..."

These ARE stored. They just can't compete with synthesis concepts semantically.

### Finding 5: TOON Encoding is NOT the Bottleneck

TOON provides 57% token reduction (benchmark: 3810 → 1617 tokens). The problem isn't encoding efficiency - it's retrieving **the wrong 10 results**. TOON efficiently compresses irrelevant content.

### Finding 6: Use Case Requirements Matrix

| Use Case | Trigger | Query Need | Current | Required |
|----------|---------|------------|---------|----------|
| Session Recovery | `/coldstart` | "What was I working on?" | Returns philosophy | Recent session-specific |
| Strategy Injection | `UserPromptSubmit` | "What strategies worked?" | Works reasonably | Keep as-is |
| Knowledge Lookup | Operator question | "How does X work?" | Returns generic | Filter to episteme/techne |
| Task Context | Mid-session | "What's E2-041 about?" | Returns wrong sessions | Filter by source_path/ID |

**Conclusion:** One-size-fits-all semantic search cannot serve multiple use cases. The architecture needs **retrieval modes**.

---

## Recommendations

### Option A: Extend Current Architecture (Incremental)

**What:** Add retrieval modes to existing `search_memories()` function.

```python
def search_memories(self, query_vector, space_id=None, filters=None, limit=10,
                    mode='semantic', recency_weight=0.0, concept_types=None):
    # mode: 'semantic' (current), 'session_recovery', 'knowledge_lookup'
    # recency_weight: 0.0 (pure semantic) to 1.0 (pure recency)
    # concept_types: filter to specific types (e.g., ['Critique', 'Decision'])
```

**Pros:** Minimal disruption, incremental improvement
**Cons:** Doesn't fix underlying semantic bias, band-aid approach

### Option B: Hybrid Retrieval Architecture (Recommended)

**What:** Implement true hybrid retrieval combining semantic + temporal + metadata filtering.

1. **Retrieval modes** as first-class concept:
   - `session_recovery`: Filter to last 100 concepts, boost by recency
   - `strategy_injection`: Current behavior (works for strategies)
   - `knowledge_lookup`: Filter to episteme/techne, exclude synthesis
   - `task_context`: Filter by source_path pattern matching

2. **Scoring formula:**
   ```
   final_score = (semantic_similarity * semantic_weight) +
                 (recency_score * recency_weight) +
                 (type_boost * type_weight)
   ```

3. **Caller specifies mode** - coldstart uses `session_recovery`, UserPromptSubmit uses `strategy_injection`

**Pros:** Addresses root cause, scalable to future use cases
**Cons:** Moderate implementation effort, requires API changes

### Option C: Replace with RAG Library (Architectural)

**What:** Replace custom retrieval with established RAG library (LangChain, LlamaIndex, Haystack).

**Pros:** Mature tooling, community support, pre-built temporal/metadata filtering
**Cons:** Learning curve, potential lock-in, may not fit HAIOS-specific needs

### Recommendation

**Option B (Hybrid Retrieval)** is recommended. The problem is well-understood, the solution is tractable, and it preserves HAIOS's custom architecture while adding the missing capability.

Option C should be evaluated if Option B proves insufficient after implementation.

---

## Spawned Work Items

Based on deep investigation:

- [ ] E2-045: Dynamic coldstart query (use checkpoint content to formulate query)
- [ ] E2-046: Implement retrieval modes (session-recovery, knowledge-lookup, strategy-injection)
- [ ] E2-047: Add temporal weighting to search_memories scoring
- [ ] E2-057: Add concept_type filtering to search_memories
- [ ] E2-058: Implement mode parameter in memory_search_with_experience MCP tool
- [ ] ADR-037: Memory Retrieval Architecture (formalize Option B design)

---

## Expected Deliverables

- [x] Initial recon report (Session 71)
- [x] Deep investigation findings (Session 72)
- [x] Recommendations for retrieval architecture (Option A/B/C with recommendation)
- [x] Memory storage (concepts from investigations)
- [x] Use case requirements matrix

---

## References

- INV-003: Strategy quality improvement (related - content quality vs retrieval quality)
- ADR-036: PM Data Architecture (precedent for data architecture decisions)
- `haios_etl/mcp_server.py:43-64`: MCP tool wrapper
- `haios_etl/retrieval.py:76-154`: ReasoningAwareRetrieval search_with_experience
- `haios_etl/retrieval.py:103-105`: TODO - strategy parameters not applied
- `haios_etl/database.py:305-371`: search_memories - pure vector search
- `.claude/commands/coldstart.md:19`: Static query formulation
- `docs/reports/2025-12-04-REPORT-toon-serializer.md`: TOON efficiency validation

---
