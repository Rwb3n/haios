---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-253
title: MemoryBridge MCP Integration Implementation
author: Hephaestus
lifecycle_phase: plan
session: 165
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T10:17:38'
---
# Implementation Plan: MemoryBridge MCP Integration Implementation

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

MemoryBridge will have a functional `_call_mcp()` implementation that wraps haios_etl modules directly, enabling query and store operations without raising NotImplementedError, with optional query rewriting support.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | memory_bridge.py, cli.py, test_memory_bridge.py |
| Lines of code affected | ~206 | memory_bridge.py is 206 lines |
| New files to create | 0 | Editing existing files |
| Tests to write | 7 | 4 unit + 2 rewriting + 1 integration |
| Dependencies | 3 | haios_etl.database, extraction, retrieval |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Wraps haios_etl modules |
| Risk of regression | Low | Existing tests mock _call_mcp |
| External dependencies | Medium | GOOGLE_API_KEY required for rewriting |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Core _call_mcp | 30 min | High |
| Phase 2: Query rewriting | 20 min | High |
| Phase 3: Integration | 15 min | Medium |
| **Total** | ~65 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/memory_bridge.py:196-205
def _call_mcp(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call MCP tool. Subclasses can override for different backends.

    For MVP, this is a placeholder that will be replaced with actual
    MCP client integration or mocked in tests.
    """
    # MVP: Import and call the actual MCP server functions
    # This allows unit tests to mock _call_mcp while integration tests use real MCP
    raise NotImplementedError("Override _call_mcp or use MCPMemoryBridge subclass")
```

**Behavior:** `_call_mcp()` raises NotImplementedError for all calls

**Result:** MemoryBridge cannot be used in production - only mockable in tests

### Desired State

```python
# .claude/haios/modules/memory_bridge.py:196-230
def _call_mcp(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute memory operation by wrapping haios_etl modules."""
    if tool_name == "memory_search_with_experience":
        return self._search_with_experience(params)
    elif tool_name == "ingester_ingest":
        return self._ingest(params)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def _search_with_experience(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute search via ReasoningAwareRetrieval."""
    # Implementation wraps haios_etl.retrieval
    ...

def _ingest(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ingest operation."""
    # Implementation wraps haios_etl.ingester
    ...
```

**Behavior:** `_call_mcp()` dispatches to haios_etl modules

**Result:** MemoryBridge is functional for query() and store() operations

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: _call_mcp dispatches to search
```python
def test_call_mcp_search_dispatches_correctly():
    """_call_mcp with memory_search_with_experience calls _search_with_experience."""
    bridge = MemoryBridge()
    bridge._search_with_experience = Mock(return_value={"results": [], "reasoning": {}})
    bridge._call_mcp("memory_search_with_experience", {"query": "test"})
    bridge._search_with_experience.assert_called_once_with({"query": "test"})
```

### Test 2: _call_mcp dispatches to ingest
```python
def test_call_mcp_ingest_dispatches_correctly():
    """_call_mcp with ingester_ingest calls _ingest."""
    bridge = MemoryBridge()
    bridge._ingest = Mock(return_value={"concept_ids": [], "classification": "unknown"})
    bridge._call_mcp("ingester_ingest", {"content": "test", "source_path": "test.md"})
    bridge._ingest.assert_called_once()
```

### Test 3: _call_mcp unknown tool raises ValueError
```python
def test_call_mcp_unknown_tool_raises():
    """_call_mcp with unknown tool raises ValueError."""
    bridge = MemoryBridge()
    with pytest.raises(ValueError, match="Unknown tool"):
        bridge._call_mcp("nonexistent_tool", {})
```

### Test 4: query applies rewriting when enabled
```python
def test_query_applies_rewriting_when_enabled():
    """query() applies rewriting when enable_rewriting=True."""
    bridge = MemoryBridge(enable_rewriting=True)
    bridge._rewrite_query = Mock(return_value="rewritten")
    bridge._call_mcp = Mock(return_value={"results": [], "reasoning": {}})
    bridge.query("original query")
    bridge._rewrite_query.assert_called_once_with("original query")
```

### Test 5: query skips rewriting when disabled
```python
def test_query_skips_rewriting_when_disabled():
    """query() skips rewriting when enable_rewriting=False."""
    bridge = MemoryBridge(enable_rewriting=False)
    bridge._rewrite_query = Mock()
    bridge._call_mcp = Mock(return_value={"results": [], "reasoning": {}})
    bridge.query("original query")
    bridge._rewrite_query.assert_not_called()
```

### Test 6: short query passthrough
```python
def test_rewrite_short_query_passthrough():
    """Queries shorter than threshold pass through unchanged."""
    bridge = MemoryBridge()
    result = bridge._rewrite_query("hi")
    assert result == "hi"
```

### Test 7: rewrite falls back on error
```python
def test_rewrite_falls_back_on_api_error(monkeypatch):
    """Rewriting falls back to original on API error."""
    bridge = MemoryBridge()
    # Mock genai to raise exception
    monkeypatch.setattr("google.generativeai.GenerativeModel", Mock(side_effect=Exception("API error")))
    result = bridge._rewrite_query("longer query that should be rewritten")
    assert result == "longer query that should be rewritten"
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/memory_bridge.py`
**Location:** Lines 196-205 - Replace `_call_mcp` stub

**Current Code:**
```python
# memory_bridge.py:196-205
def _call_mcp(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call MCP tool. Subclasses can override for different backends.
    """
    raise NotImplementedError("Override _call_mcp or use MCPMemoryBridge subclass")
```

**Changed Code:**
```python
# memory_bridge.py:196-280 (expanded)
def _call_mcp(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute memory operation by wrapping haios_etl modules."""
    if tool_name == "memory_search_with_experience":
        return self._search_with_experience(params)
    elif tool_name == "ingester_ingest":
        return self._ingest(params)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def _search_with_experience(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute search via ReasoningAwareRetrieval."""
    from pathlib import Path
    import sys
    # Add project root for haios_etl imports
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from haios_etl.database import DatabaseManager
    from haios_etl.extraction import ExtractionManager
    from haios_etl.retrieval import ReasoningAwareRetrieval

    db = DatabaseManager(str(self._db_path))
    extractor = ExtractionManager(self._api_key)
    retrieval = ReasoningAwareRetrieval(db, extractor)

    query = params.get("query", "")
    if self._enable_rewriting:
        query = self._rewrite_query(query)

    result = retrieval.search_with_experience(
        query=query,
        space_id=params.get("space_id"),
        mode=params.get("mode", "semantic")
    )
    return result

def _ingest(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ingest operation via ingester module."""
    from pathlib import Path
    import sys
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from haios_etl.ingester import ingest_content

    result = ingest_content(
        content=params.get("content", ""),
        source_path=params.get("source_path", ""),
        content_type_hint=params.get("content_type_hint", "unknown")
    )
    return {
        "concept_ids": result.get("concept_ids", []),
        "classification": result.get("classification", "unknown"),
        "entity_ids": result.get("entity_ids", [])
    }

def _rewrite_query(self, query: str) -> str:
    """Rewrite conversational query for better retrieval (E2-063)."""
    REWRITE_MIN_LENGTH = 10
    if len(query) < REWRITE_MIN_LENGTH:
        return query

    try:
        import google.generativeai as genai
        if not self._api_key:
            return query

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        prompt = f"""Rewrite this conversational query for semantic search in a technical codebase.
Domain: HAIOS - AI agent orchestration system with concepts like coldstart, checkpoints, memory retrieval, governance hooks, ADRs, backlog items, synthesis.
Remove conversational fluff, expand implicit references, use domain vocabulary.
Return ONLY the rewritten query, no explanation.

Query: {query}"""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Query rewrite failed: {e}, using original query")
        return query
```

### Call Chain Context

```
query() / store()
    |
    +-> _call_mcp_with_retry()
    |       Handles retries on timeout
    |
    +-> _call_mcp()              # <-- What we're implementing
    |       Dispatches to:
    |       ├── _search_with_experience() -> haios_etl.retrieval
    |       └── _ingest() -> haios_etl.ingester
    |
    +-> Returns QueryResult / StoreResult
```

### Function/Component Signatures

```python
def __init__(self,
             work_engine_callback: Optional[Callable] = None,
             db_path: Optional[Path] = None,
             api_key: Optional[str] = None,
             enable_rewriting: bool = True):
    """
    Initialize MemoryBridge.

    Args:
        work_engine_callback: Optional callback to update work items
        db_path: Path to haios_memory.db (default: project_root/haios_memory.db)
        api_key: Google API key for embeddings/rewriting (default: GOOGLE_API_KEY env)
        enable_rewriting: Whether to rewrite queries for better retrieval (default: True)
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Wrap haios_etl vs MCP protocol | Wrap haios_etl directly | MCP is for external tools; MemoryBridge runs in Python same as haios_etl |
| Import inside methods | Yes | Avoids circular imports, allows mocking in tests |
| Query rewriting toggle | enable_rewriting param | Some use cases want raw queries (debugging, testing) |
| Graceful degradation | Return empty on errors | L4 invariant - MUST NOT block on MCP failure |

### Input/Output Examples

**Before (current):**
```python
bridge = MemoryBridge()
bridge.query("test")  # Raises NotImplementedError
```

**After (expected):**
```python
bridge = MemoryBridge(db_path=Path("haios_memory.db"))
result = bridge.query("implementation patterns", mode="knowledge_lookup")
# Returns: QueryResult(concepts=[...], reasoning={strategy_used: ..., learned_from: N})
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Missing GOOGLE_API_KEY | Skip rewriting, use original query | Test 7 |
| Unknown tool name | Raise ValueError | Test 3 |
| Empty query | Pass through, let retrieval handle | N/A (retrieval's concern) |
| Database not found | Raise exception (fail fast) | Integration test |

### Open Questions

**Q: Should MemoryBridge cache DatabaseManager/ExtractionManager instances?**

No for MVP - create fresh instances per call. Caching adds complexity and stateful behavior. The performance hit is acceptable for current usage patterns. Can optimize later if profiling shows bottleneck.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add tests 1-7 to `tests/test_memory_bridge.py`
- [ ] Verify all tests fail (red) - NotImplementedError for dispatch tests

### Step 2: Update __init__ Signature
- [ ] Add `db_path`, `api_key`, `enable_rewriting` parameters
- [ ] Initialize `self._db_path`, `self._api_key`, `self._enable_rewriting`
- [ ] Tests still fail (no _call_mcp implementation yet)

### Step 3: Implement _call_mcp Dispatch
- [ ] Replace NotImplementedError stub with tool dispatch logic
- [ ] Add `_search_with_experience()` and `_ingest()` method stubs
- [ ] Tests 1-3 pass (green)

### Step 4: Implement _search_with_experience
- [ ] Import haios_etl modules inside method
- [ ] Create DatabaseManager, ExtractionManager, ReasoningAwareRetrieval
- [ ] Call search_with_experience and return result
- [ ] Integration test can run (may need real db)

### Step 5: Implement _rewrite_query
- [ ] Add REWRITE_MIN_LENGTH constant
- [ ] Implement short query passthrough
- [ ] Implement Gemini-based rewriting with fallback
- [ ] Tests 6-7 pass (green)

### Step 6: Wire Rewriting into query()
- [ ] Check `self._enable_rewriting` before calling `_rewrite_query`
- [ ] Apply rewriting in `_search_with_experience` before search
- [ ] Tests 4-5 pass (green)

### Step 7: Add Runtime Consumer (CLI + Justfile)
- [ ] Add `cmd_memory_query()` to `.claude/haios/modules/cli.py`
- [ ] Add `memory-query` recipe to `justfile`
- [ ] Verify `just memory-query "test"` works

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new methods
- [ ] **MUST:** Verify README content matches actual file state

### Step 9: Consumer Verification
- [ ] Grep for `MemoryBridge` to verify no outdated usage
- [ ] Verify no stale NotImplementedError references in docs

> **Anti-pattern prevented:** "Ceremonial Completion" - code migrated but consumers still reference old location (see epistemic_state.md)

---

## Verification

- [ ] Tests pass: `pytest tests/test_memory_bridge.py -v`
- [ ] **MUST:** All READMEs current (`.claude/haios/modules/README.md`)
- [ ] Runtime consumer works: `just memory-query "test query"`
- [ ] Full suite passes: `pytest tests/ -v`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| haios_etl API changes | Medium | Import inside functions, not module level |
| Missing GOOGLE_API_KEY | Low | Graceful degradation - skip rewriting |
| Database not found | Medium | Clear error message, fail fast |
| haios_etl/ingester.py may not have ingest_content | Medium | Verify API, may need to use DatabaseManager directly |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/memory_bridge.py` | _call_mcp no longer raises NotImplementedError | [x] | Lines 226-240 |
| `tests/test_memory_bridge.py` | 7 new tests exist and pass | [x] | 21 tests total, 7 new |
| `.claude/haios/modules/README.md` | Documents new methods | [x] | E2-253 section added |
| `.claude/haios/modules/cli.py` | cmd_memory_query() exists | [x] | Line 162 |
| `justfile` | memory-query recipe exists | [x] | Line 184 |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_memory_bridge.py -v
# Expected: 7+ tests passed

just memory-query "test query"
# Expected: Returns results or empty (no error)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (21 passed in 0.77s)
- [x] **Runtime consumer exists** (just memory-query calls cli.py)
- [x] WHY captured (concept IDs 80633-80642)
- [x] **MUST:** READMEs updated in all modified directories
- [x] **MUST:** Consumer verification complete
- [x] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-052 Section 17: Modular Architecture specification
- E2-241: MemoryBridge stub creation
- E2-063: Query rewriting implementation (in memory_retrieval.py)
- ADR-037: Hybrid retrieval modes

---
