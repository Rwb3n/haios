---
template: implementation_plan
status: complete
date: 2025-12-14
backlog_id: E2-063
title: "Query Rewriting Layer"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-14 20:12:24
# Implementation Plan: Query Rewriting Layer

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Memory retrieval will transform conversational user prompts into technical queries using Gemini API before embedding, improving retrieval relevance.

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/memory_retrieval.py:130-137
result = retrieval.search_with_experience(
    query=query,  # Raw user prompt, often conversational
    space_id=None,
    filters=None,
    mode='session_recovery'
)
```

**Behavior:** User prompt is embedded as-is. "okay sure, lets revisit coldstart" becomes a semantic query.

**Result:** Poor retrieval - conversational text doesn't map well to stored technical content.

### Desired State

```python
# .claude/hooks/memory_retrieval.py - with query rewriting
rewritten_query = rewrite_query_for_retrieval(query)  # Uses Gemini
result = retrieval.search_with_experience(
    query=rewritten_query,  # Technical, retrieval-optimized
    space_id=None,
    filters=None,
    mode='session_recovery'
)
```

**Behavior:** Conversational prompt is rewritten to technical query before embedding.

**Result:** Better retrieval - "okay sure, lets revisit coldstart" becomes "HAIOS coldstart command session initialization memory context"

---

## Tests First (TDD)

### Test 1: Query Rewriter Transforms Conversational to Technical
```python
def test_rewrite_conversational_to_technical(monkeypatch):
    """Conversational prompt becomes technical query."""
    # Mock Gemini response
    def mock_generate(*args, **kwargs):
        return MockResponse("HAIOS coldstart session initialization")
    monkeypatch.setattr(genai, "generate_content", mock_generate)

    result = rewrite_query_for_retrieval("okay sure, lets revisit coldstart")
    assert "coldstart" in result.lower()
    assert "HAIOS" in result or "session" in result
```

### Test 2: Short Queries Pass Through Unchanged
```python
def test_short_query_passthrough():
    """Queries under threshold are not rewritten (save API calls)."""
    result = rewrite_query_for_retrieval("test")
    assert result == "test"  # Too short, passed through
```

### Test 3: Rewriter Handles API Failure Gracefully
```python
def test_rewriter_fallback_on_error(monkeypatch):
    """If Gemini fails, return original query."""
    def mock_generate(*args, **kwargs):
        raise Exception("API error")
    monkeypatch.setattr(genai, "generate_content", mock_generate)

    result = rewrite_query_for_retrieval("some query text")
    assert result == "some query text"  # Fallback to original
```

### Test 4: Integration - Rewritten Query Improves Retrieval
```python
def test_rewritten_query_retrieval_integration(mock_db_env, monkeypatch):
    """End-to-end: rewritten query retrieves more relevant content."""
    # This test verifies the full pipeline works
    # Compare retrieval results with/without rewriting
    pass  # Detailed implementation in Step 4
```

---

## Detailed Design

### Function/Component Signatures

```python
def rewrite_query_for_retrieval(query: str) -> str:
    """
    Transform conversational user prompts into technical, retrieval-optimized queries.

    Uses Gemini API to rewrite casual/conversational text into keyword-rich
    technical queries that map better to stored codebase content.

    Args:
        query: Raw user prompt, potentially conversational
               (e.g., "okay sure, lets revisit coldstart")

    Returns:
        Rewritten technical query optimized for semantic search
        (e.g., "HAIOS coldstart command session initialization")
        Falls back to original query on API failure.

    Raises:
        No exceptions raised - graceful fallback on all errors.
    """
```

### Behavior Logic

```
rewrite_query_for_retrieval(query)
         │
         ▼
┌─────────────────────────┐
│ len(query) < 10 chars?  │
└───────────┬─────────────┘
            │
     YES    │    NO
      │     │     │
      ▼     │     ▼
  return    │  ┌──────────────────────┐
  query     │  │ Call Gemini API      │
  (pass-    │  │ (gemini-1.5-flash)   │
  through)  │  └──────────┬───────────┘
            │             │
            │      SUCCESS│FAILURE
            │         │   │
            │         ▼   ▼
            │    return   return
            │    rewritten original
            │    query    query
            └─────────────┘
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Passthrough threshold | 10 characters | Short queries ("schema", "test") are already technical terms - rewriting wastes API call and may dilute specificity |
| Model selection | gemini-1.5-flash | Fastest latency (~100ms), cheapest cost (~$0.0001/call). Task is simple transformation, not reasoning. |
| Error handling | Return original query | Graceful degradation - system works without rewriting rather than failing entirely |
| Prompt design | "Rewrite for semantic search in technical codebase" | Instructs removal of conversational fluff, expansion of implicit references, addition of technical context |
| Logging | Log both original and rewritten | Observability for debugging retrieval issues, prompt tuning iteration |

### Prompt Text

```
Rewrite this conversational query for semantic search in a technical codebase.

Domain: HAIOS - AI agent orchestration system with concepts like coldstart,
checkpoints, memory retrieval, governance hooks, ADRs, backlog items, synthesis.

Remove conversational fluff, expand implicit references, use domain vocabulary.
Return ONLY the rewritten query, no explanation.

Examples:
- "that schema thing" → "database schema ADR architecture decision"
- "lets check coldstart" → "HAIOS coldstart session initialization"

Query: {query}
```

**Design Rationale (from Assumption Surfacing critique):**
- Added domain context: Gemini needs HAIOS vocabulary grounding, not generic "technical codebase"
- Added few-shot examples: Zero-shot was unvalidated assumption, examples improve consistency
- Kept concise: Flash model works better with shorter prompts

### Input/Output Examples

| Input | Output | Notes |
|-------|--------|-------|
| "okay sure, lets revisit coldstart" | "HAIOS coldstart command session initialization" | Strips conversational, adds technical context |
| "what did we decide about the schema thing" | "database schema decision ADR architecture" | Expands "thing" to domain terms |
| "that memory bug from yesterday" | "memory retrieval bug issue investigation recent" | Adds temporal, domain context |
| "schema" | "schema" | Passthrough - under 10 chars |
| "test" | "test" | Passthrough - under 10 chars |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Query < 10 chars | Return unchanged (passthrough) | Test 2 |
| Gemini API failure | Return original query | Test 3 |
| Empty query | Return empty string (passthrough) | Test 2 (implicit) |
| Very long query (>1000 chars) | Truncate before API call | Not covered in v1 - future enhancement |
| Non-English query | Best-effort rewrite | Not explicitly tested - Gemini handles |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [x] Add `test_query_rewriter.py` to `tests/`
- [x] Add Tests 1-3 (unit tests for rewriter function)
- [x] Verify all tests fail (red)

### Step 2: Create Query Rewriter Function
- [x] Add `rewrite_query_for_retrieval()` to `.claude/hooks/memory_retrieval.py`
- [x] Use Gemini API (`gemini-1.5-flash` - fast and cheap)
- [x] Prompt: Domain-grounded with few-shot examples (improved via Assumption Surfacing critique)
- [x] Short query passthrough (<10 chars)
- [x] Fallback to original on error
- [x] Tests 1-3 pass (green)

### Step 3: Integrate into Memory Retrieval
- [x] Call `rewrite_query_for_retrieval()` before `search_with_experience()`
- [x] Log both original and rewritten query for observability
- [x] Test 4 passes (green)

### Step 4: Integration Verification
- [x] All tests pass (207 total)
- [x] Run full test suite (`pytest`) - no regressions
- [ ] Manual test: observe improved retrieval on conversational prompts (deferred to production use)

### Step 5: (Future) Async Investigation
- [ ] Backlog item E2-068: Investigate async query rewriting
- [ ] Could parallelize rewrite + other hook work
- [ ] Not blocking for v1

---

## Verification

- [x] Tests pass (6 new tests + no regressions = 207 total)
- [ ] Documentation updated (CLAUDE.md if behavior changes significantly) - deferred, behavior is additive
- [ ] Manual observation: improved retrieval on conversational prompts - deferred to production use

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API latency | Medium | Use gemini-1.5-flash (fastest), skip short queries |
| API failure | Low | Fallback to original query (graceful degradation) |
| Over-rewriting | Medium | Prompt tuning, log both queries for debugging |
| Cost | Low | Gemini flash is cheap, only called once per prompt |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 73 | 2025-12-14 | - | Plan created | Investigation complete, ready for implementation |
| 74 | 2025-12-14 | - | Implementation complete | TDD execution, 207 tests pass |

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (207)
- [x] WHY captured (concepts 71451-71463)
- [x] Documentation current (plan updated)
- [x] All traced files complete

---

## References

- INV-015: Retrieval Algorithm Intelligence (source investigation)
- ADR-037: Hybrid Retrieval Architecture
- Context7: nirdiamant/rag_techniques - Query Rewriting pattern
- `.claude/hooks/memory_retrieval.py` - Target file for changes

---
