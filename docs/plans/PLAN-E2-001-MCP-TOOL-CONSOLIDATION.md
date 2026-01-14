---
template: implementation_plan
status: complete
date: 2025-12-08
backlog_id: E2-001
title: "E2-001 MCP Tool Consolidation"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-08
# System Auto: last updated on: 2025-12-08 22:52:38
# Implementation Plan: E2-001 MCP Tool Consolidation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Establish `ingester_ingest` as the de facto MCP tool for memory storage, deprecate `memory_store`, and update all active references across the codebase.

---

## Problem Statement

**Session 47 Finding:** Two MCP tools (`memory_store` and `ingester_ingest`) serve overlapping purposes, causing confusion and maintenance burden.

| Tool | Issues |
|------|--------|
| `memory_store` | Requires manual classification, `metadata` param requires JSON string (not dict), no entity extraction |
| `ingester_ingest` | Auto-classifies, extracts entities, provenance tracking, no parameter issues |

`ingester_ingest` is strictly superior. Consolidation reduces cognitive load and eliminates parameter gotchas.

---

## AODEV TDD Methodology

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
           (tests)            (impl)    (green)
```

**Key Principle:** Write tests BEFORE implementation. Tests define expected behavior.

---

## Phase 1: OBSERVE - Current State

### 1.1 Active Code References
| File | Line | Type | Action Needed |
|------|------|------|---------------|
| `mcp_server.py` | 129-177 | Function def | Add deprecation docstring |
| `new-checkpoint.md` | 29 | Command | Change to `ingester_ingest` |

### 1.2 Documentation References
| File | Type | Action Needed |
|------|------|---------------|
| `memory-agent/SKILL.md` | Skill | Make `ingester_ingest` primary |
| `extract-content/SKILL.md` | Skill | Update reference |
| `CLAUDE.md` | Config | Add deprecation note |
| `MCP_INTEGRATION.md` | Docs | Add deprecation note |
| `.claude/mcp/README.md` | Docs | Add deprecation note |

### 1.3 Test References
| File | Tests | Action |
|------|-------|--------|
| `test_mcp.py` | 3 tests (lines 111-161) | Keep (validates deprecated function) |

---

## Phase 2: ANALYZE - Test Specification (TDD RED)

### 2.1 Deprecation Warning Test
```python
# Test: memory_store returns deprecation warning in response
def test_memory_store_deprecation_warning():
    result = memory_store(content="test", content_type="techne", source_path="test.md")
    assert "deprecated" in result.lower() or "ingester_ingest" in result.lower()
```

### 2.2 Functional Equivalence Tests
```python
# Test: ingester_ingest handles all memory_store use cases
def test_ingester_covers_memory_store_cases():
    # Case 1: Manual classification (episteme)
    result = ingester_ingest(content="fact", source_path="test.md", content_type_hint="episteme")
    assert result.classification == "episteme"

    # Case 2: Manual classification (techne)
    result = ingester_ingest(content="how-to", source_path="test.md", content_type_hint="techne")
    assert result.classification == "techne"

    # Case 3: Auto-classification
    result = ingester_ingest(content="learning", source_path="test.md", content_type_hint="unknown")
    assert result.classification in ["episteme", "techne", "doxa"]
```

### 2.3 Command Migration Test
```python
# Test: /new-checkpoint uses ingester_ingest (manual verification)
# Verify: new-checkpoint.md contains "ingester_ingest" not "memory_store"
```

---

## Phase 3: DECIDE - Design Decisions

### DD-048-01: Soft Deprecation Strategy
**Decision:** Mark `memory_store` as deprecated but do not remove.
**Rationale:** Backward compatibility; existing code continues to work.
**Alternative Rejected:** Hard removal - breaks any external callers.

### DD-048-02: Deprecation Warning Location
**Decision:** Add warning to function docstring AND return value.
**Rationale:** Visible in both IDE hints and runtime output.

### DD-048-03: Skill Documentation Priority
**Decision:** `ingester_ingest` listed FIRST in Related Tools table.
**Rationale:** Primary recommendation should be visually prominent.

### DD-048-04: Test Retention
**Decision:** Keep `test_memory_store_*` tests.
**Rationale:** Validates deprecated function still works (backward compat).

---

## Phase 4: EXECUTE - Implementation

### 4.1 Update `mcp_server.py` - Add Deprecation
```python
@mcp.tool()
def memory_store(...) -> str:
    """
    [DEPRECATED] Store content in memory with Greek Triad classification.

    NOTE: This tool is deprecated. Use `ingester_ingest` instead, which provides:
    - Auto-classification (no manual content_type required)
    - Entity extraction
    - Provenance tracking
    - No metadata JSON string issues

    ...existing docstring...
    """
    # Add deprecation notice to return value
    result = f"[DEPRECATED: Use ingester_ingest instead] {result}"
```

### 4.2 Update `new-checkpoint.md` - Migrate Command
```markdown
# BEFORE
2. Call `mcp__haios-memory__memory_store(content="...", content_type="techne", ...)`

# AFTER
2. Call `mcp__haios-memory__ingester_ingest(content="Checkpoint Session <num>: <summary>", source_path="docs/checkpoints/<filename>", content_type_hint="techne")`
```

### 4.3 Update `memory-agent/SKILL.md` - Reorder and Annotate
```markdown
## Related Tools

| Tool | Purpose |
|------|---------|
| `ingester_ingest` | **PRIMARY** - Auto-classify and store with entity extraction |
| `memory_search_with_experience` | Retrieve context + strategies |
| `memory_stats` | Check memory system status |
| `memory_store` | **DEPRECATED** - Manual classification (use ingester_ingest) |
```

### 4.4 Update `extract-content/SKILL.md` - Replace Reference
```markdown
# BEFORE
4. Use `memory_store` to persist relevant items

# AFTER
4. Use `ingester_ingest` to persist relevant items
```

### 4.5 Update `CLAUDE.md` - Add Deprecation Note
```markdown
| `memory_store` | **DEPRECATED** - Use `ingester_ingest` instead |
```

### 4.6 Update MCP Documentation
- `.claude/mcp/README.md` - Add deprecation note
- `docs/MCP_INTEGRATION.md` - Add deprecation note

---

## Phase 5: VERIFY - Validation

### 5.1 Test Execution
- [ ] All existing tests pass (187/188 pre-existing)
- [ ] New deprecation warning test passes
- [ ] Functional equivalence tests pass

### 5.2 Manual Verification
- [ ] `/new-checkpoint` command works with `ingester_ingest`
- [ ] `memory_store` still functions (backward compat)
- [ ] Deprecation warning visible in `memory_store` output

### 5.3 Documentation Audit
- [ ] `memory-agent/SKILL.md` shows `ingester_ingest` as primary
- [ ] `CLAUDE.md` MCP table has deprecation note
- [ ] No broken references in documentation

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| External callers using `memory_store` | Medium | Soft deprecation - function still works |
| `ingester_ingest` API key missing | Low | Falls back gracefully (existing behavior) |
| Test changes break CI | Low | Keep existing tests, add new ones |

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Deprecation visible | `memory_store` output contains "DEPRECATED" |
| Primary tool clear | `ingester_ingest` first in skill docs |
| Commands migrated | `new-checkpoint.md` uses `ingester_ingest` |
| Tests pass | All 188+ tests green |
| Docs updated | 6 files updated with deprecation notes |

---

## References

- Session 47 Checkpoint: `docs/checkpoints/2025-12-08-03-SESSION-47-adr031-implementation-complete.md`
- Backlog Item: E2-001 (Memory-Governance Integration)
- MCP Server: `haios_etl/mcp_server.py`
- Memory Agent Skill: `.claude/skills/memory-agent/SKILL.md`

---

**Status:** COMPLETE (Session 48)
**Completed:** 2025-12-08

### Implementation Summary
- Phase 2 (TDD RED): 1 test written, confirmed failing
- Phase 4 (EXECUTE): 7 files updated
- Phase 5 (VERIFY): 189/190 tests passing (1 pre-existing failure unrelated)
