---
template: implementation_plan
status: complete
date: 2025-12-20
backlog_id: E2-FIX-004
title: "Fix Synthesis Query Ordering Bug"
author: Hephaestus
lifecycle_phase: plan
session: 88
spawned_by: INV-019
related: [PLAN-SYNTHESIS-001, E2-FIX-001]
milestone: M3-Cycles
version: "1.2"
---
# generated: 2025-12-20
# System Auto: last updated on: 2025-12-20 10:49:55
# Implementation Plan: Fix Synthesis Query Ordering Bug

@docs/README.md
@haios_etl/synthesis.py
@docs/investigations/INVESTIGATION-INV-019-synthesis-coverage-gap-query-ordering-bug.md

---

## Goal

Synthesis will process ALL concepts with embeddings (not just 1-10k), enabling full memory consolidation coverage.

---

## Current State vs Desired State

### Current State

```python
# haios_etl/synthesis.py:109-116
sql = """
    SELECT c.id, c.content, e.vector
    FROM concepts c
    JOIN embeddings e ON c.id = e.concept_id
    WHERE c.synthesized_at IS NULL
    ORDER BY c.id
    LIMIT ?
"""
```

**Behavior:** Query always picks lowest IDs first. With LIMIT 1000, synthesis only ever processes concepts 1-1000.

**Result:**
- 99.6% of clustering happens in concepts 1-10,000
- Concepts 60,000+ have 0% synthesis coverage
- 53,000 ancient concepts never processed

### Desired State

```python
# haios_etl/synthesis.py:109-116 - Option A (Minimal)
sql = """
    SELECT c.id, c.content, e.vector
    FROM concepts c
    JOIN embeddings e ON c.id = e.concept_id
    WHERE c.synthesized_at IS NULL
      AND c.synthesis_cluster_id IS NULL
    ORDER BY c.id
    LIMIT ?
"""
```

**Behavior:** Query excludes already-clustered concepts, making progress through the full concept space.

**Result:**
- Each synthesis run processes NEW concepts
- Eventually covers all 72k concepts
- Concepts 60k+ start getting synthesized

---

## Tests First (TDD)

### Test 1: Query Excludes Already-Clustered Concepts
```python
def test_find_similar_concepts_excludes_clustered(db_manager, synthesis_manager):
    """Concepts with synthesis_cluster_id set should be excluded."""
    # Setup: Create 3 concepts, mark 1 as clustered
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    for i in range(3):
        cursor.execute("INSERT INTO concepts (type, content) VALUES (?, ?)",
                      ('Directive', f'Test concept {i}'))
        concept_id = cursor.lastrowid
        # Add embedding
        embedding = [0.1] * 768
        cursor.execute("INSERT INTO embeddings (concept_id, vector, model, dimensions) VALUES (?, ?, ?, ?)",
                      (concept_id, struct.pack(f'{768}f', *embedding), 'test', 768))

    # Mark first concept as clustered
    cursor.execute("UPDATE concepts SET synthesis_cluster_id = 999 WHERE id = 1")
    conn.commit()

    # Action
    clusters = synthesis_manager.find_similar_concepts(limit=10)

    # Assert: Clustered concept should not be in any cluster
    all_member_ids = [m for c in clusters for m in c.member_ids]
    assert 1 not in all_member_ids
```

### Test 2: Progress Through ID Space
```python
def test_synthesis_progresses_through_id_space(synthesis_manager):
    """Repeated synthesis runs should process different concepts."""
    # Run 1
    clusters_1 = synthesis_manager.find_similar_concepts(limit=100)
    ids_1 = set(m for c in clusters_1 for m in c.member_ids)

    # Simulate marking as clustered (what store_synthesis does)
    # ... (mark ids_1 with cluster_id)

    # Run 2
    clusters_2 = synthesis_manager.find_similar_concepts(limit=100)
    ids_2 = set(m for c in clusters_2 for m in c.member_ids)

    # Assert: No overlap between runs
    assert ids_1.isdisjoint(ids_2), "Second run should process different concepts"
```

### Test 3: Backward Compatibility - Existing Behavior Preserved
```python
def test_find_similar_concepts_still_respects_limit(synthesis_manager):
    """LIMIT parameter should still work correctly."""
    clusters = synthesis_manager.find_similar_concepts(limit=5)
    total_members = sum(c.member_count for c in clusters)
    assert total_members <= 5  # Respects limit
```

---

## Detailed Design

### Function Signature (No Change)

```python
def find_similar_concepts(self, limit: int = 1000) -> List[ClusterInfo]:
    """
    Group concepts by vector similarity.

    Now excludes concepts that already have synthesis_cluster_id set,
    ensuring progress through the full concept space.
    """
```

### Behavior Logic

**Current Flow (Buggy):**
```
find_similar_concepts(limit=1000)
    |
    v
Query: WHERE synthesized_at IS NULL   <-- CHECKS synthesized_at
       ORDER BY c.id LIMIT 1000
    |
    v
Returns concepts 1-1000 (same every run)
    |
    v
_build_clusters(rows)
    |
    +---> In-memory `clustered = set()` tracks THIS RUN only
    |     Greedy: for each item, find similar (>0.85 cosine)
    |     Create cluster if 2+ members, max 20
    |
    v
For each cluster -> synthesize_cluster() -> store_synthesis()
    |
    v
store_synthesis():
    - Creates new SynthesizedInsight (synthesized_at = now())
    - Line 474-478: UPDATE source concepts SET synthesis_cluster_id = X
                                                    ^^^^^^^^^^^^^^^^^
                                                    SETS DIFFERENT COLUMN!
```

**The Mismatch (Root Cause):**
```
Query filters on:     synthesized_at IS NULL
But store sets:       synthesis_cluster_id = X

Result: 6,765 concepts have cluster_id but STILL have synthesized_at = NULL
        They pass the filter and get re-selected forever!
```

**Evidence from database:**
| cluster_status | synth_status | count |
|----------------|--------------|-------|
| has_cluster_id | no_synth_at | 6,765 |
| no_cluster_id | no_synth_at | 56,869 |

**Fixed Flow:**
```
find_similar_concepts(limit=1000)
    |
    v
Query: WHERE synthesized_at IS NULL
         AND synthesis_cluster_id IS NULL   <-- ALIGN WITH WHAT STORE SETS
       ORDER BY c.id LIMIT 1000
    |
    v
Returns UNCLUSTERED concepts (progresses through ID space)
    |
    v
[rest of flow unchanged]
```

### Exact Code Change

**File:** `haios_etl/synthesis.py`
**Location:** Lines 109-116 in `find_similar_concepts()`

**Current Code:**
```python
# haios_etl/synthesis.py:108-117
        # Get concepts with embeddings that haven't been synthesized
        sql = """
            SELECT c.id, c.content, e.vector
            FROM concepts c
            JOIN embeddings e ON c.id = e.concept_id
            WHERE c.synthesized_at IS NULL
            ORDER BY c.id
            LIMIT ?
        """
```

**Changed Code:**
```python
# haios_etl/synthesis.py:108-118
        # Get concepts with embeddings that haven't been clustered
        sql = """
            SELECT c.id, c.content, e.vector
            FROM concepts c
            JOIN embeddings e ON c.id = e.concept_id
            WHERE c.synthesized_at IS NULL
              AND c.synthesis_cluster_id IS NULL
            ORDER BY c.id
            LIMIT ?
        """
```

**Diff:**
```diff
         # Get concepts with embeddings that haven't been synthesized
+        # Get concepts with embeddings that haven't been clustered
         sql = """
             SELECT c.id, c.content, e.vector
             FROM concepts c
             JOIN embeddings e ON c.id = e.concept_id
             WHERE c.synthesized_at IS NULL
+              AND c.synthesis_cluster_id IS NULL
             ORDER BY c.id
             LIMIT ?
         """
```

### Call Chain Context

```
run_synthesis_pipeline(limit=1000)           # cli.py or orchestration
    |
    +-> find_similar_concepts(limit=1000)    # THIS FUNCTION (synthesis.py:92)
    |       Returns: List[ClusterInfo]
    |
    +-> for cluster in clusters:
    |       synthesize_cluster(cluster)      # LLM call
    |       store_synthesis(result)          # DB write, sets synthesis_cluster_id
    |
    +-> find_similar_traces(limit=100)       # Similar pattern for traces
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Filter mechanism | `synthesis_cluster_id IS NULL` | Already tracked by store_synthesis (line 474-478), no new columns needed |
| Keep ORDER BY id | Yes | Deterministic, easy to reason about progress |
| No schema changes | Yes | synthesis_cluster_id already exists and is being set |
| Keep synthesized_at check | Yes | Belt-and-suspenders, doesn't hurt |

### Input/Output Examples

**Before Fix (Current Behavior):**
```
Run 1: find_similar_concepts(limit=1000)
  Query returns: concepts 1-1000
  Clusters: [1,5,12], [2,8], [3,15,22], ...
  store_synthesis sets cluster_id on: 1,5,12,2,8,3,15,22,...

Run 2: find_similar_concepts(limit=1000)
  Query returns: concepts 1-1000 AGAIN (synthesized_at still NULL!)
  Same concepts, same results, no progress
```

**After Fix:**
```
Run 1: find_similar_concepts(limit=1000)
  Query returns: concepts 1-1000 (all have cluster_id = NULL)
  Clusters formed, store_synthesis sets cluster_id on clustered ones

Run 2: find_similar_concepts(limit=1000)
  Query returns: concepts that still have cluster_id = NULL
  If 200 were clustered in Run 1, returns 201-1200
  PROGRESS!
```

**Real Example with Current Data:**
```
Current state:
  - Concepts 1-6765: have synthesis_cluster_id (already clustered)
  - Concepts 6766-72731: have synthesis_cluster_id = NULL

After fix, first run with limit=1000:
  Query will return concepts 6766-7765 (first 1000 unclustered)
  These are concepts that have NEVER been considered for clustering!
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| All concepts already clustered | Returns empty list | Implicit in Test 1 |
| Mixed clustered/unclustered | Only unclustered returned | Test 1 |
| LIMIT > remaining unclustered | Returns what's available | Test 3 |
| Concept clusters but doesn't form group | cluster_id set to placeholder? | Need to verify |

### Open Question

**Q: What happens to concepts that are CONSIDERED but don't form clusters (singletons)?**

Looking at code (lines 231-239):
```python
# Only keep clusters with minimum size
if len(cluster_members) >= self.MIN_CLUSTER_SIZE:
    clusters.append(...)
```

Singletons are NOT added to clusters, so they don't get `synthesis_cluster_id` set.
They will be re-considered next run. This is **correct behavior** - maybe they'll cluster with new concepts later.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_synthesis.py`
- [ ] Run `pytest tests/test_synthesis.py -v` - verify new tests fail

### Step 2: Modify Query (2 lines)
- [ ] Edit `haios_etl/synthesis.py:109-116`
- [ ] Add `AND c.synthesis_cluster_id IS NULL` to WHERE clause
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Integration Verification
- [ ] Run `pytest tests/test_synthesis.py -v` - all pass
- [ ] Run `pytest` - no regressions
- [ ] Run test synthesis: `python -m haios_etl.cli synthesis run --dry-run --limit 100`

### Step 4: Live Test (Optional)
- [ ] Run actual synthesis with small limit: `python -m haios_etl.cli synthesis run --limit 5000 --skip-cross`
- [ ] Verify new concepts are being processed (check IDs > 10000)

---

## Verification

- [ ] Tests pass
- [ ] Documentation updated (this plan)
- [ ] Dry-run shows progress into new ID ranges

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaks existing synthesis | Medium | Test 3 ensures backward compatibility |
| Performance regression | Low | Same query complexity, just different filter |
| Unexpected clustering quality | Low | Run with small LIMIT first, verify quality |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 88 | 2025-12-20 | - | Plan created | INV-019 investigation complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `haios_etl/synthesis.py` | Line 117 has `AND c.synthesis_cluster_id IS NULL` | [x] | Verified |
| `tests/test_synthesis.py` | Tests for cluster exclusion exist (TestSynthesisQueryProgress) | [x] | 4 new tests |

**Verification Commands:**
```bash
# Actual output from verification
pytest tests/test_synthesis.py -v
# Result: 41 passed in 13.23s (including 4 new E2-FIX-004 tests)

# Database verification after fix:
# Eligible concepts by range:
#   0-10k:    3,217 (singletons)
#   10k-60k: 49,286 (NEVER PROCESSED BEFORE)
#   60k+:     1,042 (recent concepts)
# Total: 53,545 concepts now reachable
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | synthesis.py line 117, test_synthesis.py line 228-408 |
| Test output pasted above? | Yes | 41 passed |
| Any deviations from plan? | No | Implemented as planned |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (41/41)
- [x] WHY captured (concepts 72741-72748)
- [x] Documentation current (plan updated)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- INV-019: Synthesis Coverage Gap Investigation
- PLAN-SYNTHESIS-001-memory-consolidation.md
- E2-FIX-001: Synthesis Embedding Gap (related prior fix)
- Session 88 introspection (this session)

---
