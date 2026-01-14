---
template: implementation_plan
status: complete
date: 2025-11-28
title: "ReasoningBank Strategy Extraction Implementation"
backlog_id: PLAN-REASONINGBANK-001
author: Hephaestus
project_phase: Phase 4+ Enhancement
version: "1.1"
---
# generated: 2025-11-29
# System Auto: last updated on: 2025-12-09 18:49:02
# ReasoningBank Strategy Extraction

> **Navigation:** [Quick Reference](#quick-reference) | [Strategic Overview](#strategic-overview) | [Implementation Details](#implementation-details) | [Validation](#validation)

> **Cold Start:** Read this document to understand the ReasoningBank alignment work. For vision context, see @docs/VISION_ANCHOR.md first.

---

## Quick Reference

### Status: COMPLETE

| Item | Status |
|------|--------|
| Migration 006 | APPLIED |
| `extract_strategy()` | IMPLEMENTED |
| Strategy columns in DB | STORED |
| `relevant_strategies` in response | WORKING |
| Tests | 52 passing (+4 new) |
| Live validation | CONFIRMED |

### Key Commands

```bash
# Run tests
python -m pytest tests/test_retrieval.py -v

# Test MCP integration
# Use memory_search_with_experience tool - strategies auto-extracted
```

### Key Files

| File | Purpose |
|------|---------|
| `haios_etl/extraction.py:331-412` | `extract_strategy()` method |
| `haios_etl/retrieval.py:238-294` | `record_reasoning_trace()` with strategy |
| `haios_etl/migrations/006_add_strategy_columns.sql` | Schema migration |
| `tests/test_retrieval.py:170-289` | Strategy extraction tests |

---

## Strategic Overview

### The Problem

The memory system stored WHAT HAPPENED (execution metadata), not WHAT WAS LEARNED (transferable strategies). This violated the ReasoningBank paper's core insight.

### The Solution

After every search operation, use LLM to extract:
- **Success:** "What strategy made this work?"
- **Failure:** "What should be avoided?"

Store as `{title, description, content}` per ReasoningBank paper.

### Architecture

```
User Query
    |
    v
ReasoningBank Lookup -----> Find similar past traces
    |                              |
    v                              v
Execute Search            Return relevant_strategies
    |                     (for prompt injection)
    v
Strategy Extraction (LLM)
    |
    v
Store in reasoning_traces
(strategy_title, strategy_description, strategy_content)
```

### The Two Pillars

| Pillar | Library/Paper | Status |
|--------|---------------|--------|
| **LangExtract** | google/langextract | ALIGNED - entity/concept extraction |
| **ReasoningBank** | arxiv:2509.25140 | ALIGNED - strategy extraction |

---

## Implementation Details

### Database Schema (Migration 006)

```sql
ALTER TABLE reasoning_traces ADD COLUMN strategy_title TEXT;
ALTER TABLE reasoning_traces ADD COLUMN strategy_description TEXT;
ALTER TABLE reasoning_traces ADD COLUMN strategy_content TEXT;
ALTER TABLE reasoning_traces ADD COLUMN extraction_model TEXT;
```

### extract_strategy() Method

Location: `haios_etl/extraction.py:331-412`

```python
def extract_strategy(
    self,
    query: str,
    approach: str,
    outcome: str,
    results_summary: str = "",
    error_details: str = ""
) -> dict:
    """
    Extract transferable strategy from execution outcome.
    Per ReasoningBank paper: stores WHAT WAS LEARNED, not what happened.
    Returns: {title, description, content}
    """
```

**Success Prompt:**
```
Analyze this successful memory search execution.
Extract a HIGH-LEVEL STRATEGY that could help with similar future tasks.
Output JSON: {title, description, content}
```

**Failure Prompt:**
```
Analyze this failed memory search execution.
Extract a PREVENTIVE LESSON to avoid this failure in future.
Output JSON: {title, description, content}
```

### Response Format

```python
{
    'results': [...],
    'reasoning': {
        'strategy_used': 'default_hybrid',
        'learned_from': 1,
        'outcome': 'success',
        'execution_time_ms': 264,
        'relevant_strategies': [
            {
                'title': 'Leverage Diverse Retrieval',
                'content': 'When broad queries return many results...'
            }
        ]
    }
}
```

### Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-005 | Use Gemini for strategy extraction | Same model as ETL |
| DD-006 | Store strategy in same table | Minimal schema change |
| DD-007 | Fallback to structured default on LLM failure | Graceful degradation |

---

## Validation

### Test Results

```
52 passed in 5.56s
```

New tests added:
- `test_extract_strategy_called_on_success`
- `test_extract_strategy_called_on_failure`
- `test_response_includes_relevant_strategies`
- `test_relevant_strategies_empty_when_no_strategy_content`

### Live MCP Validation

```
Query 1: "ReasoningBank strategy extraction"
  learned_from: 0 (no history)
  Strategy extracted: "Leverage Diverse Retrieval for Complex Queries"

Query 2: Same query
  learned_from: 1 (found previous)
  relevant_strategies: ["Leverage Diverse Retrieval..."]
```

---

## Related Documents

### This Document Links To:
- @docs/VISION_ANCHOR.md - Core architectural vision
- @docs/epistemic_state.md - Current system state
- @docs/specs/TRD-ETL-v2.md - ETL specification
- @haios_etl/retrieval.py - Implementation
- @haios_etl/extraction.py - Strategy extraction

### Documents That Link Here:
- @docs/epistemic_state.md - Phase 4+ Enhancement section
- @docs/checkpoints/2025-11-28-SESSION-15-reasoningbank-strategy-extraction.md
- @CLAUDE.md - Key reference locations

---

## Sources

- [ReasoningBank Paper](https://arxiv.org/abs/2509.25140) (Google Research, Sept 2025)
- [LangExtract GitHub](https://github.com/google/langextract)

---

## Appendix: Gap Analysis (Historical)

Before implementation, the gap was:

| Aspect | Paper (ReasoningBank) | Our Implementation | Gap |
|--------|----------------------|-------------------|-----|
| Memory Content | `{title, description, content}` | `{query, approach, outcome}` | CRITICAL |
| Success Processing | LLM extracts strategies | Records `outcome='success'` | CRITICAL |
| Failure Processing | LLM articulates lessons | Records `outcome='failure'` | CRITICAL |

**Root Cause:** Stored WHAT HAPPENED, not WHAT WAS LEARNED.

**Resolution:** Implemented strategy extraction (Session 15, 2025-11-28).
