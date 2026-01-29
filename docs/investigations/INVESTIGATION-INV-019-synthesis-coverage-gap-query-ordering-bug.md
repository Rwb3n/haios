---
template: investigation
status: complete
date: 2025-12-20
backlog_id: null
title: 'Investigation: Synthesis Coverage Gap - Query Ordering Bug'
author: Hephaestus
session: 88
lifecycle_phase: discovery
related:
- PLAN-SYNTHESIS-001
- E2-FIX-001
milestone: M3-Cycles
memory_refs: []
version: '1.1'
generated: '2026-01-25'
last_updated: '2026-01-25T22:07:04'
---
# Investigation: Synthesis Coverage Gap - Query Ordering Bug

@docs/README.md
@docs/epistemic_state.md
@haios_etl/synthesis.py

---

## Context

During Session 88 introspection on memory system health, discovered that synthesis is only covering 11% of ancient memory (concepts 1-60k), and 0% of recent memory (60k+). This affects retrieval quality because SynthesizedInsights dominate search results but represent only a fraction of the knowledge base.

**Related prior work:**
- PLAN-SYNTHESIS-001-memory-consolidation.md (original synthesis design)
- 2025-11-30-EVALUATION-synthesis-pipeline.md (evaluation report)
- E2-FIX-001: Synthesis embedding gap (fixed embeddings, not coverage)

---

## Objective

1. Identify root cause of low synthesis coverage
2. Determine if this is a bug or intentional design
3. Propose fix if bug confirmed
4. Estimate cost/effort of full synthesis coverage

---

## Scope

### In Scope
- Synthesis query logic (synthesis.py)
- Clustering coverage analysis
- Recent concepts (60k+) synthesis gap

### Out of Scope
- Cross-pollination performance (separate issue, E2-102 addresses with --skip-cross)
- Epoch 3 memory-v2 design

---

## Hypotheses

1. **H1 (PRIMARY):** Query ordering bug - `ORDER BY id ASC LIMIT 1000` always picks lowest IDs, never reaching concepts 60k+
2. **H2:** Progress tracking bug - `synthesized_at` not set on source concepts, causing re-processing
3. **H3:** Threshold issue - 85% similarity too strict for diverse concepts
4. **H4 (NULL):** Intentional design - synthesis was meant to be "best effort" on recent concepts only

---

## Investigation Steps

1. [x] Query concept distribution across ID ranges
2. [x] Analyze synthesis_cluster_members to find which concepts are clustered
3. [x] Read synthesis.py to understand query logic
4. [x] Check if `synthesized_at` is being set correctly
5. [x] Verify embedding coverage for recent concepts
6. [x] Apply Systematic Reasoner framework for rigorous analysis

---

## Findings

### The Data

| Metric | Value |
|--------|-------|
| Total concepts | 72,474 |
| Ancient (1-60k) | 60,000 |
| Recent (60k+) | 12,732 |
| Synthesized (SynthesizedInsight type) | 9,093 |
| Unique sources used in synthesis | 6,767 |
| **Coverage of ancient** | **11.3%** |
| **Coverage of recent** | **0%** |

### Clustering Distribution by ID Range

| Range | Clustered Count | % of Range |
|-------|-----------------|------------|
| 1-1000 | 728 | 73% |
| 1001-5000 | 2,652 | 66% |
| 5001-10000 | 3,358 | 67% |
| 10001-30000 | 29 | 0.15% |
| 30001-60000 | 1 | 0.002% |
| 60000+ | 0 | 0% |

**99.6% of all clustering happens in concepts 1-10,000.**

### Root Cause Identified

**synthesis.py:109-116:**
```python
sql = """
    SELECT c.id, c.content, e.vector
    FROM concepts c
    JOIN embeddings e ON c.id = e.concept_id
    WHERE c.synthesized_at IS NULL
    ORDER BY c.id
    LIMIT ?
"""
```

**Two bugs:**

1. **ORDER BY c.id ASC** - Always picks lowest IDs first. With LIMIT 1000 (default), synthesis never reaches concepts beyond ~10k, and NEVER reaches 60k+.

2. **Progress not persisted** - The query checks `synthesized_at IS NULL`, but line 471-478 only sets `synthesis_cluster_id`, NOT `synthesized_at`. This causes:
   - Same concepts re-eligible every run
   - But the in-memory `clustered` set prevents re-clustering within a single run
   - Net effect: marginal progress on each run, but very slow

### Verification

Recent concepts DO have embeddings:
```
concepts 60000-60019: ALL have embeddings, ALL have synthesized_at = NULL
```

They are eligible for synthesis but never selected due to ORDER BY id ASC.

### H1 CONFIRMED, H2 CONFIRMED, H3 REJECTED, H4 REJECTED

- H1: Query ordering bug - **CONFIRMED** (ORDER BY id never reaches 60k+)
- H2: Progress tracking - **CONFIRMED** (synthesized_at not set)
- H3: Threshold - REJECTED (clustering IS happening in 1-10k range at ~70% rate)
- H4: Intentional - REJECTED (LIMIT is parameterized, suggesting intended scalability)

---

## Proposed Fix

### Option A: Minimal Fix (RECOMMENDED)

1. Change query to exclude already-clustered concepts:
```python
WHERE c.synthesized_at IS NULL
  AND c.synthesis_cluster_id IS NULL
ORDER BY c.id
```

2. Or use RANDOM ordering for fair sampling:
```python
ORDER BY RANDOM()
```

### Option B: Full Fix

1. Set `synthesized_at` on source concepts after clustering
2. Add progress tracking (last_processed_id)
3. Add CLI option for target ID range

### Cost Estimate

- ~53,000 unclustered ancient concepts
- ~3,500 unclustered recent concepts (non-SynthesizedInsight)
- At 85% threshold, expect ~30% to form clusters
- Estimated ~17,000 new clusters = ~17,000 LLM calls
- At ~$0.001/call (Gemini Flash) = ~$17
- Runtime: ~3-5 hours at 1 cluster/second

---

## Spawned Work Items

- [ ] E2-FIX-004: Fix synthesis query ordering bug
- [ ] E2-107: Full synthesis run after fix (optional, can defer)

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Recommendations (Option A minimal fix)
- [ ] Memory storage (store findings after review)

---

## Decision Required

**Operator decision needed:**

1. **Fix now (E2-FIX-004):** Minimal effort, enables future synthesis runs to cover more memory
2. **Defer to Epoch 3:** Memory-v2 redesign may make this moot

**Recommendation:** Fix now. The fix is 2-3 lines of code, low risk, and enables incremental improvement while Epoch 3 develops.

---

## References

- `haios_etl/synthesis.py:109-116` - The buggy query
- `haios_etl/synthesis.py:471-478` - Progress tracking gap
- PLAN-SYNTHESIS-001-memory-consolidation.md
- 2025-11-30-EVALUATION-synthesis-pipeline.md
- Session 88 introspection (this session)

---
