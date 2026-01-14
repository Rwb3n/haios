---
template: implementation_plan
status: draft
date: 2025-12-14
backlog_id: ADR-037
title: "Hybrid Retrieval Architecture"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-14 13:11:33
# Implementation Plan: Hybrid Retrieval Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Implement hybrid retrieval architecture that combines semantic similarity with temporal weighting and metadata filtering to serve multiple use cases (session recovery, strategy injection, knowledge lookup, task context).

---

## Problem Statement

**From INV-010:** Memory retrieval returns philosophically-related content instead of task-relevant content. Coldstart needs "what was I working on?" but gets "what is HAIOS?"

**Root Causes:**
1. Pure semantic search with no temporal weighting
2. Synthesis concepts (98.6% of recent embeddings) crowd out specific content
3. One-size-fits-all retrieval serving different use cases
4. `filters` parameter exists but unused in SQL

---

## Methodology: AODEV TDD

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
              |          |
              v          v
           (Tests)   (Implementation)
```

Each phase writes tests BEFORE implementation. Red-Green-Refactor.

---

## Current State vs Desired State

### Current State

```python
# database.py:305 - Pure semantic, no filtering
def search_memories(self, query_vector, space_id=None, filters=None, limit=10):
    sql = """
        SELECT ... vec_distance_cosine(e.vector, ?) as distance
        ORDER BY distance ASC LIMIT ?
    """
    # filters parameter UNUSED
```

**Behavior:** Returns 10 most semantically similar results regardless of recency or type.

**Result:** Coldstart gets philosophy (0.84 score) instead of Session 70 work (0.64 score).

### Desired State

```python
# database.py - Hybrid retrieval with modes
def search_memories(self, query_vector, space_id=None, limit=10,
                    mode='semantic', recency_weight=0.0, concept_types=None):
    # Mode-specific SQL generation
    if mode == 'session_recovery':
        # Filter to recent, exclude synthesis, boost recency
    elif mode == 'knowledge_lookup':
        # Filter to episteme/techne, pure semantic
    # ...
```

**Behavior:** Caller specifies mode; retrieval adapts to use case.

**Result:** Coldstart with `mode='session_recovery'` returns Session 70 concepts 71291-71321.

---

## Tests First (TDD)

### Test 1: Mode Parameter Accepted
```python
def test_search_memories_accepts_mode():
    results = db.search_memories(vector, mode='session_recovery')
    assert results is not None  # No error thrown
```

### Test 2: Session Recovery Returns Recent Content
```python
def test_session_recovery_returns_recent():
    # Setup: Insert old concept (id=100) and recent concept (id=71300)
    results = db.search_memories(vector, mode='session_recovery')
    assert results[0]['id'] > 70000  # Recent content first
```

### Test 3: Session Recovery Excludes Synthesis
```python
def test_session_recovery_excludes_synthesis():
    results = db.search_memories(vector, mode='session_recovery')
    types = [r['type'] for r in results]
    assert 'SynthesizedInsight' not in types
```

### Test 4: Knowledge Lookup Filters to Episteme/Techne
```python
def test_knowledge_lookup_filters_types():
    results = db.search_memories(vector, mode='knowledge_lookup')
    types = [r['type'] for r in results]
    assert all(t in ['episteme', 'techne', 'Critique', 'Decision'] for t in types)
```

### Test 5: Semantic Mode Unchanged (Backward Compat)
```python
def test_semantic_mode_unchanged():
    results_new = db.search_memories(vector, mode='semantic')
    results_old = db.search_memories(vector)  # default
    assert results_new == results_old
```

### Test 6: MCP Tool Accepts Mode Parameter
```python
def test_mcp_accepts_mode():
    result = memory_search_with_experience("query", mode="session_recovery")
    assert 'error' not in result
```

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add tests 1-6 to `tests/test_database.py` and `tests/test_mcp.py`
- [ ] Verify all tests fail (red)

### Step 2: Implement Mode Parameter
- [ ] Add `mode` parameter to `search_memories()` signature
- [ ] Add `mode` parameter to `memory_search_with_experience()` MCP tool
- [ ] Test 1 and Test 5 pass (backward compat)

### Step 3: Implement Session Recovery Mode
- [ ] Add SQL filtering: `WHERE c.id > (SELECT MAX(id) - 100 FROM concepts)`
- [ ] Add type exclusion: `AND c.type != 'SynthesizedInsight'`
- [ ] Add recency scoring: `ORDER BY c.id DESC` (id as proxy for time)
- [ ] Tests 2-3 pass

### Step 4: Implement Knowledge Lookup Mode
- [ ] Add type filter: `WHERE c.type IN ('episteme', 'techne', ...)`
- [ ] Test 4 passes

### Step 5: Update Coldstart
- [ ] Change coldstart.md to use `mode='session_recovery'`
- [ ] Test 6 passes

### Step 6: Verify Integration
- [ ] Run full test suite
- [ ] Measure coldstart token usage before/after
- [ ] Document in ADR-037

---

## Verification

- [ ] All new tests pass (retrieval modes, scoring, filters)
- [ ] Existing tests still pass (backward compatibility)
- [ ] Coldstart token usage reduced (measure before/after)
- [ ] Session 70 content surfaces in session_recovery mode
- [ ] Documentation updated (ADR-037, CLAUDE.md, MCP docs)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing callers | High | Default mode=SEMANTIC preserves current behavior |
| Recency weighting too aggressive | Medium | Make weights configurable, tune empirically |
| Performance degradation | Medium | Benchmark before/after, optimize SQL if needed |
| Synthesis still dominates | Medium | type_boost parameter allows negative weights for synthesis |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] All traced files complete

---

## References

- **INV-010:** Memory Retrieval Architecture Mismatch (source investigation)
- **ADR-036:** PM Data Architecture (precedent for data architecture decisions)
- `haios_etl/database.py:305-371`: Current search_memories implementation
- `haios_etl/retrieval.py:76-154`: ReasoningAwareRetrieval class
- `haios_etl/mcp_server.py:43-64`: MCP tool wrapper

---
